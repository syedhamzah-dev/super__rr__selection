"""
src/robustness_analysis.py
SupeRR Selector - Sample-Size Sensitivity & Role/Phase Cohort Robustness Module

This module evaluates:
1. Sample-size sensitivity: How rankings, eligible cohorts, and top-tier memberships
   change under alternative evidence threshold configurations.
2. Role and phase cohort robustness: How tactical positions (Top/Middle/Finisher) and
   match phases (Powerplay/Middle/Death) interact with clutch performance metrics.
"""

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, kendalltau
from typing import Dict, List, Tuple


# Evidence Threshold Scenarios
EVIDENCE_SENSITIVITY_SCENARIOS = {
    "Baseline": {
        "description": "Production Module 5: Strong (c>=40, m>=10, s>=60) + Moderate (c>=20, m>=5, s>=35)",
        "min_clutch": 20,
        "min_matches": 5,
        "min_ers": 35.0,
        "min_overall": 30
    },
    "Relaxed_Clutch_15": {
        "description": "Lower clutch floor (c>=15, m>=5, s>=30) to test emerging talent inclusion",
        "min_clutch": 15,
        "min_matches": 5,
        "min_ers": 30.0,
        "min_overall": 30
    },
    "Strict_Clutch_30": {
        "description": "Tightened clutch floor (c>=30, m>=8, s>=45) to restrict small samples",
        "min_clutch": 30,
        "min_matches": 8,
        "min_ers": 45.0,
        "min_overall": 50
    },
    "Strong_Evidence_Only": {
        "description": "Strict veteran floor: Strong Evidence only (c>=40, m>=10, s>=60)",
        "min_clutch": 40,
        "min_matches": 10,
        "min_ers": 60.0,
        "min_overall": 60
    },
    "High_Match_Breadth": {
        "description": "Increased match exposure floor (c>=20, m>=10, s>=35) to require cross-match breadth",
        "min_clutch": 20,
        "min_matches": 10,
        "min_ers": 35.0,
        "min_overall": 30
    },
    "Low_Exposure_Probe": {
        "description": "Exploratory low-sample floor (c>=10, m>=3, s>=25) for scouting emerging watchlist",
        "min_clutch": 10,
        "min_matches": 3,
        "min_ers": 25.0,
        "min_overall": 30
    }
}


