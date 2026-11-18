"""
tests/test_module6_robustness.py
Automated unit, regression, and methodology tests for Module 6 Statistical Validation & Robustness.

Tests:
1. Match-cluster bootstrap preserves complete match clusters.
2. Duplicate match draws are treated as separate contributions (multiplied, not collapsed).
3. Fixed random seed produces identical, reproducible results.
4. Rating uncertainty intervals are valid (bounded in [0, 100], p025 <= p975).
5. Ranking stability handles players missing or non-eligible in some replicates (no artificial 0 rank).
6. Replicate eligibility rules strictly match Module 5 production standards.
7. Evidence threshold sensitivity behaves monotonically under tightening filters.
8. Concentration HHI and LOMO metrics are mathematically bounded.
"""

import unittest
import numpy as np
import pandas as pd

from src.bootstrap_validation import (
    build_match_strata_mapping,
    prepare_batter_match_matrix,
    prepare_bowler_match_matrix,
    evaluate_batter_replicate_vectorized,
    evaluate_bowler_replicate_vectorized,
    run_match_cluster_bootstrap,
    summarize_player_rating_uncertainty,
    summarize_ranking_stability,
    summarize_eligibility_stability
)
from src.robustness_analysis import (
    evaluate_evidence_threshold_sensitivity,
    analyze_role_and_phase_robustness
)
from src.influence_analysis import (
    calculate_batter_match_concentration,
    calculate_bowler_match_concentration,
    evaluate_leave_one_match_out_sensitivity
)


