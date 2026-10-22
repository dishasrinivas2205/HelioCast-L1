"""
Automated SQLite & CSV Catalog Database Manager for Aditya-L1 Solar Flares.
Persists independent SoLEXS and HEL1OS detections as well as the
unified Master Flare Catalogue with complete physical parameters.
"""

from contextlib import contextmanager
from dataclasses import asdict
import os
from pathlib import Path
import sqlite3
from typing import Any, Dict, Generator, List, Optional
import pandas as pd

from heliocast.logging import get_logger
from heliocast.nowcaster.helios_detector import HeliosFlareEvent
from heliocast.nowcaster.master_fusion import MasterFlareEvent
from heliocast.nowcaster.solexs_detector import SolexsFlareEvent

logger = get_logger("heliocast.nowcaster.catalog")


class FlareCatalogDatabase:
    """
    Automated SQLite & CSV Flare Catalog Manager.
    """

    def __init__(self, db_path: str = "data/catalog/aditya_flares.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_tables()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Safe SQLite connection lifecycle with auto-commit."""
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_tables(self) -> None:
        """Create tables for independent and master catalogues."""
        with self._get_connection() as conn:
            # Independent SoLEXS table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS solexs_events (
                    event_id TEXT PRIMARY KEY,
                    instrument TEXT,
                    start_time TEXT,
                    peak_time TEXT,
                    end_time TEXT,
                    duration_minutes REAL,
                    peak_flux REAL,
                    baseline_flux REAL,
                    net_flare_flux REAL,
                    flare_class TEXT,
                    quality_mask INTEGER,
                    snr REAL,
                    logged_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Independent HEL1OS table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS helios_events (
                    event_id TEXT PRIMARY KEY,
                    instrument TEXT,
                    start_time TEXT,
                    peak_time TEXT,
                    end_time TEXT,
                    duration_seconds REAL,
                    peak_count_rate REAL,
                    baseline_count_rate REAL,
                    non_thermal_fluence REAL,
                    snr REAL,
                    quality_mask INTEGER,
                    logged_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Unified Master Flare table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS master_flare_events (
                    master_id TEXT PRIMARY KEY,
                    flare_class TEXT,
                    start_time TEXT,
                    peak_time TEXT,
                    end_time TEXT,
                    duration_minutes REAL,
                    solexs_peak_flux REAL,
                    helios_peak_count_rate REAL,
                    spectral_hardness_ratio REAL,
                    neupert_correlation REAL,
                    neupert_verified INTEGER,
                    confirmation_status TEXT,
                    confidence_score REAL,
                    solexs_event_id TEXT,
                    helios_event_id TEXT,
                    dispatched_alert INTEGER DEFAULT 0,
                    logged_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indices for fast time-range queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_master_peak ON master_flare_events(peak_time)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_master_class ON master_flare_events(flare_class)")

    def store_solexs_events(self, events: List[SolexsFlareEvent]) -> int:
        """Insert or replace SoLEXS detection records."""
        if not events:
            return 0
        with self._get_connection() as conn:
            for ev in events:
                data = asdict(ev)
                conn.execute("""
                    INSERT OR REPLACE INTO solexs_events (
                        event_id, instrument, start_time, peak_time, end_time,
                        duration_minutes, peak_flux, baseline_flux, net_flare_flux,
                        flare_class, quality_mask, snr
                    ) VALUES (
                        :event_id, :instrument, :start_time, :peak_time, :end_time,
                        :duration_minutes, :peak_flux, :baseline_flux, :net_flare_flux,
                        :flare_class, :quality_mask, :snr
                    )
                """, data)
        return len(events)

    def store_helios_events(self, events: List[HeliosFlareEvent]) -> int:
        """Insert or replace HEL1OS detection records."""
        if not events:
            return 0
        with self._get_connection() as conn:
            for ev in events:
                data = asdict(ev)
                conn.execute("""
                    INSERT OR REPLACE INTO helios_events (
                        event_id, instrument, start_time, peak_time, end_time,
                        duration_seconds, peak_count_rate, baseline_count_rate,
                        non_thermal_fluence, snr, quality_mask
                    ) VALUES (
                        :event_id, :instrument, :start_time, :peak_time, :end_time,
                        :duration_seconds, :peak_count_rate, :baseline_count_rate,
                        :non_thermal_fluence, :snr, :quality_mask
                    )
                """, data)
        return len(events)

    def store_master_events(self, events: List[MasterFlareEvent]) -> int:
        """Insert or replace Master Flare Catalogue records."""
        if not events:
            return 0
        with self._get_connection() as conn:
            for ev in events:
                data = asdict(ev)
                data["neupert_verified"] = int(ev.neupert_verified)
                data["dispatched_alert"] = int(ev.dispatched_alert)
                conn.execute("""
                    INSERT OR REPLACE INTO master_flare_events (
                        master_id, flare_class, start_time, peak_time, end_time,
                        duration_minutes, solexs_peak_flux, helios_peak_count_rate,
                        spectral_hardness_ratio, neupert_correlation, neupert_verified,
                        confirmation_status, confidence_score, solexs_event_id,
                        helios_event_id, dispatched_alert
                    ) VALUES (
                        :master_id, :flare_class, :start_time, :peak_time, :end_time,
                        :duration_minutes, :solexs_peak_flux, :helios_peak_count_rate,
                        :spectral_hardness_ratio, :neupert_correlation, :neupert_verified,
                        :confirmation_status, :confidence_score, :solexs_event_id,
                        :helios_event_id, :dispatched_alert
                    )
                """, data)
        return len(events)

    def get_master_catalog_df(self) -> pd.DataFrame:
        """Retrieve master catalog as a pandas DataFrame."""
        with self._get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM master_flare_events ORDER BY peak_time DESC", conn)

    def get_solexs_catalog_df(self) -> pd.DataFrame:
        """Retrieve independent SoLEXS catalog as a pandas DataFrame."""
        with self._get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM solexs_events ORDER BY peak_time DESC", conn)

    def get_helios_catalog_df(self) -> pd.DataFrame:
        """Retrieve independent HEL1OS catalog as a pandas DataFrame."""
        with self._get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM helios_events ORDER BY peak_time DESC", conn)

    def export_csv(self, output_path: str = "data/catalog/aditya_l1_master_flare_catalog.csv") -> Path:
        """Export master catalog to CSV format."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        df = self.get_master_catalog_df()
        df.to_csv(str(out), index=False)
        logger.info(f"Exported Master Flare Catalog ({len(df)} records) to {out}")
        return out
