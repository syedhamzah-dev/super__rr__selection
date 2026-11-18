"""
Test suite for Module 8: Interactive Dashboard and Data Integrity (Reconciled)
Verifies exported JSON files, governance categorizations, metric bounds,
and reconciliation with Modules 1-7.
"""

import json
from pathlib import Path
import pytest

DASHBOARD_DATA_DIR = Path("dashboard/data")

@pytest.fixture(scope="module")
def dashboard_data():
    files = {
        "overview": DASHBOARD_DATA_DIR / "overview_stats.json",
        "batters": DASHBOARD_DATA_DIR / "batters_data.json",
        "bowlers": DASHBOARD_DATA_DIR / "bowlers_data.json",
        "recruitment": DASHBOARD_DATA_DIR / "recruitment_matrix.json",
        "rr_squad": DASHBOARD_DATA_DIR / "rr_squad_data.json",
        "squad_gaps": DASHBOARD_DATA_DIR / "squad_gaps_data.json",
        "auction": DASHBOARD_DATA_DIR / "auction_scenarios.json",
        "methodology": DASHBOARD_DATA_DIR / "methodology_data.json"
    }
    
    data = {}
    for key, path in files.items():
        assert path.exists(), f"Missing required dashboard data file: {path}"
        with open(path, "r", encoding="utf-8") as f:
            data[key] = json.load(f)
    return data

class TestModule8Dashboard:

    def test_all_json_files_present_and_valid(self, dashboard_data):
        assert len(dashboard_data) == 8
        for k, v in dashboard_data.items():
            assert v is not None

    def test_reconciled_dataset_scope(self, dashboard_data):
        ov = dashboard_data["overview"]["dataset_scope"]
        assert ov["total_matches_in_metadata"] == 883
        assert ov["total_matches_with_deliveries"] == 867
        assert ov["abandoned_fixtures_count"] == 16
        assert ov["total_deliveries_analyzed"] == 200999
        assert ov["total_batter_runs"] == 269550
        assert ov["total_bowler_wickets"] == 10272
        assert ov["total_balls_faced"] == 193285
        assert ov["total_legal_balls"] == 192445
        assert ov["temporal_range"] == "2022 - 2026"

    def test_batters_and_bowlers_counts_and_authoritative_tiers(self, dashboard_data):
        batters = dashboard_data["batters"]
        bowlers = dashboard_data["bowlers"]

        assert len(batters) == 304, f"Expected 304 eligible batters, found {len(batters)}"
        assert len(bowlers) == 290, f"Expected 290 eligible bowlers, found {len(bowlers)}"

        # Authoritative Module 5 evidence tiers: Strong and Moderate only
        strong_b = sum(1 for b in batters if b["evidence_tier"] == "Strong")
        mod_b = sum(1 for b in batters if b["evidence_tier"] == "Moderate")
        assert strong_b == 201
        assert mod_b == 103
        assert strong_b + mod_b == 304

        strong_bw = sum(1 for bw in bowlers if bw["evidence_tier"] == "Strong")
        mod_bw = sum(1 for bw in bowlers if bw["evidence_tier"] == "Moderate")
        assert strong_bw == 206
        assert mod_bw == 84
        assert strong_bw + mod_bw == 290

    def test_rr_squad_baseline_reconciliation(self, dashboard_data):
        rr_squad = dashboard_data["rr_squad"]
        assert len(rr_squad) == 27, f"Expected 27 registered RR players, found {len(rr_squad)}"

        active_players = [p for p in rr_squad if p["matches_played"] > 0]
        bench_players = [p for p in rr_squad if p["matches_played"] == 0 and p["player_id"] != 4409]
        admin_players = [p for p in rr_squad if p["player_id"] == 4409]

        assert len(active_players) == 20, f"Expected 20 active players, found {len(active_players)}"
        assert len(bench_players) == 6, f"Expected 6 bench reserves, found {len(bench_players)}"
        assert len(admin_players) == 1, f"Expected 1 administrative roster registration, found {len(admin_players)}"

    def test_top_50_matrix_candidate_governance_invariants(self, dashboard_data):
        rec_matrix = dashboard_data["recruitment"]
        assert len(rec_matrix) == 50, f"Expected 50 shortlisted targets, found {len(rec_matrix)}"

        cat_counts = {}
        for p in rec_matrix:
            c = p["candidate_category"]
            cat_counts[c] = cat_counts.get(c, 0) + 1

        assert cat_counts["Viable Auction Target"] == 36
        assert cat_counts["Strategic Benchmark (BCCI Ineligible)"] == 5
        assert cat_counts["Existing RR Player (Internal Asset)"] == 4
        assert cat_counts["Strategic Benchmark (Rival Core)"] == 4
        assert cat_counts["Strategic Benchmark (Retired)"] == 1
        assert sum(cat_counts.values()) == 50

        # Verify the 4 internal assets in top 50 matrix
        internal_ids = {p["player_id"] for p in rec_matrix if p["candidate_category"] == "Existing RR Player (Internal Asset)"}
        assert internal_ids == {7260, 152, 6423, 7503}  # Jurel, Jadeja, Parag, Bishnoi

        # Verify Yashasvi Jaiswal is recognized as internal asset in full batters dataset
        jaiswal = next((b for b in dashboard_data["batters"] if b["player_id"] == 6819), None)
        assert jaiswal is not None
        assert jaiswal["candidate_category"] == "Existing RR Player (Internal Asset)"
        assert jaiswal["recommendation_priority"] == "Internal Asset (Retention Candidate)"

        # Check Pakistani players are strictly non-actionable
        for p in rec_matrix:
            if p["country"] == "Pakistan":
                assert p["candidate_category"] == "Strategic Benchmark (BCCI Ineligible)"
                assert "Ineligible" in p["availability_status"]

    def test_rdh_bounds_and_no_percentage_representation(self, dashboard_data):
        for b in dashboard_data["batters"]:
            rdh = b["recruitment_decision_score"]
            assert 0.0 <= rdh <= 90.0, f"Batter {b['player_name']} RDH {rdh} outside [0.0, 90.0]"

        for bw in dashboard_data["bowlers"]:
            rdh = bw["recruitment_decision_score"]
            assert 0.0 <= rdh <= 90.0, f"Bowler {bw['player_name']} RDH {rdh} outside [0.0, 90.0]"

    def test_auction_scenarios_budget_conservation(self, dashboard_data):
        scenarios = dashboard_data["auction"]
        assert len(scenarios) == 5, f"Expected 5 auction scenarios, found {len(scenarios)}"

        for s in scenarios:
            assert s["total_budget_units"] == 100.0
            sum_allocs = sum(a["budget_units"] for a in s["budget_allocations"])
            assert abs(sum_allocs - 100.0) < 1e-4, f"Scenario {s['scenario_name']} allocations sum to {sum_allocs}, not 100 BAU"

    def test_squad_gaps_scenarios_evaluation(self, dashboard_data):
        gaps = dashboard_data["squad_gaps"]
        assert len(gaps) == 36, f"Expected 36 role evaluations (12 roles x 3 scenarios), found {len(gaps)}"

        scenarios_in_gaps = {g["scenario"] for g in gaps}
        assert len(scenarios_in_gaps) == 3

    def test_offline_data_bundle_matches_json_feeds(self, dashboard_data):
        bundle_path = Path("dashboard/js/data_bundle.js")
        assert bundle_path.exists()
        text = bundle_path.read_text(encoding="utf-8")
        assert "window.DASHBOARD_DATA" in text
        assert "overview" in text
        assert "batters" in text
        assert "bowlers" in text
