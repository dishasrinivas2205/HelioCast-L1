"""
FastAPI REST API Routes for HelioCast-L1 Scientific Server.
Provides versioned endpoints for telemetry ingestion, nowcasting,
forecasting, database querying, and alert notifications.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
import pandas as pd
from pydantic import BaseModel, Field

from heliocast import __version__
from heliocast.alerts.dispatcher import AlertDispatcher, SpaceWeatherAlert
from heliocast.data.synthetic import SolarFlareSimulator
from heliocast.forecaster.pipeline import FlareForecastingPipeline
from heliocast.nowcaster import FlareCatalogDatabase, SolarFlareNowcaster

router = APIRouter(prefix="/api/v1", tags=["HelioCast Space Weather API"])

# Shared singleton instances
nowcaster = SolarFlareNowcaster()
forecaster = FlareForecastingPipeline()
alert_dispatcher = AlertDispatcher()
sim = SolarFlareSimulator(random_seed=42)

# Cache a default telemetry stream
_cached_df, _cached_events = sim.generate_stream(duration_hours=6.0, cadence_sec=10.0)
forecaster.train_and_evaluate(_cached_df, _cached_events)


class HealthResponse(BaseModel):
    status: str = "ONLINE"
    service: str = "HelioCast-L1 Scientific Server"
    version: str = __version__
    mission: str = "ISRO Aditya-L1"
    instruments: Dict[str, str] = {
        "SOLEXS": "1 - 22 keV (Soft X-rays, SDD)",
        "HEL1OS": "10 - 150 keV (Hard X-rays, CZT/CdTe)",
    }
    timestamp: str


class TelemetryFrameResponse(BaseModel):
    timestamp: str
    solexs_flux: float
    helios_flux: float
    hardness_ratio: float
    flare_active: bool
    flare_class: Optional[str] = None


class TelemetryBatchResponse(BaseModel):
    count: int
    cadence_sec: float
    data: List[TelemetryFrameResponse]


class MasterCatalogItem(BaseModel):
    master_id: str
    flare_class: str
    start_time: str
    peak_time: str
    end_time: str
    duration_minutes: float
    solexs_peak_flux: float
    helios_peak_count_rate: float
    spectral_hardness_ratio: float
    neupert_correlation: float
    neupert_verified: bool
    confirmation_status: str
    confidence_score: float


@router.get("/health", response_model=HealthResponse)
def get_health():
    """Retrieve subsystem health and payload availability status."""
    return HealthResponse(timestamp=datetime.now(timezone.utc).isoformat())


@router.get("/telemetry/latest", response_model=TelemetryFrameResponse)
def get_latest_telemetry():
    """Fetch the most recent telemetry frame from Aditya-L1 stream."""
    last_row = _cached_df.iloc[-1]
    fc = str(last_row["flare_class"]) if pd.notna(last_row["flare_class"]) else None
    return TelemetryFrameResponse(
        timestamp=str(last_row["timestamp"]),
        solexs_flux=float(last_row["solexs_flux"]),
        helios_flux=float(last_row["helios_flux"]),
        hardness_ratio=float(last_row["hardness_ratio"]),
        flare_active=bool(last_row["flare_active"]),
        flare_class=fc,
    )


@router.get("/telemetry/lightcurve", response_model=TelemetryBatchResponse)
def get_lightcurve(limit: int = Query(default=360, ge=10, le=3600)):
    """Fetch recent synchronized light curve telemetry batch."""
    slice_df = _cached_df.iloc[-limit:]
    records = []
    for _, row in slice_df.iterrows():
        fc = str(row["flare_class"]) if pd.notna(row["flare_class"]) else None
        records.append(
            TelemetryFrameResponse(
                timestamp=str(row["timestamp"]),
                solexs_flux=float(row["solexs_flux"]),
                helios_flux=float(row["helios_flux"]),
                hardness_ratio=float(row["hardness_ratio"]),
                flare_active=bool(row["flare_active"]),
                flare_class=fc,
            )
        )
    return TelemetryBatchResponse(
        count=len(records),
        cadence_sec=10.0,
        data=records,
    )


@router.post("/nowcast/detect", response_model=List[MasterCatalogItem])
def trigger_nowcast_detection():
    """Trigger multi-band algorithmic nowcasting on current telemetry."""
    _, _, master_evts = nowcaster.process_telemetry(_cached_df)
    items = []
    for ev in master_evts:
        items.append(
            MasterCatalogItem(
                master_id=ev.master_id,
                flare_class=ev.flare_class,
                start_time=ev.start_time,
                peak_time=ev.peak_time,
                end_time=ev.end_time,
                duration_minutes=ev.duration_minutes,
                solexs_peak_flux=ev.solexs_peak_flux,
                helios_peak_count_rate=ev.helios_peak_count_rate,
                spectral_hardness_ratio=ev.spectral_hardness_ratio,
                neupert_correlation=ev.neupert_correlation,
                neupert_verified=ev.neupert_verified,
                confirmation_status=ev.confirmation_status,
                confidence_score=ev.confidence_score,
            )
        )
    return items


@router.get("/catalog/master", response_model=List[MasterCatalogItem])
def get_master_catalog(
    min_class: Optional[str] = Query(default=None, description="Minimum flare class, e.g. 'C' or 'M'"),
    only_neupert_verified: bool = Query(default=False, description="Filter for Neupert confirmed flares only"),
):
    """Query the persistent SQLite master flare catalogue."""
    df = nowcaster.get_master_catalog()
    if df.empty:
        # Trigger detection if catalog empty
        _, _, _ = nowcaster.process_telemetry(_cached_df)
        df = nowcaster.get_master_catalog()

    if only_neupert_verified and "neupert_verified" in df.columns:
        df = df[df["neupert_verified"] == 1]

    if min_class and "flare_class" in df.columns:
        df = df[df["flare_class"].str.startswith(min_class.upper())]

    items = []
    for _, row in df.iterrows():
        items.append(
            MasterCatalogItem(
                master_id=str(row["master_id"]),
                flare_class=str(row["flare_class"]),
                start_time=str(row["start_time"]),
                peak_time=str(row["peak_time"]),
                end_time=str(row["end_time"]),
                duration_minutes=float(row["duration_minutes"]),
                solexs_peak_flux=float(row["solexs_peak_flux"]),
                helios_peak_count_rate=float(row["helios_peak_count_rate"]),
                spectral_hardness_ratio=float(row["spectral_hardness_ratio"]),
                neupert_correlation=float(row["neupert_correlation"]),
                neupert_verified=bool(row["neupert_verified"]),
                confirmation_status=str(row["confirmation_status"]),
                confidence_score=float(row["confidence_score"]),
            )
        )
    return items


@router.get("/alerts/history")
def get_alert_history():
    """Retrieve operational space weather alerts dispatched during this session."""
    return [alert.__dict__ for alert in alert_dispatcher.alert_history]
