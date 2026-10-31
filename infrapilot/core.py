"""InfraPilot core: detect -> investigate -> (reason in model.py) -> validate/execute -> verify."""
import json, re, subprocess, time, yaml, requests, pathlib

CFG = yaml.safe_load((pathlib.Path(__file__).parent / "config.yaml").read_text())
ALLOWED = set(CFG["containers"])
LOG_RE = re.compile(r"ERROR|WARN|Exception|refused|OutOfMemory|Killed|timed out|Timeout", re.I)

def sh(*args, timeout=30):
    r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    return (r.stdout + r.stderr).strip()

# ---- Detect ----
def check_health():
    out = {}
    for name, s in CFG["services"].items():
        try:
            r = requests.get(s["health"], timeout=3)
            out[name] = "UP" if r.status_code == 200 and r.json().get("status") == "UP" else f"DOWN({r.status_code})"
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
    lines = [l for l in sh("docker", "logs", "--tail", str(tail), name).splitlines() if LOG_RE.search(l)]
    return [l[:300] for l in lines[-keep:]]

def collect_evidence(bad_services):
    ev = {"health": check_health(), "containers": {}}
    for c in CFG["containers"]:
        st = container_state(c)
        ev["containers"][c] = {"state": st}
    # logs for failing services, their dependencies, and any non-running container
    focus = set(bad_services)
    for s in bad_services:
        focus.update(CFG["services"].get(s, {}).get("depends_on", []))
    focus.update(c for c, v in ev["containers"].items() if not v["state"].get("running", True) or v["state"].get("paused"))
    for c in focus:
        if c in ev["containers"]:
            ev["containers"][c]["error_logs"] = filtered_logs(c)
    return ev

# ---- Validate / Execute ----
def validate(decision):
    a, p = decision.get("action"), decision.get("params") or {}
    if a == "escalate":
        return True, "ok"
    if a in ("start_container", "restart_container", "raise_memory_limit"):
        if p.get("name") not in ALLOWED:
            return False, f"container {p.get('name')!r} not in allowlist"
        if a == "raise_memory_limit":
            mb = p.get("mb")
            if not isinstance(mb, int) or not (64 <= mb <= CFG["max_memory_mb"]):
                return False, f"mb must be int in 64..{CFG['max_memory_mb']}"
        return True, "ok"
    return False, f"action {a!r} not allowed"

def execute(decision):
    a, p = decision["action"], decision.get("params") or {}
    n = p.get("name")
    if a == "escalate":
        return f"ESCALATED: {p.get('reason', decision.get('root_cause'))}"
    if a == "start_container":
        sh("docker", "unpause", n); return sh("docker", "start", n)
    if a == "restart_container":
        sh("docker", "unpause", n); return sh("docker", "restart", n, timeout=90)
    if a == "raise_memory_limit":
        mb = f"{p['mb']}m"
        out = sh("docker", "update", "--memory", mb, "--memory-swap", mb, n)
        return out + " | " + sh("docker", "restart", n, timeout=90)

# ---- Verify ----
def smoke():
    results = []
    for s in CFG["smoke"]:
        try:
            r = requests.request(s["method"], s["url"], headers={"Authorization": "Bearer x"}, json=s.get("json"), timeout=8)
            results.append((r.status_code < 300, f"{s['method']} {s['url'].split('localhost')[1]} -> {r.status_code}"))
        except Exception as e:
            results.append((False, f"{s['method']} {s['url']} -> {type(e).__name__}"))
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
