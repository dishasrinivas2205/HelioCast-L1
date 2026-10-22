"""
Automated Flare Catalogues Hub View.
Strictly implements Step 3 of ISRO Problem Statement 15:
- Independent SoLEXS Flare Catalogue
- Independent HEL1OS Non-Thermal Burst Catalogue
- Master Fused Catalogue with Neupert Correlation Verification
"""

import pandas as pd
import streamlit as st

from heliocast.nowcaster import FlareCatalogDatabase, SolarFlareNowcaster


def render_nowcast_catalog_view():
    st.markdown("### 📋 Automated Solar Flare Catalogues (Step 3: Multi-Band Fusion)")
    st.markdown(
        "Fulfills the ISRO Problem Statement 15 requirement: "
        "Flares are detected independently in **SoLEXS (Soft X-rays)** and **HEL1OS (Hard X-rays)**, "
        "and merged into a consolidated **Master Catalogue** via physical Neupert effect verification."
    )

    db = FlareCatalogDatabase()
    nowcaster = SolarFlareNowcaster()

    # On-demand detection runner
    col_act1, col_act2 = st.columns([2, 1])
    with col_act1:
        if st.button("🚀 Re-Run Algorithmic Detection & Master Fusion", type="primary"):
            sim_df = st.session_state.get("sim_df")
            if sim_df is not None:
                with st.spinner("Processing dual-band telemetry with Neupert verification..."):
                    nowcaster.process_telemetry(sim_df)
                st.success("Algorithmic Nowcaster completed! Catalogues updated.")
                st.rerun()

    tab_master, tab_solexs, tab_helios = st.tabs([
        "🌟 Combined Master Flare Catalogue",
        "🟡 Independent SoLEXS Catalogue (Soft X-ray)",
        "🔵 Independent HEL1OS Catalogue (Hard X-ray)",
    ])

    # 1. Master Catalogue Tab
    with tab_master:
        df_master = db.get_master_catalog_df()
        st.markdown(f"#### Master Consolidated Catalogue ({len(df_master)} Events Recorded)")
        if not df_master.empty:
            # Display metrics summary
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Master Flares", len(df_master))
            m2.metric("Neupert Verified", int((df_master["neupert_verified"] == 1).sum()))
            m3.metric("M/X Class Flares", int(df_master["flare_class"].str.contains("M|X").sum()))
            m4.metric("Avg Confidence", f"{df_master['confidence_score'].mean()*100:.1f}%")

            st.dataframe(
                df_master[[
                    "master_id", "flare_class", "start_time", "peak_time", "end_time",
                    "duration_minutes", "solexs_peak_flux", "helios_peak_count_rate",
                    "spectral_hardness_ratio", "neupert_correlation", "neupert_verified",
                    "confirmation_status", "confidence_score",
                ]],
                use_container_width=True,
            )

            csv_master = df_master.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Master Flare Catalogue (CSV)",
                data=csv_master,
                file_name="aditya_l1_master_flare_catalog.csv",
                mime="text/csv",
            )
        else:
            st.info("No master flares logged yet. Run detection to populate.")

    # 2. Independent SoLEXS Tab
    with tab_solexs:
        df_sx = db.get_solexs_catalog_df()
        st.markdown(f"#### Independent SoLEXS (1-22 keV) Detections ({len(df_sx)} Events)")
        if not df_sx.empty:
            st.dataframe(
                df_sx[[
                    "event_id", "flare_class", "start_time", "peak_time", "end_time",
                    "duration_minutes", "peak_flux", "baseline_flux", "snr",
                ]],
                use_container_width=True,
            )
        else:
            st.info("No independent SoLEXS flares recorded yet.")

    # 3. Independent HEL1OS Tab
    with tab_helios:
        df_hx = db.get_helios_catalog_df()
        st.markdown(f"#### Independent HEL1OS (10-150 keV) Impulsive Bursts ({len(df_hx)} Events)")
        if not df_hx.empty:
            st.dataframe(
                df_hx[[
                    "event_id", "start_time", "peak_time", "end_time",
                    "duration_seconds", "peak_count_rate", "baseline_count_rate",
                    "non_thermal_fluence", "snr",
                ]],
                use_container_width=True,
            )
        else:
            st.info("No independent HEL1OS non-thermal bursts recorded yet.")
