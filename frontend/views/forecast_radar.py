"""
Precursor Forecasting Radar & Lead Time View.
Fulfills Step 4 & Outcome 2 of ISRO Problem Statement 15:
Trained precursor model with quantifiable lead time (15 - 45 minutes).
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from frontend.components.metrics_card import render_metric_card


def render_forecast_radar_view():
    st.markdown("### 🔮 Solar Flare Precursor Forecasting & Quantifiable Lead Time")
    st.markdown(
        "Fulfills the ISRO predictive modeling objective: identifying precursor thermal heating acceleration, "
        "energy accumulation, and non-thermal spectral hardening **before** the flare peak occurs."
    )

    forecast_res = st.session_state.get("forecast_res")
    if forecast_res is None:
        st.warning("Forecasting model not yet initialized. Please visit Live Ops first.")
        return

    # Lead Time Cards
    st.markdown("#### ⏱️ Quantifiable Lead Times Prior to Flare Peak")
    cols = st.columns(len(forecast_res.lead_times))
    for idx, lt in enumerate(forecast_res.lead_times):
        with cols[idx]:
            render_metric_card(
                label=f"Flare Event {lt.flare_class}",
                value=f"{lt.lead_time_minutes:.1f} min",
                delta=f"Peak: {lt.peak_time.split(' ')[1]}",
                subtext=f"Status: {lt.status} • Earliest Alert Trigger",
                color="#00f0ff" if lt.alert_triggered else "#ff0055",
            )

    st.markdown("---")

    col_gauge, col_importance = st.columns([1, 1])

    with col_gauge:
        st.markdown("#### Instantaneous Flare Precursor Probability")
        curr_step = st.session_state.get("step_idx", 480)
        curr_prob = float(forecast_res.probabilities[curr_step])

        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number+delta",
                value=curr_prob * 100,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "P(Flare within 30 min)", "font": {"size": 20, "color": "#f8fafc"}},
                delta={"reference": 60.0, "increasing": {"color": "#ff0055"}, "decreasing": {"color": "#00ff88"}},
                number={"suffix": "%", "font": {"size": 42, "color": "#00f0ff"}},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#94a3b8"},
                    "bar": {"color": "#ff0055" if curr_prob >= 0.60 else "#00f0ff"},
                    "bgcolor": "rgba(15, 23, 42, 0.8)",
                    "borderwidth": 2,
                    "bordercolor": "rgba(56, 189, 248, 0.3)",
                    "steps": [
                        {"range": [0, 40], "color": "rgba(0, 255, 136, 0.15)"},
                        {"range": [40, 60], "color": "rgba(255, 183, 3, 0.15)"},
                        {"range": [60, 100], "color": "rgba(255, 0, 85, 0.25)"},
                    ],
                    "threshold": {
                        "line": {"color": "#ff0055", "width": 4},
                        "thickness": 0.85,
                        "value": 60,
                    },
                },
            )
        )
        fig_gauge.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(11, 15, 25, 0.8)",
            height=340,
            margin=dict(l=30, r=30, t=50, b=30),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_importance:
        st.markdown("#### Heliophysical Feature Importance Ranking")
        importances = forecast_res.feature_importances
        df_imp = pd.DataFrame({
            "Feature": list(importances.keys()),
            "Importance": list(importances.values()),
        }).sort_values(by="Importance", ascending=True)

        fig_bar = px.bar(
            df_imp,
            x="Importance",
            y="Feature",
            orientation="h",
            color="Importance",
            color_continuous_scale=["#00f0ff", "#ffb703", "#ff0055"],
        )
        fig_bar.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(11, 15, 25, 0.8)",
            plot_bgcolor="rgba(15, 23, 42, 0.6)",
            height=340,
            margin=dict(l=30, r=30, t=20, b=30),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True)
