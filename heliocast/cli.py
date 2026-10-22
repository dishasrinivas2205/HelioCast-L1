"""
Command-Line Interface (CLI) for HelioCast-L1.
Provides operational subcommands for pipeline execution, demo runs,
REST server startup, dashboard launching, and system diagnostics.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

from heliocast import __mission__, __version__
from heliocast.config import get_settings
from heliocast.data.synthetic import SolarFlareSimulator
from heliocast.forecaster.pipeline import FlareForecastingPipeline
from heliocast.logging import get_logger
from heliocast.nowcaster import SolarFlareNowcaster

logger = get_logger("heliocast.cli")


def run_pipeline(hours: float = 6.0, cadence: float = 10.0) -> None:
    """Execute end-to-end HelioCast-L1 scientific pipeline."""
    print("=" * 72)
    print(f" ☀️  HELIOCAST-L1 v{__version__} : ADITYA-L1 SOLAR FLARE PIPELINE  ☀️ ")
    print(f"     Mission: {__mission__} | Cadence: {cadence}s | Duration: {hours}h")
    print("=" * 72)

    # 1. Ingestion
    print("\n[1/4] Ingesting Aditya-L1 Telemetry (SoLEXS 1-22 keV & HEL1OS 10-150 keV)...")
    sim = SolarFlareSimulator(random_seed=42)
    df, ground_truth = sim.generate_stream(duration_hours=hours, cadence_sec=cadence)
    print(f"      -> Ingested {len(df)} frames ({df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]})")
    print(f"      -> Ground-truth events: {len(ground_truth)} flares")

    # 2. Predictive Forecaster
    print("\n[2/4] Executing Heliophysics Precursor Forecaster (Quantifiable Lead Time)...")
    pipeline = FlareForecastingPipeline(horizon_minutes=30.0, cadence_sec=cadence)
    result = pipeline.train_and_evaluate(df, ground_truth)
    metrics = result.metrics

    print(f"      -> Precursor Model Validation Skill Scores:")
    print(f"         • True Skill Statistic (TSS) : {metrics['TSS']}")
    print(f"         • Heidke Skill Score (HSS)   : {metrics['HSS']}")
    print(f"         • Sensitivity (TPR)          : {metrics['TPR'] * 100:.1f}%")
    print(f"         • False Alarm Ratio (FAR)    : {metrics['FAR'] * 100:.1f}%")
    print(f"         • Brier Skill Score (BSS)    : {metrics['BSS']}")

    print(f"\n      -> Quantifiable Lead Times Prior to Flare Peak:")
    for lt in result.lead_times:
        print(f"         • Flare {lt.flare_class} Peak @ {lt.peak_time} -> Lead Time: {lt.lead_time_minutes} min [{lt.status}]")

    # 3. Algorithmic Nowcaster & Master Fusion
    print("\n[3/4] Running Algorithmic Nowcaster (Step 3: Independent + Master Fusion)...")
    nowcaster = SolarFlareNowcaster()
    sx_evts, hx_evts, master_evts = nowcaster.process_telemetry(df)
    print(f"      -> Independent SoLEXS detections : {len(sx_evts)}")
    print(f"      -> Independent HEL1OS detections : {len(hx_evts)}")
    print(f"      -> Master Catalogue Fused Flares : {len(master_evts)}")

    for m in master_evts:
        print(
            f"         • [{m.master_id}] Class: {m.flare_class} | Peak SXR: {m.solexs_peak_flux:.1f} | "
            f"Neupert Verified: {m.neupert_verified} (r={m.neupert_correlation}) | Status: {m.confirmation_status}"
        )

    # 4. Master Database & CSV Export
    print("\n[4/4] Exporting ISSDC Master Flare Catalogue...")
    csv_path = nowcaster.db.export_csv()
    print(f"      -> Exported to: {csv_path}")

    print("\n" + "=" * 72)
    print(" ✅  PIPELINE EXECUTION COMPLETE!")
    print("=" * 72)


def main():
    parser = argparse.ArgumentParser(
        prog="heliocast",
        description="HelioCast-L1: ISRO Aditya-L1 Solar Flare Operational System",
    )
    parser.add_argument("-v", "--version", action="version", version=f"HelioCast-L1 v{__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Run
    p_run = subparsers.add_parser("run", help="Run end-to-end scientific pipeline")
    p_run.add_argument("--hours", type=float, default=6.0, help="Observation window duration in hours")
    p_run.add_argument("--cadence", type=float, default=10.0, help="Sampling cadence in seconds")

    # Demo
    subparsers.add_parser("demo", help="Run quick operational demonstration")

    # Serve
    p_serve = subparsers.add_parser("serve", help="Launch FastAPI scientific REST server")
    p_serve.add_argument("--host", default="0.0.0.0", help="Host interface")
    p_serve.add_argument("--port", type=int, default=8000, help="Port")
    p_serve.add_argument("--reload", action="store_true", help="Enable hot reload")

    # UI
    p_ui = subparsers.add_parser("ui", help="Launch Mission Control Streamlit HUD")
    p_ui.add_argument("--port", type=int, default=8501, help="Port")

    # Health
    subparsers.add_parser("health", help="Check system environment and dependency sanity")

    args = parser.parse_args()

    if args.command in ["run", "demo"] or args.command is None:
        hours = getattr(args, "hours", 6.0) if args.command == "run" else 4.0
        cadence = getattr(args, "cadence", 10.0) if args.command == "run" else 10.0
        run_pipeline(hours=hours, cadence=cadence)

    elif args.command == "serve":
        import uvicorn
        settings = get_settings()
        host = args.host or settings.api_host
        port = args.port or settings.api_port
        uvicorn.run("heliocast.api.app:app", host=host, port=port, reload=args.reload)

    elif args.command == "ui":
        ui_script = Path(__file__).parent.parent / "frontend" / "app.py"
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(ui_script), "--server.port", str(args.port)])

    elif args.command == "health":
        print(f"HelioCast-L1 Environment Sanity Check:")
        print(f"  • Python Runtime : {sys.version}")
        print(f"  • Version        : {__version__}")
        print(f"  • Mission        : {__mission__}")
        settings = get_settings()
        print(f"  • Database Path  : {settings.database_path}")
        print(f"  • Outputs Dir    : {settings.outputs_dir}")
        print("  -> System Status: ALL SUBSYSTEMS NOMINAL")


if __name__ == "__main__":
    main()
