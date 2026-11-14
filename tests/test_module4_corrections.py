"""
tests/test_module4_corrections.py
Regression and methodology validation test suite for Module 4 corrections.
"""

import unittest
import numpy as np
import pandas as pd

from src.batter_pressure_analysis import calculate_batter_pressure_metrics, classify_batting_role
from src.bowler_pressure_analysis import calculate_bowler_pressure_metrics, classify_bowling_role
from src.clutch_analysis import calculate_batting_clutch_index, calculate_bowling_clutch_index


class TestModule4Corrections(unittest.TestCase):

    def setUp(self):
        """Create a synthetic delivery dataset with known edge cases."""
        # 10 synthetic deliveries:
        # 1: Legal dot ball (0 runs)
        # 2: Legal single (1 bat run)
        # 3: Legal four (4 bat runs)
        # 4: Wide ball (1 wide extra, 0 bat runs, illegal ball)
        # 5: No-ball overstep with 4 bat runs (1 extra, 4 bat runs, illegal ball)
        # 6: Legal ball with 4 byes (0 bat runs, 0 bowler runs, 4 total runs)
        # 7: Legal ball with 1 leg-bye (0 bat runs, 0 bowler runs, 1 total run)
        # 8: Legal wicket bowled (0 bat runs, 0 bowler runs, bowler wicket)
        # 9: No-ball with 0 bat runs (1 extra, 0 bat runs, illegal ball)
        # 10: Legal six (6 bat runs)
        self.sample_df = pd.DataFrame({
            "match_id": [1] * 10,
            "comp_id": [101] * 10,
            "striker_id": [100] * 10,
            "striker_name": ["Test Batter"] * 10,
            "batting_type": ["RHB"] * 10,
            "batting_order": [3] * 10,
            "bowler_id": [200] * 10,
            "bowler_name": ["Test Bowler"] * 10,
            "bowling_type": ["RF"] * 10,
            "pace_or_spin": ["Pace"] * 10,
            "over_phase": ["Powerplay", "Powerplay", "Middle", "Middle", "Middle", "Middle", "Death", "Death", "Death", "Death"],
            "is_legal_ball": [True, True, True, False, False, True, True, True, False, True],
            "extras_type": [None, None, None, "wide", "Overstep", "byes", "legbyes", None, "Overstep", None],
            "batter_runs": [0, 1, 4, 0, 4, 0, 0, 0, 0, 6],
            "bowler_conceded_runs": [0, 1, 4, 1, 5, 0, 0, 0, 1, 6],
            "total_runs": [0, 1, 4, 1, 5, 4, 1, 0, 1, 6],
            "is_four": [False, False, True, False, True, False, False, False, False, False],
            "is_six": [False, False, False, False, False, False, False, False, False, True],
            "is_wicket": [False, False, False, False, False, False, False, True, False, False],
            "dismissal_type": [None, None, None, None, None, None, None, "Bowled", None, None],
            "dismissed_player_id": [None, None, None, None, None, None, None, 100, None, None],
            "batting_pressure_index": [2.0, 2.5, 4.0, 4.0, 5.0, 5.5, 6.5, 7.0, 8.5, 9.0],
            "bowling_pressure_index": [2.0, 2.5, 4.0, 4.0, 5.0, 5.5, 6.5, 7.0, 8.5, 9.0],
        })

    def test_batter_balls_faced_excludes_no_balls(self):
        """Verify that balls faced counts strictly legal balls and excludes no-balls."""
        batter_metrics = calculate_batter_pressure_metrics(self.sample_df)
        b = batter_metrics.iloc[0]

        # In our 10 deliveries:
        # Wides: 1 (ball 4) -> excluded from striker deliveries
        # No-balls: 2 (balls 5 and 9) -> faced by striker, but illegal deliveries
        # Legal balls faced: 7 (balls 1, 2, 3, 6, 7, 8, 10)
        self.assertEqual(b["bf_overall"], 7, "Balls faced must exclude no-balls and wides")

    def test_batter_runs_preserves_runs_on_no_balls(self):
        """Verify that bat runs scored on no-balls are credited to career runs."""
        batter_metrics = calculate_batter_pressure_metrics(self.sample_df)
        b = batter_metrics.iloc[0]

        # Total bat runs: 0 + 1 + 4 + 0 + 4 (on no-ball!) + 0 + 0 + 0 + 0 (on no-ball) + 6 = 15 runs
        self.assertEqual(b["runs_overall"], 15, "Bat runs on no-balls must be credited to batter runs")
        # Strike rate = (15 / 7) * 100 = 214.29
        self.assertAlmostEqual(b["sr_overall"], 214.29, places=2)

    def test_batter_dots_definition(self):
        """Verify dot balls are legal deliveries faced where batter runs == 0."""
        batter_metrics = calculate_batter_pressure_metrics(self.sample_df)
        b = batter_metrics.iloc[0]

        # Legal balls where batter runs == 0:
        # Ball 1 (dot), Ball 6 (byes), Ball 7 (legbyes), Ball 8 (wicket bowled) -> 4 dot balls
        # (Ball 9 had 0 bat runs, but was a no-ball, so it cannot be a legal dot ball)
        self.assertEqual(b["dot_pct_overall"], round((4 / 7) * 100.0, 2))

    def test_bowler_dots_bifurcation(self):
        """Verify distinction between True Team Dots (total_runs == 0) and Bowler Scoreless Balls."""
        bowler_metrics = calculate_bowler_pressure_metrics(self.sample_df)
        bw = bowler_metrics.iloc[0]

        # Legal deliveries: 7 (balls 1, 2, 3, 6, 7, 8, 10)
        # True dots (total_runs == 0): Ball 1, Ball 8 -> 2 true dots
        # Scoreless balls (bowler_conceded_runs == 0): Ball 1, Ball 6 (byes), Ball 7 (legbyes), Ball 8 -> 4 scoreless balls
        expected_true_dot_pct = round((2 / 7) * 100.0, 2)
        expected_scoreless_pct = round((4 / 7) * 100.0, 2)

        self.assertEqual(bw["true_dot_pct_overall"], expected_true_dot_pct)
        self.assertEqual(bw["scoreless_pct_overall"], expected_scoreless_pct)
        self.assertNotEqual(bw["true_dot_pct_overall"], bw["scoreless_pct_overall"])

    def test_bowler_clutch_phase_adjustment(self):
        """Verify phase-adjusted economy in bowling clutch model."""
        bowler_metrics = calculate_bowler_pressure_metrics(self.sample_df)
        clutch_df = calculate_bowling_clutch_index(bowler_metrics)
        bw = clutch_df.iloc[0]

        # Check that econ_clutch_expected and delta_econ_phase_adj exist and are finite
        self.assertTrue(np.isfinite(bw["econ_clutch_expected"]))
        self.assertTrue(np.isfinite(bw["delta_econ_phase_adj"]))
        self.assertTrue(0.0 <= bw["bowling_clutch_index"] <= 10.0)

    def test_credibility_weighting_bounds(self):
        """Verify credibility weighting w = n / (n + 30) smoothly bounds scores."""
        batter_metrics = calculate_batter_pressure_metrics(self.sample_df)
        clutch_bat = calculate_batting_clutch_index(batter_metrics)
        b = clutch_bat.iloc[0]

        self.assertTrue(0.0 <= b["credibility_weight"] <= 1.0)
        self.assertTrue(0.0 <= b["batting_clutch_index"] <= 10.0)


if __name__ == "__main__":
    unittest.main()