def evaluate_evidence_threshold_sensitivity(
    df_batter_ratings: pd.DataFrame,
    df_bowler_ratings: pd.DataFrame
) -> pd.DataFrame:
    """
    Evaluates how player eligibility, top-tier retention, and rank correlations shift
    across alternative evidence threshold scenarios for both batters and bowlers.
    """
    results = []

    # 1. Batters evaluation
    b_df = df_batter_ratings.copy()
    b_base_eligible = b_df[b_df["is_eligible_for_ranking"]].sort_values("performance_rating", ascending=False).reset_index(drop=True)
    b_base_eligible["base_rank"] = b_base_eligible.index + 1
    b_base_top10 = set(b_base_eligible.head(10)["striker_id"])
    b_base_top20 = set(b_base_eligible.head(20)["striker_id"])

    for sc_name, sc_cfg in EVIDENCE_SENSITIVITY_SCENARIOS.items():
        # Apply scenario eligibility rule
        mask = (
            (b_df["bf_clutch"] >= sc_cfg["min_clutch"])
            & (b_df["matches_played"] >= sc_cfg["min_matches"])
            & (b_df["evidence_reliability_score"] >= sc_cfg["min_ers"])
            & (b_df["bf_overall"] >= sc_cfg["min_overall"])
        )
        sc_eligible = b_df[mask].sort_values("performance_rating", ascending=False).reset_index(drop=True)
        sc_eligible["sc_rank"] = sc_eligible.index + 1
        
        n_eligible = len(sc_eligible)
        sc_top10 = set(sc_eligible.head(10)["striker_id"])
        sc_top20 = set(sc_eligible.head(20)["striker_id"])
        
        top10_overlap = len(b_base_top10.intersection(sc_top10))
        top20_overlap = len(b_base_top20.intersection(sc_top20))

        # Rank correlation on overlapping cohort
        merged = b_base_eligible[["striker_id", "base_rank"]].merge(
            sc_eligible[["striker_id", "sc_rank"]], on="striker_id"
        )
        if len(merged) > 1:
            rho, _ = spearmanr(merged["base_rank"], merged["sc_rank"])
            tau, _ = kendalltau(merged["base_rank"], merged["sc_rank"])
            mean_shift = np.round(np.abs(merged["base_rank"] - merged["sc_rank"]).mean(), 2)
            max_shift = int(np.abs(merged["base_rank"] - merged["sc_rank"]).max())
        else:
            rho, tau, mean_shift, max_shift = 1.0, 1.0, 0.0, 0

        # Identify newly entered or exited players from Top 20
        entered = list(sc_top20 - b_base_top20)
        exited = list(b_base_top20 - sc_top20)
        
        entered_names = b_df.set_index("striker_id").loc[entered, "striker_name"].tolist() if entered else []
        exited_names = b_df.set_index("striker_id").loc[exited, "striker_name"].tolist() if exited else []

        results.append({
            "Discipline": "Batting",
            "Scenario": sc_name,
            "Description": sc_cfg["description"],
            "Eligible_Count": n_eligible,
            "Baseline_Count": len(b_base_eligible),
            "Top10_Retention": f"{top10_overlap}/10",
            "Top20_Retention": f"{top20_overlap}/20",
            "Spearman_Rho": round(rho, 4),
            "Kendall_Tau": round(tau, 4),
            "Mean_Rank_Shift": mean_shift,
            "Max_Rank_Shift": max_shift,
            "Top20_Entered": ", ".join(entered_names[:3]) if entered_names else "None",
            "Top20_Exited": ", ".join(exited_names[:3]) if exited_names else "None"
        })

    # 2. Bowlers evaluation
    bw_df = df_bowler_ratings.copy()
    bw_base_eligible = bw_df[bw_df["is_eligible_for_ranking"]].sort_values("performance_rating", ascending=False).reset_index(drop=True)
    bw_base_eligible["base_rank"] = bw_base_eligible.index + 1
    bw_base_top10 = set(bw_base_eligible.head(10)["bowler_id"])
    bw_base_top20 = set(bw_base_eligible.head(20)["bowler_id"])

    for sc_name, sc_cfg in EVIDENCE_SENSITIVITY_SCENARIOS.items():
        mask = (
            (bw_df["legal_balls_clutch"] >= sc_cfg["min_clutch"])
            & (bw_df["matches_played"] >= sc_cfg["min_matches"])
            & (bw_df["evidence_reliability_score"] >= sc_cfg["min_ers"])
            & (bw_df["legal_balls_overall"] >= sc_cfg["min_overall"])
        )
        sc_eligible = bw_df[mask].sort_values("performance_rating", ascending=False).reset_index(drop=True)
        sc_eligible["sc_rank"] = sc_eligible.index + 1

        n_eligible = len(sc_eligible)
        sc_top10 = set(sc_eligible.head(10)["bowler_id"])
        sc_top20 = set(sc_eligible.head(20)["bowler_id"])

        top10_overlap = len(bw_base_top10.intersection(sc_top10))
        top20_overlap = len(bw_base_top20.intersection(sc_top20))

        merged = bw_base_eligible[["bowler_id", "base_rank"]].merge(
            sc_eligible[["bowler_id", "sc_rank"]], on="bowler_id"
        )
        if len(merged) > 1:
            rho, _ = spearmanr(merged["base_rank"], merged["sc_rank"])
            tau, _ = kendalltau(merged["base_rank"], merged["sc_rank"])
            mean_shift = np.round(np.abs(merged["base_rank"] - merged["sc_rank"]).mean(), 2)
            max_shift = int(np.abs(merged["base_rank"] - merged["sc_rank"]).max())
        else:
            rho, tau, mean_shift, max_shift = 1.0, 1.0, 0.0, 0

        entered = list(sc_top20 - bw_base_top20)
        exited = list(bw_base_top20 - sc_top20)

        entered_names = bw_df.set_index("bowler_id").loc[entered, "bowler_name"].tolist() if entered else []
        exited_names = bw_df.set_index("bowler_id").loc[exited, "bowler_name"].tolist() if exited else []

        results.append({
            "Discipline": "Bowling",
            "Scenario": sc_name,
            "Description": sc_cfg["description"],
            "Eligible_Count": n_eligible,
            "Baseline_Count": len(bw_base_eligible),
            "Top10_Retention": f"{top10_overlap}/10",
            "Top20_Retention": f"{top20_overlap}/20",
            "Spearman_Rho": round(rho, 4),
            "Kendall_Tau": round(tau, 4),
            "Mean_Rank_Shift": mean_shift,
            "Max_Rank_Shift": max_shift,
            "Top20_Entered": ", ".join(entered_names[:3]) if entered_names else "None",
            "Top20_Exited": ", ".join(exited_names[:3]) if exited_names else "None"
        })

    return pd.DataFrame(results)


