"""Pluggable remediation actions.

Each action is a function registered with @action. The registry drives three things at once:
  1. the list of actions (and when to use them) given to the model in its system prompt,
  2. validation of the model's decision (params + guards) before anything runs,
  3. execution.
A target enables a subset of actions in its YAML (`actions:`), optionally with per-target limits.

To add an action: write a function below with @action(...), then enable it in your target YAML.
"""
import subprocess
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class Action:
    name: str
    params: dict          # param name -> type (str/int)
    when: str             # guidance for the model: when is this the right action?
    run: Callable         # run(params, target, limits) -> str
    guard: Callable = None  # guard(params, target, limits) -> error str or None
    needs_container: bool = True

REGISTRY: dict[str, Action] = {}

def action(name, params, when, needs_container=True, guard=None):
    def deco(fn):
        REGISTRY[name] = Action(name, params, when, fn, guard, needs_container)
        return fn
    return deco

def sh(*args, timeout=90):
    r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    return (r.stdout + r.stderr).strip()

# ---------------- built-in actions ----------------

@action("start_container", {"name": str}, "the container is stopped / exited")
def _start(p, target, limits):
    sh("docker", "unpause", p["name"])
    return sh("docker", "start", p["name"])

@action("restart_container", {"name": str},
        "the container is running but hung / unresponsive, with no resource or dependency cause")
def _restart(p, target, limits):
    sh("docker", "unpause", p["name"])
    return sh("docker", "restart", p["name"])

def _mem_guard(p, target, limits):
    mx = limits.get("max_mb", 1024)
    if not isinstance(p.get("mb"), int) or not 64 <= p["mb"] <= mx:
        return f"mb must be an integer in 64..{mx}"

@action("raise_memory_limit", {"name": str, "mb": int},
        "the container was OOMKilled or is crash-looping on memory (mb <= the target's max)", guard=_mem_guard)
def _raise_mem(p, target, limits):
    mb = f"{p['mb']}m"
    out = sh("docker", "update", "--memory", mb, "--memory-swap", mb, p["name"])
    return out + " | " + sh("docker", "restart", p["name"])

@action("escalate", {"reason": str}, "the cause is unclear, or no other enabled action fits", needs_container=False)
def _escalate(p, target, limits):
    return f"ESCALATED to a human: {p.get('reason')}"

# ---------------- used by the core loop ----------------

def enabled(target):
    return {n: (lim or {}) for n, lim in (target.get("actions") or {}).items() if n in REGISTRY}

def prompt_block(target):
    lines = []
    for n, lim in enabled(target).items():
        a = REGISTRY[n]
        ps = ", ".join(a.params)
        lines.append(f"- {n} {{{ps}}}: {a.when}" + (f" (limits: {lim})" if lim else ""))
    return "\n".join(lines)

def validate(decision, target):
    name, p = decision.get("action"), decision.get("params") or {}
    acts = enabled(target)
    if name not in acts:
        return False, f"action {name!r} is not enabled for {target['name']}"
    a = REGISTRY[name]
    if a.needs_container and p.get("name") not in target["containers"]:
        return False, f"container {p.get('name')!r} is not in the {target['name']} allowlist"
    for k, typ in a.params.items():
        if k not in p or not isinstance(p[k], typ):
            return False, f"param {k!r} missing or not {typ.__name__}"
    if a.guard and (err := a.guard(p, target, acts[name])):
        return False, err
    return True, "ok"

def execute(decision, target):
    name = decision["action"]
    return REGISTRY[name].run(decision.get("params") or {}, target, enabled(target)[name])
