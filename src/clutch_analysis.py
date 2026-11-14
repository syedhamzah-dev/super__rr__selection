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
3. Empirical Bayes Shrinkage: Shrinks raw differentials toward population expectations based
   on sample size: w = n / (n + 30).
4. Strict Reliability Tiers: Flags High, Moderate, and Insufficient evidence.
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


def calculate_batting_clutch_index(batter_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the multi-dimensional Batting Clutch Differential Index.
    
    Differentials:
    - Delta SR = SR_clutch - SR_low (higher is better)
    - Delta Dot% = Dot%_low - Dot%_clutch (higher is better: fewer dots under pressure)
    - Delta Bnd% = Bnd%_clutch - Bnd%_low (higher is better)
    - Delta RPD = RPD_clutch - RPD_low (higher is better)
    
    Applies Empirical Bayes shrinkage and bounds score within [0.0, 10.0], with 5.0 as neutral.
    """
    df = batter_df.copy()

    # Blend low-pressure baseline with role benchmark if individual low sample is sparse (< 20 balls)
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
    # Typical std: Delta SR ~ 25, Delta Dot ~ 10, Delta Bnd ~ 8, Delta RPD ~ 15
    raw_score = (
        0.40 * (df["delta_strike_rate"] / 25.0)
        + 0.30 * (df["delta_dot_pct"] / 10.0)
        + 0.20 * (df["delta_bnd_pct"] / 8.0)
        + 0.10 * np.clip(df["delta_rpd"] / 15.0, -1.0, 1.0)
    )

    # Empirical Bayes Shrinkage based on clutch balls faced
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
    
    Differentials:
    - Delta Econ = Econ_low - Econ_clutch (higher is better: lower economy under pressure)
    - Delta Dot% = Dot%_clutch - Dot%_low (higher is better: more dots under pressure)
    - Delta Bnd% = Bnd%_low - Bnd%_clutch (higher is better: fewer boundaries conceded)
    - Delta WktRate = WktRate_clutch - WktRate_low (higher is better: higher wicket strike rate)
    
    Applies Empirical Bayes shrinkage and bounds score within [0.0, 10.0], with 5.0 as neutral.
    """
    df = bowler_df.copy()

    # Blend low-pressure baseline with role benchmark if individual low sample is sparse (< 20 balls)
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
            dot_low_adj.append(row["dot_pct_low"])
            bnd_low_adj.append(row["bnd_pct_low"])
            wkt_pct_low_adj.append(ind_wkt_pct_low)
        else:
            weight_ind = n_low / 25.0
            econ_low_adj.append(weight_ind * row["economy_low"] + (1.0 - weight_ind) * bm["econ"])
            dot_low_adj.append(weight_ind * row["dot_pct_low"] + (1.0 - weight_ind) * bm["dot_pct"])
            bnd_low_adj.append(weight_ind * row["bnd_pct_low"] + (1.0 - weight_ind) * bm["bnd_pct"])
            wkt_pct_low_adj.append(weight_ind * ind_wkt_pct_low + (1.0 - weight_ind) * bm["wkt_pct"])

    df["econ_low_effective"] = np.round(econ_low_adj, 2)
    df["dot_pct_low_effective"] = np.round(dot_low_adj, 2)
    df["bnd_pct_low_effective"] = np.round(bnd_low_adj, 2)
    df["wkt_pct_low_effective"] = np.round(wkt_pct_low_adj, 2)

    # Clutch wicket percentage
    df["wkt_pct_clutch"] = np.round((df["wickets_clutch"] / np.maximum(df["legal_balls_clutch"], 1)) * 100.0, 2)

    # Differentials
    # Since average economy gets worse by ~1.5 under pressure, we add 1.5 to center neutral expectation at 0
    df["delta_economy"] = np.round(df["econ_low_effective"] - df["economy_clutch"], 2) # positive = better economy
    df["delta_dot_pct"] = np.round(df["dot_pct_clutch"] - df["dot_pct_low_effective"], 2)
    df["delta_bnd_pct"] = np.round(df["bnd_pct_low_effective"] - df["bnd_pct_clutch"], 2) # positive = fewer bnds
    df["delta_wkt_rate"] = np.round(df["wkt_pct_clutch"] - df["wkt_pct_low_effective"], 2)

    # Composite Raw Bowling Clutch Score
    # Average delta_economy is -1.5 in population, so (delta_economy + 1.5) centers at 0.0
    raw_score = (
        0.40 * ((df["delta_economy"] + 1.5) / 2.5)
        + 0.25 * (df["delta_dot_pct"] / 8.0)
        + 0.20 * (df["delta_bnd_pct"] / 6.0)
        + 0.15 * (df["delta_wkt_rate"] / 3.0)
    )

    # Empirical Bayes Shrinkage based on clutch legal balls bowled
    n_clutch = df["legal_balls_clutch"]
    credibility_weight = n_clutch / (n_clutch + 30.0)
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
