"""
Sun-Earth L1 Halo Orbit & Spacecraft Mission Geometry View.
Visualizes Aditya-L1 positioning at Lagrangian Point 1 (1.5M km from Earth).
"""

import numpy as np
import plotly.graph_objects as go
import streamlit as st


def render_orbit_visualizer_view():
    st.markdown("### ☀️ Aditya-L1 Mission Geometry & Lagrangian Point L1 Orbit")
    st.markdown(
        "ISRO's **Aditya-L1** is stationed in a quasi-periodic halo orbit around the **Sun-Earth Lagrangian Point 1 ($L_1$)**, "
        "approximately 1.5 million kilometers from Earth towards the Sun. "
        "This vantage point provides an uninterrupted, continuous view of the Sun without eclipses or occultation by Earth."
    )

    # 3D Orbit Visualization
    # Sun at origin (scaled), Earth at 1.0 AU, L1 at 0.99 AU (1.5M km from Earth)
    # Halo orbit around L1

    t = np.linspace(0, 2 * np.pi, 200)
    # Scaled coordinates for schematic visualization (x: Sun-Earth axis)
    halo_x = 0.99 + 0.006 * np.cos(t)
    halo_y = 0.015 * np.sin(t)
    halo_z = 0.010 * np.sin(2 * t)

    fig = go.Figure()

    # The Sun
    fig.add_trace(
        go.Scatter3d(
            x=[0.0],
            y=[0.0],
            z=[0.0],
            mode="markers+text",
            marker=dict(size=25, color="#ffb703", symbol="circle"),
            text=["THE SUN"],
            textposition="top center",
            name="Sun",
        )
    )

    # Earth
    fig.add_trace(
        go.Scatter3d(
            x=[1.0],
            y=[0.0],
            z=[0.0],
            mode="markers+text",
            marker=dict(size=14, color="#00f0ff", symbol="circle"),
            text=["EARTH"],
            textposition="top center",
            name="Earth",
        )
    )

    # L1 Point Marker
    fig.add_trace(
        go.Scatter3d(
            x=[0.99],
            y=[0.0],
            z=[0.0],
            mode="markers+text",
            marker=dict(size=6, color="#ffffff", symbol="cross"),
            text=["L1 Point"],
            textposition="bottom center",
            name="L1 Lagrange Point",
        )
    )

    # Aditya-L1 Halo Orbit
    fig.add_trace(
        go.Scatter3d(
            x=halo_x,
            y=halo_y,
            z=halo_z,
            mode="lines",
            line=dict(color="#00ff88", width=4),
            name="Aditya-L1 Halo Orbit",
        )
    )

    # Current Spacecraft Position
    sc_idx = 45
    fig.add_trace(
        go.Scatter3d(
            x=[halo_x[sc_idx]],
            y=[halo_y[sc_idx]],
            z=[halo_z[sc_idx]],
            mode="markers+text",
            marker=dict(size=10, color="#ff0055", symbol="diamond"),
            text=["Aditya-L1 Spacecraft"],
            textposition="top left",
            name="Current Position",
        )
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(11, 15, 25, 0.8)",
        height=520,
        margin=dict(l=20, r=20, t=20, b=20),
        scene=dict(
            xaxis=dict(title="Sun-Earth Axis (AU)", backgroundcolor="rgba(15, 23, 42, 0.6)"),
            yaxis=dict(title="Y (AU)", backgroundcolor="rgba(15, 23, 42, 0.6)"),
            zaxis=dict(title="Z (AU)", backgroundcolor="rgba(15, 23, 42, 0.6)"),
            camera=dict(eye=dict(x=1.3, y=0.4, z=0.6)),
        ),
    )

    st.plotly_chart(fig, use_container_width=True)

    # Payload Physical Characteristics
    st.markdown("#### 🔬 Aditya-L1 Solar X-Ray Payloads")
    p1, p2 = st.columns(2)
    with p1:
        st.markdown(
            """
            <div class="mission-card" style="border-left: 4px solid #ffb703;">
                <h4 style="color: #ffb703; margin-top: 0;">SoLEXS (Solar Low Energy X-ray Spectrometer)</h4>
                <ul>
                    <li><strong>Energy Passband</strong>: 1.0 – 22.0 keV (Soft X-rays)</li>
                    <li><strong>Detector Technology</strong>: Silicon Drift Detector (SDD) with Peltier cooling</li>
                    <li><strong>Energy Resolution</strong>: &lt; 250 eV @ 5.9 keV</li>
                    <li><strong>Physical Role</strong>: Measures thermal plasma heating, coronal emission measure, and slow radiative exponential decay.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p2:
        st.markdown(
            """
            <div class="mission-card" style="border-left: 4px solid #00f0ff;">
                <h4 style="color: #00f0ff; margin-top: 0;">HEL1OS (High Energy L1 Orbiting X-ray Spectrometer)</h4>
                <ul>
                    <li><strong>Energy Passband</strong>: 10.0 – 150.0 keV (Hard X-rays)</li>
                    <li><strong>Detector Technology</strong>: Cadmium Zinc Telluride (CZT) & CdTe solid-state detectors</li>
                    <li><strong>Temporal Resolution</strong>: 1.0 ms event timing</li>
                    <li><strong>Physical Role</strong>: Captures non-thermal bremsstrahlung from relativistic accelerated electron beams striking dense chromospheric footpoints.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
