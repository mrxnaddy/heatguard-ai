"""
HeatGuard AI — Streamlit dashboard (Phase 3 Integrated).

Fully connected to Phase 3 core intelligence: risk scoring, hotspot detection,
tool-calling AI agent, and location comparison, while preserving the robust
safe_call error boundaries and UI helpers from Phase 2.
"""
from __future__ import annotations

import streamlit as st

from app.ai.agent import HeatGuardAgent
from app.components.ui_helpers import (
    render_data_status_badge,
    render_empty_state,
    render_error_banner,
    render_header,
    render_placeholder,
    render_risk_badge,
    render_temperature_card,
)
from app.config import ConfigError, settings
from app.services.fortyguard_client import FortyGuardClient
from app.services.hotspot_detection import detect_hotspots
from app.services.risk_scoring import calculate_risk
from app.utils.errors import safe_call

st.set_page_config(
    page_title="HeatGuard AI",
    page_icon="🌡️",
    layout="wide",
)


@st.cache_resource
def get_client() -> FortyGuardClient:
    return FortyGuardClient(settings=settings)


@st.cache_resource
def get_agent() -> HeatGuardAgent:
    return HeatGuardAgent()


def load_locations(client: FortyGuardClient):
    return safe_call(client.get_all_locations)


def main() -> None:
    render_header()

    # --- Configuration guard: never let a missing/bad config surface as a traceback. ---
    try:
        client = get_client()
        agent = get_agent()
    except ConfigError as exc:
        render_error_banner(f"Configuration problem: {exc}")
        st.stop()
        return

    health_result = safe_call(client.health_check)
    healthy = bool(health_result.value) if health_result.ok else False

    top_left, top_right = st.columns([3, 1])
    with top_right:
        render_data_status_badge(using_mock_data=client.using_mock_data, healthy=healthy)

    locations_result = load_locations(client)

    if not locations_result.ok:
        render_error_banner(locations_result.error.user_message)
        render_empty_state("No temperature data is currently available.")
        st.stop()
        return

    locations = locations_result.value
    if not locations:
        render_empty_state("No locations are configured yet.")
        st.stop()
        return

    # --- Location selector ---
    name_to_id = {loc.name: loc.location_id for loc in locations}
    selected_name = st.selectbox("📍 Select a location", options=list(name_to_id.keys()))
    selected_id = name_to_id[selected_name]

    reading_result = safe_call(lambda: client.get_temperature(selected_id))
    if not reading_result.ok:
        render_error_banner(reading_result.error.user_message)
        st.stop()
        return
    reading = reading_result.value

    # Compute deterministic risk score via Phase 3 service
    risk = calculate_risk(reading)

    st.divider()

    left, right = st.columns([1, 1])
    with left:
        render_temperature_card(reading.name, reading.temperature_c, reading.confidence)
    with right:
        st.markdown("#### Risk Status")
        render_risk_badge(risk.level)
        st.caption(f"Deterministic Risk Score: **{risk.score} / 100**")

    st.divider()

    st.markdown("### 🗺️ Heat Map & Hotspot Intelligence")
    
    map_col, side_col = st.columns([2, 1])
    with map_col:
        st.markdown("#### 🔥 Top Heat Hotspots (Relative Outliers)")
        hotspots = detect_hotspots(locations, top_n=3)
        if hotspots:
            for idx, hs in enumerate(hotspots, 1):
                st.markdown(
                    f"**{idx}. {hs.name}** — {hs.temperature_c}°C "
                    f"(Delta: `+{hs.delta_vs_baseline_c}°C`) | Risk: **{hs.risk_level}**\n\n"
                    f"*Intervention:* {hs.suggested_intervention_type}"
                )
        else:
            render_placeholder("Top Hotspots", "No hotspot data available.", icon="🔥")

    with side_col:
        st.markdown("#### 🤖 AI Location Analysis")
        analysis_res = safe_call(lambda: agent.tools.get_location_risk(selected_name))
        if analysis_res.ok and "error" not in analysis_res.value:
            data = analysis_res.value
            st.info(
                f"**Location:** {data['name']}\n\n"
                f"**Risk Level:** {data['risk_level']} ({data['risk_score']}/100)\n\n"
                f"**Reasoning:** Elevated hyperlocal temperature reading requires priority deployment of shade and hydration facilities for vulnerable outdoor groups."
            )
        else:
            st.write("I cannot confirm this from the available data.")

    st.divider()

    planner_col, compare_col = st.columns([1, 1])
    with planner_col:
        st.markdown("#### 🏛️ AI Agent Assistant")
        user_q = st.text_input("Ask agent about heat risks or priorities:", "Which area has the highest heat risk?", key="agent_user_q")
        if st.button("Ask Agent", key="ask_agent_btn"):
            with st.spinner("Analyzing verified tool data..."):
                try:
                    agent_response = agent.answer_query(user_q)
                    if isinstance(agent_response, dict):
                        st.markdown("### 🏛️ AI Agent Heat Risk Analysis")
                        st.markdown(f"**Recommendation:** {agent_response.get('recommendation', 'N/A')}")
                        st.markdown(f"**Confidence Level:** `{agent_response.get('confidence', 'N/A').upper()}`")
                        
                        st.markdown("### 🔥 Identified Hotspots")
                        
                        for spot in agent_response.get("hotspots", []):
                            st.markdown(f"* **{spot.get('name', 'Location')}**")
                            st.markdown(f"  * **Temperature:** {spot.get('temperature_c', 0)}°C (+{spot.get('delta_vs_baseline_c', 0)}°C vs baseline)")
                            st.markdown(f"  * **Risk Level:** {spot.get('risk_level', 'N/A')}")
                            st.markdown(f"  * **Intervention:** {spot.get('suggested_intervention_type', 'N/A')}")
                            st.markdown("")
                    else:
                        st.markdown(str(agent_response))
                except Exception as exc:
                    st.error(f"Agent execution error: {exc}")

    with compare_col:
        st.markdown("#### ⚖️ Location Comparison")
        if len(locations) >= 2:
            loc_names = list(name_to_id.keys())
            comp_a = st.selectbox("Location A", loc_names, index=0, key="comp_a")
            comp_b = st.selectbox("Location B", loc_names, index=1, key="comp_b")
            
            if st.button("Compare Locations", key="compare_loc_btn"):
                comp_result = agent.tools.compare_locations(comp_a, comp_b)
                if "error" not in comp_result:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric(comp_result['location_a']['name'], f"{comp_result['location_a']['temperature_c']} °C", f"Risk: {comp_result['location_a']['risk_score']}")
                    with col_b:
                        st.metric(comp_result['location_b']['name'], f"{comp_result['location_b']['temperature_c']} °C", f"Risk: {comp_result['location_b']['risk_score']}")
                    st.success(f"**Higher Risk:** {comp_result['higher_risk']} (Delta: {comp_result['temperature_delta_c']} °C)")
                else:
                    st.error(comp_result["error"])
        else:
            st.write("Insufficient locations available for comparison.")

    st.caption(
        "HeatGuard AI · Phase 3 core intelligence build · "
        f"Mock data mode: {'ON' if client.using_mock_data else 'OFF'}"
    )


if __name__ == "__main__":
    main()