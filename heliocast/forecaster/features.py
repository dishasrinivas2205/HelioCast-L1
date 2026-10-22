"""
Causal Heliophysical Precursor Feature Extraction Engine.
Extracts strictly backward-looking time-series features from combined
SoLEXS and HEL1OS observations with zero lookahead leakage.
"""

from typing import List, Tuple
import numpy as np
import pandas as pd


FEATURE_NAMES = [
    "solexs_flux_current",
    "helios_flux_current",
    "hardness_ratio_current",
    "solexs_grad_short",
    "solexs_grad_long",
    "solexs_accel",
    "helios_grad_short",
    "solexs_rolling_std_5m",
    "solexs_rolling_std_15m",
    "helios_rolling_std_5m",
    "solexs_energy_integral_15m",
    "hardness_ratio_mean_10m",
    "hardness_ratio_delta",
    "flux_ratio_to_baseline",
]


class PrecursorFeatureExtractor:
    """
    Computes physical precursor signatures indicative of magnetic reconnection
    and pre-flare thermal plasma heating.
    """

    def __init__(self, cadence_sec: float = 10.0):
        self.cadence_sec = cadence_sec

    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract causal features from synchronized telemetry dataframe.
        """
        sxr = df["solexs_flux"].to_numpy(dtype=float)
        hxr = df["helios_flux"].to_numpy(dtype=float)
        hardness = df["hardness_ratio"].to_numpy(dtype=float)

        n = len(df)
        features = pd.DataFrame(index=df.index)

        # 1. Current instantaneous states
        features["solexs_flux_current"] = sxr
        features["helios_flux_current"] = hxr
        features["hardness_ratio_current"] = hardness

        # 2. First-order gradients (heating rate)
        # Short window: ~1 min (6 steps at 10s)
        # Long window: ~5 min (30 steps at 10s)
        w_short = max(3, int(60.0 / self.cadence_sec))
        w_long = max(6, int(300.0 / self.cadence_sec))
        w_15m = max(10, int(900.0 / self.cadence_sec))

        sxr_series = pd.Series(sxr)
        hxr_series = pd.Series(hxr)
        hr_series = pd.Series(hardness)

        # Causal backward differences
        features["solexs_grad_short"] = (sxr_series - sxr_series.shift(w_short)).fillna(0.0)
        features["solexs_grad_long"] = (sxr_series - sxr_series.shift(w_long)).fillna(0.0)
        features["helios_grad_short"] = (hxr_series - hxr_series.shift(w_short)).fillna(0.0)

        # 3. Second-order gradient / thermal acceleration
        grad1 = (sxr_series - sxr_series.shift(w_short)).fillna(0.0)
        features["solexs_accel"] = (grad1 - grad1.shift(w_short)).fillna(0.0)

        # 4. Rolling plasma turbulence & variance
        features["solexs_rolling_std_5m"] = sxr_series.rolling(window=w_long, min_periods=1).std().fillna(0.0)
        features["solexs_rolling_std_15m"] = sxr_series.rolling(window=w_15m, min_periods=1).std().fillna(0.0)
        features["helios_rolling_std_5m"] = hxr_series.rolling(window=w_long, min_periods=1).std().fillna(0.0)

        # 5. Energy accumulation integral over prior 15 minutes
        features["solexs_energy_integral_15m"] = sxr_series.rolling(window=w_15m, min_periods=1).sum().fillna(0.0) * self.cadence_sec

        # 6. Spectral hardness dynamics
        features["hardness_ratio_mean_10m"] = hr_series.rolling(window=int(600.0 / self.cadence_sec), min_periods=1).mean().fillna(0.0)
        features["hardness_ratio_delta"] = (hr_series - hr_series.shift(w_long)).fillna(0.0)

        # 7. Elevation relative to rolling quiet-Sun background
        rolling_base = sxr_series.rolling(window=w_15m * 2, min_periods=1).quantile(0.20).fillna(150.0)
        features["flux_ratio_to_baseline"] = sxr / np.maximum(rolling_base.to_numpy(), 10.0)

        # Replace any residual NaNs or infinities
        features = features.replace([np.inf, -np.inf], 0.0).fillna(0.0)
        return features[FEATURE_NAMES]
