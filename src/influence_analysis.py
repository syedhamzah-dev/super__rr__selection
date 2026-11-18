"""
src/influence_analysis.py
SupeRR Selector - Match Influence & Performance Concentration Analysis Module

This module investigates whether a small number of matches disproportionately affect
player performance ratings and rankings.

Key Diagnostics:
1. Performance Concentration Metrics:
   - Number of distinct matches with clutch exposure.
   - Herfindahl-Hirschman Index (HHI) of clutch delivery volume across matches.
   - Share of clutch runs (batters) or clutch wickets (bowlers) in top match.
2. Leave-One-Most-Influential-Match-Out (LOMO) Analysis:
   - Identifies each top player's single most productive clutch match.
   - Recomputes performance rating and leaderboard rank without that single match.
   - Classifies player resilience as Sustained, Moderately Influenced, or Match-Dependent.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

from src.clutch_analysis import calculate_batting_clutch_index, calculate_bowling_clutch_index
from src.reliability_scoring import calculate_batter_evidence_reliability, calculate_bowler_evidence_reliability
from src.player_rating import (
    calculate_batting_performance_rating,
    calculate_bowling_performance_rating,
    DEFAULT_BATTER_WEIGHTS,
    DEFAULT_BOWLER_WEIGHTS
)
from src.bowler_pressure_analysis import BOWLER_WICKET_TYPES


def calculate_batter_match_concentration(
    df_deliveries: pd.DataFrame,
    df_batter_rankings: pd.DataFrame
) -> pd.DataFrame:
    """
    Computes match-level clutch volume concentration (HHI) and top-match contribution shares
    for all eligible batters.
    """
    df_faced = df_deliveries[df_deliveries["extras_type"] != "wide"].copy()
    df_faced["is_clutch"] = df_faced["batting_pressure_index"] >= 6.0
    
    clutch_df = df_faced[df_faced["is_clutch"]]
    match_agg = clutch_df.groupby(["striker_id", "match_id"]).agg(
        bf_clutch_match=("is_wicket", "count"),
        runs_clutch_match=("batter_runs", "sum")
    ).reset_index()

    eligible_ids = set(df_batter_rankings["player_id"])
    records = []

    for pid in eligible_ids:
        sub = match_agg[match_agg["striker_id"] == pid]
        if len(sub) == 0:
            continue
            
        tot_bf = sub["bf_clutch_match"].sum()
        tot_runs = sub["runs_clutch_match"].sum()
        matches_clutch = len(sub)
        
        # Herfindahl-Hirschman Index on clutch balls faced: sum((bf_m / tot_bf)^2)
        hhi_bf = np.sum((sub["bf_clutch_match"] / tot_bf) ** 2)
        
        top_match_bf = sub["bf_clutch_match"].max()
        top_match_bf_share = top_match_bf / tot_bf if tot_bf > 0 else 0.0
        
        top_match_runs = sub["runs_clutch_match"].max()
        top_match_run_share = top_match_runs / tot_runs if tot_runs > 0 else 0.0

        records.append({
            "player_id": pid,
            "clutch_matches_count": matches_clutch,
            "clutch_bf_total": int(tot_bf),
            "clutch_runs_total": int(tot_runs),
            "clutch_volume_hhi": round(hhi_bf, 3),
            "top_match_bf_share": round(top_match_bf_share * 100.0, 1),
            "top_match_run_share": round(top_match_run_share * 100.0, 1),
            "top_match_runs": int(top_match_runs)
        })

    df_conc = pd.DataFrame(records)
    # Merge ranking info
    merged = df_batter_rankings[["rank", "player_id", "player_name", "primary_role", "performance_rating"]].merge(
        df_conc, on="player_id", how="left"
    )
    return merged.sort_values("rank", ascending=True).reset_index(drop=True)


def calculate_bowler_match_concentration(
    df_deliveries: pd.DataFrame,
    df_bowler_rankings: pd.DataFrame
) -> pd.DataFrame:
    """
    Computes match-level clutch volume concentration (HHI) and top-match contribution shares
    for all eligible bowlers.
    """
    df = df_deliveries.copy()
    df["is_clutch"] = df["bowling_pressure_index"] >= 6.0
    df["is_bowler_wkt"] = (
        (df["is_wicket"] == True) & (df["dismissal_type"].isin(BOWLER_WICKET_TYPES))
    ).astype(int)

    clutch_df = df[df["is_clutch"] & df["is_legal_ball"]]
    match_agg = clutch_df.groupby(["bowler_id", "match_id"]).agg(
        lb_clutch_match=("is_legal_ball", "sum"),
        runs_clutch_match=("bowler_conceded_runs", "sum"),
        wkts_clutch_match=("is_bowler_wkt", "sum")
    ).reset_index()

    eligible_ids = set(df_bowler_rankings["player_id"])
    records = []

    for pid in eligible_ids:
        sub = match_agg[match_agg["bowler_id"] == pid]
        if len(sub) == 0:
            continue

        tot_lb = sub["lb_clutch_match"].sum()
        tot_wkts = sub["wkts_clutch_match"].sum()
        matches_clutch = len(sub)

        hhi_lb = np.sum((sub["lb_clutch_match"] / tot_lb) ** 2)

        top_match_lb = sub["lb_clutch_match"].max()
        top_match_lb_share = top_match_lb / tot_lb if tot_lb > 0 else 0.0

        top_match_wkts = sub["wkts_clutch_match"].max()
        top_match_wkt_share = top_match_wkts / tot_wkts if tot_wkts > 0 else 0.0

        records.append({
            "player_id": pid,
            "clutch_matches_count": matches_clutch,
            "clutch_lb_total": int(tot_lb),
            "clutch_wkts_total": int(tot_wkts),
            "clutch_volume_hhi": round(hhi_lb, 3),
            "top_match_lb_share": round(top_match_lb_share * 100.0, 1),
            "top_match_wkt_share": round(top_match_wkt_share * 100.0, 1),
            "top_match_wkts": int(top_match_wkts)
        })

    df_conc = pd.DataFrame(records)
    merged = df_bowler_rankings[["rank", "player_id", "player_name", "primary_bowling_role", "performance_rating"]].merge(
        df_conc, on="player_id", how="left"
    )
    return merged.sort_values("rank", ascending=True).reset_index(drop=True)


def evaluate_leave_one_match_out_sensitivity(
    df_deliveries: pd.DataFrame,
    df_batter_ratings: pd.DataFrame,
    df_bowler_ratings: pd.DataFrame,
    top_n: int = 25
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Evaluates how player ratings and ranks change when each top-ranked player's single
    most influential match is omitted.
    """
    # 1. Batter LOMO
    b_df = df_batter_ratings.copy()
    b_eligible = b_df[b_df["is_eligible_for_ranking"]].sort_values("performance_rating", ascending=False).reset_index(drop=True)
    top_batters = b_eligible.head(top_n).copy()

    df_faced = df_deliveries[df_deliveries["extras_type"] != "wide"].copy()
    df_faced["is_clutch"] = df_faced["batting_pressure_index"] >= 6.0
    
    b_lomo_records = []
    for _, prow in top_batters.iterrows():
        pid = prow["striker_id"]
        base_rating = prow["performance_rating"]
        base_rank = prow.name + 1

        # Find player's most influential match (highest clutch runs)
        p_clutch = df_faced[(df_faced["striker_id"] == pid) & (df_faced["is_clutch"])]
        if len(p_clutch) == 0:
            continue
        match_runs = p_clutch.groupby("match_id")["batter_runs"].sum()
        top_match_id = match_runs.idxmax()
        top_match_run_val = match_runs.max()

        # Recalculate metrics excluding top_match_id for all players
        df_excl = df_faced[df_faced["match_id"] != top_match_id]
        
        # Slices for this player without top_match_id
        p_faced_excl = df_excl[df_excl["striker_id"] == pid]
        bf_ovr = len(p_faced_excl)
        runs_ovr = p_faced_excl["batter_runs"].sum()
        sr_ovr = np.round((runs_ovr / max(bf_ovr, 1)) * 100.0, 2)
        
        p_clutch_excl = p_faced_excl[p_faced_excl["is_clutch"]]
        bf_clutch = len(p_clutch_excl)
        runs_clutch = p_clutch_excl["batter_runs"].sum()
        sr_clutch = np.round((runs_clutch / max(bf_clutch, 1)) * 100.0, 2)
        dots_clutch = (p_clutch_excl["batter_runs"] == 0).sum()
        dot_pct_clutch = np.round((dots_clutch / max(bf_clutch, 1)) * 100.0, 2)
        bnds_clutch = (p_clutch_excl["is_four"] | p_clutch_excl["is_six"]).sum()
        bnd_pct_clutch = np.round((bnds_clutch / max(bf_clutch, 1)) * 100.0, 2)
        dismissals_clutch = ((p_clutch_excl["is_wicket"] == True) & (p_clutch_excl["dismissed_player_id"] == pid)).sum()
        rpd_clutch = np.round(runs_clutch / max(dismissals_clutch, 1), 2)

        # Low slice
        p_low_excl = p_faced_excl[p_faced_excl["batting_pressure_index"] < 3.5]
        bf_low = len(p_low_excl)
        runs_low = p_low_excl["batter_runs"].sum()
        sr_low = np.round((runs_low / max(bf_low, 1)) * 100.0, 2)
        dot_low = np.round(((p_low_excl["batter_runs"] == 0).sum() / max(bf_low, 1)) * 100.0, 2)
        bnd_low = np.round(((p_low_excl["is_four"] | p_low_excl["is_six"]).sum() / max(bf_low, 1)) * 100.0, 2)
        dismissals_low = ((p_low_excl["is_wicket"] == True) & (p_low_excl["dismissed_player_id"] == pid)).sum()
        rpd_low = np.round(runs_low / max(dismissals_low, 1), 2)

        # Construct single-player row
        row_dict = prow.to_dict()
        row_dict.update({
            "bf_overall": bf_ovr, "runs_overall": runs_ovr, "sr_overall": sr_ovr,
            "bf_clutch": bf_clutch, "runs_clutch": runs_clutch, "sr_clutch": sr_clutch,
            "dot_pct_clutch": dot_pct_clutch, "bnd_pct_clutch": bnd_pct_clutch, "rpd_clutch": rpd_clutch,
            "bf_low": bf_low, "runs_low": runs_low, "sr_low": sr_low,
            "dot_pct_low": dot_low, "bnd_pct_low": bnd_low, "rpd_low": rpd_low,
            "matches_played": p_faced_excl["match_id"].nunique(),
            "comps_played": 1
        })
        single_df = pd.DataFrame([row_dict])
        single_df = calculate_batting_clutch_index(single_df)
        single_df = calculate_batter_evidence_reliability(single_df)
        single_df = calculate_batting_performance_rating(single_df, DEFAULT_BATTER_WEIGHTS)
        
        excl_rating = single_df["performance_rating"].iloc[0]
        rating_shift = np.round(excl_rating - base_rating, 2)

        # Estimate new rank among eligible baseline
        new_rank = int((b_eligible["performance_rating"] > excl_rating).sum() + 1)
        rank_shift = int(new_rank - base_rank)

        # Classification
        if abs(rating_shift) <= 5.0 and abs(rank_shift) <= 5:
            classification = "Sustained / Resilient"
        elif abs(rating_shift) <= 10.0 and abs(rank_shift) <= 12:
            classification = "Moderately Influenced"
        else:
            classification = "Match-Dependent Spike"

        b_lomo_records.append({
            "player_id": pid,
            "player_name": prow["striker_name"],
            "primary_role": prow["primary_role"],
            "baseline_rank": base_rank,
            "baseline_rating": base_rating,
            "excluded_match_id": int(top_match_id),
            "excluded_match_runs": int(top_match_run_val),
            "rating_after_exclusion": excl_rating,
            "rating_shift": rating_shift,
            "rank_after_exclusion": new_rank,
            "rank_shift": rank_shift,
            "resilience_category": classification
        })

    # 2. Bowler LOMO
    bw_df = df_bowler_ratings.copy()
    bw_eligible = bw_df[bw_df["is_eligible_for_ranking"]].sort_values("performance_rating", ascending=False).reset_index(drop=True)
    top_bowlers = bw_eligible.head(top_n).copy()

    df_deliv = df_deliveries.copy()
    df_deliv["is_clutch"] = df_deliv["bowling_pressure_index"] >= 6.0
    df_deliv["is_bowler_wkt"] = (
        (df_deliv["is_wicket"] == True) & (df_deliv["dismissal_type"].isin(BOWLER_WICKET_TYPES))
    ).astype(int)

    bw_lomo_records = []
    for _, prow in top_bowlers.iterrows():
        pid = prow["bowler_id"]
        base_rating = prow["performance_rating"]
        base_rank = prow.name + 1

        # Find most influential match (highest wickets in clutch, or highest clutch legal balls)
        p_clutch = df_deliv[(df_deliv["bowler_id"] == pid) & (df_deliv["is_clutch"]) & (df_deliv["is_legal_ball"])]
        if len(p_clutch) == 0:
            continue
        match_wkts = p_clutch.groupby("match_id")["is_bowler_wkt"].sum()
        top_match_id = match_wkts.idxmax()
        top_match_wkt_val = match_wkts.max()

        # Recalculate without top match
        p_deliv_excl = df_deliv[(df_deliv["bowler_id"] == pid) & (df_deliv["match_id"] != top_match_id)]
        lb_ovr = p_deliv_excl["is_legal_ball"].sum()
        runs_ovr = p_deliv_excl["bowler_conceded_runs"].sum()
        econ_ovr = np.round((runs_ovr / max(lb_ovr, 1)) * 6.0, 2)
        wkts_ovr = p_deliv_excl["is_bowler_wkt"].sum()

        p_clutch_excl = p_deliv_excl[p_deliv_excl["is_clutch"] & p_deliv_excl["is_legal_ball"]]
        lb_clutch = len(p_clutch_excl)
        runs_clutch = p_clutch_excl["bowler_conceded_runs"].sum()
        econ_clutch = np.round((runs_clutch / max(lb_clutch, 1)) * 6.0, 2)
        true_dots = (p_clutch_excl["total_runs"] == 0).sum()
        true_dot_pct = np.round((true_dots / max(lb_clutch, 1)) * 100.0, 2)
        bnds = (p_clutch_excl["is_four"] | p_clutch_excl["is_six"]).sum()
        bnd_pct = np.round((bnds / max(lb_clutch, 1)) * 100.0, 2)
        wkts_clutch = p_clutch_excl["is_bowler_wkt"].sum()
        wkt_pct_clutch = np.round((wkts_clutch / max(lb_clutch, 1)) * 100.0, 2)

        pp_b = (p_clutch_excl["over_phase"] == "Powerplay").sum()
        mid_b = (p_clutch_excl["over_phase"] == "Middle").sum()
        death_b = (p_clutch_excl["over_phase"] == "Death").sum()

        p_low_excl = p_deliv_excl[(p_deliv_excl["bowling_pressure_index"] < 3.5) & p_deliv_excl["is_legal_ball"]]
        lb_low = len(p_low_excl)
        runs_low = p_low_excl["bowler_conceded_runs"].sum()
        econ_low = np.round((runs_low / max(lb_low, 1)) * 6.0, 2)
        true_dots_low = (p_low_excl["total_runs"] == 0).sum()
        true_dot_low = np.round((true_dots_low / max(lb_low, 1)) * 100.0, 2)
        bnds_low = (p_low_excl["is_four"] | p_low_excl["is_six"]).sum()
        bnd_low = np.round((bnds_low / max(lb_low, 1)) * 100.0, 2)
        wkts_low = p_low_excl["is_bowler_wkt"].sum()

        row_dict = prow.to_dict()
        row_dict.update({
            "legal_balls_overall": lb_ovr, "runs_conceded_overall": runs_ovr, "economy_overall": econ_ovr, "wickets_overall": wkts_ovr,
            "legal_balls_clutch": lb_clutch, "economy_clutch": econ_clutch, "true_dot_pct_clutch": true_dot_pct,
            "bnd_pct_clutch": bnd_pct, "wickets_clutch": wkts_clutch, "wkt_pct_clutch": wkt_pct_clutch,
            "pp_balls_clutch": pp_b, "mid_balls_clutch": mid_b, "death_balls_clutch": death_b,
            "legal_balls_low": lb_low, "economy_low": econ_low, "true_dot_pct_low": true_dot_low,
            "bnd_pct_low": bnd_low, "wickets_low": wkts_low,
            "matches_played": p_deliv_excl["match_id"].nunique(),
            "comps_played": 1
        })
        single_df = pd.DataFrame([row_dict])
        single_df = calculate_bowling_clutch_index(single_df)
        single_df = calculate_bowler_evidence_reliability(single_df)
        single_df = calculate_bowling_performance_rating(single_df, DEFAULT_BOWLER_WEIGHTS)

        excl_rating = single_df["performance_rating"].iloc[0]
        rating_shift = np.round(excl_rating - base_rating, 2)

        new_rank = int((bw_eligible["performance_rating"] > excl_rating).sum() + 1)
        rank_shift = int(new_rank - base_rank)

        if abs(rating_shift) <= 5.0 and abs(rank_shift) <= 5:
            classification = "Sustained / Resilient"
        elif abs(rating_shift) <= 10.0 and abs(rank_shift) <= 12:
            classification = "Moderately Influenced"
        else:
            classification = "Match-Dependent Spike"

        bw_lomo_records.append({
            "player_id": pid,
            "player_name": prow["bowler_name"],
            "primary_bowling_role": prow["primary_bowling_role"],
            "baseline_rank": base_rank,
            "baseline_rating": base_rating,
            "excluded_match_id": int(top_match_id),
            "excluded_match_wkts": int(top_match_wkt_val),
            "rating_after_exclusion": excl_rating,
            "rating_shift": rating_shift,
            "rank_after_exclusion": new_rank,
            "rank_shift": rank_shift,
            "resilience_category": classification
        })

    return pd.DataFrame(b_lomo_records), pd.DataFrame(bw_lomo_records)