def analyze_role_and_phase_robustness(
    df_batter_ratings: pd.DataFrame,
    df_bowler_ratings: pd.DataFrame
) -> Dict[str, pd.DataFrame]:
    """
    Computes comparative statistics across tactical roles and match phases
    to verify rating stability across diverse specialist cohorts.
    """
    # 1. Batting Role Analysis
    b_roles = df_batter_ratings.groupby("primary_role").agg(
        total_players=("striker_id", "count"),
        eligible_players=("is_eligible_for_ranking", "sum"),
        mean_rating=("performance_rating", "mean"),
        median_rating=("performance_rating", "median"),
        std_rating=("performance_rating", "std"),
        mean_clutch_sr=("sr_clutch", "mean"),
        mean_overall_sr=("sr_overall", "mean"),
        mean_clutch_bci=("batting_clutch_index", "mean"),
        mean_ers=("evidence_reliability_score", "mean")
    ).reset_index()
    b_roles["eligibility_rate_pct"] = np.round((b_roles["eligible_players"] / b_roles["total_players"]) * 100.0, 1)
    b_roles["mean_sr_elevation"] = np.round(b_roles["mean_clutch_sr"] - b_roles["mean_overall_sr"], 2)
    b_roles = b_roles.round(2)

    # 2. Bowling Role Analysis
    bw_roles = df_bowler_ratings.groupby("primary_bowling_role").agg(
        total_players=("bowler_id", "count"),
        eligible_players=("is_eligible_for_ranking", "sum"),
        mean_rating=("performance_rating", "mean"),
        median_rating=("performance_rating", "median"),
        std_rating=("performance_rating", "std"),
        mean_clutch_econ=("economy_clutch", "mean"),
        mean_overall_econ=("economy_overall", "mean"),
        mean_delta_econ_phase_adj=("delta_econ_phase_adj", "mean"),
        mean_boci=("bowling_clutch_index", "mean"),
        mean_ers=("evidence_reliability_score", "mean")
    ).reset_index()
    bw_roles["eligibility_rate_pct"] = np.round((bw_roles["eligible_players"] / bw_roles["total_players"]) * 100.0, 1)
    bw_roles["mean_raw_econ_inflation"] = np.round(bw_roles["mean_clutch_econ"] - bw_roles["mean_overall_econ"], 2)
    bw_roles = bw_roles.round(2)

    return {
        "batting_roles": b_roles,
        "bowling_roles": bw_roles
    }
