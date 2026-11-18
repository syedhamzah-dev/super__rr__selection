"""
tests/test_module5_ratings.py
Automated unit and methodology tests for Module 5 player ratings and rankings.
"""

import unittest
import numpy as np
import pandas as pd

from src.reliability_scoring import (
    calculate_batter_evidence_reliability,
    calculate_bowler_evidence_reliability
)
from src.player_rating import (
    calculate_batting_performance_rating,
    calculate_bowling_performance_rating,
    DEFAULT_BATTER_WEIGHTS,
    DEFAULT_BOWLER_WEIGHTS
)
from src.player_ranking import (
    generate_batter_rankings,
    generate_bowler_rankings
)
from src.ranking_validation import (
    test_batter_weight_sensitivity,
    test_bowler_weight_sensitivity
)


class TestModule5Ratings(unittest.TestCase):

    def setUp(self):
        """Create synthetic player data across diverse archetypes."""
        self.sample_batters = pd.DataFrame({
            "striker_id": [1, 2, 3, 4],
            "striker_name": ["Elite Clutch", "Accumulator", "Emerging Finisher", "Fringe"],
            "primary_role": ["Top Order", "Top Order", "Finisher", "Lower Order"],
            "matches_played": [50, 60, 12, 2],
            "comps_played": [4, 5, 2, 1],
            "bf_overall": [800, 1200, 150, 20],
            "runs_overall": [1200, 1600, 240, 20],
            "sr_overall": [150.0, 133.33, 160.0, 100.0],
            "dot_pct_overall": [32.0, 38.0, 30.0, 45.0],
            "bnd_pct_overall": [22.0, 16.0, 24.0, 10.0],
            "bf_clutch": [150, 250, 45, 8],
            "runs_clutch": [255, 300, 81, 6],
            "sr_clutch": [170.0, 120.0, 180.0, 75.0],
            "dot_pct_clutch": [30.0, 42.0, 28.0, 50.0],
            "bnd_pct_clutch": [25.0, 14.0, 26.0, 5.0],
            "rpd_clutch": [35.0, 22.0, 27.0, 6.0],
            "batting_clutch_index": [8.5, 2.5, 7.8, 4.0]
        })
        
        self.sample_bowlers = pd.DataFrame({
            "bowler_id": [101, 102, 103, 104],
            "bowler_name": ["Death Enforcer", "Run Machine", "Emerging Spinner", "Fringe"],
            "primary_bowling_role": ["Death Specialist", "Death Specialist", "Middle Enforcer", "Powerplay Specialist"],
            "matches_played": [45, 50, 15, 2],
            "comps_played": [4, 4, 2, 1],
            "legal_balls_overall": [900, 1000, 200, 24],
            "runs_conceded_overall": [1125, 1500, 240, 40],
            "economy_overall": [7.50, 9.00, 7.20, 10.00],
            "wickets_overall": [55, 40, 14, 1],
            "legal_balls_clutch": [200, 220, 50, 6],
            "economy_clutch": [8.20, 11.50, 6.80, 12.00],
            "delta_econ_phase_adj": [2.32, -1.50, 2.21, -2.50],
            "true_dot_pct_clutch": [38.0, 22.0, 36.0, 15.0],
            "bnd_pct_clutch": [16.0, 24.0, 14.0, 28.0],
            "wkt_pct_clutch": [8.5, 4.0, 8.0, 0.0],
            "wickets_clutch": [17, 9, 4, 0],
            "bowling_clutch_index": [8.2, 1.8, 7.5, 3.5]
        })

    def test_batter_reliability_scoring(self):
        """Verify evidence reliability scores and tier allocations for batters."""
        df_rel = calculate_batter_evidence_reliability(self.sample_batters)
        
        # Check range
        self.assertTrue((df_rel["evidence_reliability_score"] >= 0.0).all())
        self.assertTrue((df_rel["evidence_reliability_score"] <= 100.0).all())
        
        # Check tiers
        p1 = df_rel[df_rel["striker_id"] == 1].iloc[0]
        p4 = df_rel[df_rel["striker_id"] == 4].iloc[0]
        
        self.assertEqual(p1["evidence_tier"], "Strong Evidence")
        self.assertEqual(p4["evidence_tier"], "Not Eligible")
        self.assertTrue(p1["is_eligible_for_ranking"])
        self.assertFalse(p4["is_eligible_for_ranking"])

    def test_batting_performance_rating_bounds_and_ordering(self):
        """Verify performance rating bounds and tactical component sensitivity."""
        df_rated = calculate_batting_performance_rating(self.sample_batters)
        
        # Check bounds
        self.assertTrue((df_rated["performance_rating"] >= 0.0).all())
        self.assertTrue((df_rated["performance_rating"] <= 100.0).all())
        
        # Elite clutch batter should outrank accumulator
        p1_rating = df_rated[df_rated["striker_id"] == 1]["performance_rating"].iloc[0]
        p2_rating = df_rated[df_rated["striker_id"] == 2]["performance_rating"].iloc[0]
        self.assertGreater(p1_rating, p2_rating)

    def test_bowler_reliability_and_rating(self):
        """Verify bowler evidence tiers and run-control performance ratings."""
        df_rel = calculate_bowler_evidence_reliability(self.sample_bowlers)
        df_rated = calculate_bowling_performance_rating(df_rel)
        
        p101 = df_rated[df_rated["bowler_id"] == 101].iloc[0]
        p102 = df_rated[df_rated["bowler_id"] == 102].iloc[0]
        p104 = df_rated[df_rated["bowler_id"] == 104].iloc[0]
        
        self.assertEqual(p101["evidence_tier"], "Strong Evidence")
        self.assertEqual(p104["evidence_tier"], "Not Eligible")
        self.assertGreater(p101["performance_rating"], p102["performance_rating"])

    def test_ranking_eligibility_filter(self):
        """Verify that fringe players are strictly excluded from the main leaderboard."""
        df_b_rel = calculate_batter_evidence_reliability(self.sample_batters)
        df_b_rated = calculate_batting_performance_rating(df_b_rel)
        rankings = generate_batter_rankings(df_b_rated)
        
        main_ranks = rankings["overall_eligible"]
        self.assertNotIn(4, main_ranks["player_id"].values, "Fringe player (ID 4) must not appear in eligible ranks")
        self.assertEqual(len(main_ranks), 3, "Only eligible players (IDs 1, 2, 3) should appear")

    def test_sensitivity_stability(self):
        """Verify that alternative weighting scenarios produce coherent Spearman rank correlation."""
        df_b_rel = calculate_batter_evidence_reliability(self.sample_batters)
        df_b_rated = calculate_batting_performance_rating(df_b_rel)
        eligible = df_b_rated[df_b_rated["is_eligible_for_ranking"]].copy()
        
        summary_df, rank_comp = test_batter_weight_sensitivity(eligible)
        self.assertGreater(len(summary_df), 0)
        self.assertTrue((summary_df["Spearman_Rho"] >= 0.50).all())


if __name__ == "__main__":
    unittest.main()
