"""
src/player_squad_fit.py
SupeRR Selector - Player Squad-Fit & Recruitment Candidate Evaluation Module

This module constructs the player recruitment pool and evaluates candidates across
five transparent, decoupled dimensions:
1. Historical Performance (Module 5 Performance Rating: PR)
2. Evidence Quality (Module 5 Evidence Reliability Score: ERS & bootstrap eligibility)
3. Statistical Stability (Module 6 CI width, rank volatility, HHI, and LOMO resilience: SSS)
4. Tactical Squad Fit (Rajasthan Royals role gap criticality and phase execution: TFS)
5. Acquisition Risk (Sample-size fragility, volatility, and overseas slot constraints: ARS)

It also assigns recruitment archetypes and runs alternative-weight sensitivity scenarios.

Author: Syed Mohammad Hamzah (B.Tech CSE - Data Analytics)
Evaluator Reference: Rajasthan Royals Sports Analytics Challenge (Season 2)
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional

from src.squad_context import load_t20i_nationality_mapping
from src.squad_gap_analysis import (
    RR_TACTICAL_GAP_WEIGHTS,
    load_player_context_dictionaries,
    classify_batting_tactical_role,
    classify_bowling_tactical_role
)
from src.influence_analysis import (
    calculate_batter_match_concentration,
    calculate_bowler_match_concentration
)


def resolve_path(rel_path: str) -> str:
    if os.path.exists(rel_path):
        return rel_path
    parent_path = os.path.join("..", rel_path)
    if os.path.exists(parent_path):
        return parent_path
    return rel_path


def get_player_origin_and_overseas(
    pid: int,
    t20i_dict: Dict[int, str],
    m_comp: pd.DataFrame
) -> Tuple[str, bool]:
    """
    Determines verified country origin and overseas flag for an individual player.
    Special cases:
      - 161: Dwayne Bravo (West Indies, Overseas)
      - 88: Faf du Plessis (South Africa, Overseas)
      - 781: Sunil Narine (West Indies, Overseas)
      - All other IPL-only players without non-India T20I matches: India (Domestic)
    """
    # Special retired overseas veterans in IPL
    if pid == 161:
        return "West Indies", True
    if pid == 88:
        return "South Africa", True
    if pid == 781:
        return "West Indies", True

    nat = t20i_dict.get(pid, None)
    if nat is not None:
        if nat == "India":
            return "India", False
        return nat, True

    # Check competition records
    sub = m_comp[m_comp["player_id"] == pid]
    teams = set(sub["team_name"].unique())
    
    if "India A" in teams:
        return "India", False
    if "Pakistan A" in teams:
        return "Pakistan", True
    if "Bangladesh A" in teams:
        return "Bangladesh", True
    if "Sri Lanka A" in teams:
        return "Sri Lanka", True
    if "Afghanistan A" in teams:
        return "Afghanistan", True

    # Check if they only played in IPL
    return "India (Domestic)", False


def build_candidate_recruitment_pool(
    discipline: str = "Batting",
    data_pack_dir: str = "Data Pack"
) -> pd.DataFrame:
    """
    Constructs the master recruitment candidate dataset by joining Module 5 rankings,
    Module 6 uncertainty/stability/influence outputs, nationality data, and tactical roles.
    """
    # Load required tables
    data_pack_resolved = resolve_path(data_pack_dir)
    mapping_path = os.path.join(data_pack_resolved, "competition_team_player_mapping.csv")
    comps_path = os.path.join(data_pack_resolved, "competitions.csv")
    mapping = pd.read_csv(mapping_path)
    comps = pd.read_csv(comps_path)
    m_comp = mapping.merge(comps[["comp_id", "match_format"]], on="comp_id")
    t20i_dict = load_t20i_nationality_mapping(data_pack_resolved)
    
    bbb_pressure = pd.read_parquet(resolve_path(os.path.join("data", "processed", "ball_by_ball_pressure.parquet")))
    infl = pd.read_parquet(resolve_path(os.path.join("data", "processed", "match_influence_analysis.parquet")))
    
    wk_set, order_map, ps_map, bowl_balls, bat_balls, b_eligible, bw_eligible = load_player_context_dictionaries(data_pack_resolved)

    if discipline == "Batting":
        rankings = pd.read_csv(resolve_path(os.path.join("data", "processed", "batter_player_rankings.csv")))
        unc = pd.read_parquet(resolve_path(os.path.join("data", "processed", "batter_rating_uncertainty.parquet")))
        stab = pd.read_parquet(resolve_path(os.path.join("data", "processed", "batter_ranking_stability.parquet")))
        conc = calculate_batter_match_concentration(bbb_pressure, rankings)
        
        # Merge uncertainty & stability
        df = rankings.merge(
            unc[["player_id", "bootstrap_mean_rating", "rating_std", "rating_p025", "rating_p975", "rating_ci_width"]],
            on="player_id", how="left"
        ).merge(
            stab[["player_id", "bootstrap_mean_rank", "rank_std", "top5_freq_pct", "top10_freq_pct", "top20_freq_pct", "eligibility_pct"]],
            on="player_id", how="left"
        ).merge(
            conc[["player_id", "clutch_volume_hhi", "top_match_run_share", "clutch_matches_count"]],
            on="player_id", how="left"
        )
        
        # Merge influence
        sub_infl = infl[infl["discipline"] == "Batting"][["player_id", "rating_shift", "rank_shift", "resilience_category"]]
        df = df.merge(sub_infl, on="player_id", how="left")
        df["resilience_category"] = df["resilience_category"].fillna("Sustained / Resilient")
        df["rating_shift"] = df["rating_shift"].fillna(0.0)
        df["rank_shift"] = df["rank_shift"].fillna(0)
        
        # Tactical Role
        b_ratings = pd.read_parquet(resolve_path(os.path.join("data", "processed", "batter_player_ratings.parquet")))
        b_map = b_ratings.set_index("striker_id")["primary_role"].to_dict()
        df["tactical_role"] = [
            classify_batting_tactical_role(pid, str(b_map.get(pid, "Lower Order")), wk_set, order_map, bowl_balls, bw_eligible)
            for pid in df["player_id"]
        ]
        
    else:  # Bowling
        rankings = pd.read_csv(resolve_path(os.path.join("data", "processed", "bowler_player_rankings.csv")))
        unc = pd.read_parquet(resolve_path(os.path.join("data", "processed", "bowler_rating_uncertainty.parquet")))
        stab = pd.read_parquet(resolve_path(os.path.join("data", "processed", "bowler_ranking_stability.parquet")))
        conc = calculate_bowler_match_concentration(bbb_pressure, rankings)
        
        df = rankings.merge(
            unc[["player_id", "bootstrap_mean_rating", "rating_std", "rating_p025", "rating_p975", "rating_ci_width"]],
            on="player_id", how="left"
        ).merge(
            stab[["player_id", "bootstrap_mean_rank", "rank_std", "top5_freq_pct", "top10_freq_pct", "top20_freq_pct", "eligibility_pct"]],
            on="player_id", how="left"
        ).merge(
            conc[["player_id", "clutch_volume_hhi", "top_match_wkt_share", "clutch_matches_count"]],
            on="player_id", how="left"
        )
        
        sub_infl = infl[infl["discipline"] == "Bowling"][["player_id", "rating_shift", "rank_shift", "resilience_category"]]
        df = df.merge(sub_infl, on="player_id", how="left")
        df["resilience_category"] = df["resilience_category"].fillna("Sustained / Resilient")
        df["rating_shift"] = df["rating_shift"].fillna(0.0)
        df["rank_shift"] = df["rank_shift"].fillna(0)
        
        # Tactical Role
        bw_ratings = pd.read_parquet(resolve_path(os.path.join("data", "processed", "bowler_player_ratings.parquet")))
        b_ratings = pd.read_parquet(resolve_path(os.path.join("data", "processed", "batter_player_ratings.parquet")))
        bw_map = bw_ratings.set_index("bowler_id")["primary_bowling_role"].to_dict()
        b_map = b_ratings.set_index("striker_id")["primary_role"].to_dict()
        
        df["tactical_role"] = [
            classify_bowling_tactical_role(
                pid, str(bw_map.get(pid, "Middle Enforcer")), str(b_map.get(pid, "Lower Order")),
                order_map, ps_map, bat_balls, bowl_balls, b_eligible, bw_eligible
            )
            for pid in df["player_id"]
        ]

    # Nationality
    origins = [get_player_origin_and_overseas(pid, t20i_dict, m_comp) for pid in df["player_id"]]
    df["country"] = [o[0] for o in origins]
    df["is_overseas"] = [o[1] for o in origins]
    df["discipline"] = discipline

    return df


def calculate_candidate_squad_fit_scores(
    df_pool: pd.DataFrame,
    discipline: str = "Batting"
) -> pd.DataFrame:
    """
    Computes decoupled evaluation scores across the 5 dimensions:
    1. Historical Performance (PR)
    2. Evidence Quality (ERS)
    3. Statistical Stability Score (SSS)
    4. Tactical Squad Fit Score (TFS)
    5. Acquisition Risk Score (ARS)
    Along with the overall Recruitment Decision Heuristic (RDH) and Player Archetypes.
    """
    df = df_pool.copy()
    
    # 1. Performance Rating (PR) & Evidence Reliability Score (ERS)
    pr = df["performance_rating"].astype(float)
    ers = df["evidence_reliability_score"].astype(float)
    
    # 2. Statistical Stability Score (SSS in [0.0, 100.0])
    # Components: CI width, top20 retention, HHI, LOMO drop
    s_ci = np.clip(100.0 - (df["rating_ci_width"].fillna(50.0) / 80.0) * 100.0, 0.0, 100.0)
    s_ret = np.clip(df["top20_freq_pct"].fillna(50.0), 0.0, 100.0)
    s_hhi = np.clip(100.0 - ((df["clutch_volume_hhi"].fillna(0.25) - 0.04) / 0.50) * 100.0, 0.0, 100.0)
    s_lomo = np.clip(100.0 - (df["rating_shift"].abs().fillna(5.0) / 30.0) * 100.0, 0.0, 100.0)
    
    sss = (0.35 * s_ci + 0.30 * s_ret + 0.20 * s_hhi + 0.15 * s_lomo).round(2)
    df["statistical_stability_score"] = sss
    
    # 3. Tactical Squad Fit Score (TFS in [0.0, 100.0])
    # S_gap: Rajasthan Royals role criticality
    s_gap = df["tactical_role"].map(RR_TACTICAL_GAP_WEIGHTS).fillna(50.0)
    
    # S_phase: Clutch execution strength
    if discipline == "Batting":
        # Clutch scoring rate and boundary %
        sr_c = df["sr_clutch"].fillna(130.0)
        bnd_c = df["bnd_pct_clutch"].fillna(15.0)
        s_phase = np.clip(((sr_c - 100.0) / 100.0) * 60.0 + (bnd_c / 35.0) * 40.0, 0.0, 100.0)
    else:
        # Phase adjusted delta economy and dot %
        delta_e = df["delta_econ_phase_adj"].fillna(0.0)
        dot_c = df["true_dot_pct_clutch"].fillna(35.0)
        s_phase = np.clip(((delta_e + 2.0) / 5.0) * 60.0 + (dot_c / 50.0) * 40.0, 0.0, 100.0)
        
    # S_flexibility: All-rounder / multi-role bonus
    s_flex = np.where(
        df["tactical_role"].str.contains("All-Rounder", case=False), 100.0,
        np.where(df["tactical_role"].str.contains("All-Phase", case=False), 75.0, 50.0)
    )
    
    # S_overseas_fit: Domestic players get full 100; overseas players scaled by role urgency
    s_overseas_fit = np.where(
        ~df["is_overseas"], 100.0,
        np.clip(s_gap * 0.90, 30.0, 90.0)
    )
    
    tfs = (0.40 * s_gap + 0.30 * s_phase + 0.15 * s_flex + 0.15 * s_overseas_fit).round(2)
    df["tactical_squad_fit_score"] = tfs
    
    # 4. Acquisition Risk Score (ARS in [0.0, 100.0])
    # Higher ARS = more risky. Lower ARS = dependable asset.
    elig_penalty = 100.0 - df["eligibility_pct"].fillna(50.0)
    stab_penalty = 100.0 - sss
    
    spike_penalty = np.where(
        df["resilience_category"] == "Match-Dependent Spike", 100.0,
        np.where(df["resilience_category"] == "Moderately Influenced", 45.0, 0.0)
    )
    slot_penalty = np.where(df["is_overseas"], 40.0, 0.0)
    
    ars = (0.35 * elig_penalty + 0.30 * stab_penalty + 0.20 * spike_penalty + 0.15 * slot_penalty).round(2)
    df["acquisition_risk_score"] = ars
    
    # 5. Recruitment Decision Heuristic (RDH in [0.0, 100.0])
    # Baseline: 30% PR + 20% ERS + 20% SSS + 20% TFS - 10% ARS
    rdh = (0.30 * pr + 0.20 * ers + 0.20 * sss + 0.20 * tfs - 0.10 * ars).round(2)
    df["recruitment_decision_score"] = np.clip(rdh, 0.0, 100.0)
    
    # 6. Assign Recruitment Archetypes
    def assign_archetype(row: pd.Series) -> str:
        p = row["performance_rating"]
        e = row["evidence_reliability_score"]
        s = row["statistical_stability_score"]
        res = row["resilience_category"]
        role = row["tactical_role"]
        
        if role in ["Opening Batter"] and row["tactical_squad_fit_score"] < 50.0:
            return "Redundant Role Profile"
        if res == "Match-Dependent Spike" or s < 45.0:
            return "High-Ceiling, High-Volatility Performer"
        if "All-Rounder" in role:
            return "Multi-Role Tactical Option"
        if role in ["Death-Overs Specialist", "New-Ball / Powerplay Fast Bowler", "Finisher"]:
            if s >= 60.0:
                return "Specialist Phase Performer"
        if p >= 70.0 and e >= 60.0 and s >= 60.0:
            return "Reliable Campaign Performer"
        if p >= 75.0 and e < 60.0:
            return "Emerging High-Upside Prospect"
        if e < 40.0:
            return "Insufficient Evidence"
        return "Reliable Campaign Performer"

    df["player_archetype"] = df.apply(assign_archetype, axis=1)

    # 7. Recruitment Priority (incorporating authoritative candidate governance)
    rr_baseline_path = resolve_path(os.path.join("data", "processed", "rr_squad_baseline_2026.parquet"))
    rr_pids = set(pd.read_parquet(rr_baseline_path)["player_id"]) if os.path.exists(rr_baseline_path) else set()

    def assign_priority(row: pd.Series) -> str:
        arch = row["player_archetype"]
        rds = row["recruitment_decision_score"]
        risk = row["acquisition_risk_score"]
        country = row.get("country", "")
        pid = row.get("player_id", 0)
        
        # Governance segregation: Non-actionable benchmarks & internal assets
        if country == "Pakistan":
            return "Strategic Benchmark (BCCI Ineligible)"
        if pid in rr_pids:
            return "Internal Asset (Retention Candidate)"
        if pid in [143]:
            return "Strategic Benchmark (Retired)"
        if pid in [2933, 1699, 781, 4708]:
            return "Strategic Benchmark (Rival Core)"
        
        # Actionable auction recruitment targets
        if arch == "Redundant Role Profile":
            return "Low Priority (Redundant)"
        if arch in ["Reliable Campaign Performer", "Specialist Phase Performer", "Multi-Role Tactical Option"] and rds >= 70.0 and risk <= 40.0:
            return "High Priority"
        if rds >= 60.0:
            return "Medium Priority"
        if arch == "Emerging High-Upside Prospect":
            return "Watchlist / Emerging"
        if arch == "High-Ceiling, High-Volatility Performer":
            return "Caution / Volatile"
        return "Low Priority"

    df["recommendation_priority"] = df.apply(assign_priority, axis=1)

    return df.sort_values(by="recruitment_decision_score", ascending=False).reset_index(drop=True)


def run_alternative_weight_scenarios(
    df_evaluated: pd.DataFrame
) -> pd.DataFrame:
    """
    Stress-tests candidate rankings across 3 distinct recruitment philosophies:
    1. Balanced_Recruitment: (30% PR, 20% ERS, 20% SSS, 20% TFS, -10% ARS)
    2. Stability_First: (20% PR, 25% ERS, 30% SSS, 15% TFS, -10% ARS)
    3. Tactical_Gap_Priority: (25% PR, 15% ERS, 15% SSS, 35% TFS, -10% ARS)
    """
    df = df_evaluated.copy()
    
    pr = df["performance_rating"]
    ers = df["evidence_reliability_score"]
    sss = df["statistical_stability_score"]
    tfs = df["tactical_squad_fit_score"]
    ars = df["acquisition_risk_score"]
    
    # Compute scenario scores
    df["score_balanced"] = np.clip(0.30 * pr + 0.20 * ers + 0.20 * sss + 0.20 * tfs - 0.10 * ars, 0.0, 100.0).round(2)
    df["score_stability_first"] = np.clip(0.20 * pr + 0.25 * ers + 0.30 * sss + 0.15 * tfs - 0.10 * ars, 0.0, 100.0).round(2)
    df["score_gap_priority"] = np.clip(0.25 * pr + 0.15 * ers + 0.15 * sss + 0.35 * tfs - 0.10 * ars, 0.0, 100.0).round(2)
    
    df["rank_balanced"] = df["score_balanced"].rank(ascending=False, method="min").astype(int)
    df["rank_stability_first"] = df["score_stability_first"].rank(ascending=False, method="min").astype(int)
    df["rank_gap_priority"] = df["score_gap_priority"].rank(ascending=False, method="min").astype(int)
    
    df["max_rank_shift"] = df[["rank_balanced", "rank_stability_first", "rank_gap_priority"]].max(axis=1) - df[["rank_balanced", "rank_stability_first", "rank_gap_priority"]].min(axis=1)
    
    return df
