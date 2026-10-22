"""
Aerospace HUD Metric Card Component.
"""

import streamlit as st


def render_metric_card(
    label: str,
    value: str,
    delta: str = "",
    subtext: str = "",
    color: str = "#00f0ff",
):
    """Render a sleek glassmorphic telemetry metric card."""
    delta_html = f"<span style='color: {color}; font-size: 0.85rem; font-weight: 600;'>{delta}</span>" if delta else ""
    subtext_html = f"<div style='font-size: 0.75rem; color: #94a3b8; margin-top: 4px;'>{subtext}</div>" if subtext else ""

    html = f"""
    <div class="mission-card" style="border-top: 3px solid {color};">
        <div class="metric-label">{label}</div>
        <div style="display: flex; align-items: baseline; justify-content: space-between; margin-top: 6px;">
            <div class="metric-value" style="color: {color};">{value}</div>
            {delta_html}
        </div>
        {subtext_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
