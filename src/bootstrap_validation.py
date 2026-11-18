"""
src/bootstrap_validation.py
SupeRR Selector - Match-Cluster Bootstrap Validation Module

This module implements match-cluster bootstrap resampling to evaluate:
1. Player-level rating uncertainty intervals (percentile intervals, mean, median, std dev).
2. Leaderboard ranking stability and rank distribution across historical match samples.
3. Eligibility stability across bootstrap replicates.

Key Design Principles:
- Resamples complete matches with replacement to preserve intra-match correlation,
  pitch conditions, opponent quality, and match context.
- Treats duplicate match draws as separate bootstrap contributions.
- Supports stratified match sampling across competition/season strata to prevent
  eliminating or oversampling tournament formats.
- Uses vectorized NumPy array computations for ultra-fast, 100% exact replicate evaluation.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

from src.clutch_analysis import (
    BATTER_ROLE_LOW_BASELINES,
    BOWLER_ROLE_LOW_BASELINES,
    GLOBAL_PHASE_CLUTCH_ECONOMY
)
from src.bowler_pressure_analysis import BOWLER_WICKET_TYPES


def build_match_strata_mapping(
    df_deliveries: pd.DataFrame,
    matches_csv_path: str = "Data Pack/matches.csv",
    competitions_csv_path: str = "Data Pack/competitions.csv"
) -> pd.DataFrame:
    """
    Builds a stratified mapping for all unique matches in the delivery dataset.
    Strata separate IPL seasons, T20I seasons, and other domestic T20 competitions.
    """
    unique_matches = df_deliveries[["match_id"]].drop_duplicates()
    
    try:
        df_m = pd.read_csv(matches_csv_path)
        df_c = pd.read_csv(competitions_csv_path)
        
        merged = unique_matches.merge(df_m[["match_id", "comp_id"]], on="match_id", how="left")
        merged = merged.merge(df_c[["comp_id", "comp_name", "match_format", "season"]], on="comp_id", how="left")
        
        is_ipl = merged["comp_name"].str.contains("IPL", na=False)
        season = merged["season"].astype(str).str.replace("/", "_")
        fmt = merged["match_format"].fillna("T20").astype(str)
        
        strata = np.where(is_ipl, "IPL_" + season, fmt + "_" + season)
        merged["stratum"] = strata
        return merged[["match_id", "stratum"]]
    except Exception:
        unique_matches["stratum"] = "All_Matches"
        return unique_matches


def prepare_batter_match_matrix(
    df_deliveries: pd.DataFrame,
    df_batter_ratings: pd.DataFrame
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, pd.DataFrame, List[int], Dict[str, np.ndarray]]:
    """
    Pre-aggregates delivery data for batters by (match_id, striker_id) into a dense matrix
    and prepares static role benchmark vectors for fast vectorized bootstrap evaluation.
    """
    df_faced = df_deliveries[df_deliveries["extras_type"] != "wide"].copy()
    df_faced["is_ball_faced"] = 1
    df_faced["is_dot"] = (df_faced["batter_runs"] == 0).astype(int)
    df_faced["is_bnd"] = (df_faced["is_four"] | df_faced["is_six"]).astype(int)
    df_faced["is_dismissed"] = (
        (df_faced["is_wicket"] == True) & (df_faced["dismissed_player_id"] == df_faced["striker_id"])
    ).astype(int)

    pi_b = df_faced["batting_pressure_index"]
    is_low = (pi_b < 3.5).astype(int)
    is_clutch = (pi_b >= 6.0).astype(int)

    df_faced["bf_low"] = is_low
    df_faced["runs_low"] = df_faced["batter_runs"] * is_low
    df_faced["dot_low"] = df_faced["is_dot"] * is_low
    df_faced["bnd_low"] = df_faced["is_bnd"] * is_low
    df_faced["dismissals_low"] = df_faced["is_dismissed"] * is_low

    df_faced["bf_clutch"] = is_clutch
    df_faced["runs_clutch"] = df_faced["batter_runs"] * is_clutch
    df_faced["dot_clutch"] = df_faced["is_dot"] * is_clutch
    df_faced["bnd_clutch"] = df_faced["is_bnd"] * is_clutch
    df_faced["dismissals_clutch"] = df_faced["is_dismissed"] * is_clutch

    agg_cols = [
        "is_ball_faced", "batter_runs", "is_dot", "is_bnd", "is_dismissed",
        "bf_low", "runs_low", "dot_low", "bnd_low", "dismissals_low",
        "bf_clutch", "runs_clutch", "dot_clutch", "bnd_clutch", "dismissals_clutch"
    ]

    b_match = df_faced.groupby(["match_id", "striker_id"])[agg_cols].sum().reset_index()
    b_match["match_played"] = 1

    unique_matches = df_deliveries["match_id"].unique().tolist()
    match_to_idx = {m: i for i, m in enumerate(unique_matches)}
    b_match_mat_idx = b_match["match_id"].map(match_to_idx).values

    # Player metadata aligned to df_batter_ratings order
    player_meta = df_batter_ratings[[
        "striker_id", "striker_name", "batting_type", "primary_role"
    ]].drop_duplicates(subset=["striker_id"]).reset_index(drop=True)
    
    player_to_idx = {pid: i for i, pid in enumerate(player_meta["striker_id"])}
    b_match_player_idx = b_match["striker_id"].map(player_to_idx).values

    all_agg_cols = agg_cols + ["match_played"]
    agg_matrix = b_match[all_agg_cols].values

    # Pre-compute static role benchmark vectors for all batters
    roles = player_meta["primary_role"].values
    benchmarks = {
        "bm_sr": np.array([BATTER_ROLE_LOW_BASELINES.get(r, BATTER_ROLE_LOW_BASELINES["Middle Order"])["sr"] for r in roles]),
        "bm_dot": np.array([BATTER_ROLE_LOW_BASELINES.get(r, BATTER_ROLE_LOW_BASELINES["Middle Order"])["dot_pct"] for r in roles]),
        "bm_bnd": np.array([BATTER_ROLE_LOW_BASELINES.get(r, BATTER_ROLE_LOW_BASELINES["Middle Order"])["bnd_pct"] for r in roles]),
        "bm_rpd": np.array([BATTER_ROLE_LOW_BASELINES.get(r, BATTER_ROLE_LOW_BASELINES["Middle Order"])["rpd"] for r in roles])
    }

    return agg_matrix, b_match_mat_idx, b_match_player_idx, player_meta, unique_matches, benchmarks


def prepare_bowler_match_matrix(
    df_deliveries: pd.DataFrame,
    df_bowler_ratings: pd.DataFrame
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, pd.DataFrame, List[int], Dict[str, np.ndarray]]:
    """
    Pre-aggregates delivery data for bowlers by (match_id, bowler_id) into a dense matrix
    and prepares static role benchmark vectors for fast vectorized bootstrap evaluation.
    """
    df = df_deliveries.copy()
    df["is_true_dot"] = (df["is_legal_ball"] & (df["total_runs"] == 0)).astype(int)
    df["is_bnd_conceded"] = (df["is_four"] | df["is_six"]).astype(int)
    df["is_bowler_wkt"] = ((df["is_wicket"] == True) & (df["dismissal_type"].isin(BOWLER_WICKET_TYPES))).astype(int)

    df["is_pp"] = (df["is_legal_ball"] & (df["over_phase"] == "Powerplay")).astype(int)
    df["is_mid"] = (df["is_legal_ball"] & (df["over_phase"] == "Middle")).astype(int)
    df["is_death"] = (df["is_legal_ball"] & (df["over_phase"] == "Death")).astype(int)

    pib = df["bowling_pressure_index"]
    is_low = (pib < 3.5).astype(int)
    is_clutch = (pib >= 6.0).astype(int)

    df["legal_low"] = df["is_legal_ball"].astype(int) * is_low
    df["runs_low"] = df["bowler_conceded_runs"] * is_low
    df["true_dot_low"] = df["is_true_dot"] * is_low
    df["bnd_low"] = df["is_bnd_conceded"] * is_low
    df["wkt_low"] = df["is_bowler_wkt"] * is_low

    df["legal_clutch"] = df["is_legal_ball"].astype(int) * is_clutch
    df["runs_clutch"] = df["bowler_conceded_runs"] * is_clutch
    df["true_dot_clutch"] = df["is_true_dot"] * is_clutch
    df["bnd_clutch"] = df["is_bnd_conceded"] * is_clutch
    df["wkt_clutch"] = df["is_bowler_wkt"] * is_clutch

    df["pp_clutch"] = df["is_pp"] * is_clutch
    df["mid_clutch"] = df["is_mid"] * is_clutch
    df["death_clutch"] = df["is_death"] * is_clutch

    df["legal_overall"] = df["is_legal_ball"].astype(int)
    df["runs_overall"] = df["bowler_conceded_runs"]
    df["wkt_overall"] = df["is_bowler_wkt"]

    agg_cols = [
        "legal_overall", "runs_overall", "wkt_overall",
        "is_pp", "is_mid", "is_death",
        "legal_low", "runs_low", "true_dot_low", "bnd_low", "wkt_low",
        "legal_clutch", "runs_clutch", "true_dot_clutch", "bnd_clutch", "wkt_clutch",
        "pp_clutch", "mid_clutch", "death_clutch"
    ]

    bw_match = df.groupby(["match_id", "bowler_id"])[agg_cols].sum().reset_index()
    bw_match["match_played"] = 1

    unique_matches = df_deliveries["match_id"].unique().tolist()
    match_to_idx = {m: i for i, m in enumerate(unique_matches)}
    bw_match_mat_idx = bw_match["match_id"].map(match_to_idx).values

    player_meta = df_bowler_ratings[[
        "bowler_id", "bowler_name", "bowling_type", "pace_or_spin", "primary_bowling_role"
    ]].drop_duplicates(subset=["bowler_id"]).reset_index(drop=True)
    
    player_to_idx = {pid: i for i, pid in enumerate(player_meta["bowler_id"])}
    bw_match_player_idx = bw_match["bowler_id"].map(player_to_idx).values

    all_agg_cols = agg_cols + ["match_played"]
    agg_matrix = bw_match[all_agg_cols].values

    # Pre-compute static role benchmark vectors for all bowlers
    roles = player_meta["primary_bowling_role"].values
    benchmarks = {
        "bm_econ": np.array([BOWLER_ROLE_LOW_BASELINES.get(r, BOWLER_ROLE_LOW_BASELINES["All-Phase Bowler"])["econ"] for r in roles]),
        "bm_dot": np.array([BOWLER_ROLE_LOW_BASELINES.get(r, BOWLER_ROLE_LOW_BASELINES["All-Phase Bowler"])["dot_pct"] for r in roles]),
        "bm_bnd": np.array([BOWLER_ROLE_LOW_BASELINES.get(r, BOWLER_ROLE_LOW_BASELINES["All-Phase Bowler"])["bnd_pct"] for r in roles]),
        "bm_wkt": np.array([BOWLER_ROLE_LOW_BASELINES.get(r, BOWLER_ROLE_LOW_BASELINES["All-Phase Bowler"])["wkt_pct"] for r in roles])
    }

    return agg_matrix, bw_match_mat_idx, bw_match_player_idx, player_meta, unique_matches, benchmarks


def evaluate_batter_replicate_vectorized(
    player_totals: np.ndarray,
    bm: Dict[str, np.ndarray]
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Vectorized computation of batter ratings, clutch metrics, ERS, tiers, and ranks
    for one bootstrap replicate.
    """
    bf_ovr = player_totals[:, 0]
    runs_ovr = player_totals[:, 1]
    
    bf_low = player_totals[:, 5]
    runs_low = player_totals[:, 6]
    dot_low = player_totals[:, 7]
    bnd_low = player_totals[:, 8]
    dismissals_low = player_totals[:, 9]

    bf_clutch = player_totals[:, 10]
    runs_clutch = player_totals[:, 11]
    dot_clutch = player_totals[:, 12]
    bnd_clutch = player_totals[:, 13]
    dismissals_clutch = player_totals[:, 14]
    matches_played = player_totals[:, 15]

    bf_ovr_safe = np.maximum(bf_ovr, 1.0)
    sr_ovr = np.round((runs_ovr / bf_ovr_safe) * 100.0, 2)

    bf_low_safe = np.maximum(bf_low, 1.0)
    sr_low = np.round((runs_low / bf_low_safe) * 100.0, 2)
    dot_pct_low = np.round((dot_low / bf_low_safe) * 100.0, 2)
    bnd_pct_low = np.round((bnd_low / bf_low_safe) * 100.0, 2)
    rpd_low = np.round(runs_low / np.maximum(dismissals_low, 1.0), 2)

    bf_clutch_safe = np.maximum(bf_clutch, 1.0)
    sr_clutch = np.round((runs_clutch / bf_clutch_safe) * 100.0, 2)
    dot_pct_clutch = np.round((dot_clutch / bf_clutch_safe) * 100.0, 2)
    bnd_pct_clutch = np.round((bnd_clutch / bf_clutch_safe) * 100.0, 2)
    rpd_clutch = np.round(runs_clutch / np.maximum(dismissals_clutch, 1.0), 2)

    # Low-pressure baseline blending
    w_ind = np.clip(bf_low / 25.0, 0.0, 1.0)
    sr_low_eff = np.round(np.where(bf_low >= 25, sr_low, w_ind * sr_low + (1.0 - w_ind) * bm["bm_sr"]), 2)
    dot_low_eff = np.round(np.where(bf_low >= 25, dot_pct_low, w_ind * dot_pct_low + (1.0 - w_ind) * bm["bm_dot"]), 2)
    bnd_low_eff = np.round(np.where(bf_low >= 25, bnd_pct_low, w_ind * bnd_pct_low + (1.0 - w_ind) * bm["bm_bnd"]), 2)
    rpd_low_eff = np.round(np.where(bf_low >= 25, rpd_low, w_ind * rpd_low + (1.0 - w_ind) * bm["bm_rpd"]), 2)

    # Differentials
    delta_sr = np.round(sr_clutch - sr_low_eff, 2)
    delta_dot = np.round(dot_low_eff - dot_pct_clutch, 2)
    delta_bnd = np.round(bnd_pct_clutch - bnd_low_eff, 2)
    delta_rpd = np.round(rpd_clutch - rpd_low_eff, 2)

    raw_bci = (
        0.40 * (delta_sr / 25.0)
        + 0.30 * (delta_dot / 10.0)
        + 0.20 * (delta_bnd / 8.0)
        + 0.10 * np.clip(delta_rpd / 15.0, -1.0, 1.0)
    )
    cw = bf_clutch / (bf_clutch + 30.0)
    bci = np.round(np.clip(5.0 + 5.0 * np.tanh(cw * raw_bci), 0.0, 10.0), 2)

    # Evidence Reliability Score (ERS)
    f_clutch = np.clip(bf_clutch / 120.0 * 100.0, 0.0, 100.0)
    f_ovr = np.clip(bf_ovr / 300.0 * 100.0, 0.0, 100.0)
    f_m = np.clip(matches_played / 25.0 * 100.0, 0.0, 100.0)
    f_c = np.clip(1.0 / 3.0 * 100.0, 0.0, 100.0)
    ers = np.round(0.40 * f_clutch + 0.25 * f_ovr + 0.20 * f_m + 0.15 * f_c, 2)

    # Discrete Evidence Tiers
    is_strong = (ers >= 60.0) & (bf_clutch >= 40) & (matches_played >= 10)
    is_mod = (ers >= 35.0) & (bf_clutch >= 20) & (matches_played >= 5) & (~is_strong)
    is_eligible = is_strong | is_mod
    is_insuff = (bf_ovr >= 30) & (bf_clutch >= 10) & (~is_eligible)
    tiers = np.where(
        is_strong, "Strong Evidence",
        np.where(is_mod, "Moderate Evidence", np.where(is_insuff, "Insufficient Evidence", "Not Eligible"))
    )

    # Batting Performance Rating
    sub_scoring = np.clip((sr_clutch - 70.0) / (200.0 - 70.0) * 100.0, 0.0, 100.0)
    sub_boundary = np.clip(bnd_pct_clutch / 35.0 * 100.0, 0.0, 100.0)
    sub_rotation = np.clip(((100.0 - dot_pct_clutch) - 20.0) / (70.0 - 20.0) * 100.0, 0.0, 100.0)
    sub_preservation = np.clip(rpd_clutch / 50.0 * 100.0, 0.0, 100.0)
    sub_clutch = np.clip(bci * 10.0, 0.0, 100.0)
    sub_overall = np.clip((sr_ovr - 80.0) / (180.0 - 80.0) * 100.0, 0.0, 100.0)

    pr = np.round(
        0.30 * sub_scoring + 0.20 * sub_boundary + 0.15 * sub_rotation
        + 0.15 * sub_preservation + 0.10 * sub_clutch + 0.10 * sub_overall, 2
    )

    # Ranks among eligible cohort
    ranks = np.full(len(pr), np.nan, dtype=np.float32)
    eligible_indices = np.where(is_eligible)[0]
    if len(eligible_indices) > 0:
        eligible_ratings = pr[eligible_indices]
        # Sort descending
        order = np.argsort(-eligible_ratings)
        sorted_indices = eligible_indices[order]
        ranks[sorted_indices] = np.arange(1, len(eligible_indices) + 1, dtype=np.float32)

    return pr, ranks, is_eligible, tiers, sr_clutch, dot_pct_clutch, bnd_pct_clutch


