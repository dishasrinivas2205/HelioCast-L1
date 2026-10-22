"""
Mission Control Header & Payload Status Bar Component.
"""

from datetime import datetime, timezone
import streamlit as st
from heliocast import __mission__, __version__


def render_mission_header(active_alert: bool = False, alert_severity: str = "NOMINAL"):
    """Render top aerospace navigation and satellite telemetry status bar."""
    utc_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(56, 189, 248, 0.18); padding-bottom: 1rem; margin-bottom: 1.5rem; background: rgba(3, 7, 18, 0.4); border-radius: 12px; padding: 12px 18px;">
            <div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.7rem;">☀️</span>
                    <div>
                        <h1 style="margin: 0; font-size: 1.85rem; font-weight: 800; letter-spacing: -0.02em; background: linear-gradient(90deg, #ffffff 0%, #00f0ff 50%, #ffb703 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                            HELIOCAST-L1
                        </h1>
                        <p style="margin: 0; font-size: 0.78rem; color: #94a3b8; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.08em;">
                            {__mission__} &bull; DEEP SPACE WEATHER OBSERVATORY &bull; {utc_str}
                        </p>
                    </div>
                </div>
            </div>
            <div style="display: flex; gap: 0.65rem; align-items: center; flex-wrap: wrap;">
                <span class="telemetry-pill pill-nominal">🛰️ L1 HALO: NOMINAL</span>
                <span class="telemetry-pill pill-nominal" style="border-color: rgba(255, 183, 3, 0.4); color: #ffb703; background: rgba(255, 183, 3, 0.1);">📊 SoLEXS (1-22 keV)</span>
                <span class="telemetry-pill pill-nominal" style="border-color: rgba(0, 240, 255, 0.4); color: #00f0ff; background: rgba(0, 240, 255, 0.1);">⚡ HEL1OS (10-150 keV)</span>
                <span class="telemetry-pill {'pill-critical' if active_alert else 'pill-nominal'}">
                    {'🚨 ALERT ACTIVE' if active_alert else '🟢 SENTINEL: ARMED'}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
