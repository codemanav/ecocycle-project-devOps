"""Night watch: continuous, event-driven incident response — no button press.

Triggers (whichever comes first):
  1. Docker events for the target's containers (die, oom, kill, stop, pause, unhealthy). Pushed by the
     Docker daemon, so waiting for them costs nothing. Each one wakes the watcher immediately and starts
     an alert window of fast health polls (dependency failures take ~20 s to show up in health checks).
  2. A slow fallback health poll (default every 30 s) for failures that produce no Docker event,
     e.g. an app that hangs or starts returning errors while its container keeps running.
A failure must be seen on `confirm` consecutive polls before Ghost Hunter acts.

Headless:  python watch.py [--slow 30] [--fast 3] [--no-events] [--no-chart]
In the UI: a Watcher thread is started from app.py and its .state is rendered live.
"""
import argparse, json, signal, subprocess, threading, time
import agent, core, metrics, postmortem

TRIGGER_ACTIONS = {"die", "oom", "kill", "stop", "pause", "health_status: unhealthy"}

class Watcher:
    def __init__(self, slow_interval=30, fast_interval=3, alert_window=90, confirm=2, cooldown=20, backoff=300,
                 use_events=True, use_chart=True, log=None):
        self.slow, self.fast, self.alert_window = slow_interval, fast_interval, alert_window
        self.confirm, self.cooldown, self.backoff = confirm, cooldown, backoff
        self.use_events, self.use_chart = use_events, use_chart
        self.log = log or (lambda msg: None)
        self._stop = threading.Event()
        self._wake = threading.Event()
        self._alert_until = 0.0
        self._events_proc = None
        self.polls = 0
        self._thread = None
        self.lock = threading.Lock()  # guards .state for readers in other threads
        self.state = {"status": "stopped", "health": {}, "last_poll": None, "streak": 0,
                      "current": None, "thought": "", "incidents": [], "events": []}

    # ---- lifecycle ----
    @property
    def running(self):
        return self._thread is not None and self._thread.is_alive()

    def start(self):
        if not self.running:
            self._stop.clear()
            self._thread = threading.Thread(target=self._loop, daemon=True, name="ghosthunter-watch")
            self._thread.start()

    def stop(self):
        self._stop.set(); self._wake.set()
        if self._events_proc:
            self._events_proc.terminate()

    # ---- Docker event listener ----
    def _listen(self):
        names = core.TARGET["containers"]
        cmd = ["docker", "events", "--format", "{{json .}}", "--filter", "type=container"]
        for n in names:
            cmd += ["--filter", f"container={n}"]
        last = {}
        while not self._stop.is_set():
            try:
                self._events_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
                for line in self._events_proc.stdout:
                    try:
                        ev = json.loads(line)
                    except ValueError:
                        continue
                    action = ev.get("Action") or ev.get("status") or ""
                    name = (ev.get("Actor") or {}).get("Attributes", {}).get("name", "?")
                    if action not in TRIGGER_ACTIONS:
                        continue
                    self._alert_until = time.time() + self.alert_window
                    metrics.boost()
                    if time.time() - last.get(name, 0) > 5:  # die/kill/stop arrive together: log once
                        self._event(f"📡 docker event: {name} {action}, checking now")
                    last[name] = time.time()
                    self._wake.set()
            except Exception as e:
                self._event(f"📡 docker events unavailable ({type(e).__name__}); relying on polling")
            self._stop.wait(5)  # stream ended (daemon restart?): reconnect

    # ---- helpers ----
    def _event(self, msg):
        with self.lock:
            self.state["events"].append((time.strftime("%H:%M:%S"), msg))
            self.state["events"] = self.state["events"][-50:]
        self.log(msg)

    def _set(self, **kw):
        with self.lock:
            self.state.update(kw)

    # ---- main loop ----
    def _loop(self):
        metrics.set_background(True)
        self._set(status="watching")
        if self.use_events:
            threading.Thread(target=self._listen, daemon=True, name="ghosthunter-events").start()
        self._event(f"👀 night watch on: {'listening for Docker events + ' if self.use_events else ''}"
                    f"health check every {self.slow}s (every {self.fast}s when something looks wrong); "
                    f"acting after {self.confirm} failed checks")
        suppressed = {}  # frozenset(symptoms) -> until-ts, after an incident we could not fix
        streak = 0
        while not self._stop.is_set():
            self.polls += 1
            h = core.check_health()
            bad = core.unhealthy(h)
            streak = streak + 1 if bad else 0
            self._set(health=h, last_poll=time.time(), streak=streak)
            if bad and streak == 1:
                self._event(f"⚠️ unhealthy: {', '.join(f'{k}={h[k]}' for k in bad)} — confirming…")
            key = frozenset(bad)
            if bad and streak >= self.confirm:
                if suppressed.get(key, 0) > time.time():
                    pass  # already escalated this exact failure; don't hammer it
                else:
                    rec = self._handle(bad)
                    streak = 0
                    if not rec.get("recovered"):
                        suppressed[key] = time.time() + self.backoff
                        self._event(f"🙋 escalated; will not retry the same failure for {self.backoff}s")
                    self._stop.wait(self.cooldown)
                    continue
            alert = bool(bad) or time.time() < self._alert_until
            self._wake.wait(self.fast if alert else self.slow)
            self._wake.clear()
        metrics.set_background(False)
        self._set(status="stopped")
        self._event("⏹ night watch off")

    def _handle(self, bad):
        self._event(f"🚨 incident confirmed ({', '.join(bad)}) — Ghost Hunter taking over")
        cur = {"steps": [], "started": time.time(), "phase": "investigating", "postmortem": None}
        self._set(status="incident", current=cur, thought="")

        def emit(name, data, dt):
            with self.lock:
                cur["steps"].append((name, data, dt))
                cur["phase"] = name
            if name.startswith("reason") and isinstance(data, dict):
                self._event(f"🧠 Gemma: {data.get('action')} {data.get('params')} — {data.get('root_cause')}")
            elif name.startswith("verify"):
                ok, res = data
                self._event(f"{'✅ recovered' if ok else '❌ not recovered'} (verify {res['seconds']}s)")

        def on_thought(chunk):
            with self.lock:
                self.state["thought"] = "" if chunk is None else (self.state["thought"] + chunk)[-4000:]

        try:
            rec = agent.run_incident(emit, use_chart=self.use_chart, on_thought=on_thought, trigger="watch mode")
        except agent.Busy as e:
            self._event(f"⏸ {e}; standing by")
            self._set(status="watching", current=None, thought="")
            return {"recovered": True, "note": "busy"}
        except Exception as e:
            self._event(f"💥 agent error: {type(e).__name__}: {e}")
            rec = {"id": time.strftime("%Y%m%d-%H%M%S"), "recovered": False, "timeline": [], "charts": [],
                   "outcome": f"agent error: {e}", "started": cur["started"], "duration": 0, "symptoms": bad}

        if rec.get("note") == "nothing wrong":  # recovered on its own before we looked: not an incident
            self._event("🌫 false alarm — healthy again by the time Ghost Hunter looked; no postmortem")
            self._set(status="watching", current=None, thought="")
            return rec
        with self.lock:
            cur["phase"] = "writing postmortem"
            self.state["thought"] = ""
        self._event("📝 Gemma is writing the postmortem…")
        path = postmortem.write(rec, on_thought=on_thought)
        self._event(f"📝 postmortem saved: postmortems/{path.name}")
        with self.lock:
            cur.update(phase="done", postmortem=str(path), recovered=rec.get("recovered"),
                       duration=rec.get("duration"))
            self.state["incidents"].insert(0, cur)
            self.state["incidents"] = self.state["incidents"][:20]
            self.state["thought"] = ""
            self.state["status"] = "watching"
        return rec

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Ghost Hunter night watch")
    ap.add_argument("--slow", type=float, default=30, help="health-check interval when all is quiet")
    ap.add_argument("--fast", type=float, default=3, help="interval while something looks wrong")
    ap.add_argument("--no-events", action="store_true", help="don't listen for Docker events (poll only)")
    ap.add_argument("--no-chart", action="store_true")
    a = ap.parse_args()
    w = Watcher(slow_interval=a.slow, fast_interval=a.fast, use_events=not a.no_events, use_chart=not a.no_chart,
                log=lambda m: print(time.strftime("%H:%M:%S"), m, flush=True))
    # stop cleanly on SIGTERM (launchd/systemd/docker stop) as well as Ctrl-C
    signal.signal(signal.SIGTERM, lambda *_: w.stop())
    signal.signal(signal.SIGINT, signal.default_int_handler)
    w.start()
    try:
        while w.running:
            time.sleep(1)
    except KeyboardInterrupt:
        w.stop(); time.sleep(1)
    print(f"health checks: {w.polls} · docker stats samples: {metrics.samples}", flush=True)
