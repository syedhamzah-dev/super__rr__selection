"""
src/clutch_analysis.py
SupeRR Selector - Clutch Differential & Reliability Module

This module computes the Clutch Differential Index for batters and bowlers.
It quantifies how player performance shifts when moving from Low Pressure (<3.5)
to Clutch Pressure (>=6.0, High + Extreme).

Key Principles:
1. Multi-dimensional: Evaluates strike rate/economy, dot-ball discipline, boundary rate, and wickets.
2. Contextual Fairness: If a player has sparse low-pressure observations (e.g. a finisher),
   the low-pressure baseline blends with the role-specific population mean.
3. Credibility-Weighted Shrinkage: Shrinks raw differentials toward population expectations based
   on sample size using the classical Bühlmann credibility formula:
       w = n / (n + k), where k = 30.0 (credibility stability parameter).
   This avoids overfitting small-sample fluctuations while giving full credit to established performers.
4. Phase-Adjusted Bowling Economy: Eliminates phase confounding (Death vs Middle vs Powerplay)
   by evaluating clutch economy against the bowler's expected economy given their actual phase delivery mix.
5. Strict Reliability Tiers: Flags High, Moderate, and Insufficient evidence.
"""

import numpy as np
import pandas as pd


# Role-specific low-pressure population baselines (from 200,999 deliveries)
BATTER_ROLE_LOW_BASELINES = {
    "Top Order": {"sr": 151.5, "dot_pct": 34.4, "bnd_pct": 21.3, "rpd": 34.2},
    "Middle Order": {"sr": 152.2, "dot_pct": 30.8, "bnd_pct": 19.5, "rpd": 31.5},
    "Finisher": {"sr": 153.6, "dot_pct": 32.4, "bnd_pct": 20.5, "rpd": 28.4},
    "Lower Order": {"sr": 137.3, "dot_pct": 36.9, "bnd_pct": 17.8, "rpd": 16.2}
}

BOWLER_ROLE_LOW_BASELINES = {
    "Powerplay Specialist": {"econ": 7.38, "dot_pct": 50.2, "bnd_pct": 19.3, "wkt_pct": 4.1},
    "Middle Enforcer": {"econ": 7.07, "dot_pct": 38.3, "bnd_pct": 13.1, "wkt_pct": 4.8},
    "Death Specialist": {"econ": 8.51, "dot_pct": 37.6, "bnd_pct": 18.6, "wkt_pct": 6.2},
    "All-Phase Bowler": {"econ": 7.45, "dot_pct": 41.5, "bnd_pct": 16.2, "wkt_pct": 5.0}
}

# Empirical benchmark clutch economy rates across phases (evaluated on deliveries with bowling PI >= 6.0)
GLOBAL_PHASE_CLUTCH_ECONOMY = {
    "Powerplay": 9.18,
    "Middle": 9.01,
    "Death": 10.52
}


