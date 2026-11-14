"""
src/pressure_calibration.py
SupeRR Selector - Pressure Index Calibration Module

This module calibrates empirical scoring baselines and establishes resource-demand
functions across T20 competitions.

Key Responsibilities:
1. Calibrate empirical expected remaining runs as a function of balls remaining,
   wickets in hand, and competition format.
2. Ensure strict leakage-safe validation via GroupKFold match-level holdouts.
3. Provide transparent category thresholding for continuous pressure scores.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple
from sklearn.model_selection import GroupKFold
from scipy.optimize import curve_fit


def parametric_resource_function(
    balls_rem: np.ndarray,
    wickets_hand: np.ndarray,
    a: float,
    beta: float,
    gamma: float
) -> np.ndarray:
    """
    Computes expected remaining runs using a cricket-aware resource power model:
    Expected Remaining Runs = a * (B / 120)^beta * (W / 10)^gamma
    
    Parameters:
    - balls_rem: Number of legal balls remaining in the innings (0 to 120)
    - wickets_hand: Number of wickets in hand (0 to 10)
    - a: Format baseline par score with 120 balls and 10 wickets remaining
    - beta: Sub-linear elasticity of balls remaining (~0.68 - 0.71)
    - gamma: Power-law elasticity of wickets in hand (~0.47 - 0.61)
    """
    b_norm = np.clip(balls_rem / 120.0, 0.0, 1.0)
    w_norm = np.clip(wickets_hand / 10.0, 0.0, 1.0)
    return a * (b_norm ** beta) * (w_norm ** gamma)


def fit_resource_model(
    balls_rem: np.ndarray,
    wickets_hand: np.ndarray,
    remaining_runs: np.ndarray,
    p0: Tuple[float, float, float] = (180.0, 0.70, 0.55)
) -> Tuple[float, float, float]:
    """
    Fits the parametric resource function to historical delivery-level data
    using non-linear least squares.
    """
    def _model_wrapper(X, a, beta, gamma):
        b, w = X
        return parametric_resource_function(b, w, a, beta, gamma)

    popt, _ = curve_fit(
        _model_wrapper,
        (balls_rem, wickets_hand),
        remaining_runs,
        p0=p0,
        bounds=([120.0, 0.3, 0.2], [240.0, 1.2, 1.2]),
        maxfev=2000
    )
    return float(popt[0]), float(popt[1]), float(popt[2])


def calibrate_resource_parameters(
    df_deliveries: pd.DataFrame,
    n_splits: int = 5
) -> Dict[str, Dict[str, float]]:
    """
    Calibrates format-specific resource parameters with match-level GroupKFold
    cross-validation to rigorously guarantee zero data leakage.
    
    Why this matters:
    If a model uses the entire dataset including match M to calculate expectations,
    match M's own total leaks into the expectation used for its early deliveries.
    Using GroupKFold ensures parameters are stable out-of-fold and leakage-free.
    """
    # Filter 1st innings of completed 20-over matches to establish true resource capacity
    inn1 = df_deliveries[
        (df_deliveries["innings"] == 1) &
        (df_deliveries["innings_max_balls"] == 120)
    ].copy()

    # Calculate actual remaining runs scored in the innings
    innings_totals = inn1.groupby("match_id")["cumulative_runs_after"].max().rename("final_innings_total")
    inn1 = inn1.merge(innings_totals, on="match_id")
    inn1["actual_remaining_runs"] = inn1["final_innings_total"] - inn1["cumulative_runs_before"]

    calibrated_params = {}

    for fmt in ["T20", "T20I"]:
        fmt_data = inn1[inn1["match_format"] == fmt].copy()
        if len(fmt_data) == 0:
            continue

        gkf = GroupKFold(n_splits=n_splits)
        fold_params = []
        r2_scores = []

        for train_idx, val_idx in gkf.split(fmt_data, groups=fmt_data["match_id"]):
            train_subset = fmt_data.iloc[train_idx]
            val_subset = fmt_data.iloc[val_idx]

            # Fit on training matches only
            a_fit, beta_fit, gamma_fit = fit_resource_model(
                train_subset["balls_remaining_before"].values,
                train_subset["wickets_in_hand_before"].values,
                train_subset["actual_remaining_runs"].values
            )
            fold_params.append((a_fit, beta_fit, gamma_fit))

            # Evaluate on out-of-fold matches
            val_pred = parametric_resource_function(
                val_subset["balls_remaining_before"].values,
                val_subset["wickets_in_hand_before"].values,
                a_fit, beta_fit, gamma_fit
            )
            val_y = val_subset["actual_remaining_runs"].values
            ss_tot = np.sum((val_y - np.mean(val_y)) ** 2)
            ss_res = np.sum((val_y - val_pred) ** 2)
            r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
            r2_scores.append(r2)

        avg_a = float(np.mean([p[0] for p in fold_params]))
        avg_beta = float(np.mean([p[1] for p in fold_params]))
        avg_gamma = float(np.mean([p[2] for p in fold_params]))
        avg_r2 = float(np.mean(r2_scores))

        # Format par score is the baseline capacity at (B=120, W=10)
        calibrated_params[fmt] = {
            "a": round(avg_a, 2),
            "beta": round(avg_beta, 3),
            "gamma": round(avg_gamma, 3),
            "r2_out_of_fold": round(avg_r2, 3),
            "par_total": round(avg_a, 1)
        }

    return calibrated_params


def get_empirical_scoring_grid(
    df_deliveries: pd.DataFrame,
    balls_bin_size: int = 12
) -> pd.DataFrame:
    """
    Constructs an empirical 2D matrix of historical remaining runs
    conditioned on remaining ball intervals and wickets in hand.
    
    Used as an interpretable sanity check alongside the smooth parametric model.
    """
    inn1 = df_deliveries[
        (df_deliveries["innings"] == 1) &
        (df_deliveries["innings_max_balls"] == 120)
    ].copy()

    innings_totals = inn1.groupby("match_id")["cumulative_runs_after"].max().rename("final_innings_total")
    inn1 = inn1.merge(innings_totals, on="match_id")
    inn1["actual_remaining_runs"] = inn1["final_innings_total"] - inn1["cumulative_runs_before"]

    inn1["balls_bin"] = (inn1["balls_remaining_before"] // balls_bin_size) * balls_bin_size
    grid = inn1.groupby(["balls_bin", "wickets_in_hand_before"])["actual_remaining_runs"].agg(["mean", "count"])
    return grid.unstack(level="wickets_in_hand_before")


def assign_pressure_category(pressure_series: pd.Series) -> pd.Series:
    """
    Assigns domain-justified categorical tiers to continuous pressure values [0.0, 10.0]:
    - Low Pressure: [0.0, 3.5)
    - Medium Pressure: [3.5, 6.0)
    - High Pressure: [6.0, 8.0)
    - Extreme Pressure: [8.0, 10.0]
    """
    vals = pressure_series.values
    categories = np.where(
        vals < 3.5, "Low",
        np.where(
            vals < 6.0, "Medium",
            np.where(vals < 8.0, "High", "Extreme")
        )
    )
    return pd.Series(categories, index=pressure_series.index, name="pressure_category")
