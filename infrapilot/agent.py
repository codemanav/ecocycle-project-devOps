import time, json, pathlib
import core, model, metrics
LOG = pathlib.Path(__file__).parent / "audit.jsonl"

def wait_for_failure(timeout=60):
    """Poll health until something is DOWN (faults like a stopped DB take ~20s to surface)."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        h = core.check_health()
        if core.unhealthy(h):
            return h, round(time.time() - t0, 1)
        time.sleep(2)
    return core.check_health(), round(time.time() - t0, 1)

def run_incident(emit=print, use_chart=True, on_thought=None):
    """One incident: detect -> investigate -> reason -> recover -> verify (one retry).
    emit(step_name, data, seconds) is called after every step; data is bytes for the chart step.
    on_thought(chunk) streams Gemma's reasoning while it thinks; a None chunk marks a new reasoning step."""
    metrics.start()
    def step(name, fn):
        t = time.time(); out = fn(); dt = round(time.time() - t, 1)
        emit(name, out, dt)
        if not isinstance(out, bytes):
            with LOG.open("a") as f:
                f.write(json.dumps({"ts": time.time(), "step": name, "sec": dt, "data": out}, default=str) + "\n")
        return out
    health = step("detect", core.check_health)
    bad = core.unhealthy(health)
    if not bad:
        return {"recovered": True, "note": "nothing wrong"}
    previous, d = [], None
    for attempt in (1, 2):
        ev = step(f"investigate #{attempt}", lambda: core.collect_evidence(bad))
        chart = metrics.chart_png() if use_chart else None
        if chart:
            step(f"chart #{attempt}", lambda: chart)
        if on_thought: on_thought(None)
        d = step(f"reason #{attempt}", lambda: model.decide(ev, previous or None, chart, on_thought))
        ok, why = core.validate(d)
        if not ok:
            step("rejected", lambda: why); return {"recovered": False, "decision": d}
        if d["action"] == "escalate":
            step("escalate", lambda: d["params"]); return {"recovered": False, "decision": d}
        step(f"execute #{attempt}", lambda: core.execute(d))
        good, res = step(f"verify #{attempt}", core.verify)
        if good:
            return {"recovered": True, "decision": d, "verify": res}
        previous.append(d)
        bad = core.unhealthy(core.check_health()) or bad
    return {"recovered": False, "decision": d}
