"""
HelioCast-L1 Mission Control Aerospace HUD & 3D Solar Observatory.
Main Streamlit Application Entrypoint.
ISRO Problem Statement 15 Solution: Solar Flare Nowcasting & Forecasting for Aditya-L1.
"""

import sys
from pathlib import Path
import streamlit as st

# Ensure repository root is on sys.path regardless of where streamlit is launched from
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Set page configuration before any other Streamlit call
st.set_page_config(
    page_title="HelioCast-L1 • Aditya-L1 Solar Observatory",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load Aerospace Deep Space CSS Styling
css_path = Path(__file__).parent / "styles.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from frontend.components.navbar import render_mission_header
from frontend.views.data_explorer import render_data_explorer_view
from frontend.views.evaluation_hub import render_evaluation_hub_view
from frontend.views.forecast_radar import render_forecast_radar_view
from frontend.views.isro_pitch_deck import render_pitch_deck_view
from frontend.views.live_ops import render_live_ops_view
from frontend.views.nowcast_catalog import render_nowcast_catalog_view
from frontend.views.observatory import render_solar_observatory_view
from frontend.views.orbit_visualizer import render_orbit_visualizer_view
from heliocast import __mission__, __version__

# Sidebar Navigation
with st.sidebar:
    st.markdown(
        f"""
        <div style="padding: 0.5rem 0 1.25rem 0; border-bottom: 1px solid rgba(56, 189, 248, 0.2);">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.4rem;">☀️</span>
                <span style="font-size: 1.25rem; font-weight: 800; color: #00f0ff; letter-spacing: -0.02em;">HELIOCAST-L1</span>
            </div>
            <div style="font-size: 0.75rem; color: #94a3b8; font-family: monospace; margin-top: 4px;">
                v{__version__} &bull; ISRO Aditya-L1 &bull; Hackyard
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    view_selection = st.radio(
        "MISSION CONTROL VIEWS",
        options=[
            "☀️ 3D Solar Observatory",
            "🛰️ Live Flight Ops & Simulator",
            "📈 Dual-Band Light Curve Explorer",
            "📋 Automated Flare Catalogues (Step 3)",
            "🔮 Precursor Forecasting Radar (Step 4)",
            "🏆 Heliophysics Evaluation Hub",
            "🌌 L1 Orbit & Spacecraft Visualizer",
            "📜 ISRO Pitch Deck & Guide",
        ],
        index=0,
    )

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="mission-card" style="font-size: 0.8rem; padding: 14px;">
            <div style="color: #ffb703; font-weight: 700; margin-bottom: 6px; font-family: monospace; letter-spacing: 0.05em;">
                🛰️ MISSION ARCHITECTURE
            </div>
            <div style="color: #cbd5e1; margin-bottom: 3px;">• <strong>Spacecraft</strong>: Aditya-L1 (ISRO)</div>
            <div style="color: #cbd5e1; margin-bottom: 3px;">• <strong>Station</strong>: Sun-Earth L1 (1.5M km)</div>
            <div style="color: #ffb703; margin-bottom: 3px;">• <strong>SoLEXS</strong>: 1 - 22 keV (Thermal SDD)</div>
            <div style="color: #00f0ff; margin-bottom: 3px;">• <strong>HEL1OS</strong>: 10 - 150 keV (CZT Burst)</div>
            <div style="color: #00ff88; margin-top: 6px;">• <strong>Neupert Verification</strong>: Active</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Render Global Navigation Header
render_mission_header(
    active_alert=st.session_state.get("active_alert", False),
    alert_severity="CRITICAL" if st.session_state.get("active_alert") else "NOMINAL",
)

# Route Views
if view_selection == "☀️ 3D Solar Observatory":
    render_solar_observatory_view()
elif view_selection == "🛰️ Live Flight Ops & Simulator":
    render_live_ops_view()
elif view_selection == "📈 Dual-Band Light Curve Explorer":
    render_data_explorer_view()
elif view_selection == "📋 Automated Flare Catalogues (Step 3)":
    render_nowcast_catalog_view()
elif view_selection == "🔮 Precursor Forecasting Radar (Step 4)":
    render_forecast_radar_view()
elif view_selection == "🏆 Heliophysics Evaluation Hub":
    render_evaluation_hub_view()
elif view_selection == "🌌 L1 Orbit & Spacecraft Visualizer":
    render_orbit_visualizer_view()
elif view_selection == "📜 ISRO Pitch Deck & Guide":
    render_pitch_deck_view()