def calculate_batting_clutch_index(batter_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the multi-dimensional Batting Clutch Differential Index.
    
    Differentials:
    - Delta SR = SR_clutch - SR_low (higher is better)
    - Delta Dot% = Dot%_low - Dot%_clutch (higher is better: fewer dots under pressure)
    - Delta Bnd% = Bnd%_clutch - Bnd%_low (higher is better)
    - Delta RPD = RPD_clutch - RPD_low (higher is better)
    
    Applies Credibility-Weighted Shrinkage (Bühlmann model, k=30) and bounds score within [0.0, 10.0],
    with 5.0 as neutral.
    """
    df = batter_df.copy()

    # Blend low-pressure baseline with role benchmark if individual low sample is sparse (< 25 balls)
    sr_low_adj = []
    dot_low_adj = []
    bnd_low_adj = []
    rpd_low_adj = []

    for _, row in df.iterrows():
        role = row.get("primary_role", "Middle Order")
        bm = BATTER_ROLE_LOW_BASELINES.get(role, BATTER_ROLE_LOW_BASELINES["Middle Order"])
        n_low = row["bf_low"]

        if n_low >= 25:
            sr_low_adj.append(row["sr_low"])
            dot_low_adj.append(row["dot_pct_low"])
            bnd_low_adj.append(row["bnd_pct_low"])
            rpd_low_adj.append(row["rpd_low"])
        else:
            weight_ind = n_low / 25.0
            sr_low_adj.append(weight_ind * row["sr_low"] + (1.0 - weight_ind) * bm["sr"])
            dot_low_adj.append(weight_ind * row["dot_pct_low"] + (1.0 - weight_ind) * bm["dot_pct"])
            bnd_low_adj.append(weight_ind * row["bnd_pct_low"] + (1.0 - weight_ind) * bm["bnd_pct"])
            rpd_low_adj.append(weight_ind * row["rpd_low"] + (1.0 - weight_ind) * bm["rpd"])

    df["sr_low_effective"] = np.round(sr_low_adj, 2)
    df["dot_pct_low_effective"] = np.round(dot_low_adj, 2)
    df["bnd_pct_low_effective"] = np.round(bnd_low_adj, 2)
    df["rpd_low_effective"] = np.round(rpd_low_adj, 2)

    # Differentials
    df["delta_strike_rate"] = np.round(df["sr_clutch"] - df["sr_low_effective"], 2)
    df["delta_dot_pct"] = np.round(df["dot_pct_low_effective"] - df["dot_pct_clutch"], 2) # positive = fewer dots
    df["delta_bnd_pct"] = np.round(df["bnd_pct_clutch"] - df["bnd_pct_low_effective"], 2)
    df["delta_rpd"] = np.round(df["rpd_clutch"] - df["rpd_low_effective"], 2)

    # Composite Raw Clutch Score
    raw_score = (
        0.40 * (df["delta_strike_rate"] / 25.0)
        + 0.30 * (df["delta_dot_pct"] / 10.0)
        + 0.20 * (df["delta_bnd_pct"] / 8.0)
        + 0.10 * np.clip(df["delta_rpd"] / 15.0, -1.0, 1.0)
    )

    # Credibility-Weighted Shrinkage based on clutch balls faced: w = n / (n + 30.0)
    n_clutch = df["bf_clutch"]
    credibility_weight = n_clutch / (n_clutch + 30.0)
    df["credibility_weight"] = np.round(credibility_weight, 3)

    # Standardized 0-10 Clutch Index (5.0 is neutral)
    clutch_index = 5.0 + 5.0 * np.tanh(credibility_weight * raw_score)
    df["batting_clutch_index"] = np.round(np.clip(clutch_index, 0.0, 10.0), 2)

    # Sample Reliability Tiers
    df["sample_reliability"] = np.where(
        (df["bf_overall"] >= 120) & (df["bf_clutch"] >= 40), "High",
        np.where(
            (df["bf_overall"] >= 60) & (df["bf_clutch"] >= 20), "Moderate",
            "Insufficient"
        )
    )

    return df


def calculate_bowling_clutch_index(bowler_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the multi-dimensional Bowling Clutch Differential Index.
    
    Eliminates phase confounding by evaluating economy against expected economy given
    the bowler's actual phase delivery distribution in clutch pressure:
    - Delta Econ (Phase-Adjusted) = Econ_clutch_expected - Econ_clutch_observed (higher is better)
    - Delta True Dot% = True_Dot%_clutch - True_Dot%_low (higher is better: more team dots)
    - Delta Bnd% = Bnd%_low - Bnd%_clutch (higher is better: fewer boundaries conceded)
    - Delta WktRate = WktRate_clutch - WktRate_low (higher is better: higher wicket strike rate)
    
    Applies Credibility-Weighted Shrinkage (Bühlmann model, k=30) and bounds score within [0.0, 10.0],
    with 5.0 as neutral.
    """
    df = bowler_df.copy()

    # Blend low-pressure baseline with role benchmark if individual low sample is sparse (< 25 balls)
    econ_low_adj = []
    dot_low_adj = []
    bnd_low_adj = []
    wkt_pct_low_adj = []

    for _, row in df.iterrows():
        role = row.get("primary_bowling_role", "All-Phase Bowler")
        bm = BOWLER_ROLE_LOW_BASELINES.get(role, BOWLER_ROLE_LOW_BASELINES["All-Phase Bowler"])
        n_low = row["legal_balls_low"]

        # Calculate low wicket percentage
        ind_wkt_pct_low = (row["wickets_low"] / np.maximum(n_low, 1)) * 100.0

        if n_low >= 25:
            econ_low_adj.append(row["economy_low"])
            dot_low_adj.append(row["true_dot_pct_low"] if "true_dot_pct_low" in row else row["dot_pct_low"])
            bnd_low_adj.append(row["bnd_pct_low"])
            wkt_pct_low_adj.append(ind_wkt_pct_low)
        else:
            weight_ind = n_low / 25.0
            actual_dot = row["true_dot_pct_low"] if "true_dot_pct_low" in row else row["dot_pct_low"]
            econ_low_adj.append(weight_ind * row["economy_low"] + (1.0 - weight_ind) * bm["econ"])
            dot_low_adj.append(weight_ind * actual_dot + (1.0 - weight_ind) * bm["dot_pct"])
            bnd_low_adj.append(weight_ind * row["bnd_pct_low"] + (1.0 - weight_ind) * bm["bnd_pct"])
            wkt_pct_low_adj.append(weight_ind * ind_wkt_pct_low + (1.0 - weight_ind) * bm["wkt_pct"])

    df["econ_low_effective"] = np.round(econ_low_adj, 2)
    df["dot_pct_low_effective"] = np.round(dot_low_adj, 2)
    df["bnd_pct_low_effective"] = np.round(bnd_low_adj, 2)
    df["wkt_pct_low_effective"] = np.round(wkt_pct_low_adj, 2)

    # Clutch wicket percentage
    df["wkt_pct_clutch"] = np.round((df["wickets_clutch"] / np.maximum(df["legal_balls_clutch"], 1)) * 100.0, 2)

    # Phase-expected economy under clutch pressure (eliminates Death vs PP bias)
    n_clutch = np.maximum(df["legal_balls_clutch"], 1)
    pp_b = df["pp_balls_clutch"] if "pp_balls_clutch" in df.columns else pd.Series(0, index=df.index)
    mid_b = df["mid_balls_clutch"] if "mid_balls_clutch" in df.columns else pd.Series(0, index=df.index)
    death_b = df["death_balls_clutch"] if "death_balls_clutch" in df.columns else pd.Series(0, index=df.index)

    phase_sum = pp_b + mid_b + death_b
    econ_clutch_exp = (
        pp_b * GLOBAL_PHASE_CLUTCH_ECONOMY["Powerplay"]
        + mid_b * GLOBAL_PHASE_CLUTCH_ECONOMY["Middle"]
        + death_b * GLOBAL_PHASE_CLUTCH_ECONOMY["Death"]
    ) / np.maximum(phase_sum, 1)

    default_econ = df["primary_bowling_role"].map(lambda r: BOWLER_ROLE_LOW_BASELINES.get(r, {}).get("econ", 8.0))
    df["econ_clutch_expected"] = np.round(np.where(phase_sum > 0, econ_clutch_exp, default_econ), 2)

    # Phase-adjusted economy differential (positive = conceded fewer runs than phase benchmark)
    df["delta_econ_phase_adj"] = np.round(df["econ_clutch_expected"] - df["economy_clutch"], 2)

    # Unadjusted economy differential (contextual metric)
    df["delta_economy"] = np.round(df["econ_low_effective"] - df["economy_clutch"], 2)

    # Dot, boundary, and wicket differentials
    clutch_dot = df["true_dot_pct_clutch"] if "true_dot_pct_clutch" in df.columns else df["dot_pct_clutch"]
    df["delta_dot_pct"] = np.round(clutch_dot - df["dot_pct_low_effective"], 2)
    df["delta_bnd_pct"] = np.round(df["bnd_pct_low_effective"] - df["bnd_pct_clutch"], 2)
    df["delta_wkt_rate"] = np.round(df["wkt_pct_clutch"] - df["wkt_pct_low_effective"], 2)

    # Composite Raw Bowling Clutch Score
    # delta_econ_phase_adj naturally centers at ~0.0 (std 1.53), eliminating arbitrary offset constants
    raw_score = (
        0.40 * (df["delta_econ_phase_adj"] / 1.50)
        + 0.25 * (df["delta_dot_pct"] / 8.0)
        + 0.20 * (df["delta_bnd_pct"] / 6.0)
        + 0.15 * (df["delta_wkt_rate"] / 3.0)
    )

    # Credibility-Weighted Shrinkage based on clutch legal balls: w = n / (n + 30.0)
    credibility_weight = df["legal_balls_clutch"] / (df["legal_balls_clutch"] + 30.0)
    df["credibility_weight"] = np.round(credibility_weight, 3)

    # Standardized 0-10 Bowling Clutch Index (5.0 is neutral)
    clutch_index = 5.0 + 5.0 * np.tanh(credibility_weight * raw_score)
    df["bowling_clutch_index"] = np.round(np.clip(clutch_index, 0.0, 10.0), 2)

    # Sample Reliability Tiers
    df["sample_reliability"] = np.where(
        (df["legal_balls_overall"] >= 120) & (df["legal_balls_clutch"] >= 40), "High",
        np.where(
            (df["legal_balls_overall"] >= 60) & (df["legal_balls_clutch"] >= 20), "Moderate",
            "Insufficient"
        )
    )

    return df
