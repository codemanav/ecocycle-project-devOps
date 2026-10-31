import os, re, time, pathlib
import streamlit as st
import agent, core, model, metrics, postmortem
from watch import Watcher

st.set_page_config(page_title="Ghost Hunter", page_icon="🎃", layout="wide")
metrics.start()  # sample docker stats from app start so the chart has history

# ---------------- Halloween styling ----------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Creepster&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
:root { --pumpkin:#ff7518; --hex:#a855f7; --bone:#ece4d9; --ink:#0b0a10; --crypt:#1a1424; --slime:#7CFC00; }
.stApp {
  background:
    radial-gradient(1200px 500px at 85% -10%, rgba(168,85,247,.18), transparent 60%),
    radial-gradient(900px 400px at -10% 110%, rgba(255,117,24,.12), transparent 60%),
    var(--ink);
}
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.gh-title { font-family:'Creepster', cursive; font-size:4.2rem; line-height:1; margin:0;
  color:var(--pumpkin); letter-spacing:2px;
  text-shadow: 0 0 18px rgba(255,117,24,.55), 0 0 40px rgba(168,85,247,.35); }
.gh-sub { color:#b9a9c9; margin:.35rem 0 1.2rem 0; font-size:1.02rem; }
.gh-sub b { color:var(--bone); }
.gh-ghost { display:inline-block; animation: float 3.2s ease-in-out infinite; }
.gh-bat { display:inline-block; animation: flap 1.4s ease-in-out infinite; opacity:.85; }
@keyframes float { 0%,100% { transform: translateY(0) } 50% { transform: translateY(-10px) } }
@keyframes flap { 0%,100% { transform: translateY(0) rotate(-6deg) } 50% { transform: translateY(-6px) rotate(6deg) } }
h2, h3, h4 { color: var(--bone) !important; }
div[data-testid="stVerticalBlockBorderWrapper"] { border-color: rgba(168,85,247,.45) !important;
  box-shadow: 0 0 22px rgba(168,85,247,.12); }
.stButton > button { border:1px solid rgba(255,117,24,.55); background:linear-gradient(180deg,#22182c,#140f1b);
  color:var(--bone); transition: all .15s ease; }
.stButton > button:hover { border-color:var(--pumpkin); color:#fff; box-shadow:0 0 14px rgba(255,117,24,.5); }
.stTabs [data-baseweb="tab"] { font-weight:600; }
.stTabs [aria-selected="true"] { color: var(--pumpkin) !important; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg,#140f1b,#0b0a10); border-right:1px solid #2a2036; }
div[data-testid="stMetric"] { background:var(--crypt); border:1px solid #2a2036; border-radius:10px; padding:.5rem .8rem; }
code { color: #ffb37a !important; }
.gh-foot { color:#6f6280; font-size:.8rem; margin-top:2rem; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_watcher():
    return Watcher(interval=5)

watcher = get_watcher()

# ---------------- sidebar ----------------
st.sidebar.markdown("### 🕯️ Hunt settings")
_choices = {"🔮 Gemma 4 · Gemini API": "gemini", "🔒 Gemma 4 · local open-weight (Ollama)": "ollama"}
_cur = [k for k, v in _choices.items() if v == model.backend()][0]
_pick = st.sidebar.radio("Model backend", list(_choices), index=list(_choices).index(_cur))
os.environ["GHOSTHUNTER_MODEL_BACKEND"] = _choices[_pick]
if model.backend() == "ollama":
    st.sidebar.caption("Runs fully on this machine. Incident logs never leave your network.")
use_chart = st.sidebar.toggle("📈 Send metrics chart to Gemma (multimodal)", value=True)
watcher.use_chart = use_chart
st.sidebar.divider()
watch_on = st.sidebar.toggle("🌙 Night watch (autonomous)", value=watcher.running,
                             help="Ghost Hunter polls health every 5s, hunts down incidents on its own, "
                                  "then writes a postmortem.")
if watch_on and not watcher.running:
    watcher.start()
elif not watch_on and watcher.running:
    watcher.stop()
st.sidebar.divider()
st.sidebar.caption(f"Target: **{core.TARGET['name']}** · `{pathlib.Path(core.TARGET['_path']).name}`")

st.markdown(
    f'<p class="gh-title"><span class="gh-ghost">👻</span> Ghost Hunter <span class="gh-bat">🦇</span></p>'
    f'<p class="gh-sub">Hunting the <b>real</b> root cause behind haunted services, powered by '
    f'<b>{model.describe()}</b>. Detect → Investigate → Reason → Exorcise → Verify → Postmortem</p>',
    unsafe_allow_html=True)

# ---------------- shared renderers ----------------
def decision_card(data, dt):
    with st.container(border=True):
        st.markdown(f"### 🔮 Gemma 4's diagnosis · {dt}s")
        st.markdown(f"**The ghost (root cause):** {data.get('root_cause')}")
        st.markdown(f"**Exorcism (action):** `{data.get('action')}` `{data.get('params')}` · "
                    f"confidence **{data.get('confidence')}**")
        if data.get("chart_observation"):
            st.markdown(f"**📈 Seen in the chart:** {data['chart_observation']}")
        if data.get("note"):
            st.caption(data["note"])
        st.markdown("**🕯️ Evidence:**")
        for e in data.get("evidence", []):
            st.code(str(e), language=None)

def render_step(name, data, dt):
    if name.startswith("chart"):
        st.image(data, caption="Metrics chart sent to Gemma 4 (image input)", width=560)
    elif name.startswith("reason") and isinstance(data, dict):
        decision_card(data, dt)
    elif name.startswith("verify"):
        ok, res = data
        (st.success if ok else st.error)(
            f"{'✨ Exorcised' if ok else '💀 Still haunted'}: verified in {res['seconds']}s · smoke: {res['smoke']}")
    elif name.startswith("execute"):
        st.info(f"🪄 {name}: {data}")
    else:
        with st.expander(f"{name} · {dt}s"):
            st.json(data) if isinstance(data, (dict, list)) else st.code(str(data))

def show_postmortem(path):
    path = pathlib.Path(path)
    md = path.read_text()
    img = re.search(r"!\[[^\]]*\]\(([^)]+\.png)\)", md)
    md = re.sub(r"!\[[^\]]*\]\([^)]+\.png\)\n?", "", md)
    st.markdown(md, unsafe_allow_html=True)
    if img and (path.parent / img.group(1)).exists():
        st.image(str(path.parent / img.group(1)), caption="Metrics chart Gemma saw", width=560)
    st.download_button("⬇ Download .md", md, file_name=path.name, key=f"dl-{path.name}")

def health_list(h):
    for k, v in h.items():
        st.write(("🟢" if v == "UP" else "👻") + f" **{k}** · {v}")

live_tab, pm_tab = st.tabs(["👻 Live hunt", "📜 Postmortems"])
SCEN = core.scenarios()

# ---------------- live tab ----------------
with live_tab:
    left, right = st.columns([1, 2.2])
    with left:
        st.subheader("🎃 Summon a ghost")
        chosen = None
        for key, sc in SCEN.items():
            if st.button(f"{key} · {sc['title']}", use_container_width=True, help=sc.get("story")):
                chosen = key
        st.divider()
        manual = st.button("🔦 Hunt now (current state)", use_container_width=True, disabled=watcher.running)
        if st.button("🧹 Banish all ghosts (reset)", use_container_width=True):
            with st.spinner("Recreating containers…"):
                core.inject("reset"); time.sleep(35)
            st.rerun()

    if watcher.running:
        # Night watch: just inject; the watcher detects and fixes it on its own.
        if chosen:
            core.inject(chosen)
            st.toast(f"👻 Summoned {chosen} · {SCEN[chosen]['title']}. No button press needed: Ghost Hunter is watching.")

        @st.fragment(run_every=2)
        def live_feed():
            with watcher.lock:
                s = {k: (list(v) if isinstance(v, list) else v) for k, v in watcher.state.items()}
                cur = dict(s["current"]) if s["current"] else None
                if cur: cur["steps"] = list(cur["steps"])
            with right:
                badge = {"watching": "🕯️ Keeping night watch", "incident": "👻 Ghost sighted: hunting",
                         "stopped": "💤 Asleep"}
                last = f" · last check {int(time.time() - s['last_poll'])}s ago" if s["last_poll"] else ""
                st.subheader(f"{badge.get(s['status'], s['status'])}{last}")
                if s["health"]:
                    cols = st.columns(len(s["health"]))
                    for c, (k, v) in zip(cols, s["health"].items()):
                        c.metric(k, "🟢 UP" if v == "UP" else "👻 DOWN", v if v != "UP" else None,
                                 delta_color="inverse" if v != "UP" else "off")
                if cur and (s["status"] == "incident" or cur.get("phase") != "done"):
                    st.markdown(f"#### 👻 Hunt in progress · {int(time.time() - cur['started'])}s · _{cur['phase']}_")
                    for name, data, dt in cur["steps"]:
                        render_step(name, data, dt)
                    if s["thought"]:
                        with st.expander("🔮 Gemma 4 is peering into the logs… (live)", expanded=True):
                            st.markdown(s["thought"][-3000:])
                elif s["incidents"]:
                    last_inc = s["incidents"][0]
                    (st.success if last_inc.get("recovered") else st.error)(
                        f"Last hunt: {'✨ exorcised' if last_inc.get('recovered') else '🙋 escalated'} in "
                        f"{last_inc.get('duration')}s · postmortem: {pathlib.Path(last_inc['postmortem']).name}")
                    with st.expander("Last hunt, step by step"):
                        for name, data, dt in last_inc["steps"]:
                            render_step(name, data, dt)
                st.markdown("##### 🕸️ Activity")
                for ts, msg in reversed(s["events"][-12:]):
                    st.markdown(f"`{ts}` {msg}")
        live_feed()
    else:
        with left:
            st.subheader("🏚️ Services")
            health_list(core.check_health())
        with right:
            st.subheader("🕸️ Hunt timeline")
            if chosen or manual:
                if chosen:
                    st.info(f"👻 Summoning **{chosen} · {SCEN[chosen]['title']}**. {SCEN[chosen].get('story', '')}")
                    core.inject(chosen)
                    with st.spinner("Listening for things that go bump in the night…"):
                        h, secs = agent.wait_for_failure()
                    st.write(f"⏱ ghost sighted after {secs}s")

                live = {"box": None, "text": ""}
                def on_thought(chunk):
                    if chunk is None:  # a new reasoning step starts
                        live["text"] = ""
                        live["box"] = st.expander("🔮 Gemma 4 is peering into the logs… (live)", expanded=True).empty()
                        return
                    live["text"] += chunk
                    if live["box"]: live["box"].markdown(live["text"][-3000:])

                try:
                    rec = agent.run_incident(render_step, use_chart=use_chart, on_thought=on_thought)
                except agent.Busy as e:
                    st.warning(f"⏸ {e}. Try again in a moment.")
                    st.stop()
                if rec.get("note") == "nothing wrong":
                    st.info("🟢 No ghosts here. All services healthy.")
                else:
                    (st.success if rec["recovered"] else st.error)(
                        f"✨ Exorcised: {rec['duration']}s from detection to verified fix" if rec["recovered"]
                        else f"💀 Still haunted: {rec.get('outcome')}")
                    if rec["recovered"]:
                        st.snow()
                    with st.spinner("📜 Gemma is writing the postmortem…"):
                        path = postmortem.write(rec)
                    st.success(f"📜 Postmortem saved: postmortems/{path.name} (see the Postmortems tab)")
            else:
                st.write("Summon a ghost on the left, or turn on **🌙 Night watch** in the sidebar "
                         "and let Ghost Hunter catch failures on its own.")

# ---------------- postmortems tab ----------------
with pm_tab:
    files = postmortem.list_all()
    if not files:
        st.write("No postmortems yet. Every hunt gets one, written by Gemma 4.")
    else:
        pick = st.selectbox("Incident", files, format_func=lambda p: p.stem)
        show_postmortem(pick)

st.markdown('<p class="gh-foot">🎃 Ghost Hunter · open-source incident response with Gemma 4 · '
            'Hacktoberfest 2026</p>', unsafe_allow_html=True)
