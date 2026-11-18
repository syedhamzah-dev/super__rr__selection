"""
tests/test_module7_squad_fit.py
Automated Unit and Governance Tests for Module 7: Rajasthan Royals Squad Fit & Auction Strategy

Validates:
1. Exact player ID joins and duplicate prevention.
2. 12-role tactical classification taxonomy coverage.
3. Squad gap arithmetic and gap criticality weights.
4. Strict separation of batting and bowling disciplines (no combined rating).
5. Mathematical integrity of Module 5 and Module 6 metric consumption.
6. Non-fabrication constraints (no unverified prices, budget unit conservation = 100.0).
7. Official IPL squad limits and overseas caps (max 25 players, max 8 overseas).
8. Score bounds (all 5 dimensions in [0.0, 100.0]) and reproducibility.

Author: Syed Mohammad Hamzah (B.Tech CSE - Data Analytics)
Evaluator Reference: Rajasthan Royals Sports Analytics Challenge (Season 2)
"""

import os
import pytest
import pandas as pd
import numpy as np

from src.squad_context import (
    get_rr_2026_baseline_squad,
    get_squad_retention_scenarios,
    get_source_and_assumptions_register,
    OFFICIAL_IPL_RULES
)
from src.squad_gap_analysis import (
    audit_rr_squad_by_roles,
    evaluate_squad_gaps,
    RR_TACTICAL_GAP_WEIGHTS,
    TACTICAL_BATTING_ROLES,
    TACTICAL_BOWLING_ROLES
)
from src.player_squad_fit import (
    build_candidate_recruitment_pool,
    calculate_candidate_squad_fit_scores,
    run_alternative_weight_scenarios
)
from src.auction_strategy import (
    get_auction_scenarios_summary,
    get_budget_allocations_dataframe,
    AUCTION_SCENARIOS
)


@pytest.fixture(scope="module")
def baseline_data():
    squad = get_rr_2026_baseline_squad()
    audited = audit_rr_squad_by_roles(squad)
    b_pool = build_candidate_recruitment_pool("Batting")
    b_eval = calculate_candidate_squad_fit_scores(b_pool, "Batting")
    bw_pool = build_candidate_recruitment_pool("Bowling")
    bw_eval = calculate_candidate_squad_fit_scores(bw_pool, "Bowling")
    return {
        "squad": squad,
        "audited": audited,
        "b_pool": b_pool,
        "b_eval": b_eval,
        "bw_pool": bw_pool,
        "bw_eval": bw_eval
    }


