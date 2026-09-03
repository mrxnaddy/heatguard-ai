"""
Reusable Streamlit UI components for HeatGuard AI.

Kept deliberately small in Phase 2: a branded header, a live/mock data
status badge, a temperature card, and a generic placeholder panel used
for the Phase-3 sections (risk status, hotspots, AI analysis, action
planner, comparison) so the dashboard already looks complete and
professional even before that logic exists.
"""
from __future__ import annotations

import streamlit as st

# Risk-level color system — used consistently everywhere a risk level is
# shown, so color doubles as the legend rather than being decorative.
RISK_COLORS = {
    "Low": "#2E7D32",       # green
    "Moderate": "#F9A825",  # amber
    "High": "#EF6C00",      # orange
    "Extreme": "#C62828",   # red
}


def render_header() -> None:
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.2rem;">
            <span style="font-size:2rem;">🌡️</span>
            <span style="font-size:1.8rem; font-weight:700;">HeatGuard AI</span>
        </div>
        <div style="color:#6b7280; margin-bottom:1rem;">
            Hyperlocal heat-risk intelligence &amp; action platform — powered by FortyGuard
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_data_status_badge(using_mock_data: bool, healthy: bool) -> None:
    if using_mock_data:
        label, color, bg = "MOCK DATA", "#92400e", "#fef3c7"
    elif healthy:
        label, color, bg = "LIVE DATA", "#065f46", "#d1fae5"
    else:
        label, color, bg = "CACHED DATA (connection issue)", "#991b1b", "#fee2e2"

    st.markdown(
        f"""
        <span style="
            display:inline-block; padding:0.25rem 0.7rem; border-radius:999px;
            background:{bg}; color:{color}; font-weight:600; font-size:0.8rem;
            letter-spacing:0.02em;">
            ● {label}
        </span>
        """,
        unsafe_allow_html=True,
    )


def render_temperature_card(name: str, temperature_c: float, confidence: str) -> None:
    st.metric(label=f"Current Temperature — {name}", value=f"{temperature_c:.1f} °C")
    st.caption(f"Data confidence: {confidence}")


def render_risk_badge(level: str | None) -> None:
    if level is None:
        st.info("Risk score not yet calculated for this location.")
        return
    color = RISK_COLORS.get(level, "#6b7280")
    st.markdown(
        f"""
        <div style="
            display:inline-block; padding:0.35rem 0.9rem; border-radius:8px;
            background:{color}20; border:1px solid {color}; color:{color};
            font-weight:700;">
            {level} Risk
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_placeholder(title: str, description: str, icon: str = "🧩") -> None:
    """
    A polished, honest placeholder for a Phase-3 feature.

    We deliberately label these as "coming in Phase 3" rather than faking
    content, so the shell never misrepresents what's implemented yet.
    """
    st.markdown(f"#### {icon} {title}")
    with st.container(border=True):
        st.write(description)
        st.caption("Coming in Phase 3.")


def render_error_banner(message: str) -> None:
    st.error(f"⚠️ {message}")


def render_empty_state(message: str) -> None:
    st.info(message)
