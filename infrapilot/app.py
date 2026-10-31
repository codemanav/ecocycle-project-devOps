import time, streamlit as st
import agent, core, inject, model, metrics

st.set_page_config(page_title="InfraPilot", page_icon="🛰️", layout="wide")
metrics.start()  # sample docker stats from app start so the chart has history

SCENARIOS = {
    "A": ("Stop users-db", "A naive restart script would restart users-service — wrong, the DB is down."),
    "B": ("Starve marketplace memory", "A naive restart script would restart into the same OOM — crash loop."),
    "C": ("Freeze marketplace", "Here a restart IS the right call — InfraPilot should pick it only now."),
}

st.title("🛰️ InfraPilot")
st.caption(f"Autonomous incident response for EcoCycle · powered by **{model.model_id()}** via Gemini API · "
           "Detect → Investigate → Reason → Recover → Verify")

left, right = st.columns([1, 2.2])
with left:
    st.subheader("Services")
    for k, v in core.check_health().items():
        st.write(("🟢" if v == "UP" else "🔴") + f" **{k}** — {v}")
    st.subheader("Haunt it 👻")
    chosen = None
    for key, (label, _) in SCENARIOS.items():
        if st.button(f"{key} · {label}", use_container_width=True):
            chosen = key
    st.divider()
    use_chart = st.toggle("Send metrics chart to Gemma (multimodal)", value=True)
    manual = st.button("▶ Run InfraPilot on current state", use_container_width=True)
    if st.button("↺ Reset EcoCycle", use_container_width=True):
        with st.spinner("Recreating containers…"):
            inject.inject("reset"); time.sleep(35)
        st.rerun()

with right:
    st.subheader("Incident timeline")
    if chosen or manual:
        if chosen:
            st.info(f"👻 Injecting **{chosen} · {SCENARIOS[chosen][0]}**. {SCENARIOS[chosen][1]}")
            inject.inject(chosen)
            with st.spinner("Waiting for monitoring to detect the failure…"):
                h, secs = agent.wait_for_failure()
            st.write(f"⏱ failure detected after {secs}s")

        def emit(name, data, dt):
            if name.startswith("chart"):
                st.image(data, caption="Metrics chart sent to Gemma 4 (image input)", width=560)
            elif name.startswith("reason"):
                with st.container(border=True):
                    st.markdown(f"### 🧠 Gemma 4 decision · {dt}s")
                    st.markdown(f"**Root cause:** {data.get('root_cause')}")
                    st.markdown(f"**Action:** `{data.get('action')}` `{data.get('params')}` · "
                                f"confidence **{data.get('confidence')}**")
                    if data.get("chart_observation"):
                        st.markdown(f"**From the chart:** {data['chart_observation']}")
                    st.markdown("**Evidence:**")
                    for e in data.get("evidence", []):
                        st.code(str(e), language=None)
            elif name.startswith("verify"):
                ok, res = data
                (st.success if ok else st.error)(
                    f"✔ verify — {'recovered' if ok else 'NOT recovered'} in {res['seconds']}s · smoke: {res['smoke']}")
            else:
                with st.expander(f"{name} — {dt}s"):
                    st.json(data) if isinstance(data, (dict, list)) else st.code(str(data))

        # live view of Gemma's reasoning while it thinks
        live = {"box": None, "text": ""}
        def on_thought(chunk):
            if chunk is None:  # a new reasoning step starts
                live["text"] = ""
                exp = st.expander("💭 Gemma 4 is thinking… (live)", expanded=True)
                live["box"] = exp.empty()
                return
            live["text"] += chunk
            live["box"].markdown(live["text"][-3000:])

        t0 = time.time()
        res = agent.run_incident(emit, use_chart=use_chart, on_thought=on_thought)
        if res["recovered"]:
            st.balloons() if res.get("decision") else None
            st.success(f"✅ Recovered — total {round(time.time() - t0, 1)}s from detection to verified fix")
        else:
            st.error("Not recovered — escalated to a human")
    else:
        st.write("Pick a scenario on the left. InfraPilot will detect, diagnose with Gemma 4, fix, and verify.")
