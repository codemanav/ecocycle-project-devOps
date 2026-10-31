"""Model client with two interchangeable backends, chosen by GHOSTHUNTER_MODEL_BACKEND:
  gemini (default) - Gemma 4 via the Gemini API (GHOSTHUNTER_MODEL, default gemma-4-26b-a4b-it)
  ollama           - open-weight Gemma 4 running locally (OLLAMA_MODEL, default gemma4:e4b);
                     incident data never leaves the machine."""
import os, json, re, pathlib, time
_env = pathlib.Path(__file__).parent / ".env"
if _env.exists():
    for _l in _env.read_text().splitlines():
        if "=" in _l and not _l.startswith("#"):
            _k, _v = _l.split("=", 1); os.environ.setdefault(_k.strip(), _v.strip())

def system_prompt():
    """Built from the target file and the action registry, so a new target or action needs no prompt edits."""
    import core, actions
    t = core.TARGET
    graph = "\n".join(f"- {e}" for e in t.get("call_graph") or []) or "- (not provided)"
    return f"""You are Ghost Hunter, an SRE agent for the {t['name']} docker-compose app.
{(t.get('description') or '').strip()}
Call graph / dependencies:
{graph}
Given evidence (health, container states, filtered error logs) and, if attached, a chart of per-container
CPU % and memory MB over the last 2 minutes, find the ROOT CAUSE. It may be a different container than the
one showing symptoms (e.g. a service is DOWN only because its database is stopped).
Allowed actions (container names must come from the evidence):
{actions.prompt_block(t)}
Reply ONLY with JSON: {{"root_cause": str, "evidence": [quoted log/state lines or chart observations],
"chart_observation": str (what the chart shows, or "no chart"), "action": str, "params": {{...}}, "confidence": 0-1}}.
If previous attempts are given, do not repeat an action that failed."""

_client = None

def deadline(): return int(os.environ.get("GHOSTHUNTER_DEADLINE_S", "150"))

def backend(): return os.environ.get("GHOSTHUNTER_MODEL_BACKEND", "gemini").lower()

def model_id():
    if backend() == "ollama":
        return os.environ.get("OLLAMA_MODEL", "gemma4:e4b")
    return os.environ.get("GHOSTHUNTER_MODEL", "gemma-4-26b-a4b-it")

def describe(): return f"{model_id()} ({'local, Ollama' if backend() == 'ollama' else 'Gemini API'})"

def _gemini():
    global _client
    if _client is None:
        from google import genai
        from google.genai import types
        # reads GEMINI_API_KEY; kept module-level so it isn't garbage-collected.
        # Hard timeout so a slow API response can't stall a live incident.
        _client = genai.Client(http_options=types.HttpOptions(
            timeout=int(os.environ.get("GHOSTHUNTER_TIMEOUT_MS", "120000")),
            retry_options=types.HttpRetryOptions(attempts=1)))
    return _client

def _parse(answer):
    m = re.search(r"\{.*\}", answer, re.S)
    if not m:
        raise ValueError(f"no JSON in model reply: {answer[:200]!r}")
    return json.loads(m.group(0))

