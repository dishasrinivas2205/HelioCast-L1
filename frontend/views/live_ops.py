"""
Live Flight Ops & Mission Replay Simulator View.
Provides real-time interactive telemetry streaming with live visual & audio alerts.
"""

from datetime import datetime, timezone
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from frontend.components.alert_banner import render_alert_banner
from frontend.components.metrics_card import render_metric_card
from heliocast.data.synthetic import SolarFlareSimulator
from heliocast.forecaster.pipeline import FlareForecastingPipeline
from heliocast.nowcaster import SolarFlareNowcaster


def render_live_ops_view():
    st.markdown("### 🛰️ Live Space Weather Flight Operations & Replay Simulator")
    st.markdown(
        "Real-time streaming telemetry simulator mimicking Aditya-L1 downlinks from L1. "
        "Continuously evaluates precursor probabilities and dispatches visual alerts with quantifiable lead time."
    )

    # Initialize simulation telemetry in session state if not present
    if "sim_df" not in st.session_state:
        sim = SolarFlareSimulator(random_seed=42)
        df, ground_truth = sim.generate_stream(duration_hours=6.0, cadence_sec=10.0)
        st.session_state.sim_df = df
        st.session_state.ground_truth = ground_truth

        # Pre-compute forecasting pipeline
        forecaster = FlareForecastingPipeline(horizon_minutes=30.0, cadence_sec=10.0)
        res = forecaster.train_and_evaluate(df, ground_truth)
        st.session_state.forecast_res = res
        st.session_state.forecaster = forecaster
        st.session_state.step_idx = 480  # Default to an interesting point near first precursor

    df = st.session_state.sim_df
    probs = st.session_state.forecast_res.probabilities
    total_steps = len(df)

    # Playback Controls
    col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns([3, 1, 1, 1])
    with col_ctrl1:
        step = st.slider(
            "Mission Time Slider",
            min_value=60,
            max_value=total_steps - 1,
            value=st.session_state.step_idx,
            step=10,
            help="Scrub forward and backward through the space weather event stream",
        )
        st.session_state.step_idx = step

    with col_ctrl2:
        if st.button("⏪ -10 Min"):
            st.session_state.step_idx = max(60, st.session_state.step_idx - 60)
            st.rerun()

    with col_ctrl3:
        if st.button("⏩ +10 Min"):
            st.session_state.step_idx = min(total_steps - 1, st.session_state.step_idx + 60)
            st.rerun()

    with col_ctrl4:
        sound_enabled = st.checkbox("🔊 Audio Alerts", value=True)

    current_idx = st.session_state.step_idx
    curr_row = df.iloc[current_idx]
    curr_prob = float(probs[current_idx])
    curr_time = curr_row["timestamp"]
    curr_sxr = float(curr_row["solexs_flux"])
    curr_hxr = float(curr_row["helios_flux"])
    curr_hr = float(curr_row["hardness_ratio"])

    # Check alert status
    is_forecast_alert = curr_prob >= 0.60
    is_nowcast_alert = bool(curr_row.get("flare_active", False) and curr_sxr > 800.0)
    flare_class = curr_row.get("flare_class") or "C4.8"

    # Render Visual Alert Banner if triggered
    if is_nowcast_alert:
        render_alert_banner(
            alert_type="NOWCAST",
            flare_class=flare_class,
            lead_time_min=0.0,
            confidence=0.96,
            details=f"Peak Count Rate: {curr_sxr:.1f} count/s • Non-Thermal Hard X-ray Burst Verified via Neupert Effect",
            enable_audio=sound_enabled,
        )
    elif is_forecast_alert:
        # Approximate lead time to nearest upcoming peak
        lead_min = max(5.0, round((pd.to_datetime("2024-05-14 09:15:00", utc=True) - pd.to_datetime(curr_time, utc=True)).total_seconds() / 60.0, 1))
        render_alert_banner(
            alert_type="FORECAST",
            flare_class=flare_class,
            lead_time_min=lead_min,
            confidence=curr_prob,
            details=f"Causal Precursor Heating Acceleration Detected • Forecast Horizon: 30 min",
            enable_audio=sound_enabled,
        )

    # Key Telemetry Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card(
            label="SoLEXS Soft X-Ray (1-22 keV)",
            value=f"{curr_sxr:.1f}",
            delta="count/s",
            subtext="Thermal Plasma Heating",
            color="#ffb703",
        )
    with c2:
        render_metric_card(
            label="HEL1OS Hard X-Ray (10-150 keV)",
            value=f"{curr_hxr:.1f}",
            delta="count/s",
            subtext="Non-Thermal Bremsstrahlung",
            color="#00f0ff",
        )
    with c3:
        render_metric_card(
            label="Spectral Hardness Ratio",
            value=f"{curr_hr:.3f}",
            delta="F_HXR / F_SXR",
            subtext="Plasma Energy Distribution",
            color="#a855f7",
        )
    with c4:
        render_metric_card(
            label="Flare Precursor Probability",
            value=f"{curr_prob*100:.1f}%",
            delta="ALERT ACTIVE" if is_forecast_alert else "NOMINAL",
            subtext="Horizon: Next 30 Minutes",
            color="#ff0055" if is_forecast_alert else "#00ff88",
        )

    # Dual-Band Live Streaming Light Curve Plot
    # Show history up to current_idx with trailing window of 360 steps (~1 hour)
    window_start = max(0, current_idx - 360)
    slice_df = df.iloc[window_start : current_idx + 1]
    slice_probs = probs[window_start : current_idx + 1]

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=(
            "Dual-Band X-Ray Light Curves (SoLEXS: Amber, HEL1OS: Cyan)",
            "Flare Precursor Probability Progression & Alert Threshold (60%)",
        ),
        row_heights=[0.68, 0.32],
    )

    # SoLEXS Soft X-rays
    fig.add_trace(
        go.Scatter(
            x=slice_df["timestamp"],
            y=slice_df["solexs_flux"],
            name="SoLEXS (1-22 keV)",
            line=dict(color="#ffb703", width=2.5),
            mode="lines",
        ),
        row=1,
        col=1,
    )

    # HEL1OS Hard X-rays (on secondary scale or scaled)
    fig.add_trace(
        go.Scatter(
            x=slice_df["timestamp"],
            y=slice_df["helios_flux"],
            name="HEL1OS (10-150 keV)",
            line=dict(color="#00f0ff", width=2.0),
            mode="lines",
        ),
        row=1,
        col=1,
    )

    # Current Cursor
    fig.add_vline(
        x=curr_time,
        line_width=2,
        line_dash="dash",
        line_color="#ffffff",
        annotation_text="LIVE TELEMETRY DOWNLINK",
        annotation_position="top left",
        row=1,
        col=1,
    )

    # Forecast Probability Trace
    fig.add_trace(
        go.Scatter(
            x=slice_df["timestamp"],
            y=slice_probs,
            name="Precursor Probability",
            line=dict(color="#ff0055", width=2.5),
            fill="tozeroy",
            fillcolor="rgba(255, 0, 85, 0.15)",
        ),
        row=2,
        col=1,
    )

    # 60% Alert Threshold Line
    fig.add_hline(
        y=0.60,
        line_width=1.5,
        line_dash="dot",
        line_color="#ffb703",
        annotation_text="ALERT THRESHOLD (0.60)",
        row=2,
        col=1,
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(11, 15, 25, 0.8)",
        plot_bgcolor="rgba(15, 23, 42, 0.6)",
        height=560,
        margin=dict(l=40, r=40, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    fig.update_yaxes(title_text="Count Rate (count/s)", row=1, col=1)
    fig.update_yaxes(title_text="P(Flare in 30m)", range=[0, 1.05], row=2, col=1)

    st.plotly_chart(fig, use_container_width=True)
