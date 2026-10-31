"""Ghost Hunter core: detect -> investigate -> (reason, in model.py) -> validate/execute -> verify.

Everything about the system being protected comes from a target YAML (default targets/ecocycle.yaml,
override with GHOSTHUNTER_TARGET). Nothing in this file is specific to EcoCycle.
"""
import json, os, pathlib, re, subprocess, time
import requests, yaml
import actions

HOME = pathlib.Path(__file__).resolve().parent

def load_target(path=None):
    p = pathlib.Path(path or os.environ.get("GHOSTHUNTER_TARGET", HOME / "targets" / "ecocycle.yaml"))
    if not p.is_absolute():
        p = HOME / p
    t = yaml.safe_load(p.read_text())
    comp = t.get("compose") or {}
    t["_compose_dir"] = str((HOME / comp.get("dir", ".")).resolve())
    t["_compose_env"] = {**os.environ, **{k: str(v) for k, v in (comp.get("env") or {}).items()}}
    t["_path"] = str(p)
    return t

TARGET = load_target()
LOG_RE = re.compile(r"ERROR|WARN|Exception|refused|OutOfMemory|Killed|timed out|Timeout", re.I)

def sh(*args, timeout=30):
    r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    return (r.stdout + r.stderr).strip()

# ---- Detect ----
def check_health():
    out = {}
    for name, s in TARGET["services"].items():
        try:
            r = requests.get(s["health"], timeout=3)
            body = r.json() if "json" in r.headers.get("content-type", "") else {}
            up = r.status_code == 200 and body.get("status", "UP") == "UP"
            out[name] = "UP" if up else f"DOWN({r.status_code})"
        except Exception as e:
            out[name] = f"DOWN({type(e).__name__})"
    return out

def unhealthy(h):
    return [k for k, v in h.items() if v != "UP"]

# ---- Investigate ----
def container_state(name):
    raw = sh("docker", "inspect", name)
    try:
        d = json.loads(raw)[0]
    except Exception:
        return {"error": raw[:200]}
    st = d["State"]
    return {"status": st["Status"], "running": st["Running"], "paused": st["Paused"],
            "exit_code": st["ExitCode"], "oom_killed": st["OOMKilled"],
            "restart_count": d["RestartCount"], "memory_limit_mb": (d["HostConfig"]["Memory"] // 2**20) or None,
            "health": st.get("Health", {}).get("Status")}

def filtered_logs(name, tail=400, keep=25):
    """Only WARN/ERROR/exception-ish lines: app logs can be flooded (e.g. SQL logging)."""
    lines = [l for l in sh("docker", "logs", "--tail", str(tail), name).splitlines() if LOG_RE.search(l)]
    return [l[:300] for l in lines[-keep:]]

def collect_evidence(bad_services):
    ev = {"health": check_health(), "containers": {}}
    for c in TARGET["containers"]:
        ev["containers"][c] = {"state": container_state(c)}
    # logs for failing services, their dependencies, and any container that is not running normally
    focus = set(bad_services)
    for s in bad_services:
        focus.update(TARGET["services"].get(s, {}).get("depends_on", []))
    focus.update(c for c, v in ev["containers"].items()
                 if not v["state"].get("running", True) or v["state"].get("paused"))
    for c in focus:
        if c in ev["containers"]:
            ev["containers"][c]["error_logs"] = filtered_logs(c)
    return ev

# ---- Validate / Execute (delegated to the pluggable action registry) ----
def validate(decision):
    return actions.validate(decision, TARGET)

def execute(decision):
    return actions.execute(decision, TARGET)

# ---- Verify ----
def smoke():
    sm = TARGET.get("smoke") or {}
    headers = sm.get("headers") or {}
    results = []
    for s in sm.get("requests", []):
        short = re.sub(r"^https?://[^/]+?(:\d+)", r"\1", s["url"])
        try:
            r = requests.request(s["method"], s["url"], headers=headers, json=s.get("json"), timeout=8)
            results.append((r.status_code < 300, f"{s['method']} {short} -> {r.status_code}"))
        except Exception as e:
            results.append((False, f"{s['method']} {short} -> {type(e).__name__}"))
    return all(ok for ok, _ in results), [d for _, d in results]

def verify(wait=90):
    t0 = time.time()
    while time.time() - t0 < wait:
        h = check_health()
        if not unhealthy(h):
            ok, detail = smoke()
            if ok:
                return True, {"health": h, "smoke": detail, "seconds": round(time.time() - t0, 1)}
        time.sleep(3)
    return False, {"health": check_health(), "smoke": smoke()[1], "seconds": wait}

# ---- Fault injection (demo / test scenarios from the target file) ----
def _run_steps(steps):
    out = []
    for cmd in steps:
        r = subprocess.run([str(c) for c in cmd], cwd=TARGET["_compose_dir"], env=TARGET["_compose_env"],
                           capture_output=True, text=True, timeout=180)
        out.append(f"$ {' '.join(map(str, cmd))} -> {r.returncode}")
    return out

def scenarios():
    return TARGET.get("scenarios") or {}

def inject(key):
    if key == "reset":
        return _run_steps(TARGET.get("reset") or [])
    return _run_steps(scenarios()[key]["inject"])
