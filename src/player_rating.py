"""
src/player_rating.py
SupeRR Selector - Multi-Dimensional Player Performance Rating Module

This module calculates transparent, cricket-justified performance ratings in [0.0, 100.0]
for batters and bowlers across distinct tactical dimensions.

Key Principles:
1. Multi-Dimensional: Does not reduce players to a single arbitrary metric.
2. Traceable: Sub-scores for each dimension are explicitly retained in the exported dataset.
3. Separation of Concerns: Measures performance quality only; sample confidence is handled
   separately by src/reliability_scoring.py.
"""

import numpy as np
import pandas as pd


# Default Batter Weight Configuration
DEFAULT_BATTER_WEIGHTS = {
    "scoring_rate": 0.30,        # Clutch strike rate
    "boundary_generation": 0.20, # Clutch boundary percentage
    "strike_rotation": 0.15,     # Dot-ball avoidance in clutch
    "wicket_preservation": 0.15, # Runs per dismissal in clutch
    "clutch_elevation": 0.10,    # Batting clutch index differential
    "overall_baseline": 0.10     # Overall career strike rate baseline
}

# Default Bowler Weight Configuration
DEFAULT_BOWLER_WEIGHTS = {
    "run_control": 0.25,         # Phase-adjusted delta economy
    "dot_ball_creation": 0.20,   # Clutch true team dot-ball percentage
    "wicket_taking": 0.20,       # Clutch wicket rate (wickets per ball)
    "boundary_suppression": 0.15,# Boundary avoidance in clutch
    "overall_baseline": 0.10,    # Overall career economy baseline
    "clutch_elevation": 0.10     # Bowling clutch index differential
}


def calculate_batting_performance_rating(
    df_batter: pd.DataFrame,
    weights: dict = None
) -> pd.DataFrame:
    """
    Computes transparent multi-dimensional performance ratings for batters.
    
    Sub-scores (each in [0.0, 100.0]):
    - subscore_scoring: (sr_clutch - 70) / (200 - 70) * 100
    - subscore_boundary: bnd_pct_clutch / 35.0 * 100
    - subscore_rotation: ((100 - dot_pct_clutch) - 20) / (70 - 20) * 100
    - subscore_preservation: rpd_clutch / 50.0 * 100
    - subscore_clutch_index: batting_clutch_index * 10.0
    - subscore_overall_sr: (sr_overall - 80) / (180 - 80) * 100
    """
    df = df_batter.copy()
    w = weights or DEFAULT_BATTER_WEIGHTS
    
    # 1. Scoring rate under clutch pressure (SR benchmark: 70 to 200)
    sub_scoring = np.clip((df["sr_clutch"] - 70.0) / (200.0 - 70.0) * 100.0, 0.0, 100.0)
    
    # 2. Boundary generation under clutch pressure (Benchmark: 0% to 35%)
    sub_boundary = np.clip(df["bnd_pct_clutch"] / 35.0 * 100.0, 0.0, 100.0)
    
    # 3. Strike rotation / dot avoidance (Non-dot %: 20% to 70%)
    non_dot_pct = 100.0 - df["dot_pct_clutch"]
    sub_rotation = np.clip((non_dot_pct - 20.0) / (70.0 - 20.0) * 100.0, 0.0, 100.0)
    
    # 4. Wicket preservation (Runs per dismissal: 0 to 50 runs)
    sub_preservation = np.clip(df["rpd_clutch"] / 50.0 * 100.0, 0.0, 100.0)
    
    # 5. Clutch elevation index (0 to 10 scale * 10 -> 0 to 100)
    sub_clutch = np.clip(df["batting_clutch_index"] * 10.0, 0.0, 100.0)
    
    # 6. Overall baseline quality (Overall SR benchmark: 80 to 180)
    sub_overall = np.clip((df["sr_overall"] - 80.0) / (180.0 - 80.0) * 100.0, 0.0, 100.0)
    
    df["subscore_scoring"] = np.round(sub_scoring, 2)
    df["subscore_boundary"] = np.round(sub_boundary, 2)
    df["subscore_rotation"] = np.round(sub_rotation, 2)
    df["subscore_preservation"] = np.round(sub_preservation, 2)
    df["subscore_clutch"] = np.round(sub_clutch, 2)
    df["subscore_overall"] = np.round(sub_overall, 2)
    
    rating = (
        w["scoring_rate"] * sub_scoring
        + w["boundary_generation"] * sub_boundary
        + w["strike_rotation"] * sub_rotation
        + w["wicket_preservation"] * sub_preservation
        + w["clutch_elevation"] * sub_clutch
        + w["overall_baseline"] * sub_overall
    )
    df["performance_rating"] = np.round(rating, 2)
    return df


