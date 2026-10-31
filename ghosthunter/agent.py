import fcntl, time, json, pathlib, threading
import core, model, metrics
LOG = pathlib.Path(__file__).parent / "audit.jsonl"
# Only one remediation may run at a time: a thread lock within this process, plus a lock file so a
# UI watcher, a headless watcher and the CLI never act on the same incident concurrently.
INCIDENT_LOCK = threading.Lock()
LOCK_FILE = pathlib.Path(__file__).parent / ".incident.lock"

class Busy(Exception):
    """Another Ghost Hunter (thread or process) is already handling an incident."""

def wait_for_failure(timeout=60):
    """Poll health until something is DOWN (faults like a stopped DB take ~20s to surface)."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        h = core.check_health()
        if core.unhealthy(h):
            return h, round(time.time() - t0, 1)
        time.sleep(2)
    return core.check_health(), round(time.time() - t0, 1)

def run_incident(emit=print, use_chart=True, on_thought=None, trigger="manual"):
    """One incident: detect -> investigate -> reason -> recover -> verify (one retry).
    emit(step_name, data, seconds) is called after every step; data is bytes for the chart step.
    on_thought(chunk) streams Gemma's reasoning while it thinks; a None chunk marks a new reasoning step.
    Returns a record with the full timeline (used for the postmortem)."""
    if not INCIDENT_LOCK.acquire(blocking=False):
        raise Busy("another incident is being handled in this process")
    try:
        with open(LOCK_FILE, "w") as lf:
            try:
                fcntl.flock(lf, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise Busy("another Ghost Hunter process is handling an incident")
            try:
                return _run(emit, use_chart, on_thought, trigger)
            finally:
                fcntl.flock(lf, fcntl.LOCK_UN)
    finally:
        INCIDENT_LOCK.release()

def _run(emit, use_chart, on_thought, trigger):
    metrics.boost()
    rec = {"id": time.strftime("%Y%m%d-%H%M%S"), "trigger": trigger, "model": model.describe(),
           "started": time.time(), "timeline": [], "decisions": [], "charts": []}

    def step(name, fn):
        t = time.time(); out = fn(); dt = round(time.time() - t, 1)
        emit(name, out, dt)
        if isinstance(out, bytes):
            rec["charts"].append(out)
        else:
            rec["timeline"].append({"t": round(t - rec["started"], 1), "step": name, "sec": dt, "data": out})
            with LOG.open("a") as f:
                f.write(json.dumps({"ts": time.time(), "incident": rec["id"], "step": name, "sec": dt, "data": out},
                                   default=str) + "\n")
        return out

    def done(recovered, **kw):
        rec.update(recovered=recovered, ended=time.time(), **kw)
        rec["duration"] = round(rec["ended"] - rec["started"], 1)
        return rec

    health = step("detect", core.check_health)
    bad = core.unhealthy(health)
    rec["symptoms"] = {k: v for k, v in health.items() if v != "UP"}
    if not bad:
        return done(True, note="nothing wrong")
    previous, d = [], None
    for attempt in (1, 2):
        ev = step(f"investigate #{attempt}", lambda: core.collect_evidence(bad))
        chart = metrics.chart_png() if use_chart else None
        if chart:
            step(f"chart #{attempt}", lambda: chart)
        if on_thought: on_thought(None)
        def reason():
            try:
                return model.decide(ev, previous or None, chart, on_thought)
            except Exception as e:  # API down and no local fallback: never act blind, hand off to a human
                return {"root_cause": "unknown: no model available to diagnose", "evidence": [],
                        "action": "escalate", "confidence": 0,
                        "params": {"reason": f"model unavailable ({type(e).__name__}: {str(e)[:120]})"}}
        d = step(f"reason #{attempt}", reason)
        rec["decisions"].append(d)
        ok, why = core.validate(d)
        if not ok:
            step("rejected", lambda: why); return done(False, decision=d, outcome=f"rejected by allowlist: {why}")
        if d["action"] == "escalate":
            step("escalate", lambda: d["params"]); return done(False, decision=d, outcome="escalated to a human")
        step(f"execute #{attempt}", lambda: core.execute(d))
        good, res = step(f"verify #{attempt}", core.verify)
        if good:
            return done(True, decision=d, verify=res, outcome="recovered and verified")
        previous.append(d)
        bad = core.unhealthy(core.check_health()) or bad
    return done(False, decision=d, outcome="not recovered after 2 attempts")
