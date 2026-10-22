"""
Quantifiable Lead-Time Estimation Subsystem for HelioCast-L1.
Evaluates how many minutes before the solar flare peak
the predictive precursor model triggers a space weather alert.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


@dataclass
class LeadTimeRecord:
    """Individual lead-time assessment for a flare event."""
    event_id: str
    flare_class: str
    peak_time: str
    alert_trigger_time: Optional[str]
    lead_time_minutes: float
    alert_triggered: bool
    status: str                     # EARLY_WARNING_SUCCESS, MARGINAL_WARNING, MISSED_EVENT


class LeadTimeEstimator:
    """
    Computes empirical lead times between precursor model alerts and actual flare peaks.
    """

    def __init__(
        self,
        alert_threshold: float = 0.60,
        max_lookahead_min: float = 60.0,
        min_lead_min: float = 5.0,
    ):
        self.alert_threshold = alert_threshold
        self.max_lookahead_min = max_lookahead_min
        self.min_lead_min = min_lead_min

    def evaluate(
        self,
        telemetry_df: pd.DataFrame,
        probabilities: np.ndarray,
        flare_events: List[Dict[str, Any]],
    ) -> List[LeadTimeRecord]:
        """
        Compute lead time for each solar flare event in the test dataset.
        """
        timestamps = pd.to_datetime(telemetry_df["timestamp"], utc=True)
        results: List[LeadTimeRecord] = []

        for fl in flare_events:
            peak_dt = pd.to_datetime(fl.get("peak_time"), utc=True)
            fl_class = fl.get("flare_class", "C1.0")
            event_id = fl.get("event_id", f"AL1-{peak_dt.strftime('%Y%m%d-%H%M%S')}")

            # Define valid precursor evaluation window: [peak_dt - max_lookahead, peak_dt]
            precursor_mask = (
                (timestamps >= peak_dt - pd.Timedelta(minutes=self.max_lookahead_min))
                & (timestamps < peak_dt)
            )
            prec_indices = np.where(precursor_mask.to_numpy())[0]

            alert_time = None
            lead_time_min = 0.0
            alert_triggered = False

            if len(prec_indices) > 0:
                # Find earliest timestamp within precursor window where probability exceeds threshold
                prob_slice = probabilities[prec_indices]
                trigger_locs = np.where(prob_slice >= self.alert_threshold)[0]

                if len(trigger_locs) > 0:
                    earliest_idx = prec_indices[trigger_locs[0]]
                    alert_time = timestamps.iloc[earliest_idx]
                    lead_time_min = round((peak_dt - alert_time).total_seconds() / 60.0, 1)
                    alert_triggered = True

            if alert_triggered and lead_time_min >= self.min_lead_min:
                status = "EARLY_WARNING_SUCCESS"
            elif alert_triggered:
                status = "MARGINAL_WARNING"
            else:
                status = "MISSED_EVENT"

            results.append(
                LeadTimeRecord(
                    event_id=event_id,
                    flare_class=fl_class,
                    peak_time=peak_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    alert_trigger_time=alert_time.strftime("%Y-%m-%d %H:%M:%S") if alert_time else None,
                    lead_time_minutes=lead_time_min,
                    alert_triggered=alert_triggered,
                    status=status,
                )
            )

        return results