def calculate_bowling_performance_rating(
    df_bowler: pd.DataFrame,
    weights: dict = None
) -> pd.DataFrame:
    """
    Computes transparent multi-dimensional performance ratings for bowlers.
    
    Sub-scores (each in [0.0, 100.0]):
    - subscore_run_control: (delta_econ_phase_adj - (-3.0)) / (3.0 - (-3.0)) * 100
    - subscore_dot_creation: (true_dot_pct_clutch - 15.0) / (50.0 - 15.0) * 100
    - subscore_wicket_taking: wkt_pct_clutch / 12.0 * 100
    - subscore_boundary_suppression: (30.0 - bnd_pct_clutch) / (30.0 - 10.0) * 100
    - subscore_overall_econ: (11.0 - economy_overall) / (11.0 - 6.0) * 100
    - subscore_clutch_index: bowling_clutch_index * 10.0
    """
    df = df_bowler.copy()
    w = weights or DEFAULT_BOWLER_WEIGHTS
    
    # 1. Run control: Phase-adjusted delta economy (Benchmark: -3.0 to +3.0 RPO)
    # Higher delta_econ_phase_adj means conceded fewer runs than expected given phase mix
    sub_run_control = np.clip((df["delta_econ_phase_adj"] - (-3.0)) / (3.0 - (-3.0)) * 100.0, 0.0, 100.0)
    
    # 2. True team dot-ball creation in clutch (Benchmark: 15% to 50%)
    dot_col = "true_dot_pct_clutch" if "true_dot_pct_clutch" in df.columns else "dot_pct_clutch"
    sub_dots = np.clip((df[dot_col] - 15.0) / (50.0 - 15.0) * 100.0, 0.0, 100.0)
    
    # 3. Wicket-taking rate under clutch pressure (Benchmark: 0% to 12% wickets per ball)
    sub_wkts = np.clip(df["wkt_pct_clutch"] / 12.0 * 100.0, 0.0, 100.0)
    
    # 4. Boundary suppression in clutch (Benchmark: 10% to 30% boundary rate conceded, lower is better)
    sub_bnd_supp = np.clip((30.0 - df["bnd_pct_clutch"]) / (30.0 - 10.0) * 100.0, 0.0, 100.0)
    
    # 5. Overall career economy baseline (Benchmark: 6.0 to 11.0 RPO, lower is better)
    sub_overall_econ = np.clip((11.0 - df["economy_overall"]) / (11.0 - 6.0) * 100.0, 0.0, 100.0)
    
    # 6. Clutch elevation index (0 to 10 scale * 10 -> 0 to 100)
    sub_clutch = np.clip(df["bowling_clutch_index"] * 10.0, 0.0, 100.0)
    
    df["subscore_run_control"] = np.round(sub_run_control, 2)
    df["subscore_dot_creation"] = np.round(sub_dots, 2)
    df["subscore_wicket_taking"] = np.round(sub_wkts, 2)
    df["subscore_boundary_suppression"] = np.round(sub_bnd_supp, 2)
    df["subscore_overall"] = np.round(sub_overall_econ, 2)
    df["subscore_clutch"] = np.round(sub_clutch, 2)
    
    rating = (
        w["run_control"] * sub_run_control
        + w["dot_ball_creation"] * sub_dots
        + w["wicket_taking"] * sub_wkts
        + w["boundary_suppression"] * sub_bnd_supp
        + w["overall_baseline"] * sub_overall_econ
        + w["clutch_elevation"] * sub_clutch
    )
    df["performance_rating"] = np.round(rating, 2)
    return df
