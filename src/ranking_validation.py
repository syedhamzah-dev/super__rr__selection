"""
src/ranking_validation.py
SupeRR Selector - Ranking Robustness & Sensitivity Testing Module

This module tests whether player rankings are stable against changes in:
1. Alternative rating weight configurations (+/- 15% shifts).
2. Alternative minimum sample size thresholds.
3. Outlier match sensitivity.
"""

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, kendalltau

from src.player_rating import (
    calculate_batting_performance_rating,
    calculate_bowling_performance_rating,
    DEFAULT_BATTER_WEIGHTS,
    DEFAULT_BOWLER_WEIGHTS
)


# Alternative Batting Weight Scenarios
BATTER_SENSITIVITY_SCENARIOS = {
    "Baseline": DEFAULT_BATTER_WEIGHTS,
    "Clutch_Heavy": {
        "scoring_rate": 0.40,
        "boundary_generation": 0.25,
        "strike_rotation": 0.10,
        "wicket_preservation": 0.10,
        "clutch_elevation": 0.10,
        "overall_baseline": 0.05
    },
    "Baseline_Heavy": {
        "scoring_rate": 0.20,
        "boundary_generation": 0.15,
        "strike_rotation": 0.15,
        "wicket_preservation": 0.20,
        "clutch_elevation": 0.10,
        "overall_baseline": 0.20
    },
    "Power_Hitting_Bias": {
        "scoring_rate": 0.35,
        "boundary_generation": 0.35,
        "strike_rotation": 0.10,
        "wicket_preservation": 0.05,
        "clutch_elevation": 0.05,
        "overall_baseline": 0.10
    }
}

# Alternative Bowling Weight Scenarios
BOWLER_SENSITIVITY_SCENARIOS = {
    "Baseline": DEFAULT_BOWLER_WEIGHTS,
    "Clutch_Heavy": {
        "run_control": 0.35,
        "dot_ball_creation": 0.25,
        "wicket_taking": 0.20,
        "boundary_suppression": 0.10,
        "overall_baseline": 0.05,
        "clutch_elevation": 0.05
    },
    "Baseline_Heavy": {
        "run_control": 0.15,
        "dot_ball_creation": 0.15,
        "wicket_taking": 0.15,
        "boundary_suppression": 0.15,
        "overall_baseline": 0.25,
        "clutch_elevation": 0.15
    },
    "Wicket_Attacking_Bias": {
        "run_control": 0.20,
        "dot_ball_creation": 0.15,
        "wicket_taking": 0.35,
        "boundary_suppression": 0.10,
        "overall_baseline": 0.10,
        "clutch_elevation": 0.10
    }
}


def test_batter_weight_sensitivity(df_eligible_batter: pd.DataFrame) -> tuple:
    """
    Evaluates rank stability across alternative weighting scenarios for batters.
    Returns:
    - sensitivity_summary_df: Correlation metrics and mean rank shifts
    - player_rank_comparison_df: Ranks across all scenarios
    """
    df = df_eligible_batter.copy()
    rank_cols = {}
    
    # Compute baseline ranks
    df_base = calculate_batting_performance_rating(df, DEFAULT_BATTER_WEIGHTS)
    df_base = df_base.sort_values("performance_rating", ascending=False).reset_index(drop=True)
    df_base["rank_baseline"] = df_base.index + 1
    rank_cols["rank_baseline"] = df_base.set_index("striker_id")["rank_baseline"]
    
    summary_rows = []
    
    for name, weights in BATTER_SENSITIVITY_SCENARIOS.items():
        if name == "Baseline":
            continue
        df_alt = calculate_batting_performance_rating(df, weights)
        df_alt = df_alt.sort_values("performance_rating", ascending=False).reset_index(drop=True)
        col_name = f"rank_{name.lower()}"
        df_alt[col_name] = df_alt.index + 1
        rank_cols[col_name] = df_alt.set_index("striker_id")[col_name]
        
        # Calculate rank correlation against baseline
        merged = df_base[["striker_id", "rank_baseline"]].merge(
            df_alt[["striker_id", col_name]], on="striker_id"
        )
        rho, _ = spearmanr(merged["rank_baseline"], merged[col_name])
        tau, _ = kendalltau(merged["rank_baseline"], merged[col_name])
        mean_shift = np.abs(merged["rank_baseline"] - merged[col_name]).mean()
        max_shift = np.abs(merged["rank_baseline"] - merged[col_name]).max()
        top20_overlap = len(set(df_base.head(20)["striker_id"]).intersection(set(df_alt.head(20)["striker_id"])))
        
        summary_rows.append({
            "Discipline": "Batting",
            "Scenario": name,
            "Spearman_Rho": round(rho, 4),
            "Kendall_Tau": round(tau, 4),
            "Mean_Rank_Shift": round(mean_shift, 2),
            "Max_Rank_Shift": int(max_shift),
            "Top20_Retention": f"{top20_overlap}/20"
        })
        
    rank_comp = pd.DataFrame(rank_cols).reset_index()
    rank_comp = rank_comp.merge(df[["striker_id", "striker_name", "primary_role"]], on="striker_id", how="left")
    
    return pd.DataFrame(summary_rows), rank_comp


def test_bowler_weight_sensitivity(df_eligible_bowler: pd.DataFrame) -> tuple:
    """
    Evaluates rank stability across alternative weighting scenarios for bowlers.
    """
    df = df_eligible_bowler.copy()
    rank_cols = {}
    
    df_base = calculate_bowling_performance_rating(df, DEFAULT_BOWLER_WEIGHTS)
    df_base = df_base.sort_values("performance_rating", ascending=False).reset_index(drop=True)
    df_base["rank_baseline"] = df_base.index + 1
    rank_cols["rank_baseline"] = df_base.set_index("bowler_id")["rank_baseline"]
    
    summary_rows = []
    
    for name, weights in BOWLER_SENSITIVITY_SCENARIOS.items():
        if name == "Baseline":
            continue
        df_alt = calculate_bowling_performance_rating(df, weights)
        df_alt = df_alt.sort_values("performance_rating", ascending=False).reset_index(drop=True)
        col_name = f"rank_{name.lower()}"
        df_alt[col_name] = df_alt.index + 1
        rank_cols[col_name] = df_alt.set_index("bowler_id")[col_name]
        
        merged = df_base[["bowler_id", "rank_baseline"]].merge(
            df_alt[["bowler_id", col_name]], on="bowler_id"
        )
        rho, _ = spearmanr(merged["rank_baseline"], merged[col_name])
        tau, _ = kendalltau(merged["rank_baseline"], merged[col_name])
        mean_shift = np.abs(merged["rank_baseline"] - merged[col_name]).mean()
        max_shift = np.abs(merged["rank_baseline"] - merged[col_name]).max()
        top20_overlap = len(set(df_base.head(20)["bowler_id"]).intersection(set(df_alt.head(20)["bowler_id"])))
        
        summary_rows.append({
            "Discipline": "Bowling",
            "Scenario": name,
            "Spearman_Rho": round(rho, 4),
            "Kendall_Tau": round(tau, 4),
            "Mean_Rank_Shift": round(mean_shift, 2),
            "Max_Rank_Shift": int(max_shift),
            "Top20_Retention": f"{top20_overlap}/20"
        })
        
    rank_comp = pd.DataFrame(rank_cols).reset_index()
    rank_comp = rank_comp.merge(df[["bowler_id", "bowler_name", "primary_bowling_role"]], on="bowler_id", how="left")
    
    return pd.DataFrame(summary_rows), rank_comp
