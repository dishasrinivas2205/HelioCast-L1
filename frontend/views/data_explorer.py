"""
Synchronized Dual-Band Light Curve Explorer View.
Fulfills Step 2 of ISRO Problem Statement 15:
Visually understand typical solar flare light curves in soft and hard X-rays.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.signal import savgol_filter
import streamlit as st


def render_data_explorer_view():
    st.markdown("### 📈 Synchronized Dual-Band X-Ray Light Curve Explorer")
    st.markdown(
        "Interactive analysis of Aditya-L1 **SoLEXS (1-22 keV)** and **HEL1OS (10-150 keV)** telemetry. "
        "Demonstrates the solar Neupert Effect: thermal soft X-ray rise derivative tracks non-thermal hard X-ray emission."
    )

    df = st.session_state.get("sim_df")
    if df is None:
        st.warning("Telemetry stream not initialized. Please visit Live Ops first.")
        return

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        time_filter = st.selectbox(
            "Select Observation Window",
            options=["Full Telemetry Stream (6 Hours)", "Event 1: C4.8 Flare Window", "Event 2: M2.5 Flare Window"],
        )
    with col2:
        show_neupert_derivative = st.checkbox("Show Neupert Derivative dF_SXR/dt", value=True)
    with col3:
        show_hardness_ratio = st.checkbox("Show Hardness Ratio", value=True)

    # Slice dataframe according to selection
    if "Event 1" in time_filter:
        view_df = df.iloc[300:650].copy()
    elif "Event 2" in time_filter:
        view_df = df.iloc[1100:1600].copy()
    else:
        view_df = df.copy()

    # Calculate Neupert derivative
    sxr = view_df["solexs_flux"].to_numpy(dtype=float)
    w_len = min(15, len(sxr) if len(sxr) % 2 != 0 else len(sxr) - 1)
    smooth_sxr = savgol_filter(sxr, window_length=w_len, polyorder=2)
    d_sxr = np.maximum(0.0, np.gradient(smooth_sxr))

    # Scale derivative to compare with HEL1OS on same visual axis
    hxr = view_df["helios_flux"].to_numpy(dtype=float)
    scale_factor = np.max(hxr) / max(1e-3, np.max(d_sxr))
    d_sxr_scaled = d_sxr * scale_factor

    # Create subplots
    rows = 2 if show_hardness_ratio else 1
    row_heights = [0.75, 0.25] if show_hardness_ratio else [1.0]

    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=(
            "Aditya-L1 Dual-Band X-Ray Irradiance & Neupert Coupling",
            "Spectral Hardness Ratio (F_HEL1OS / F_SoLEXS)" if show_hardness_ratio else None,
        ),
        row_heights=row_heights,
    )

    # 1. SoLEXS Soft X-rays
    fig.add_trace(
        go.Scatter(
            x=view_df["timestamp"],
            y=view_df["solexs_flux"],
            name="SoLEXS Soft X-Ray (1-22 keV)",
            line=dict(color="#ffb703", width=2.5),
        ),
        row=1,
        col=1,
    )

    # 2. HEL1OS Hard X-rays
    fig.add_trace(
        go.Scatter(
            x=view_df["timestamp"],
            y=view_df["helios_flux"],
            name="HEL1OS Hard X-Ray (10-150 keV)",
            line=dict(color="#00f0ff", width=2.0),
        ),
        row=1,
        col=1,
    )

    # 3. Neupert Derivative
    if show_neupert_derivative:
        fig.add_trace(
            go.Scatter(
                x=view_df["timestamp"],
                y=d_sxr_scaled,
                name="d/dt F_SoLEXS (Neupert Rise Derivative)",
                line=dict(color="#00ff88", width=1.5, dash="dot"),
            ),
            row=1,
            col=1,
        )

    # 4. Hardness ratio
    if show_hardness_ratio:
        fig.add_trace(
            go.Scatter(
                x=view_df["timestamp"],
                y=view_df["hardness_ratio"],
                name="Hardness Ratio",
                line=dict(color="#a855f7", width=1.5),
                fill="tozeroy",
                fillcolor="rgba(168, 85, 247, 0.15)",
            ),
            row=2,
            col=1,
        )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(2, 4, 10, 0.95)",
        plot_bgcolor="rgba(8, 14, 28, 0.75)",
        height=600,
        margin=dict(l=40, r=40, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family="JetBrains Mono", size=11)),
        hovermode="x unified",
    )
    fig.update_xaxes(gridcolor="rgba(56, 189, 248, 0.08)", zerolinecolor="rgba(56, 189, 248, 0.15)")
    fig.update_yaxes(title_text="Count Rate (count/s)", gridcolor="rgba(56, 189, 248, 0.08)", zerolinecolor="rgba(56, 189, 248, 0.15)", row=1, col=1)
    if show_hardness_ratio:
        fig.update_yaxes(title_text="Hardness", gridcolor="rgba(56, 189, 248, 0.08)", zerolinecolor="rgba(56, 189, 248, 0.15)", row=2, col=1)

    st.plotly_chart(fig, use_container_width=True)

    # Export CSV download
    csv = view_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Synchronized Telemetry Data (CSV)",
        data=csv,
        file_name="aditya_l1_synchronized_telemetry.csv",
        mime="text/csv",
    )
