"""
Mission Control Header & Payload Status Bar Component.
"""

from datetime import datetime, timezone
import streamlit as st
from heliocast import __mission__, __version__


def render_mission_header(active_alert: bool = False, alert_severity: str = "NOMINAL"):
    """Render top aerospace navigation and satellite telemetry status bar."""
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(56, 189, 248, 0.2); padding-bottom: 1rem; margin-bottom: 1.5rem;">
            <div>
                <h1 style="margin: 0; font-size: 1.85rem; font-weight: 700; background: linear-gradient(90deg, #00f0ff, #ffb703); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    ☀️ HELIOCAST-L1
                </h1>
                <p style="margin: 2px 0 0 0; font-size: 0.85rem; color: #94a3b8; font-family: 'JetBrains Mono', monospace;">
                    {__mission__} • SOLAR FLARE NOWCASTING & PRECURSOR FORECASTING PLATFORM
                </p>
            </div>
            <div style="display: flex; gap: 0.75rem; align-items: center;">
                <span class="telemetry-pill pill-nominal">🛰️ L1 ORBIT: NOMINAL</span>
                <span class="telemetry-pill pill-nominal">📊 SoLEXS: 1-22 keV</span>
                <span class="telemetry-pill pill-nominal">⚡ HEL1OS: 10-150 keV</span>
                <span class="telemetry-pill {'pill-critical' if active_alert else 'pill-nominal'}">
                    {'🚨 ALERT ACTIVE' if active_alert else '🟢 SENTINEL: ARMED'}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
