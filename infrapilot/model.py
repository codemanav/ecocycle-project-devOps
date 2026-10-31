"""Model client. Backend chosen by INFRAPILOT_MODEL_BACKEND=gemini|ollama (ollama added later)."""
import os, json, re, pathlib
_env = pathlib.Path(__file__).parent / ".env"
if _env.exists():
    for _l in _env.read_text().splitlines():
        if "=" in _l and not _l.startswith("#"):
            _k, _v = _l.split("=", 1); os.environ.setdefault(_k.strip(), _v.strip())

SYSTEM = """You are InfraPilot, an SRE agent for the EcoCycle docker-compose app.
Given evidence (health, container states, filtered error logs) and, if attached, a chart of per-container
CPU % and memory MB over the last 2 minutes, find the ROOT CAUSE. It may be a different container than the
one showing symptoms (e.g. a service is DOWN only because its database is stopped).
Allowed actions:
- start_container {name}: container is stopped/exited
- restart_container {name}: container is hung/unresponsive with no resource or dependency cause
- raise_memory_limit {name, mb}: container OOMKilled or crash-looping on memory (mb <= 1024)
- escalate {reason}: unclear, or none of the above fits
Reply ONLY with JSON: {"root_cause": str, "evidence": [quoted log/state lines or chart observations],
"chart_observation": str (what the chart shows, or "no chart"), "action": str, "params": {...}, "confidence": 0-1}.
If previous attempts are given, do not repeat an action that failed."""

_client = None

def model_id(): return os.environ.get("INFRAPILOT_MODEL", "gemma-4-26b-a4b-it")

def _gemini():
    global _client
    if _client is None:
        from google import genai
        from google.genai import types
        # reads GEMINI_API_KEY; kept module-level so it isn't garbage-collected.
        # Hard timeout so a slow API response can't stall a live incident.
        _client = genai.Client(http_options=types.HttpOptions(
            timeout=int(os.environ.get("INFRAPILOT_TIMEOUT_MS", "120000")),
            retry_options=types.HttpRetryOptions(attempts=1)))
    return _client

def _call(contents, on_thought=None):
    """Stream the reply; Gemma 4 thinks first (~1-2k tokens, not configurable), so we surface
    its thoughts live via on_thought(text_chunk) and parse the JSON answer at the end."""
    from google.genai import types
    cfg = types.GenerateContentConfig(thinking_config=types.ThinkingConfig(include_thoughts=True))
    answer = ""
    for ch in _gemini().models.generate_content_stream(model=model_id(), contents=contents, config=cfg):
        if not ch.candidates or not ch.candidates[0].content:
            continue
        for p in ch.candidates[0].content.parts or []:
            if p.thought:
                if on_thought and p.text: on_thought(p.text)
            else:
                answer += p.text or ""
    m = re.search(r"\{.*\}", answer, re.S)
    return json.loads(m.group(0))

def decide(evidence, previous=None, chart=None, on_thought=None):
    prompt = "EVIDENCE:\n" + json.dumps(evidence, separators=(",", ":"))
    if previous: prompt += "\n\nPREVIOUS ATTEMPTS (failed):\n" + json.dumps(previous, separators=(",", ":"))
    text = SYSTEM + "\nKeep your internal reasoning short: check each container once, then decide.\n\n" + prompt
    if chart:
        from google.genai import types
        try:
            return _call([types.Part.from_bytes(data=chart, mime_type="image/png"), text], on_thought)
        except Exception as e:  # timeout / transient API error / unparsable reply
            if on_thought: on_thought(f"\n\n[multimodal call failed: {type(e).__name__}; retrying text-only]\n\n")
            d = _call([text], on_thought)
            d["note"] = f"multimodal call failed ({type(e).__name__}); decided from text evidence only"
            return d
    try:
        return _call([text], on_thought)
    except Exception as e:
        if on_thought: on_thought(f"\n\n[call failed: {type(e).__name__}; retrying]\n\n")
        return _call([text], on_thought)
