"""
HelioCast-L1 Full-Screen Cinematic Solar Observatory HUD.
Zero Sidebar • 100% Full Screen • Touch Effects • Scroll Animations.
ISRO Problem Statement 15 Solution: Solar Flare Nowcasting & Precursor Forecasting.
"""

import sys
from pathlib import Path
import streamlit as st

# Ensure repository root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# 1. Full-Screen Page Configuration (Sidebar collapsed & wide mode)
st.set_page_config(
    page_title="HelioCast-L1 • Aditya-L1 Solar Observatory",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Inject Full-Screen Deep Space CSS Theme with Touch Effects
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

# 3. Global Navigation Header (Full Width)
render_mission_header(
    active_alert=st.session_state.get("active_alert", False),
    alert_severity="CRITICAL" if st.session_state.get("active_alert") else "NOMINAL",
)

# 4. Floating Glassmorphic Top Navigation HUD Bar (Full Width • Touch Optimized)
NAV_OPTIONS = [
    "☀️ 3D Sun",
    "🛰️ Live Flight Ops",
    "📈 Dual-Band Curves",
    "📋 Flare Catalogues",
    "🔮 Precursor Radar",
    "🏆 Heliophysics Hub",
    "🌌 L1 Orbit",
    "📜 ISRO Pitch Deck",
]

if "active_nav" not in st.session_state or st.session_state.active_nav not in NAV_OPTIONS:
    st.session_state.active_nav = NAV_OPTIONS[0]

if "display_mode" not in st.session_state:
    st.session_state.display_mode = "🎯 Focused HUD"

col_bar_left, col_bar_right = st.columns([6.8, 3.2], vertical_alignment="center")
with col_bar_left:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; padding: 2px 0;">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.76rem; color: #ffb703; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase;">
                ⚡ ADITYA-L1 MISSION CONTROL HUD
            </span>
            <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: #00ff88; box-shadow: 0 0 8px #00ff88;"></span>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #64748b;">
                TOUCH-RESPONSIVE INTERFACE &bull; 8 SUBSYSTEMS
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_bar_right:
    selected_mode = st.segmented_control(
        "Display Mode",
        options=["🎯 Focused HUD", "📜 Continuous Scroll"],
        default=st.session_state.display_mode,
        label_visibility="collapsed",
        key="hud_display_mode",
    )
    if selected_mode and selected_mode != st.session_state.display_mode:
        st.session_state.display_mode = selected_mode
        st.rerun()

# Full-width interactive touch pills for all 8 views
selected_nav = st.pills(
    "Mission Views",
    options=NAV_OPTIONS,
    default=st.session_state.active_nav,
    label_visibility="collapsed",
    key="hud_nav_pills",
)
if selected_nav and selected_nav != st.session_state.active_nav:
    st.session_state.active_nav = selected_nav
    st.rerun()

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# 5. Routing Engine: Focused View or Continuous Scroll
if "Continuous Scroll" in st.session_state.display_mode:
    # --- CONTINUOUS CINEMATIC SCROLL EXPERIENCE ---
    st.markdown(
        """
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 12px; padding: 10px 18px; margin-bottom: 2rem; display: flex; flex-wrap: wrap; gap: 14px; align-items: center; justify-content: center; backdrop-filter: blur(12px);">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #ffb703; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase;">⚡ Quick Jump:</span>
            <a href="#section-observatory" style="color: #00f0ff; text-decoration: none; font-size: 0.82rem; font-family: 'JetBrains Mono', monospace; padding: 4px 10px; border-radius: 6px; background: rgba(0,240,255,0.08); transition: all 0.2s;">☀️ 3D Sun</a>
            <a href="#section-live-ops" style="color: #00f0ff; text-decoration: none; font-size: 0.82rem; font-family: 'JetBrains Mono', monospace; padding: 4px 10px; border-radius: 6px; background: rgba(0,240,255,0.08); transition: all 0.2s;">🛰️ Live Ops</a>
            <a href="#section-light-curves" style="color: #00f0ff; text-decoration: none; font-size: 0.82rem; font-family: 'JetBrains Mono', monospace; padding: 4px 10px; border-radius: 6px; background: rgba(0,240,255,0.08); transition: all 0.2s;">📈 Light Curves</a>
            <a href="#section-catalogues" style="color: #00f0ff; text-decoration: none; font-size: 0.82rem; font-family: 'JetBrains Mono', monospace; padding: 4px 10px; border-radius: 6px; background: rgba(0,240,255,0.08); transition: all 0.2s;">📋 Catalogues</a>
            <a href="#section-forecast" style="color: #00f0ff; text-decoration: none; font-size: 0.82rem; font-family: 'JetBrains Mono', monospace; padding: 4px 10px; border-radius: 6px; background: rgba(0,240,255,0.08); transition: all 0.2s;">🔮 Forecast Radar</a>
            <a href="#section-benchmarks" style="color: #00f0ff; text-decoration: none; font-size: 0.82rem; font-family: 'JetBrains Mono', monospace; padding: 4px 10px; border-radius: 6px; background: rgba(0,240,255,0.08); transition: all 0.2s;">🏆 Heliophysics Hub</a>
            <a href="#section-orbit" style="color: #00f0ff; text-decoration: none; font-size: 0.82rem; font-family: 'JetBrains Mono', monospace; padding: 4px 10px; border-radius: 6px; background: rgba(0,240,255,0.08); transition: all 0.2s;">🌌 L1 Orbit</a>
            <a href="#section-pitch-deck" style="color: #00f0ff; text-decoration: none; font-size: 0.82rem; font-family: 'JetBrains Mono', monospace; padding: 4px 10px; border-radius: 6px; background: rgba(0,240,255,0.08); transition: all 0.2s;">📜 Pitch Deck</a>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown("<div class='animate-fade-in'>", unsafe_allow_html=True)
    
    st.markdown("<div id='section-observatory' class='scroll-section'></div>", unsafe_allow_html=True)
    render_solar_observatory_view()
    
    st.markdown("<div class='section-divider'></div><div id='section-live-ops' class='scroll-section'></div>", unsafe_allow_html=True)
    render_live_ops_view()
    
    st.markdown("<div class='section-divider'></div><div id='section-light-curves' class='scroll-section'></div>", unsafe_allow_html=True)
    render_data_explorer_view()
    
    st.markdown("<div class='section-divider'></div><div id='section-catalogues' class='scroll-section'></div>", unsafe_allow_html=True)
    render_nowcast_catalog_view()
    
    st.markdown("<div class='section-divider'></div><div id='section-forecast' class='scroll-section'></div>", unsafe_allow_html=True)
    render_forecast_radar_view()
    
    st.markdown("<div class='section-divider'></div><div id='section-benchmarks' class='scroll-section'></div>", unsafe_allow_html=True)
    render_evaluation_hub_view()
    
    st.markdown("<div class='section-divider'></div><div id='section-orbit' class='scroll-section'></div>", unsafe_allow_html=True)
    render_orbit_visualizer_view()
    
    st.markdown("<div class='section-divider'></div><div id='section-pitch-deck' class='scroll-section'></div>", unsafe_allow_html=True)
    render_pitch_deck_view()
    
    st.markdown("</div>", unsafe_allow_html=True)

else:
    # --- FOCUSED HUD VIEW (Single Click Switch) ---
    st.markdown("<div class='animate-fade-in'>", unsafe_allow_html=True)
    
    current = st.session_state.active_nav
    if "3D Solar Observatory" in current:
        render_solar_observatory_view()
    elif "Live Flight Ops" in current:
        render_live_ops_view()
    elif "Light Curves" in current:
        render_data_explorer_view()
    elif "Catalogues" in current:
        render_nowcast_catalog_view()
    elif "Precursor Forecast" in current:
        render_forecast_radar_view()
    elif "Heliophysics" in current:
        render_evaluation_hub_view()
    elif "Orbit" in current:
        render_orbit_visualizer_view()
    elif "Pitch Deck" in current:
        render_pitch_deck_view()
    else:
        render_solar_observatory_view()
        
    st.markdown("</div>", unsafe_allow_html=True)

# 6. Global Aerospace Footer
st.markdown(
    """
    <div style="margin-top: 5rem; padding: 2rem 0; border-top: 1px solid rgba(56, 189, 248, 0.15); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; color: #64748b; font-size: 0.82rem; font-family: 'JetBrains Mono', monospace;">
        <div>
            ☀️ <strong>HELIOCAST-L1 v2.0.0</strong> &bull; ISRO Aditya-L1 Mission Operations &bull; Sun-Earth L1 Halo Orbit
        </div>
        <div>
            Payloads: SoLEXS (1-22 keV SDD) &bull; HEL1OS (10-150 keV CZT) &bull; Neupert Verification: Active
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
