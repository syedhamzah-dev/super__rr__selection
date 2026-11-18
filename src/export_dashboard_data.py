"""
SupeRR Selector - Module 8 Dashboard Data Exporter (Audited & Reconciled)
Exports verified Parquet and CSV outputs from Modules 1-7 into clean,
structured, lightweight JSON files and an offline JS bundle for the interactive dashboard.
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd

def resolve_path(relative_path: str) -> Path:
    p = Path(relative_path)
    if p.exists():
        return p
    p_parent = Path("..") / relative_path
    if p_parent.exists():
        return p_parent
    return p

def sanitize_for_json(obj):
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, float, np.float64, np.float32)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return round(float(obj), 2)
    elif isinstance(obj, (np.ndarray, list)):
        return [sanitize_for_json(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif pd.isna(obj):
        return None
    return obj

def parse_evidence_tier(tier_val) -> tuple[str, str]:
    tier_str = str(tier_val)
    if "Strong" in tier_str:
        return "Strong", "Strong Evidence"
    elif "Moderate" in tier_str:
        return "Moderate", "Moderate Evidence"
    elif "Insufficient" in tier_str:
        return "Insufficient", "Insufficient Evidence"
    else:
        return "Not_Eligible", "Not Eligible"

def export_dashboard_data(output_dir: str = "dashboard/data"):
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    print(f"Exporting reconciled dashboard data to: {out_path.resolve()}")

    # 1. Load Audited Squad Baseline to get RR Player IDs
    rr_baseline_df = pd.read_parquet(resolve_path("data/processed/rr_squad_baseline_2026.parquet"))
    rr_pids = set(rr_baseline_df["player_id"].tolist())

    # Governance Classifier
    def get_governance(pid: int, country: str):
        if pid in rr_pids:
            return "Existing RR Player (Internal Asset)", "Existing RR Squad Member (Internal Retention / Roster Core)"
        if country == "Pakistan":
            return "Strategic Benchmark (BCCI Ineligible)", "Ineligible for IPL Auction (BCCI Policy Restriction; Global Role Model)"
        if pid in [143]:
            return "Strategic Benchmark (Retired)", "Retired from IPL Competition (Historical Reference Benchmark)"
        if pid in [2933, 1699, 781, 4708]:
            return "Strategic Benchmark (Rival Core)", "Conditional on Release (Rival Franchise Core Asset; Comparative Benchmark)"
        return "Viable Auction Target", "Potential Auction Candidate (Availability unconfirmed; conditional on official IPL 2027 player registration)"

    # 2. Export Batters Data (304 eligible batters)
    b_df = pd.read_parquet(resolve_path("data/processed/batter_squad_fit_evaluations.parquet"))
    batters_list = []
    for _, row in b_df.iterrows():
        pid = int(row["player_id"])
        country = str(row["country"])
        cat, avail = get_governance(pid, country)
        tier_code, tier_label = parse_evidence_tier(row["evidence_tier"])
        
        b_item = {
            "rank": int(row["rank"]),
            "player_id": pid,
            "player_name": str(row["player_name"]),
            "country": country,
            "is_overseas": bool(row["is_overseas"]),
            "primary_role": str(row["primary_role"]),
            "tactical_role": str(row["tactical_role"]),
            "player_archetype": str(row.get("player_archetype", "Standard Batter")),
            "performance_rating": round(float(row["performance_rating"]), 2),
            "evidence_reliability_score": round(float(row["evidence_reliability_score"]), 2),
            "evidence_tier": tier_code,
            "evidence_tier_label": tier_label,
            "matches_played": int(row["matches_played"]),
            "comps_played": int(row["comps_played"]),
            # Overall
            "bf_overall": int(row["bf_overall"]),
            "runs_overall": int(row["runs_overall"]),
            "sr_overall": round(float(row["sr_overall"]), 2),
            # Clutch
            "bf_clutch": int(row["bf_clutch"]),
            "runs_clutch": int(row["runs_clutch"]),
            "sr_clutch": round(float(row["sr_clutch"]), 2),
            "bnd_pct_clutch": round(float(row["bnd_pct_clutch"]), 2),
            "dot_pct_clutch": round(float(row["dot_pct_clutch"]), 2),
            "rpd_clutch": round(float(row["rpd_clutch"]), 2),
            "batting_clutch_index": round(float(row["batting_clutch_index"]), 2),
            # Robustness
            "bootstrap_mean_rating": round(float(row["bootstrap_mean_rating"]), 2),
            "rating_std": round(float(row["rating_std"]), 2),
            "rating_p025": round(float(row["rating_p025"]), 2),
            "rating_p975": round(float(row["rating_p975"]), 2),
            "rating_ci_width": round(float(row["rating_ci_width"]), 2),
            "bootstrap_mean_rank": round(float(row["bootstrap_mean_rank"]), 1),
            "rank_std": round(float(row["rank_std"]), 2),
            "top5_freq_pct": round(float(row["top5_freq_pct"]), 2),
            "top10_freq_pct": round(float(row["top10_freq_pct"]), 2),
            "top20_freq_pct": round(float(row["top20_freq_pct"]), 2),
            "eligibility_pct": round(float(row["eligibility_pct"]), 2),
            "clutch_volume_hhi": round(float(row["clutch_volume_hhi"]), 4),
            "top_match_run_share": round(float(row["top_match_run_share"]), 2),
            "lomo_rating_shift": round(float(row["rating_shift"]), 2),
            "resilience_category": str(row["resilience_category"]),
            # Squad Fit & Decision
            "statistical_stability_score": round(float(row["statistical_stability_score"]), 2),
            "tactical_squad_fit_score": round(float(row["tactical_squad_fit_score"]), 2),
            "acquisition_risk_score": round(float(row["acquisition_risk_score"]), 2),
            "recruitment_decision_score": round(float(row["recruitment_decision_score"]), 2),
            "recommendation_priority": str(row["recommendation_priority"]),
            "candidate_category": cat,
            "availability_status": avail,
            # Sensitivity
            "score_balanced": round(float(row["score_balanced"]), 2),
            "score_stability_first": round(float(row["score_stability_first"]), 2),
            "score_gap_priority": round(float(row["score_gap_priority"]), 2),
            "rank_balanced": int(row["rank_balanced"]),
            "rank_stability_first": int(row["rank_stability_first"]),
            "rank_gap_priority": int(row["rank_gap_priority"]),
        }
        batters_list.append(b_item)

    with open(out_path / "batters_data.json", "w", encoding="utf-8") as f:
        json.dump(batters_list, f, indent=2)
    print(f" -> Exported batters_data.json ({len(batters_list)} batters)")

    # 3. Export Bowlers Data (290 eligible bowlers)
    bw_df = pd.read_parquet(resolve_path("data/processed/bowler_squad_fit_evaluations.parquet"))
    bowlers_list = []
    for _, row in bw_df.iterrows():
        pid = int(row["player_id"])
        country = str(row["country"])
        cat, avail = get_governance(pid, country)
        tier_code, tier_label = parse_evidence_tier(row["evidence_tier"])
        
        bw_item = {
            "rank": int(row["rank"]),
            "player_id": pid,
            "player_name": str(row["player_name"]),
            "country": country,
            "is_overseas": bool(row["is_overseas"]),
            "primary_bowling_role": str(row["primary_bowling_role"]),
            "tactical_role": str(row["tactical_role"]),
            "player_archetype": str(row.get("player_archetype", "Standard Bowler")),
            "performance_rating": round(float(row["performance_rating"]), 2),
            "evidence_reliability_score": round(float(row["evidence_reliability_score"]), 2),
            "evidence_tier": tier_code,
            "evidence_tier_label": tier_label,
            "matches_played": int(row["matches_played"]),
            "comps_played": int(row["comps_played"]),
            # Overall
            "legal_balls_overall": int(row["legal_balls_overall"]),
            "economy_overall": round(float(row["economy_overall"]), 2),
            "wickets_overall": int(row["wickets_overall"]),
            # Clutch
            "legal_balls_clutch": int(row["legal_balls_clutch"]),
            "economy_clutch": round(float(row["economy_clutch"]), 2),
            "wickets_clutch": int(row["wickets_clutch"]),
            "delta_econ_phase_adj": round(float(row["delta_econ_phase_adj"]), 2),
            "true_dot_pct_clutch": round(float(row["true_dot_pct_clutch"]), 2),
            "bnd_pct_clutch": round(float(row["bnd_pct_clutch"]), 2),
            "bowling_clutch_index": round(float(row["bowling_clutch_index"]), 2),
            # Robustness
            "bootstrap_mean_rating": round(float(row["bootstrap_mean_rating"]), 2),
            "rating_std": round(float(row["rating_std"]), 2),
            "rating_p025": round(float(row["rating_p025"]), 2),
            "rating_p975": round(float(row["rating_p975"]), 2),
            "rating_ci_width": round(float(row["rating_ci_width"]), 2),
            "bootstrap_mean_rank": round(float(row["bootstrap_mean_rank"]), 1),
            "rank_std": round(float(row["rank_std"]), 2),
            "top5_freq_pct": round(float(row["top5_freq_pct"]), 2),
            "top10_freq_pct": round(float(row["top10_freq_pct"]), 2),
            "top20_freq_pct": round(float(row["top20_freq_pct"]), 2),
            "eligibility_pct": round(float(row["eligibility_pct"]), 2),
            "clutch_volume_hhi": round(float(row["clutch_volume_hhi"]), 4),
            "top_match_wkt_share": round(float(row["top_match_wkt_share"]), 2),
            "lomo_rating_shift": round(float(row["rating_shift"]), 2),
            "resilience_category": str(row["resilience_category"]),
            # Squad Fit & Decision
            "statistical_stability_score": round(float(row["statistical_stability_score"]), 2),
            "tactical_squad_fit_score": round(float(row["tactical_squad_fit_score"]), 2),
            "acquisition_risk_score": round(float(row["acquisition_risk_score"]), 2),
            "recruitment_decision_score": round(float(row["recruitment_decision_score"]), 2),
            "recommendation_priority": str(row["recommendation_priority"]),
            "candidate_category": cat,
            "availability_status": avail,
            # Sensitivity
            "score_balanced": round(float(row["score_balanced"]), 2),
            "score_stability_first": round(float(row["score_stability_first"]), 2),
            "score_gap_priority": round(float(row["score_gap_priority"]), 2),
            "rank_balanced": int(row["rank_balanced"]),
            "rank_stability_first": int(row["rank_stability_first"]),
            "rank_gap_priority": int(row["rank_gap_priority"]),
        }
        bowlers_list.append(bw_item)

    with open(out_path / "bowlers_data.json", "w", encoding="utf-8") as f:
        json.dump(bowlers_list, f, indent=2)
    print(f" -> Exported bowlers_data.json ({len(bowlers_list)} bowlers)")

    # 4. Export Recruitment Recommendation Matrix (50 targets)
    rec_df = pd.read_parquet(resolve_path("data/processed/recruitment_recommendation_matrix.parquet"))
    rec_list = []
    for _, row in rec_df.iterrows():
        tier_code, tier_label = parse_evidence_tier(row["evidence_tier"])
        rec_list.append({
            "player_id": int(row["player_id"]),
            "player_name": str(row["player_name"]),
            "discipline": str(row["discipline"]),
            "country": str(row["country"]),
            "is_overseas": bool(row["is_overseas"]),
            "tactical_role": str(row["tactical_role"]),
            "performance_rating": round(float(row["performance_rating"]), 2),
            "evidence_reliability_score": round(float(row["evidence_reliability_score"]), 2),
            "evidence_tier": tier_code,
            "evidence_tier_label": tier_label,
            "bootstrap_eligibility_pct": round(float(row["bootstrap_eligibility_pct"]), 2),
            "rating_ci_width": round(float(row["rating_ci_width"]), 2),
            "top20_freq_pct": round(float(row["top20_freq_pct"]), 2),
            "clutch_volume_hhi": round(float(row["clutch_volume_hhi"]), 4),
            "lomo_rating_shift": round(float(row["lomo_rating_shift"]), 2),
            "tactical_squad_fit_score": round(float(row["tactical_squad_fit_score"]), 2),
            "statistical_stability_score": round(float(row["statistical_stability_score"]), 2),
            "acquisition_risk_score": round(float(row["acquisition_risk_score"]), 2),
            "recruitment_decision_score": round(float(row["recruitment_decision_score"]), 2),
            "player_archetype": str(row["player_archetype"]),
            "recommendation_priority": str(row["recommendation_priority"]),
            "squad_gap_addressed": str(row["squad_gap_addressed"]),
            "candidate_category": str(row["candidate_category"]),
            "availability_status": str(row["availability_status"]),
        })
    with open(out_path / "recruitment_matrix.json", "w", encoding="utf-8") as f:
        json.dump(rec_list, f, indent=2)
    print(f" -> Exported recruitment_matrix.json ({len(rec_list)} shortlisted targets)")

    # 5. Export RR Squad Baseline (27 registered players)
    rr_list = []
    for _, row in rr_baseline_df.iterrows():
        mp = int(row["matches_played"])
        pid = int(row["player_id"])
        if pid == 4409:
            status = "Administrative Roster Registration (Non-Participant)"
        elif mp > 0:
            status = f"Active Playing XI / Rotation ({mp} matches)"
        else:
            status = "Bench / Tactical Reserve Specialist (0 matches)"
            
        rr_list.append({
            "player_id": pid,
            "player_name": str(row["player_name"]),
            "matches_played": mp,
            "roster_status": status,
            "is_wk": bool(row["is_wk"]),
            "avg_batting_order": round(float(row["avg_batting_order"]), 1) if pd.notna(row["avg_batting_order"]) else None,
            "country": str(row["country"]),
            "is_overseas": bool(row["is_overseas"]),
            "bat_role": str(row["tactical_bat_role"]),
            "bowl_role": str(row["tactical_bowl_role"]),
            "bat_rating": round(float(row["bat_rating"]), 2) if pd.notna(row["bat_rating"]) else None,
            "bowl_rating": round(float(row["bowl_rating"]), 2) if pd.notna(row["bowl_rating"]) else None,
        })
    with open(out_path / "rr_squad_data.json", "w", encoding="utf-8") as f:
        json.dump(rr_list, f, indent=2)
    print(f" -> Exported rr_squad_data.json ({len(rr_list)} RR squad records)")

    # 6. Export RR Squad Gap Analysis (36 evaluations: 12 roles x 3 scenarios)
    gap_df = pd.read_parquet(resolve_path("data/processed/rr_squad_gap_analysis.parquet"))
    gap_list = []
    for _, row in gap_df.iterrows():
        gap_list.append({
            "discipline": str(row["discipline"]),
            "tactical_role": str(row["tactical_role"]),
            "squad_count_total": int(row["squad_count_total"]),
            "squad_count_domestic": int(row["squad_count_domestic"]),
            "squad_count_overseas": int(row["squad_count_overseas"]),
            "players_in_role": str(row["players_in_role"]),
            "depth_status": str(row["depth_status"]),
            "gap_criticality_weight": round(float(row["gap_criticality_weight"]), 1),
            "gap_severity": str(row["gap_severity"]),
            "scenario": str(row["scenario"])
        })
    with open(out_path / "squad_gaps_data.json", "w", encoding="utf-8") as f:
        json.dump(gap_list, f, indent=2)
    print(f" -> Exported squad_gaps_data.json ({len(gap_list)} role evaluations)")

    # 7. Export Auction Scenarios & Budget Allocations
    scen_df = pd.read_parquet(resolve_path("data/processed/auction_strategy_scenarios.parquet"))
    alloc_df = pd.read_parquet(resolve_path("data/processed/auction_budget_allocations.parquet"))

    scenario_candidates = {
        "Scenario_1_Balanced_Reinforcement": {
            "Top_Order_Anchor": ["Devdutt Padikkal (Domestic)", "Angkrish Raghuvanshi (Domestic)"],
            "Death_Finisher": ["Tim David (Overseas)", "Matthew Wade (Overseas)", "Mahipal Lomror (Domestic)"],
            "Middle_Spinner": ["Liam Dawson (Overseas)", "Mujeeb Ur Rahman (Overseas)", "George Dockrell (Overseas)"],
            "Death_Bowler": ["Benjamin Sears (Overseas)", "Nathan Ellis (Overseas)", "Mohsin Khan (Domestic)"]
        },
        "Scenario_2_Bowling_Depth_Priority": {
            "Death_Bowler": ["Benjamin Sears (Overseas)", "Nathan Ellis (Overseas)", "Tushar Deshpande (Domestic)"],
            "Middle_Spinner": ["Liam Dawson (Overseas)", "Mujeeb Ur Rahman (Overseas)"],
            "Powerplay_Pacer": ["Nathan Ellis (Overseas)", "Mohsin Khan (Domestic)"],
            "Death_Finisher": ["Ashutosh Sharma (Domestic)", "Mahipal Lomror (Domestic)"]
        },
        "Scenario_3_Power_Hitting_Boundary_Maximization": {
            "Death_Finisher": ["Tim David (Overseas)", "Matthew Wade (Overseas)", "Ashutosh Sharma (Domestic)"],
            "Top_Order_Anchor": ["Abhishek Sharma (Domestic)", "Phil Salt (Overseas)"],
            "Middle_Stabilizer": ["Naman Dhir (Domestic)", "Ayush Badoni (Domestic)"],
            "Death_Bowler": ["Benjamin Sears (Overseas)", "Nathan Ellis (Overseas)"]
        },
        "Scenario_4_Young_Domestic_Core_Future_Pipeline": {
            "Top_Order_Anchor": ["Angkrish Raghuvanshi (Domestic)", "Abhishek Sharma (Domestic)"],
            "Middle_Stabilizer": ["Naman Dhir (Domestic)", "Ayush Badoni (Domestic)"],
            "Death_Finisher": ["Ashutosh Sharma (Domestic)", "Mahipal Lomror (Domestic)"],
            "Death_Bowler": ["Mohsin Khan (Domestic)", "Tushar Deshpande (Domestic)"]
        },
        "Scenario_5_Elite_Overseas_Spine": {
            "Death_Finisher": ["Tim David (Overseas)", "Matthew Wade (Overseas)"],
            "Death_Bowler": ["Benjamin Sears (Overseas)", "Nathan Ellis (Overseas)"],
            "Middle_Spinner": ["Liam Dawson (Overseas)", "Mujeeb Ur Rahman (Overseas)"],
            "Top_Order_Anchor": ["Phil Salt (Overseas)", "Finn Allen (Overseas)"]
        }
    }

    scenarios_list = []
    for _, srow in scen_df.iterrows():
        skey = str(srow["scenario_key"])
        sub_alloc = alloc_df[alloc_df["scenario_key"] == skey]
        allocs = []
        for _, arow in sub_alloc.iterrows():
            allocs.append({
                "allocation_category": str(arow["allocation_category"]),
                "budget_units": round(float(arow["budget_units"]), 1),
                "pct_of_budget": round(float(arow["pct_of_budget"]), 1)
            })
        
        scenarios_list.append({
            "scenario_key": skey,
            "scenario_name": str(srow["scenario_name"]),
            "strategic_focus": str(srow["strategic_focus"]),
            "total_budget_units": round(float(srow["total_budget_units"]), 1),
            "overseas_slots_demanded": int(srow["overseas_slots_demanded"]),
            "main_advantages": str(srow["main_advantages"]),
            "main_risks": str(srow["main_risks"]),
            "squad_balance_impact": str(srow["squad_balance_impact"]),
            "budget_allocations": allocs,
            "key_candidate_targets": scenario_candidates.get(skey, {})
        })
    with open(out_path / "auction_scenarios.json", "w", encoding="utf-8") as f:
        json.dump(scenarios_list, f, indent=2)
    print(f" -> Exported auction_scenarios.json ({len(scenarios_list)} scenarios)")

    # 8. Export Overview Summary Statistics (Audited & Reconciled Scope)
    strong_batters = sum(1 for b in batters_list if b["evidence_tier"] == "Strong")
    moderate_batters = sum(1 for b in batters_list if b["evidence_tier"] == "Moderate")

    strong_bowlers = sum(1 for bw in bowlers_list if bw["evidence_tier"] == "Strong")
    moderate_bowlers = sum(1 for bw in bowlers_list if bw["evidence_tier"] == "Moderate")

    top_actionable_batters = [b for b in batters_list if b["candidate_category"] == "Viable Auction Target"]
    top_actionable_batters.sort(key=lambda x: x["recruitment_decision_score"], reverse=True)

    top_actionable_bowlers = [bw for bw in bowlers_list if bw["candidate_category"] == "Viable Auction Target"]
    top_actionable_bowlers.sort(key=lambda x: x["recruitment_decision_score"], reverse=True)

    overview_dict = {
        "dataset_scope": {
            "total_matches_in_metadata": 883,
            "total_matches_with_deliveries": 867,
            "abandoned_fixtures_count": 16,
            "total_deliveries_analyzed": 200999,
            "total_batter_runs": 269550,
            "total_bowler_wickets": 10272,
            "total_balls_faced": 193285,
            "total_legal_balls": 192445,
            "total_wides": 7714,
            "total_no_balls": 840,
            "competitions_covered": [
                {"name": "Indian Premier League (IPL)", "code": "IPL", "seasons": "2022, 2023, 2024, 2025, 2026", "matches": 371},
                {"name": "International T20s (T20I)", "code": "T20I", "seasons": "2022-2026", "matches": 486},
                {"name": "Emerging Teams & Rising Stars Asia Cups", "code": "Asia Cups", "seasons": "2024, 2025", "matches": 26}
            ],
            "temporal_range": "2022 - 2026"
        },
        "candidate_pool": {
            "total_batters_evaluated": 1091,
            "eligible_batters_count": len(batters_list),
            "strong_evidence_batters": strong_batters,
            "moderate_evidence_batters": moderate_batters,
            "total_bowlers_evaluated": 734,
            "eligible_bowlers_count": len(bowlers_list),
            "strong_evidence_bowlers": strong_bowlers,
            "moderate_evidence_bowlers": moderate_bowlers,
        },
        "rr_squad_baseline": {
            "total_registered_players": 27,
            "active_playing_xi_rotation": 20,
            "bench_reserve_specialists": 6,
            "administrative_registrations": 1,
            "domestic_players_count": 19,
            "overseas_players_count": 8,
            "retention_scenarios": {
                "Scenario_A": {"name": "Core Continuity Baseline", "retained": 14, "open_slots": 11, "overseas_retained": 4},
                "Scenario_B": {"name": "Moderate Refresh", "retained": 10, "open_slots": 15, "overseas_retained": 3},
                "Scenario_C": {"name": "Radical Reset", "retained": 6, "open_slots": 19, "overseas_retained": 2}
            }
        },
        "tactical_gaps": [
            {"role": "Death-Overs Specialist", "discipline": "Bowling", "severity": "Critical", "criticality": 90.0, "status": "Critical Void"},
            {"role": "Finisher", "discipline": "Batting", "severity": "Critical", "criticality": 87.5, "status": "Critical Void"},
            {"role": "New-Ball / Powerplay Fast Bowler", "discipline": "Bowling", "severity": "Low", "criticality": 85.0, "status": "Adequate Depth"},
            {"role": "Middle-Overs Spinner", "discipline": "Bowling", "severity": "High", "criticality": 80.0, "status": "Limited Depth"},
            {"role": "Middle-Order Batter", "discipline": "Batting", "severity": "Critical", "criticality": 70.0, "status": "Critical Void"},
            {"role": "Top-Order Batter", "discipline": "Batting", "severity": "Critical", "criticality": 65.0, "status": "Critical Void"}
        ],
        "top_actionable_targets": {
            "batting": [
                {"name": b["player_name"], "role": b["tactical_role"], "country": b["country"], "is_overseas": b["is_overseas"], "rdh": b["recruitment_decision_score"], "pr": b["performance_rating"], "tfs": b["tactical_squad_fit_score"], "ars": b["acquisition_risk_score"]}
                for b in top_actionable_batters[:5]
            ],
            "bowling": [
                {"name": bw["player_name"], "role": bw["tactical_role"], "country": bw["country"], "is_overseas": bw["is_overseas"], "rdh": bw["recruitment_decision_score"], "pr": bw["performance_rating"], "tfs": bw["tactical_squad_fit_score"], "ars": bw["acquisition_risk_score"]}
                for bw in top_actionable_bowlers[:5]
            ]
        }
    }
    with open(out_path / "overview_stats.json", "w", encoding="utf-8") as f:
        json.dump(overview_dict, f, indent=2)
    print(f" -> Exported overview_stats.json")

    # 9. Export Methodology & Register Data
    reg_df = pd.read_parquet(resolve_path("data/processed/source_and_assumptions_register.parquet"))
    reg_list = []
    for _, row in reg_df.iterrows():
        reg_list.append({
            "item_id": str(row["item_id"]),
            "category": str(row["category"]),
            "description": str(row["description"]),
            "source": str(row["source"]),
            "verification_date": str(row["verification_date"]),
            "status": str(row["status"]),
            "impact_on_model": str(row["impact_on_model"])
        })

    methodology_dict = {
        "metric_definitions": {
            "PR": {
                "name": "Performance Rating",
                "scale": "0.00 to 100.00",
                "summary": "Combines pressure-adjusted baseline scoring/economy with clutch performance multipliers and Empirical Bayes credibility shrinkage toward tournament prior mean.",
                "formula": "PR = Credibility_Weight * Raw_Pressure_Score + (1 - Credibility_Weight) * Prior_Mean"
            },
            "ERS": {
                "name": "Evidence Reliability Score",
                "scale": "0.00 to 100.00",
                "summary": "Multi-dimensional exposure metric capturing volume, clutch sample size, matches played, and tournament breadth through linear saturation functions.",
                "formula": "ERS = 0.40 * S_clutch + 0.25 * S_overall + 0.20 * S_matches + 0.15 * S_comps",
                "benchmarks": "Saturation caps: 120 clutch deliveries, 300 total deliveries, 25 matches, 3 competitions.",
                "tiers": "Strong Evidence: ERS >= 60.0 & Clutch >= 40 & Matches >= 10 | Moderate Evidence: ERS >= 35.0 & Clutch >= 20 & Matches >= 5 | Insufficient: Sample too small for primary ranking"
            },
            "SSS": {
                "name": "Statistical Stability Score (Top-Tier Impact Retention Index)",
                "scale": "0.00 to 100.00",
                "summary": "Calibrated Top-Tier Impact Retention Index evaluating candidate resilience across 1,000 bootstrap resamples, rank volatility (Top-20 retention frequency), match volume concentration (HHI), and leave-one-match-out (LOMO) rating shifts.",
                "formula": "SSS = 0.35 * Boot_Rel + 0.30 * Top20_Freq + 0.20 * (1 - HHI) + 0.15 * LOMO_Res",
                "note": "Specifically calibrated to measure a player's ability to retain elite top-tier impact across resampled tournament states without single-match sample dependency."
            },
            "TFS": {
                "name": "Tactical Squad Fit Score",
                "scale": "0.00 to 100.00",
                "summary": "Measures direct alignment between player tactical role and Rajasthan Royals squad voids across retention scenarios, applying a 0.90x modifier to overseas players to reflect international roster limits."
            },
            "ARS": {
                "name": "Acquisition Risk Score",
                "scale": "0.00 to 100.00 (Higher = Higher Risk)",
                "summary": "Quantifies auction bidding inflation risk, overseas slot scarcity, statistical volatility, and historical availability constraints.",
                "penalty": "Includes a +6.0 risk penalty for overseas candidates."
            },
            "RDH": {
                "name": "Recruitment Decision Holistic Score",
                "scale": "0.00 to 90.00 (Theoretical Maximum: 90.00)",
                "summary": "Synthesizes performance, reliability, stability, and tactical fit while penalizing acquisition risk. Operates on a strict 0.00 to 90.00 theoretical scale because positive weights sum to 0.90.",
                "formula": "RDH = clip(0.30 * PR + 0.20 * ERS + 0.20 * SSS + 0.20 * TFS - 0.10 * ARS, 0.0, 90.0)",
                "critical_rule": "Theoretical range is strictly [0.0, 90.0]. Never display RDH as a percentage or win probability."
            }
        },
        "candidate_governance_rules": [
            {
                "category": "Viable Auction Target",
                "badge_class": "badge-viable",
                "description": "Actionable recruitment recommendations for Rajasthan Royals. Availability unconfirmed pending official IPL 2027 auction player registration."
            },
            {
                "category": "Strategic Benchmark (BCCI Ineligible)",
                "badge_class": "badge-ineligible",
                "description": "Pakistani players (e.g., Sufiyan Muqeem, Imad Wasim, Haris Rauf). Ineligible for IPL under long-standing regulatory policy. Displayed strictly as international analytical benchmarks, never as actionable auction recommendations."
            },
            {
                "category": "Strategic Benchmark (Rival Core)",
                "badge_class": "badge-rival",
                "description": "Elite franchise cornerstones (e.g., Jasprit Bumrah, Suryakumar Yadav, Sunil Narine, Rinku Singh) highly likely to be retained by rival teams. Included for comparative performance benchmarking."
            },
            {
                "category": "Strategic Benchmark (Retired)",
                "badge_class": "badge-retired",
                "description": "Veterans retired from IPL competition (e.g., Dinesh Karthik) serving as historical reference benchmarks."
            },
            {
                "category": "Existing RR Player (Internal Asset)",
                "badge_class": "badge-internal",
                "description": "Current Rajasthan Royals roster players (e.g., Dhruv Jurel, Ravindra Jadeja, Riyan Parag, Ravi Bishnoi, Yashasvi Jaiswal) evaluated as internal retention assets."
            }
        ],
        "assumptions_register": reg_list
    }
    with open(out_path / "methodology_data.json", "w", encoding="utf-8") as f:
        json.dump(methodology_dict, f, indent=2)
    print(f" -> Exported methodology_data.json")

    # 10. Create Offline JavaScript Bundle (Ensures dashboard works even via file:// double-click)
    js_bundle_content = f"""/**
 * SupeRR Selector - Bundled Data Feed
 * Auto-generated offline fallback data for environments where fetch() is blocked by CORS (e.g. file:// protocol).
 */
window.DASHBOARD_DATA = {{
  overview: {json.dumps(overview_dict)},
  batters: {json.dumps(batters_list)},
  bowlers: {json.dumps(bowlers_list)},
  rrSquad: {json.dumps(rr_list)},
  squadGaps: {json.dumps(gap_list)},
  recruitmentMatrix: {json.dumps(rec_list)},
  auctionScenarios: {json.dumps(scenarios_list)},
  methodology: {json.dumps(methodology_dict)}
}};
"""
    with open(Path("dashboard/js/data_bundle.js"), "w", encoding="utf-8") as f:
        f.write(js_bundle_content)
    print(f" -> Exported dashboard/js/data_bundle.js (Offline fallback bundle)")

    # Mirror to data/dashboard
    backup_path = Path("data/dashboard")
    backup_path.mkdir(parents=True, exist_ok=True)
    for p in out_path.glob("*.json"):
        with open(p, "r", encoding="utf-8") as f_in:
            data = json.load(f_in)
        with open(backup_path / p.name, "w", encoding="utf-8") as f_out:
            json.dump(data, f_out, indent=2)
    print(f" -> Mirrored all JSON files to data/dashboard/")

if __name__ == "__main__":
    export_dashboard_data()
