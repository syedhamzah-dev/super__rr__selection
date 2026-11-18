"""
src/player_ranking.py
SupeRR Selector - Evidence-Based Player Ranking Module

This module generates transparent, stratified ranking tables for batters and bowlers.
It strictly filters by evidence eligibility so that small-sample noise is never
mixed into the primary leaderboard.
"""

import numpy as np
import pandas as pd


def generate_batter_rankings(df_batter: pd.DataFrame) -> dict:
    """
    Generates structured ranking tables for batters:
    - overall_eligible: Main leaderboard of eligible batters (Strong + Moderate evidence)
    - by_role: Dict of rankings partitioned by tactical role
    - standout_clutch: Top performers by clutch differential index
    - high_upside_watchlist: Top performing players with emerging/limited evidence
    - regression_risks: High volume players whose performance regresses under pressure
    """
    df = df_batter.copy()
    
    # 1. Primary eligible ranking
    eligible = df[df["is_eligible_for_ranking"]].copy()
    eligible = eligible.sort_values(by="performance_rating", ascending=False).reset_index(drop=True)
    eligible["overall_rank"] = eligible.index + 1
    
    # Clean export schema
    cols_export = [
        "overall_rank", "striker_id", "striker_name", "primary_role",
        "performance_rating", "evidence_reliability_score", "evidence_tier",
        "bf_overall", "runs_overall", "sr_overall",
        "bf_clutch", "runs_clutch", "sr_clutch", "bnd_pct_clutch", "dot_pct_clutch", "rpd_clutch",
        "batting_clutch_index", "matches_played", "comps_played"
    ]
    main_ranking = eligible[cols_export].copy()
    main_ranking.rename(columns={"overall_rank": "rank", "striker_id": "player_id", "striker_name": "player_name"}, inplace=True)
    
    # 2. Role-wise rankings
    role_rankings = {}
    for role in ["Top Order", "Middle Order", "Finisher"]:
        sub = eligible[eligible["primary_role"] == role].copy().reset_index(drop=True)
        sub["role_rank"] = sub.index + 1
        cols_role = ["role_rank", "striker_id", "striker_name", "performance_rating", "evidence_reliability_score", "sr_clutch", "bnd_pct_clutch", "batting_clutch_index", "matches_played"]
        sub_export = sub[cols_role].rename(columns={"role_rank": "rank", "striker_id": "player_id", "striker_name": "player_name"})
        role_rankings[role] = sub_export
        
    # 3. Standout clutch performers (Clutch Index >= 7.0 among eligible)
    standout_clutch = eligible[eligible["batting_clutch_index"] >= 7.0].sort_values(by="batting_clutch_index", ascending=False).reset_index(drop=True)
    standout_clutch["rank"] = standout_clutch.index + 1
    
    # 4. High-upside watchlist (Moderate & Insufficient evidence with performance rating >= 70.0)
    watchlist = df[(df["evidence_tier"].isin(["Moderate Evidence", "Insufficient Evidence"])) & (df["performance_rating"] >= 70.0)].copy()
    watchlist = watchlist.sort_values(by="performance_rating", ascending=False).reset_index(drop=True)
    watchlist["rank"] = watchlist.index + 1
    
    # 5. Regression risks (Strong evidence, but lowest clutch indices < 3.0)
    regression_risks = eligible[(eligible["evidence_tier"] == "Strong Evidence") & (eligible["batting_clutch_index"] < 3.0)].sort_values(by="batting_clutch_index", ascending=True).reset_index(drop=True)
    regression_risks["rank"] = regression_risks.index + 1
    
    return {
        "overall_eligible": main_ranking,
        "by_role": role_rankings,
        "standout_clutch": standout_clutch,
        "watchlist": watchlist,
        "regression_risks": regression_risks
    }


def generate_bowler_rankings(df_bowler: pd.DataFrame) -> dict:
    """
    Generates structured ranking tables for bowlers:
    - overall_eligible: Main leaderboard of eligible bowlers (Strong + Moderate evidence)
    - by_role: Dict of rankings partitioned by bowling role
    - standout_clutch: Top performers by phase-adjusted clutch execution
    - high_upside_watchlist: Emerging bowlers with strong performance but moderate evidence
    - regression_risks: High evidence bowlers whose economy inflates under pressure
    """
    df = df_bowler.copy()
    
    eligible = df[df["is_eligible_for_ranking"]].copy()
    eligible = eligible.sort_values(by="performance_rating", ascending=False).reset_index(drop=True)
    eligible["overall_rank"] = eligible.index + 1
    
    dot_col = "true_dot_pct_clutch" if "true_dot_pct_clutch" in eligible.columns else "dot_pct_clutch"
    cols_export = [
        "overall_rank", "bowler_id", "bowler_name", "primary_bowling_role",
        "performance_rating", "evidence_reliability_score", "evidence_tier",
        "legal_balls_overall", "economy_overall", "wickets_overall",
        "legal_balls_clutch", "economy_clutch", "delta_econ_phase_adj",
        dot_col, "bnd_pct_clutch", "wickets_clutch",
        "bowling_clutch_index", "matches_played", "comps_played"
    ]
    main_ranking = eligible[cols_export].copy()
    main_ranking.rename(columns={"overall_rank": "rank", "bowler_id": "player_id", "bowler_name": "player_name"}, inplace=True)
    
    # 2. Role-wise rankings
    role_rankings = {}
    for role in ["Powerplay Specialist", "Middle Enforcer", "Death Specialist", "All-Phase Bowler"]:
        sub = eligible[eligible["primary_bowling_role"] == role].copy().reset_index(drop=True)
        sub["role_rank"] = sub.index + 1
        cols_role = ["role_rank", "bowler_id", "bowler_name", "performance_rating", "evidence_reliability_score", "economy_clutch", "delta_econ_phase_adj", dot_col, "wickets_clutch", "matches_played"]
        sub_export = sub[cols_role].rename(columns={"role_rank": "rank", "bowler_id": "player_id", "bowler_name": "player_name"})
        role_rankings[role] = sub_export
        
    # 3. Standout clutch bowlers
    standout_clutch = eligible[eligible["delta_econ_phase_adj"] >= 1.50].sort_values(by="delta_econ_phase_adj", ascending=False).reset_index(drop=True)
    standout_clutch["rank"] = standout_clutch.index + 1
    
    # 4. High-upside watchlist
    watchlist = df[(df["evidence_tier"].isin(["Moderate Evidence", "Insufficient Evidence"])) & (df["performance_rating"] >= 70.0)].copy()
    watchlist = watchlist.sort_values(by="performance_rating", ascending=False).reset_index(drop=True)
    watchlist["rank"] = watchlist.index + 1
    
    # 5. Regression risks (Strong evidence, but negative delta economy < -1.0)
    regression_risks = eligible[(eligible["evidence_tier"] == "Strong Evidence") & (eligible["delta_econ_phase_adj"] < -1.0)].sort_values(by="delta_econ_phase_adj", ascending=True).reset_index(drop=True)
    regression_risks["rank"] = regression_risks.index + 1
    
    return {
        "overall_eligible": main_ranking,
        "by_role": role_rankings,
        "standout_clutch": standout_clutch,
        "watchlist": watchlist,
        "regression_risks": regression_risks
    }
