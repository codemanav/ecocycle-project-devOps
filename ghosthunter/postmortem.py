"""Gemma-written postmortems, saved as Markdown in ghosthunter/postmortems/."""
import json, pathlib, re, time
import model

DIR = pathlib.Path(__file__).parent / "postmortems"

def _slim(rec):
    """Incident record -> compact data for the prompt (drop bulky evidence, keep what a postmortem needs)."""
    tl = []
    for e in rec["timeline"]:
        d = e["data"]
        if e["step"].startswith("investigate"):
            d = {"health": d.get("health"),
                 "abnormal_containers": {c: v for c, v in d.get("containers", {}).items()
                                         if v["state"].get("status") != "running" or v["state"].get("oom_killed")
                                         or v["state"].get("paused") or v.get("error_logs")}}
            for v in d["abnormal_containers"].values():
                if "error_logs" in v: v["error_logs"] = v["error_logs"][-6:]
        tl.append({"t": e["t"], "step": e["step"], "sec": e["sec"], "data": d})
    return {k: rec.get(k) for k in ("id", "trigger", "model", "symptoms", "recovered", "outcome", "duration")} | \
           {"started": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(rec["started"])), "timeline": tl}

def _fallback(rec, err):
    d = rec.get("decision") or {}
    return (f"# Incident {rec['id']}\n\n**Status:** {'Resolved' if rec.get('recovered') else 'Unresolved'} · "
            f"**Duration:** {rec.get('duration')}s · **Model:** {rec.get('model')}\n\n"
            f"_Postmortem generation failed ({err}); raw summary below._\n\n"
            f"- **Symptoms:** {rec.get('symptoms')}\n- **Root cause:** {d.get('root_cause')}\n"
            f"- **Action:** `{d.get('action')}` `{d.get('params')}`\n- **Outcome:** {rec.get('outcome')}\n")

def write(rec, on_thought=None):
    """Generate and save a postmortem for an incident record. Returns the saved path."""
    DIR.mkdir(exist_ok=True)
    try:
        md = model.write_postmortem(_slim(rec), on_thought)
    except Exception as e:
        md = _fallback(rec, type(e).__name__)
    title = re.search(r"^#\s+(.+)$", md, re.M)
    slug = re.sub(r"[^a-z0-9]+", "-", (title.group(1) if title else "incident").lower()).strip("-")[:50]
    path = DIR / f"{rec['id']}-{slug}.md"
    if rec.get("charts"):
        img = path.with_suffix(".png")
        img.write_bytes(rec["charts"][0])
        md += f"\n\n## Metrics at diagnosis time\n\n![Metrics chart Gemma saw]({img.name})\n"
    md += (f"\n\n---\n<details><summary>Raw decision JSON</summary>\n\n```json\n"
           f"{json.dumps(rec.get('decisions'), indent=1, default=str)}\n```\n</details>\n"
           f"\n_Written by Ghost Hunter with {rec.get('model')}._\n")
    path.write_text(md)
    return path

def list_all():
    return sorted(DIR.glob("*.md"), reverse=True) if DIR.exists() else []
