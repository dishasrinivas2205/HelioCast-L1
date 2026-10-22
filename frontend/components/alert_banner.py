"""
Visual & Acoustic Space Weather Alert Banner Component.
Fulfills Expected Outcome 3: Visual alerts triggered on flare nowcast/forecast.
"""

import streamlit as st
from frontend.audio_alerts import get_audio_alert_html


def render_alert_banner(
    alert_type: str,            # "FORECAST" or "NOWCAST"
    flare_class: str,
    lead_time_min: float,
    confidence: float,
    details: str,
    enable_audio: bool = True,
):
    """
    Renders high-visibility glowing strobe banner and triggers browser audio chime.
    """
    if alert_type == "FORECAST":
        banner_class = "alert-banner-forecast"
        icon = "⚡"
        title = f"PRECURSOR FORECAST EARLY WARNING: {flare_class} SOLAR FLARE IMMINENT"
        badge = f"<span class='telemetry-pill pill-warning'>LEAD TIME: {lead_time_min:.1f} MIN</span>"
        audio_snippet = get_audio_alert_html("warning") if enable_audio else ""
    else:
        banner_class = "alert-banner-nowcast"
        icon = "🚨"
        title = f"NOWCAST CONFIRMED: {flare_class} SOLAR ERUPTION REGISTERED"
        badge = "<span class='telemetry-pill pill-critical'>NEUPERT VERIFIED</span>"
        audio_snippet = get_audio_alert_html("critical") if enable_audio else ""

    html = f"""
    <div class="{banner_class}">
        <div style="font-size: 2.2rem; margin-right: 1.25rem;">{icon}</div>
        <div style="flex-grow: 1;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                <span style="font-weight: 700; font-size: 1.15rem; letter-spacing: 0.02em;">{title}</span>
                {badge}
            </div>
            <div style="font-size: 0.9rem; color: #cbd5e1;">
                {details} • <strong>Confidence Score: {confidence*100:.1f}%</strong>
            </div>
        </div>
    </div>
    {audio_snippet}
    """
    st.markdown(html, unsafe_allow_html=True)