def evaluate_bowler_replicate_vectorized(
    player_totals: np.ndarray,
    bm: Dict[str, np.ndarray]
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Vectorized computation of bowler ratings, clutch metrics, ERS, tiers, and ranks
    for one bootstrap replicate.
    """
    lb_ovr = player_totals[:, 0]
    runs_ovr = player_totals[:, 1]
    
    lb_low = player_totals[:, 6]
    runs_low = player_totals[:, 7]
    true_dot_low = player_totals[:, 8]
    bnd_low = player_totals[:, 9]
    wkt_low = player_totals[:, 10]

    lb_clutch = player_totals[:, 11]
    runs_clutch = player_totals[:, 12]
    true_dot_clutch = player_totals[:, 13]
    bnd_clutch = player_totals[:, 14]
    wkt_clutch = player_totals[:, 15]

    pp_b = player_totals[:, 16]
    mid_b = player_totals[:, 17]
    death_b = player_totals[:, 18]
    matches_played = player_totals[:, 19]

    lb_ovr_safe = np.maximum(lb_ovr, 1.0)
    econ_ovr = np.round((runs_ovr / lb_ovr_safe) * 6.0, 2)

    lb_low_safe = np.maximum(lb_low, 1.0)
    econ_low = np.round((runs_low / lb_low_safe) * 6.0, 2)
    true_dot_pct_low = np.round((true_dot_low / lb_low_safe) * 100.0, 2)
    bnd_pct_low = np.round((bnd_low / lb_low_safe) * 100.0, 2)
    ind_wkt_pct_low = (wkt_low / lb_low_safe) * 100.0

    lb_clutch_safe = np.maximum(lb_clutch, 1.0)
    econ_clutch = np.round((runs_clutch / lb_clutch_safe) * 6.0, 2)
    true_dot_pct_clutch = np.round((true_dot_clutch / lb_clutch_safe) * 100.0, 2)
    bnd_pct_clutch = np.round((bnd_clutch / lb_clutch_safe) * 100.0, 2)
    wkt_pct_clutch = np.round((wkt_clutch / lb_clutch_safe) * 100.0, 2)

    # Low-pressure baseline blending
    w_ind = np.clip(lb_low / 25.0, 0.0, 1.0)
    econ_low_eff = np.round(np.where(lb_low >= 25, econ_low, w_ind * econ_low + (1.0 - w_ind) * bm["bm_econ"]), 2)
    dot_low_eff = np.round(np.where(lb_low >= 25, true_dot_pct_low, w_ind * true_dot_pct_low + (1.0 - w_ind) * bm["bm_dot"]), 2)
    bnd_low_eff = np.round(np.where(lb_low >= 25, bnd_pct_low, w_ind * bnd_pct_low + (1.0 - w_ind) * bm["bm_bnd"]), 2)
    wkt_low_eff = np.round(np.where(lb_low >= 25, ind_wkt_pct_low, w_ind * ind_wkt_pct_low + (1.0 - w_ind) * bm["bm_wkt"]), 2)

    # Phase expected economy under clutch pressure
    phase_sum = pp_b + mid_b + death_b
    econ_clutch_exp_raw = (
        pp_b * GLOBAL_PHASE_CLUTCH_ECONOMY["Powerplay"]
        + mid_b * GLOBAL_PHASE_CLUTCH_ECONOMY["Middle"]
        + death_b * GLOBAL_PHASE_CLUTCH_ECONOMY["Death"]
    ) / np.maximum(phase_sum, 1.0)

    econ_clutch_exp = np.round(np.where(phase_sum > 0, econ_clutch_exp_raw, bm["bm_econ"]), 2)
    delta_econ_phase_adj = np.round(econ_clutch_exp - econ_clutch, 2)

    # Differentials
    delta_dot = np.round(true_dot_pct_clutch - dot_low_eff, 2)
    delta_bnd = np.round(bnd_low_eff - bnd_pct_clutch, 2)
    delta_wkt = np.round(wkt_pct_clutch - wkt_low_eff, 2)

    raw_score = (
        0.40 * (delta_econ_phase_adj / 1.50)
        + 0.25 * (delta_dot / 8.0)
        + 0.20 * (delta_bnd / 6.0)
        + 0.15 * (delta_wkt / 3.0)
    )
    cw = lb_clutch / (lb_clutch + 30.0)
    boci = np.round(np.clip(5.0 + 5.0 * np.tanh(cw * raw_score), 0.0, 10.0), 2)

    # Evidence Reliability Score (ERS)
    f_clutch = np.clip(lb_clutch / 120.0 * 100.0, 0.0, 100.0)
    f_ovr = np.clip(lb_ovr / 300.0 * 100.0, 0.0, 100.0)
    f_m = np.clip(matches_played / 25.0 * 100.0, 0.0, 100.0)
    f_c = np.clip(1.0 / 3.0 * 100.0, 0.0, 100.0)
    ers = np.round(0.40 * f_clutch + 0.25 * f_ovr + 0.20 * f_m + 0.15 * f_c, 2)

    # Discrete Evidence Tiers
    is_strong = (ers >= 60.0) & (lb_clutch >= 40) & (matches_played >= 10)
    is_mod = (ers >= 35.0) & (lb_clutch >= 20) & (matches_played >= 5) & (~is_strong)
    is_eligible = is_strong | is_mod
    is_insuff = (lb_ovr >= 30) & (lb_clutch >= 10) & (~is_eligible)
    tiers = np.where(
        is_strong, "Strong Evidence",
        np.where(is_mod, "Moderate Evidence", np.where(is_insuff, "Insufficient Evidence", "Not Eligible"))
    )

    # Bowling Performance Rating
    sub_rc = np.clip((delta_econ_phase_adj - (-3.0)) / (3.0 - (-3.0)) * 100.0, 0.0, 100.0)
    sub_dots = np.clip((true_dot_pct_clutch - 15.0) / (50.0 - 15.0) * 100.0, 0.0, 100.0)
    sub_wkts = np.clip(wkt_pct_clutch / 12.0 * 100.0, 0.0, 100.0)
    sub_bnd = np.clip((30.0 - bnd_pct_clutch) / (30.0 - 10.0) * 100.0, 0.0, 100.0)
    sub_ovr = np.clip((11.0 - econ_ovr) / (11.0 - 6.0) * 100.0, 0.0, 100.0)
    sub_clutch = np.clip(boci * 10.0, 0.0, 100.0)

    pr = np.round(
        0.25 * sub_rc + 0.20 * sub_dots + 0.20 * sub_wkts
        + 0.15 * sub_bnd + 0.10 * sub_ovr + 0.10 * sub_clutch, 2
    )

    # Ranks among eligible cohort
    ranks = np.full(len(pr), np.nan, dtype=np.float32)
    eligible_indices = np.where(is_eligible)[0]
    if len(eligible_indices) > 0:
        eligible_ratings = pr[eligible_indices]
        order = np.argsort(-eligible_ratings)
        sorted_indices = eligible_indices[order]
        ranks[sorted_indices] = np.arange(1, len(eligible_indices) + 1, dtype=np.float32)

    return pr, ranks, is_eligible, tiers, econ_clutch, delta_econ_phase_adj, true_dot_pct_clutch


def run_match_cluster_bootstrap(
    df_deliveries: pd.DataFrame,
    df_batter_ratings: pd.DataFrame,
    df_bowler_ratings: pd.DataFrame,
    n_replicates: int = 1000,
    random_seed: int = 42,
    stratify: bool = True
) -> Dict[str, dict]:
    """
    Executes fast match-cluster bootstrap resampling across n_replicates.
    Returns collected replicate arrays for rating, rank, eligibility, and metrics.
    """
    np.random.seed(random_seed)

    # 1. Prepare match aggregation matrices and static benchmark vectors
    b_matrix, b_match_idx, b_player_idx, b_meta, unique_matches, b_benchmarks = prepare_batter_match_matrix(
        df_deliveries, df_batter_ratings
    )
    bw_matrix, bw_match_idx, bw_player_idx, bw_meta, _, bw_benchmarks = prepare_bowler_match_matrix(
        df_deliveries, df_bowler_ratings
    )

    n_matches = len(unique_matches)
    n_batters = len(b_meta)
    n_bowlers = len(bw_meta)

    # 2. Setup strata
    match_strata_df = build_match_strata_mapping(df_deliveries)
    match_to_stratum = dict(zip(match_strata_df["match_id"], match_strata_df["stratum"]))
    
    if stratify:
        strata_indices = {}
        for idx, m in enumerate(unique_matches):
            st = match_to_stratum.get(m, "Other")
            strata_indices.setdefault(st, []).append(idx)
        strata_groups = {st: np.array(idxs) for st, idxs in strata_indices.items()}
    else:
        strata_groups = {"All": np.arange(n_matches)}

    # 3. Storage arrays for replicate outcomes
    b_ratings = np.zeros((n_batters, n_replicates), dtype=np.float32)
    b_ranks = np.full((n_batters, n_replicates), np.nan, dtype=np.float32)
    b_eligible = np.zeros((n_batters, n_replicates), dtype=bool)
    b_tiers = np.empty((n_batters, n_replicates), dtype=object)
    b_sr_clutch = np.zeros((n_batters, n_replicates), dtype=np.float32)
    b_dot_clutch = np.zeros((n_batters, n_replicates), dtype=np.float32)
    b_bnd_clutch = np.zeros((n_batters, n_replicates), dtype=np.float32)

    bw_ratings = np.zeros((n_bowlers, n_replicates), dtype=np.float32)
    bw_ranks = np.full((n_bowlers, n_replicates), np.nan, dtype=np.float32)
    bw_eligible = np.zeros((n_bowlers, n_replicates), dtype=bool)
    bw_tiers = np.empty((n_bowlers, n_replicates), dtype=object)
    bw_econ_clutch = np.zeros((n_bowlers, n_replicates), dtype=np.float32)
    bw_delta_econ = np.zeros((n_bowlers, n_replicates), dtype=np.float32)
    bw_dot_clutch = np.zeros((n_bowlers, n_replicates), dtype=np.float32)

    # 4. Bootstrap loop
    successful_replicates = 0

    for rep in range(n_replicates):
        # Sample match indices with replacement within strata
        sampled_matches = []
        for st, idx_arr in strata_groups.items():
            draw = np.random.choice(idx_arr, size=len(idx_arr), replace=True)
            sampled_matches.extend(draw)

        sampled_matches = np.array(sampled_matches)
        match_draw_counts = np.bincount(sampled_matches, minlength=n_matches)

        # Aggregate Batters
        b_row_weights = match_draw_counts[b_match_idx]
        b_weighted = b_matrix * b_row_weights[:, None]
        b_totals = np.zeros((n_batters, b_matrix.shape[1]), dtype=np.float32)
        for c in range(b_matrix.shape[1]):
            b_totals[:, c] = np.bincount(b_player_idx, weights=b_weighted[:, c], minlength=n_batters)

        (
            b_pr, b_rk, b_el, b_tr, b_sr, b_dt, b_bd
        ) = evaluate_batter_replicate_vectorized(b_totals, b_benchmarks)

        b_ratings[:, rep] = b_pr
        b_ranks[:, rep] = b_rk
        b_eligible[:, rep] = b_el
        b_tiers[:, rep] = b_tr
        b_sr_clutch[:, rep] = b_sr
        b_dot_clutch[:, rep] = b_dt
        b_bnd_clutch[:, rep] = b_bd

        # Aggregate Bowlers
        bw_row_weights = match_draw_counts[bw_match_idx]
        bw_weighted = bw_matrix * bw_row_weights[:, None]
        bw_totals = np.zeros((n_bowlers, bw_matrix.shape[1]), dtype=np.float32)
        for c in range(bw_matrix.shape[1]):
            bw_totals[:, c] = np.bincount(bw_player_idx, weights=bw_weighted[:, c], minlength=n_bowlers)

        (
            bw_pr, bw_rk, bw_el, bw_tr, bw_ec, bw_de, bw_dt
        ) = evaluate_bowler_replicate_vectorized(bw_totals, bw_benchmarks)

        bw_ratings[:, rep] = bw_pr
        bw_ranks[:, rep] = bw_rk
        bw_eligible[:, rep] = bw_el
        bw_tiers[:, rep] = bw_tr
        bw_econ_clutch[:, rep] = bw_ec
        bw_delta_econ[:, rep] = bw_de
        bw_dot_clutch[:, rep] = bw_dt

        successful_replicates += 1

    return {
        "metadata": {
            "n_replicates": n_replicates,
            "successful_replicates": successful_replicates,
            "random_seed": random_seed,
            "stratified": stratify,
            "n_matches": n_matches
        },
        "batters": {
            "meta": b_meta,
            "ratings": b_ratings,
            "ranks": b_ranks,
            "eligible": b_eligible,
            "tiers": b_tiers,
            "sr_clutch": b_sr_clutch,
            "dot_clutch": b_dot_clutch,
            "bnd_clutch": b_bnd_clutch
        },
        "bowlers": {
            "meta": bw_meta,
            "ratings": bw_ratings,
            "ranks": bw_ranks,
            "eligible": bw_eligible,
            "tiers": bw_tiers,
            "econ_clutch": bw_econ_clutch,
            "delta_econ": bw_delta_econ,
            "dot_clutch": bw_dot_clutch
        }
    }


def summarize_player_rating_uncertainty(
    boot_results: dict,
    df_baseline_ratings: pd.DataFrame,
    discipline: str = "batter"
) -> pd.DataFrame:
    """
    Computes descriptive bootstrap uncertainty intervals for player performance ratings
    and core clutch metrics.
    """
    data = boot_results["batters"] if discipline == "batter" else boot_results["bowlers"]
    meta = data["meta"].copy()
    ratings = data["ratings"]
    n_reps = ratings.shape[1]

    id_col = "striker_id" if discipline == "batter" else "bowler_id"
    name_col = "striker_name" if discipline == "batter" else "bowler_name"
    role_col = "primary_role" if discipline == "batter" else "primary_bowling_role"

    mean_rating = np.round(np.mean(ratings, axis=1), 2)
    median_rating = np.round(np.median(ratings, axis=1), 2)
    std_rating = np.round(np.std(ratings, axis=1), 2)
    p025_rating = np.round(np.percentile(ratings, 2.5, axis=1), 2)
    p975_rating = np.round(np.percentile(ratings, 97.5, axis=1), 2)
    ci_width = np.round(p975_rating - p025_rating, 2)

    summary = pd.DataFrame({
        "player_id": meta[id_col],
        "player_name": meta[name_col],
        "primary_role": meta[role_col],
        "bootstrap_mean_rating": mean_rating,
        "bootstrap_median_rating": median_rating,
        "rating_std": std_rating,
        "rating_p025": p025_rating,
        "rating_p975": p975_rating,
        "rating_ci_width": ci_width,
        "successful_replicates": n_reps
    })

    # Merge baseline performance rating and ERS
    base_sub = df_baseline_ratings[[
        id_col, "performance_rating", "evidence_reliability_score", "evidence_tier", "is_eligible_for_ranking"
    ]].rename(columns={
        id_col: "player_id",
        "performance_rating": "baseline_rating",
        "evidence_reliability_score": "baseline_ers",
        "evidence_tier": "baseline_tier",
        "is_eligible_for_ranking": "baseline_eligible"
    })
    summary = summary.merge(base_sub, on="player_id", how="left")

    # Add primary clutch metric interval
    if discipline == "batter":
        sr_arr = data["sr_clutch"]
        summary["sr_clutch_mean"] = np.round(np.mean(sr_arr, axis=1), 2)
        summary["sr_clutch_p025"] = np.round(np.percentile(sr_arr, 2.5, axis=1), 2)
        summary["sr_clutch_p975"] = np.round(np.percentile(sr_arr, 97.5, axis=1), 2)
    else:
        econ_arr = data["econ_clutch"]
        delta_arr = data["delta_econ"]
        summary["econ_clutch_mean"] = np.round(np.mean(econ_arr, axis=1), 2)
        summary["econ_clutch_p025"] = np.round(np.percentile(econ_arr, 2.5, axis=1), 2)
        summary["econ_clutch_p975"] = np.round(np.percentile(econ_arr, 97.5, axis=1), 2)
        summary["delta_econ_mean"] = np.round(np.mean(delta_arr, axis=1), 2)

    cols = [
        "player_id", "player_name", "primary_role", "baseline_rating",
        "bootstrap_mean_rating", "bootstrap_median_rating", "rating_std",
        "rating_p025", "rating_p975", "rating_ci_width",
        "baseline_ers", "baseline_tier", "baseline_eligible", "successful_replicates"
    ] + [c for c in summary.columns if c not in [
        "player_id", "player_name", "primary_role", "baseline_rating",
        "bootstrap_mean_rating", "bootstrap_median_rating", "rating_std",
        "rating_p025", "rating_p975", "rating_ci_width",
        "baseline_ers", "baseline_tier", "baseline_eligible", "successful_replicates"
    ]]
    return summary[cols].sort_values("baseline_rating", ascending=False).reset_index(drop=True)


def summarize_ranking_stability(
    boot_results: dict,
    df_baseline_rankings: pd.DataFrame,
    discipline: str = "batter"
) -> pd.DataFrame:
    """
    Computes ranking stability diagnostics for all players who appear in the baseline rankings
    or meet eligibility across bootstrap replicates.
    """
    data = boot_results["batters"] if discipline == "batter" else boot_results["bowlers"]
    meta = data["meta"].copy()
    ranks = data["ranks"] # shape: (n_players, n_reps) with NaN for non-eligible replicates
    eligible_arr = data["eligible"]
    n_reps = ranks.shape[1]

    id_col = "striker_id" if discipline == "batter" else "bowler_id"
    name_col = "striker_name" if discipline == "batter" else "bowler_name"
    role_col = "primary_role" if discipline == "batter" else "primary_bowling_role"

    reps_eligible_cnt = np.sum(eligible_arr, axis=1)
    eligible_pct = np.round((reps_eligible_cnt / n_reps) * 100.0, 2)

    top5_cnt = np.sum((ranks <= 5.0), axis=1)
    top10_cnt = np.sum((ranks <= 10.0), axis=1)
    top20_cnt = np.sum((ranks <= 20.0), axis=1)

    top5_freq = np.round((top5_cnt / n_reps) * 100.0, 2)
    top10_freq = np.round((top10_cnt / n_reps) * 100.0, 2)
    top20_freq = np.round((top20_cnt / n_reps) * 100.0, 2)

    mean_ranks = []
    med_ranks = []
    std_ranks = []
    p025_ranks = []
    p975_ranks = []

    for i in range(len(meta)):
        valid = ranks[i, ~np.isnan(ranks[i, :])]
        if len(valid) > 0:
            mean_ranks.append(np.round(np.mean(valid), 2))
            med_ranks.append(np.round(np.median(valid), 1))
            std_ranks.append(np.round(np.std(valid), 2))
            p025_ranks.append(np.round(np.percentile(valid, 2.5), 1))
            p975_ranks.append(np.round(np.percentile(valid, 97.5), 1))
        else:
            mean_ranks.append(np.nan)
            med_ranks.append(np.nan)
            std_ranks.append(np.nan)
            p025_ranks.append(np.nan)
            p975_ranks.append(np.nan)

    df_stab = pd.DataFrame({
        "player_id": meta[id_col],
        "player_name": meta[name_col],
        "primary_role": meta[role_col],
        "bootstrap_mean_rank": mean_ranks,
        "bootstrap_median_rank": med_ranks,
        "rank_std": std_ranks,
        "rank_p025": p025_ranks,
        "rank_p975": p975_ranks,
        "top5_freq_pct": top5_freq,
        "top10_freq_pct": top10_freq,
        "top20_freq_pct": top20_freq,
        "replicates_eligible": reps_eligible_cnt,
        "eligibility_pct": eligible_pct,
        "total_replicates": n_reps
    })

    # Merge baseline rank
    base_ranks = df_baseline_rankings[["rank", "player_id"]].rename(columns={"rank": "baseline_rank"})
    df_stab = df_stab.merge(base_ranks, on="player_id", how="left")

    cols = [
        "player_id", "player_name", "primary_role", "baseline_rank",
        "bootstrap_mean_rank", "bootstrap_median_rank", "rank_std",
        "rank_p025", "rank_p975", "top5_freq_pct", "top10_freq_pct", "top20_freq_pct",
        "eligibility_pct", "replicates_eligible", "total_replicates"
    ]
    return df_stab[cols].sort_values("baseline_rank", na_position="last").reset_index(drop=True)


def summarize_eligibility_stability(
    boot_results: dict,
    discipline: str = "batter"
) -> pd.DataFrame:
    """
    Computes the percentage of bootstrap replicates in which each player is classified into
    Strong Evidence, Moderate Evidence, Insufficient Evidence, or Not Eligible.
    """
    data = boot_results["batters"] if discipline == "batter" else boot_results["bowlers"]
    meta = data["meta"].copy()
    tiers = data["tiers"] # shape: (n_players, n_reps)
    n_reps = tiers.shape[1]

    id_col = "striker_id" if discipline == "batter" else "bowler_id"
    name_col = "striker_name" if discipline == "batter" else "bowler_name"
    role_col = "primary_role" if discipline == "batter" else "primary_bowling_role"

    pct_strong = np.round((np.sum(tiers == "Strong Evidence", axis=1) / n_reps) * 100.0, 2)
    pct_mod = np.round((np.sum(tiers == "Moderate Evidence", axis=1) / n_reps) * 100.0, 2)
    pct_insuff = np.round((np.sum(tiers == "Insufficient Evidence", axis=1) / n_reps) * 100.0, 2)
    pct_not_elig = np.round((np.sum(tiers == "Not Eligible", axis=1) / n_reps) * 100.0, 2)
    pct_eligible = np.round(pct_strong + pct_mod, 2)

    df_elig = pd.DataFrame({
        "player_id": meta[id_col],
        "player_name": meta[name_col],
        "primary_role": meta[role_col],
        "pct_strong_evidence": pct_strong,
        "pct_moderate_evidence": pct_mod,
        "pct_insufficient_evidence": pct_insuff,
        "pct_not_eligible": pct_not_elig,
        "pct_leaderboard_eligible": pct_eligible,
        "total_replicates": n_reps
    })
    return df_elig.sort_values("pct_leaderboard_eligible", ascending=False).reset_index(drop=True)