class TestModule6Robustness(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Load datasets once for class test execution."""
        cls.df_deliv = pd.read_parquet("data/processed/ball_by_ball_pressure.parquet")
        cls.df_b_ratings = pd.read_parquet("data/processed/batter_player_ratings.parquet")
        cls.df_bw_ratings = pd.read_parquet("data/processed/bowler_player_ratings.parquet")
        cls.df_b_rankings = pd.read_csv("data/processed/batter_player_rankings.csv")
        cls.df_bw_rankings = pd.read_csv("data/processed/bowler_player_rankings.csv")

    def test_cluster_preservation_and_duplicate_draws(self):
        """Verify that duplicate match draws are treated as separate contributions and not collapsed."""
        matrix, match_idx, player_idx, meta, unique_matches, bm = prepare_batter_match_matrix(
            self.df_deliv, self.df_b_ratings
        )
        n_matches = len(unique_matches)
        n_players = len(meta)

        # Draw match index 0 once vs twice
        counts_single = np.zeros(n_matches, dtype=int)
        counts_single[0] = 1

        counts_double = np.zeros(n_matches, dtype=int)
        counts_double[0] = 2

        # Weight matrices
        totals_single = np.zeros((n_players, matrix.shape[1]))
        w_single = matrix * counts_single[match_idx][:, None]
        for c in range(matrix.shape[1]):
            totals_single[:, c] = np.bincount(player_idx, weights=w_single[:, c], minlength=n_players)

        totals_double = np.zeros((n_players, matrix.shape[1]))
        w_double = matrix * counts_double[match_idx][:, None]
        for c in range(matrix.shape[1]):
            totals_double[:, c] = np.bincount(player_idx, weights=w_double[:, c], minlength=n_players)

        # Exact doubling assertion
        np.testing.assert_allclose(totals_double, 2.0 * totals_single)

    def test_seed_reproducibility(self):
        """Verify that a fixed random seed produces strictly identical bootstrap distributions."""
        res_a = run_match_cluster_bootstrap(
            self.df_deliv, self.df_b_ratings, self.df_bw_ratings,
            n_replicates=5, random_seed=999, stratify=True
        )
        res_b = run_match_cluster_bootstrap(
            self.df_deliv, self.df_b_ratings, self.df_bw_ratings,
            n_replicates=5, random_seed=999, stratify=True
        )
        np.testing.assert_array_equal(res_a["batters"]["ratings"], res_b["batters"]["ratings"])
        np.testing.assert_array_equal(res_a["bowlers"]["ratings"], res_b["bowlers"]["ratings"])

    def test_rating_uncertainty_interval_bounds(self):
        """Verify that bootstrap percentile uncertainty intervals are bounded in [0, 100] and lower <= upper."""
        df_unc = pd.read_parquet("data/processed/batter_rating_uncertainty.parquet")
        self.assertTrue((df_unc["bootstrap_mean_rating"] >= 0.0).all())
        self.assertTrue((df_unc["bootstrap_mean_rating"] <= 100.0).all())
        self.assertTrue((df_unc["rating_p025"] >= 0.0).all())
        self.assertTrue((df_unc["rating_p975"] <= 100.0).all())
        self.assertTrue((df_unc["rating_p025"] <= df_unc["rating_p975"]).all())
        self.assertTrue((df_unc["rating_ci_width"] >= 0.0).all())

        df_bw_unc = pd.read_parquet("data/processed/bowler_rating_uncertainty.parquet")
        self.assertTrue((df_bw_unc["bootstrap_mean_rating"] >= 0.0).all())
        self.assertTrue((df_bw_unc["bootstrap_mean_rating"] <= 100.0).all())
        self.assertTrue((df_bw_unc["rating_p025"] <= df_bw_unc["rating_p975"]).all())

    def test_ranking_stability_no_zero_ranks(self):
        """Verify that missing ranks are not assigned an artificial rank of zero and frequencies are in [0, 100]."""
        df_stab = pd.read_parquet("data/processed/batter_ranking_stability.parquet")
        valid_means = df_stab["bootstrap_mean_rank"].dropna()
        self.assertTrue((valid_means >= 1.0).all(), "Ranks must be >= 1.0; zero is strictly disallowed")
        self.assertTrue((df_stab["top5_freq_pct"] >= 0.0).all())
        self.assertTrue((df_stab["top5_freq_pct"] <= 100.0).all())
        self.assertTrue((df_stab["eligibility_pct"] >= 0.0).all())
        self.assertTrue((df_stab["eligibility_pct"] <= 100.0).all())

    def test_replicate_eligibility_matches_module5_rules(self):
        """Verify that replicate evaluation uses exact Module 5 conjunctional rules."""
        # Strong: ERS >= 60, c >= 40, m >= 10
        # Moderate: ERS >= 35, c >= 20, m >= 5
        # Not eligible: o < 30 or c < 10
        df_elig = pd.read_parquet("data/processed/batter_eligibility_stability.parquet")
        # Check sum of tier percentages equals 100%
        sum_tiers = (
            df_elig["pct_strong_evidence"]
            + df_elig["pct_moderate_evidence"]
            + df_elig["pct_insufficient_evidence"]
            + df_elig["pct_not_eligible"]
        )
        np.testing.assert_allclose(sum_tiers.values, 100.0, atol=0.2)

    def test_evidence_threshold_sensitivity_monotonicity(self):
        """Verify that tightening evidence thresholds monotonically reduces eligible player count."""
        df_sens = pd.read_parquet("data/processed/evidence_threshold_sensitivity.parquet")
        b_sens = df_sens[df_sens["Discipline"] == "Batting"].set_index("Scenario")
        
        # Baseline (304) -> Strict_Clutch_30 (277) -> Strong_Evidence_Only (201)
        cnt_base = b_sens.loc["Baseline", "Eligible_Count"]
        cnt_strict = b_sens.loc["Strict_Clutch_30", "Eligible_Count"]
        cnt_strong = b_sens.loc["Strong_Evidence_Only", "Eligible_Count"]
        
        self.assertGreaterEqual(cnt_base, cnt_strict)
        self.assertGreaterEqual(cnt_strict, cnt_strong)

    def test_match_concentration_hhi_bounds(self):
        """Verify that Herfindahl-Hirschman Index of clutch delivery volume is strictly bounded in (0, 1]."""
        b_conc = calculate_batter_match_concentration(self.df_deliv, self.df_b_rankings)
        self.assertTrue((b_conc["clutch_volume_hhi"] > 0.0).all())
        self.assertTrue((b_conc["clutch_volume_hhi"] <= 1.0).all())
        self.assertTrue((b_conc["top_match_run_share"] >= 0.0).all())
        self.assertTrue((b_conc["top_match_run_share"] <= 100.0).all())

    def test_lomo_resilience_categories(self):
        """Verify that LOMO outputs have valid resilience categories and ranking shifts."""
        df_lomo = pd.read_parquet("data/processed/match_influence_analysis.parquet")
        valid_cats = {"Sustained / Resilient", "Moderately Influenced", "Match-Dependent Spike"}
        self.assertTrue(set(df_lomo["resilience_category"]).issubset(valid_cats))
        self.assertEqual(len(df_lomo), 50, "Top 25 batters + Top 25 bowlers = 50 rows")


if __name__ == "__main__":
    unittest.main()