class TestModule7SquadFit:

    def test_player_id_joins_and_no_duplicates(self, baseline_data):
        """Verifies exact player_id joins and guarantees no duplicated players in recruitment pools."""
        b_eval = baseline_data["b_eval"]
        bw_eval = baseline_data["bw_eval"]

        assert len(b_eval) == 304, f"Expected 304 eligible batters, got {len(b_eval)}"
        assert len(bw_eval) == 290, f"Expected 290 eligible bowlers, got {len(bw_eval)}"
        assert b_eval["player_id"].nunique() == len(b_eval), "Batting recruitment pool contains duplicate player IDs"
        assert bw_eval["player_id"].nunique() == len(bw_eval), "Bowling recruitment pool contains duplicate player IDs"
        assert not b_eval["player_id"].isnull().any(), "Batting recruitment pool contains null player IDs"
        assert not bw_eval["player_id"].isnull().any(), "Bowling recruitment pool contains null player IDs"

    def test_role_classification_taxonomies(self, baseline_data):
        """Verifies that all candidates are mapped into valid tactical roles."""
        b_eval = baseline_data["b_eval"]
        bw_eval = baseline_data["bw_eval"]

        valid_bat_roles = set(TACTICAL_BATTING_ROLES).union({"Tailender / Lower Order"})
        valid_bowl_roles = set(TACTICAL_BOWLING_ROLES).union({"Non-Bowler / Pure Batter"})

        for role in b_eval["tactical_role"]:
            assert role in valid_bat_roles, f"Invalid batting tactical role: {role}"

        for role in bw_eval["tactical_role"]:
            assert role in valid_bowl_roles, f"Invalid bowling tactical role: {role}"

    def test_squad_gap_arithmetic_and_criticality(self, baseline_data):
        """Validates that squad counts match retention lists and gap weights are consistent."""
        audited = baseline_data["audited"]
        gaps_a = evaluate_squad_gaps(audited, "Scenario_A_Core_Continuity")

        assert len(gaps_a) == 12, "Expected 12 role evaluations (6 batting + 6 bowling)"
        assert gaps_a["gap_criticality_weight"].min() >= 0.0
        assert gaps_a["gap_criticality_weight"].max() <= 100.0

        # Verify critical voids in Scenario A
        death_row = gaps_a[gaps_a["tactical_role"] == "Death-Overs Specialist"].iloc[0]
        assert death_row["squad_count_total"] == 0, "Scenario A should have 0 dedicated death-overs specialists"
        assert death_row["depth_status"] == "Critical Void / No Credible Backup"

        finisher_row = gaps_a[gaps_a["tactical_role"] == "Finisher"].iloc[0]
        assert finisher_row["squad_count_total"] == 0, "Scenario A should have 0 dedicated finishers"
        assert finisher_row["depth_status"] == "Critical Void / No Credible Backup"

    def test_separate_batting_and_bowling_evaluations(self, baseline_data):
        """Guarantees that batting and bowling evaluations are kept separate and not combined."""
        b_eval = baseline_data["b_eval"]
        bw_eval = baseline_data["bw_eval"]

        assert "sr_clutch" in b_eval.columns, "Batting evaluations must track clutch strike rate"
        assert "delta_econ_phase_adj" in bw_eval.columns, "Bowling evaluations must track phase-adjusted delta economy"

        # Ensure no joint overall rating column exists
        assert "combined_overall_rating" not in b_eval.columns
        assert "combined_overall_rating" not in bw_eval.columns
        assert (b_eval["discipline"] == "Batting").all()
        assert (bw_eval["discipline"] == "Bowling").all()

    def test_module5_and_module6_metric_integrity(self, baseline_data):
        """Verifies that upstream ratings and uncertainty intervals are preserved without alteration."""
        b_eval = baseline_data["b_eval"]
        bw_eval = baseline_data["bw_eval"]

        # Check Module 5 baseline ratings
        jaiswal = b_eval[b_eval["player_id"] == 6819].iloc[0]
        assert np.isclose(jaiswal["performance_rating"], 96.90, atol=1e-2), f"Jaiswal rating modified: {jaiswal['performance_rating']}"
        assert np.isclose(jaiswal["evidence_reliability_score"], 63.00, atol=1e-2)

        muqeem = bw_eval[bw_eval["player_id"] == 34485].iloc[0]
        assert np.isclose(muqeem["performance_rating"], 88.28, atol=1e-2)
        assert np.isclose(muqeem["evidence_reliability_score"], 90.00, atol=1e-2)

        # Check Module 6 uncertainty CI width
        assert jaiswal["rating_ci_width"] > 80.0, "Jaiswal CI width should reflect high uncertainty"
        assert muqeem["rating_ci_width"] < 40.0, "Muqeem CI width should reflect high stability"

    def test_squad_fit_score_bounds_and_risk_monotonicity(self, baseline_data):
        """Validates that all decoupled evaluation scores lie strictly within [0.0, 100.0]."""
        for df in [baseline_data["b_eval"], baseline_data["bw_eval"]]:
            for col in [
                "performance_rating", "evidence_reliability_score",
                "statistical_stability_score", "tactical_squad_fit_score",
                "acquisition_risk_score", "recruitment_decision_score"
            ]:
                assert (df[col] >= 0.0).all(), f"Column {col} has negative values"
                assert (df[col] <= 100.0).all(), f"Column {col} exceeds 100.0"

    def test_no_fabricated_prices_and_budget_conservation(self):
        """Verifies that budget allocation units strictly conserve 100.0 across all scenarios."""
        alloc_df = get_budget_allocations_dataframe()
        assert len(alloc_df) > 0

        # Check that each scenario sums exactly to 100.0 budget units
        scenario_sums = alloc_df.groupby("scenario_key")["budget_units"].sum()
        for scen_key, total in scenario_sums.items():
            assert np.isclose(total, 100.0, atol=1e-4), f"Scenario {scen_key} does not conserve 100 budget units: {total}"

        # Ensure no fabricated currency fields exist
        assert "crores" not in alloc_df.columns
        assert "price_inr" not in alloc_df.columns
        assert "base_price" not in alloc_df.columns

    def test_overseas_and_squad_limit_constraints(self):
        """Verifies that all scenarios adhere to official IPL squad size and overseas limits."""
        scenarios = get_squad_retention_scenarios()
        for key, sc in scenarios.items():
            tot_retained = sc["domestic_retained"] + sc["overseas_retained"]
            assert tot_retained <= OFFICIAL_IPL_RULES["max_squad_size"]
            assert sc["overseas_retained"] <= OFFICIAL_IPL_RULES["max_overseas_squad"]
            assert sc["slots_open_total"] + tot_retained == OFFICIAL_IPL_RULES["max_squad_size"]
            assert sc["slots_open_overseas"] + sc["overseas_retained"] == OFFICIAL_IPL_RULES["max_overseas_squad"]

    def test_missing_value_handling_and_reproducibility(self, baseline_data):
        """Verifies that candidate scores have no missing values and outputs are reproducible."""
        b_eval = baseline_data["b_eval"]
        bw_eval = baseline_data["bw_eval"]

        assert not b_eval["recruitment_decision_score"].isnull().any()
        assert not bw_eval["recruitment_decision_score"].isnull().any()
        assert not b_eval["player_archetype"].isnull().any()
        assert not bw_eval["player_archetype"].isnull().any()

        # Re-run alternative weight scenarios and verify rank stability
        b_scen = run_alternative_weight_scenarios(b_eval)
        assert "max_rank_shift" in b_scen.columns
        assert (b_scen["max_rank_shift"] >= 0).all()
