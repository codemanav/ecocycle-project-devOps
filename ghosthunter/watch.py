"""Continuous watch mode: poll health, and when a failure is confirmed, run the full
detect -> investigate -> reason -> recover -> verify loop and write a postmortem — no button press.

Headless:  python watch.py [--interval 5] [--no-chart]
In the UI: a Watcher thread is started from app.py and its .state is rendered live.
"""
import argparse, threading, time
import agent, core, metrics, postmortem

class Watcher:
    def __init__(self, interval=5, confirm=2, cooldown=20, backoff=300, use_chart=True, log=None):
        self.interval, self.confirm, self.cooldown, self.backoff = interval, confirm, cooldown, backoff
        self.use_chart = use_chart
        self.log = log or (lambda msg: None)
        self._stop = threading.Event()
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
        self._stop.set()

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
        metrics.start()
        self._set(status="watching")
        self._event(f"👀 watch mode on — polling every {self.interval}s, acting after {self.confirm} failed polls")
        suppressed = {}  # frozenset(symptoms) -> until-ts, after an incident we could not fix
        streak = 0
        while not self._stop.is_set():
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
            self._stop.wait(self.interval)
        self._set(status="stopped")
        self._event("⏹ watch mode off")

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
    ap = argparse.ArgumentParser(description="Ghost Hunter continuous watch mode")
    ap.add_argument("--interval", type=float, default=5)
    ap.add_argument("--no-chart", action="store_true")
    a = ap.parse_args()
    w = Watcher(interval=a.interval, use_chart=not a.no_chart,
                log=lambda m: print(time.strftime("%H:%M:%S"), m, flush=True))
    w.start()
    try:
        while w.running:
            time.sleep(1)
    except KeyboardInterrupt:
        w.stop(); time.sleep(1)
