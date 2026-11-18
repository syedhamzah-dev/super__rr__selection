"""
src/squad_gap_analysis.py
SupeRR Selector - Rajasthan Royals Squad Composition & Tactical Gap Analysis Module

This module conducts a forensic role audit of the Rajasthan Royals squad:
1. Implements a 12-role tactical framework covering 6 batting and 6 bowling roles.
2. Maps players into roles using verified scorecard positions, ball-by-ball delivery types,
   and wicketkeeping designations.
3. Audits squad depth across retention scenarios (Scenario A, B, C).
4. Quantifies role gap criticality, overseas dependencies, and squad balance.

Author: Syed Mohammad Hamzah (B.Tech CSE - Data Analytics)
Evaluator Reference: Rajasthan Royals Sports Analytics Challenge (Season 2)
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional

from src.squad_context import (
    get_rr_2026_baseline_squad,
    get_squad_retention_scenarios,
    OFFICIAL_IPL_RULES
)

# 12-Role Tactical Framework Specification
TACTICAL_BATTING_ROLES = [
    "Opening Batter",
    "Top-Order Batter",
    "Middle-Order Batter",
    "Finisher",
    "Wicketkeeper-Batter",
    "Batting All-Rounder"
]

TACTICAL_BOWLING_ROLES = [
    "New-Ball / Powerplay Fast Bowler",
    "Middle-Overs Spinner",
    "Middle-Overs Pace Option",
    "Death-Overs Specialist",
    "All-Phase Bowler",
    "Bowling All-Rounder"
]

# Tactical Gap Criticality Weights for Rajasthan Royals Ahead of IPL 2027
# Scale 0.0 to 100.0 (Higher = more urgent squad requirement)
RR_TACTICAL_GAP_WEIGHTS = {
    # Batting gaps
    "Finisher": 100.0,                  # Critical Void: Hetmyer dropped to 105 SR; Ferreira consumes overseas slot
    "Middle-Order Batter": 80.0,        # Limited Depth: Parag carries bulk; lack of secondary domestic power
    "Wicketkeeper-Batter": 70.0,        # Limited Backup: Jurel is elite starter, but 0 viable Indian backup keepers
    "Batting All-Rounder": 65.0,        # Moderate Depth: Parag/Jadeja present, but need lower-order power depth
    "Top-Order Batter": 40.0,           # Adequate Depth: Jurel/Parag/Pretorius provide top-order coverage
    "Opening Batter": 30.0,             # Adequate Depth: Jaiswal + Sooryavanshi form dominant young opening pair
    
    # Bowling gaps
    "Death-Overs Specialist": 100.0,     # Critical Void: Archer is solo; secondary death conceded 11.4+ RPO
    "Middle-Overs Spinner": 85.0,       # High Priority: Bishnoi conceded 9.88 RPO; need attacking wicket threat
    "Bowling All-Rounder": 75.0,        # High Priority: Need multi-phase pace/spin all-rounders to lengthen batting
    "All-Phase Bowler": 70.0,           # High Priority: Relieves Archer from carrying multiple crisis phases
    "New-Ball / Powerplay Fast Bowler": 60.0, # Moderate Depth: Archer/Burger/Sandeep cover initial overs
    "Middle-Overs Pace Option": 50.0    # Moderate Depth: Covered by domestic pace backups
}


def resolve_path(rel_path: str) -> str:
    if os.path.exists(rel_path):
        return rel_path
    parent_path = os.path.join("..", rel_path)
    if os.path.exists(parent_path):
        return parent_path
    return rel_path


def load_player_context_dictionaries(
    data_pack_dir: str = "Data Pack"
) -> Tuple[set, Dict[int, float], Dict[int, str], Dict[int, int], Dict[int, int], set, set]:
    """
    Loads lookup dictionaries from raw and processed tables for exact role mapping.
    """
    p11_path = resolve_path(os.path.join("data", "processed", "playing_eleven_clean.parquet"))
    bbb_path = resolve_path(os.path.join("data", "processed", "ball_by_ball_state.parquet"))
    b_ratings_path = resolve_path(os.path.join("data", "processed", "batter_player_ratings.parquet"))
    bw_ratings_path = resolve_path(os.path.join("data", "processed", "bowler_player_ratings.parquet"))

    p11 = pd.read_parquet(p11_path)
    bbb = pd.read_parquet(bbb_path)
    b_ratings = pd.read_parquet(b_ratings_path)
    bw_ratings = pd.read_parquet(bw_ratings_path)

    # Wicketkeeper set
    wk_set = set(p11[p11["is_wk"] == True]["player_id"])

    # Average batting order
    order_map = p11[p11["is_played"] == 1].groupby("player_id")["batting_order"].mean().to_dict()

    # Bowler pace or spin
    ps_df = bbb[["bowler_id", "pace_or_spin"]].dropna().drop_duplicates(subset=["bowler_id"])
    ps_map = ps_df.set_index("bowler_id")["pace_or_spin"].to_dict()

    # Volume totals
    bowl_balls = bbb.groupby("bowler_id")["is_legal_ball"].sum().to_dict()
    bat_balls = bbb[bbb["extras_type"] != "wide"].groupby("striker_id")["is_legal_ball"].count().to_dict()

    # Eligible sets
    b_eligible = set(b_ratings[b_ratings["is_eligible_for_ranking"]]["striker_id"])
    bw_eligible = set(bw_ratings[bw_ratings["is_eligible_for_ranking"]]["bowler_id"])

    return wk_set, order_map, ps_map, bowl_balls, bat_balls, b_eligible, bw_eligible


def classify_batting_tactical_role(
    player_id: int,
    primary_role: str,
    wk_set: set,
    order_map: Dict[int, float],
    bowl_balls: Dict[int, int],
    bw_eligible: set
) -> str:
    """
    Classifies a player into one of the 6 tactical batting roles or Tailender.
    """
    if primary_role == "Lower Order":
        return "Tailender / Lower Order"

    is_wk = player_id in wk_set
    avg_order = order_map.get(player_id, np.nan)
    has_bowl_rating = player_id in bw_eligible
    balls_bowled = bowl_balls.get(player_id, 0)

    if is_wk:
        return "Wicketkeeper-Batter"
    if (has_bowl_rating or balls_bowled >= 60) and primary_role in ["Top Order", "Middle Order", "Finisher"]:
        return "Batting All-Rounder"
    if primary_role == "Top Order":
        if not np.isnan(avg_order) and avg_order <= 2.2:
            return "Opening Batter"
        return "Top-Order Batter"
    if primary_role == "Middle Order":
        return "Middle-Order Batter"
    if primary_role == "Finisher":
        return "Finisher"
    return "Tailender / Lower Order"


def classify_bowling_tactical_role(
    player_id: int,
    primary_bowling_role: str,
    primary_bat_role: str,
    order_map: Dict[int, float],
    ps_map: Dict[int, str],
    bat_balls: Dict[int, int],
    bowl_balls: Dict[int, int],
    b_eligible: set,
    bw_eligible: set
) -> str:
    """
    Classifies a player into one of the 6 tactical bowling roles or Non-Bowler.
    """
    balls_bowled = bowl_balls.get(player_id, 0)
    if balls_bowled < 18 and player_id not in bw_eligible:
        return "Non-Bowler / Pure Batter"

    avg_order = order_map.get(player_id, np.nan)
    ps = ps_map.get(player_id, "Pace")
    has_bat_rating = player_id in b_eligible
    bf = bat_balls.get(player_id, 0)

    # Bowling all-rounder: recognized bowler who can bat effectively in top 8
    if (has_bat_rating or bf >= 60) and (not np.isnan(avg_order) and avg_order <= 8.5) and primary_bat_role in ["Middle Order", "Finisher", "Lower Order"]:
        if primary_bowling_role in ["Death Specialist", "Powerplay Specialist", "Middle Enforcer", "All-Phase Bowler"]:
            return "Bowling All-Rounder"

    if primary_bowling_role == "Death Specialist":
        return "Death-Overs Specialist"
    if primary_bowling_role == "All-Phase Bowler":
        return "All-Phase Bowler"
    if primary_bowling_role == "Powerplay Specialist" and ps == "Pace":
        return "New-Ball / Powerplay Fast Bowler"
    if ps == "Spin":
        return "Middle-Overs Spinner"
    return "Middle-Overs Pace Option"


def audit_rr_squad_by_roles(
    squad_df: pd.DataFrame,
    data_pack_dir: str = "Data Pack"
) -> pd.DataFrame:
    """
    Audits the Rajasthan Royals squad by assigning each player their tactical batting and bowling roles.
    """
    wk_set, order_map, ps_map, bowl_balls, bat_balls, b_eligible, bw_eligible = load_player_context_dictionaries(data_pack_dir)
    
    b_ratings = pd.read_parquet(resolve_path(os.path.join("data", "processed", "batter_player_ratings.parquet")))
    bw_ratings = pd.read_parquet(resolve_path(os.path.join("data", "processed", "bowler_player_ratings.parquet")))
    
    b_sub = b_ratings[["striker_id", "primary_role", "performance_rating"]].rename(
        columns={"striker_id": "player_id", "primary_role": "b_primary_role", "performance_rating": "bat_rating"}
    )
    bw_sub = bw_ratings[["bowler_id", "primary_bowling_role", "performance_rating"]].rename(
        columns={"bowler_id": "player_id", "primary_bowling_role": "bw_primary_role", "performance_rating": "bowl_rating"}
    )
    
    squad = squad_df.merge(b_sub, on="player_id", how="left").merge(bw_sub, on="player_id", how="left")
    squad["b_primary_role"] = squad["b_primary_role"].fillna("Lower Order")
    squad["bw_primary_role"] = squad["bw_primary_role"].fillna("Middle Enforcer")
    
    bat_roles = []
    bowl_roles = []
    for _, row in squad.iterrows():
        pid = int(row["player_id"])
        prole = str(row["b_primary_role"])
        pb_role = str(row["bw_primary_role"])
        
        brole = classify_batting_tactical_role(pid, prole, wk_set, order_map, bowl_balls, bw_eligible)
        bwrole = classify_bowling_tactical_role(pid, pb_role, prole, order_map, ps_map, bat_balls, bowl_balls, b_eligible, bw_eligible)
        
        bat_roles.append(brole)
        bowl_roles.append(bwrole)
        
    squad["tactical_bat_role"] = bat_roles
    squad["tactical_bowl_role"] = bowl_roles
    return squad


def evaluate_squad_gaps(
    squad_df: pd.DataFrame,
    scenario_key: str = "Scenario_A_Core_Continuity"
) -> pd.DataFrame:
    """
    Computes role-by-role coverage and tactical gap status for a given squad.
    """
    scenarios = get_squad_retention_scenarios()
    scen = scenarios.get(scenario_key, scenarios["Scenario_A_Core_Continuity"])
    retained_ids = set(scen["retained_player_ids"])
    
    # Filter squad for retained players if analyzing retention scenario
    active_squad = squad_df[squad_df["player_id"].isin(retained_ids)].copy()
    
    records = []
    
    # 1. Evaluate Batting Roles
    for role in TACTICAL_BATTING_ROLES:
        sub = active_squad[active_squad["tactical_bat_role"] == role]
        count_total = len(sub)
        count_domestic = len(sub[~sub["is_overseas"]])
        count_overseas = len(sub[sub["is_overseas"]])
        player_names = ", ".join(sub["player_name"].tolist()) if count_total > 0 else "None"
        
        gap_weight = RR_TACTICAL_GAP_WEIGHTS.get(role, 50.0)
        
        # Depth assessment
        if count_total >= 2:
            depth_status = "Adequate Depth"
            gap_severity = "Low"
        elif count_total == 1:
            depth_status = "Limited Depth"
            gap_severity = "Moderate" if gap_weight < 80 else "High"
        else:
            depth_status = "Critical Void / No Credible Backup"
            gap_severity = "Critical"
            
        records.append({
            "discipline": "Batting",
            "tactical_role": role,
            "squad_count_total": count_total,
            "squad_count_domestic": count_domestic,
            "squad_count_overseas": count_overseas,
            "players_in_role": player_names,
            "depth_status": depth_status,
            "gap_criticality_weight": gap_weight,
            "gap_severity": gap_severity,
            "scenario": scen["name"]
        })
        
    # 2. Evaluate Bowling Roles
    for role in TACTICAL_BOWLING_ROLES:
        sub = active_squad[active_squad["tactical_bowl_role"] == role]
        count_total = len(sub)
        count_domestic = len(sub[~sub["is_overseas"]])
        count_overseas = len(sub[sub["is_overseas"]])
        player_names = ", ".join(sub["player_name"].tolist()) if count_total > 0 else "None"
        
        gap_weight = RR_TACTICAL_GAP_WEIGHTS.get(role, 50.0)
        
        if count_total >= 2:
            depth_status = "Adequate Depth"
            gap_severity = "Low"
        elif count_total == 1:
            depth_status = "Limited Depth"
            gap_severity = "Moderate" if gap_weight < 80 else "High"
        else:
            depth_status = "Critical Void / No Credible Backup"
            gap_severity = "Critical"
            
        records.append({
            "discipline": "Bowling",
            "tactical_role": role,
            "squad_count_total": count_total,
            "squad_count_domestic": count_domestic,
            "squad_count_overseas": count_overseas,
            "players_in_role": player_names,
            "depth_status": depth_status,
            "gap_criticality_weight": gap_weight,
            "gap_severity": gap_severity,
            "scenario": scen["name"]
        })
        
    return pd.DataFrame(records)
