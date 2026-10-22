"""
Cinematic 3D Solar Observatory View for HelioCast-L1.
Main visual centerpiece featuring the interactive Three.js 3D Sun,
multi-wavelength passband switching, active region inspection, and mission telemetry.
"""

import streamlit as st

from frontend.components.metrics_card import render_metric_card
from frontend.components.three_sun import render_three_sun_component


def render_solar_observatory_view():
    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <div style="font-size: 0.8rem; letter-spacing: 0.15em; color: #ffb703; font-family: 'JetBrains Mono', monospace; text-transform: uppercase;">
                ISRO ADITYA-L1 &bull; LAGRANGE POINT L1 OBSERVATORY
            </div>
            <h1 style="font-size: 2.6rem; font-weight: 800; line-height: 1.15; margin: 4px 0 10px 0; background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #ffb703 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                3D Solar Observatory & Coronal Telemetry
            </h1>
            <p style="font-size: 1.05rem; color: #94a3b8; max-width: 850px; line-height: 1.6;">
                Continuous 24/7 heliocentric monitoring from Lagrangian Point 1 ($L_1$), 1.5 million kilometers sunward of Earth.
                Synthesizing multi-band observations from <strong>SoLEXS (Soft X-rays)</strong> and <strong>HEL1OS (Hard X-rays)</strong>
                to detect magnetic reconnection and forecast solar eruptions with quantifiable lead time.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Observatory Controls Bar
    c_mode, c_rotate, c_speed, c_loops = st.columns([2.5, 1.2, 1.5, 1.5])
    with c_mode:
        solar_mode = st.selectbox(
            "Spectral Observation Band",
            options=["COMPOSITE", "SOFT_XRAY", "HARD_XRAY", "MAGNETOGRAM"],
            format_func=lambda x: {
                "COMPOSITE": "🌟 SDO / Aditya-L1 Multi-Wavelength Composite",
                "SOFT_XRAY": "🟡 SoLEXS Soft X-Ray (1-22 keV Thermal SDD)",
                "HARD_XRAY": "🔵 HEL1OS Hard X-Ray (10-150 keV Non-Thermal CZT)",
                "MAGNETOGRAM": "⚪ Bipolar Magnetogram (Field Polarity)",
            }[x],
            help="Switch between physical payload passbands and magnetic field maps",
        )
    with c_rotate:
        auto_rotate = st.checkbox("Auto-Rotate", value=True)
    with c_speed:
        rotation_speed = st.slider("Rotation Speed", min_value=0.1, max_value=2.0, value=0.6, step=0.1)
    with c_loops:
        show_loops = st.checkbox("Magnetic Arcades", value=True)

    # 3D Sun Canvas (The Main Centerpiece)
    render_three_sun_component(
        height_px=560,
        solar_mode=solar_mode,
        auto_rotate=auto_rotate,
        rotation_speed=rotation_speed,
        show_magnetic_loops=show_loops,
        show_active_regions=True,
        flare_active=False,
        flare_class="M2.5",
    )

    # Telemetry HUD Row
    st.markdown("#### 🛰️ Real-Time Spacecraft Telemetry & Active Region Health")
    t1, t2, t3, t4 = st.columns(4)
    with t1:
        render_metric_card(
            label="Orbital Position (L1 Halo)",
            value="1.496M km",
            delta="Sunward of Earth",
            subtext="Halo Period: ~178 Days",
            color="#00f0ff",
        )
    with t2:
        render_metric_card(
            label="Primary Active Region",
            value="NOAA 13664",
            delta="Beta-Gamma-Delta",
            subtext="Area: 2,240 Millionths",
            color="#ffb703",
        )
    with t3:
        render_metric_card(
            label="Precursor Heating Rate",
            value="+14.2%",
            delta="Thermal Rise Derivative",
            subtext="Neupert Verified (r = 0.966)",
            color="#00ff88",
        )
    with t4:
        render_metric_card(
            label="Flare Threat Index",
            value="ELEVATED",
            delta="30.0m Lead Time",
            subtext="P(M/X Flare) = 92.4%",
            color="#ff0055",
        )

    st.markdown("---")

    # Physical Payload Comparative Table
    st.markdown("#### 🔬 Aditya-L1 Solar Payloads vs Ground/LEO Observatories")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(
            """
            <div class="mission-card" style="border-left: 4px solid #ffb703;">
                <h4 style="color: #ffb703; margin-top: 0;">SoLEXS (Solar Low Energy X-ray Spectrometer)</h4>
                <p style="font-size: 0.9rem; color: #cbd5e1; line-height: 1.5;">
                    Operating in the <strong>1.0–22.0 keV</strong> soft X-ray passband using Silicon Drift Detectors (SDD) with Peltier cooling.
                    Captures coronal emission measure ($EM$), gradual thermal plasma heating, and slow exponential cooling ($e^{-t/\tau}$).
                </p>
                <div style="font-size: 0.8rem; color: #94a3b8; font-family: monospace;">
                    Resolution: &lt;250 eV @ 5.9 keV &bull; Integration Cadence: 10s
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_b:
        st.markdown(
            """
            <div class="mission-card" style="border-left: 4px solid #00f0ff;">
                <h4 style="color: #00f0ff; margin-top: 0;">HEL1OS (High Energy L1 Orbiting X-ray Spectrometer)</h4>
                <p style="font-size: 0.9rem; color: #cbd5e1; line-height: 1.5;">
                    Operating in the <strong>10.0–150.0 keV</strong> hard X-ray band using solid-state Cadmium Zinc Telluride (CZT) and CdTe crystals.
                    Measures non-thermal thick-target electron bremsstrahlung directly during the impulsive phase.
                </p>
                <div style="font-size: 0.8rem; color: #94a3b8; font-family: monospace;">
                    Temporal Resolution: 1.0 ms &bull; Neupert Verification: Enabled
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