def _call_ollama(text, chart=None, on_thought=None, raw=False):
    """Stream from a local Ollama server. Thinking arrives in message.thinking, the answer in message.content."""
    import base64, requests
    msg = {"role": "user", "content": text}
    if chart:
        msg["images"] = [base64.b64encode(chart).decode()]
    url = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/") + "/api/chat"
    body = {"model": model_id(), "messages": [msg], "stream": True, "think": True,
            "options": {"temperature": 0.2, "num_ctx": int(os.environ.get("OLLAMA_NUM_CTX", "8192"))}, "keep_alive": "30m"}
    timeout = int(os.environ.get("GHOSTHUNTER_TIMEOUT_MS", "120000")) / 1000
    answer, t0 = "", time.time()
    with requests.post(url, json=body, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line:
                continue
            ev = json.loads(line)
            if ev.get("error"):
                raise RuntimeError(ev["error"])
            if time.time() - t0 > deadline():
                raise TimeoutError(f"model call exceeded {deadline()}s")
            m = ev.get("message") or {}
            if m.get("thinking") and on_thought:
                on_thought(m["thinking"])
            answer += m.get("content") or ""
    return answer if raw else _parse(answer)

def _call(contents, on_thought=None, raw=False):
    """Stream the reply; Gemma 4 thinks first (~1-2k tokens, not configurable), so we surface
    its thoughts live via on_thought(text_chunk) and parse the JSON answer at the end."""
    from google.genai import types
    cfg = types.GenerateContentConfig(thinking_config=types.ThinkingConfig(include_thoughts=True))
    answer, t0 = "", time.time()
    for ch in _gemini().models.generate_content_stream(model=model_id(), contents=contents, config=cfg):
        if time.time() - t0 > deadline():
            raise TimeoutError(f"model call exceeded {deadline()}s")
        if not ch.candidates or not ch.candidates[0].content:
            continue
        for p in ch.candidates[0].content.parts or []:
            if p.thought:
                if on_thought and p.text: on_thought(p.text)
            else:
                answer += p.text or ""
    return answer if raw else _parse(answer)

def _ask(text, chart, on_thought):
    if backend() == "ollama":
        return _call_ollama(text, chart, on_thought)
    if chart:
        from google.genai import types
        return _call([types.Part.from_bytes(data=chart, mime_type="image/png"), text], on_thought)
    return _call([text], on_thought)

def decide(evidence, previous=None, chart=None, on_thought=None):
    prompt = "EVIDENCE:\n" + json.dumps(evidence, separators=(",", ":"))
    if previous: prompt += "\n\nPREVIOUS ATTEMPTS (failed):\n" + json.dumps(previous, separators=(",", ":"))
    text = system_prompt() + "\nKeep your internal reasoning short: check each container once, then decide.\n\n" + prompt
    if chart:
        try:
            return _ask(text, chart, on_thought)
        except Exception as e:  # timeout / transient API error / unparsable reply
            if on_thought: on_thought(f"\n\n[multimodal call failed: {type(e).__name__}; retrying text-only]\n\n")
            d = _ask(text, None, on_thought)
            d["note"] = f"multimodal call failed ({type(e).__name__}); decided from text evidence only"
            return d
    try:
        return _ask(text, None, on_thought)
    except Exception as e:
        if on_thought: on_thought(f"\n\n[call failed: {type(e).__name__}; retrying]\n\n")
        return _ask(text, None, on_thought)


POSTMORTEM = """You are Ghost Hunter, an SRE agent. Write a concise blameless postmortem in Markdown for the incident
below, which you (Ghost Hunter, using Gemma 4) detected and handled autonomously. Use exactly these sections:
# <short incident title>
**Status:** Resolved/Unresolved · **Duration:** Ns · **Detected by:** ... · **Model:** ...
## Summary            (2-3 sentences)
## Impact             (which services/endpoints were down and for how long)
## Timeline           (markdown table: T+seconds | event; use the timeline data, keep it to the key steps)
## Root cause         (cite the specific evidence: log lines, container state, chart observations)
## Resolution         (the action taken and how recovery was verified)
## Why not a naive restart?   (what a fixed "restart the unhealthy service" rule would have done here)
## Follow-ups         (3-5 concrete preventive actions as a checklist, e.g. alerts, limits, timeouts, health checks)
Only use facts from the incident data; do not invent numbers. Reply with the Markdown only, no code fences.

INCIDENT DATA:
"""

def write_postmortem(incident, on_thought=None):
    text = POSTMORTEM + json.dumps(incident, default=str, separators=(",", ":"))[:20000]
    if backend() == "ollama":
        md = _call_ollama(text, None, on_thought, raw=True)
    else:
        md = _call([text], on_thought, raw=True)
    return re.sub(r"^```(?:markdown|md)?\s*|\s*```\s*$", "", md.strip())
