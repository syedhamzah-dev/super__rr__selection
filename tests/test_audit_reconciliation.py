"""
tests/test_audit_reconciliation.py
Automated forensic audit and delivery-level reconciliation tests for SupeRR Selector.
Verifies all cricket scoring identities, edge-case deliveries, dot-ball bifurcations,
wickets, eligibility counts, and sensitivity ranges.
"""

import unittest
import pandas as pd
import numpy as np


class TestAuditReconciliation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Load raw and processed datasets once for class-wide verification."""
        cls.df_raw = pd.read_csv("Data Pack/ball_by_ball.csv", low_memory=False)
        cls.df_pressure = pd.read_parquet("data/processed/ball_by_ball_pressure.parquet")
        cls.df_batter_ranks = pd.read_csv("data/processed/batter_player_rankings.csv")
        cls.df_bowler_ranks = pd.read_csv("data/processed/bowler_player_rankings.csv")
        cls.df_sensitivity = pd.read_csv("data/processed/player_ranking_sensitivity.csv")

    def test_balls_faced_and_deliveries_reconciliation(self):
        """Verify delivery volume, balls faced, wides, and no-balls."""
        total_deliveries = len(self.df_raw)
        self.assertEqual(total_deliveries, 200999)

        wides_count = (self.df_raw["extras_type"] == "wide").sum()
        self.assertEqual(wides_count, 7714)

        overstep_count = (self.df_raw["extras_type"] == "Overstep").sum()
        other_nb_count = (self.df_raw["extras_type"] == "other").sum()
        total_no_balls = overstep_count + other_nb_count
        self.assertEqual(overstep_count, 576)
        self.assertEqual(other_nb_count, 264)
        self.assertEqual(total_no_balls, 840)

        # Standard T20 scorecard balls faced: non-wides
        balls_faced = (self.df_raw["extras_type"] != "wide").sum()
        self.assertEqual(balls_faced, 193285)

        # Legal balls: deliveries that advance the over
        legal_balls = self.df_pressure["is_legal_ball"].sum()
        self.assertEqual(legal_balls, 192445)
        # 200,999 - 7,714 wides - 840 no-balls = 192,445 legal balls
        self.assertEqual(total_deliveries - wides_count - total_no_balls, legal_balls)

    def test_run_reconciliation_identities(self):
        """Verify exact run accounting across team runs, batter runs, extras, and bowler conceded."""
        total_bat_runs = self.df_raw["runs"].sum()
        self.assertEqual(total_bat_runs, 269550)

        e1 = self.df_raw["extras1_runs"].sum()
        e2 = self.df_raw["extras_2_runs"].sum()
        total_extras = e1 + e2
        self.assertEqual(total_extras, 14707)

        total_team_runs = total_bat_runs + total_extras
        self.assertEqual(total_team_runs, 284257)

        # Bowler conceded runs and fielding extras
        bowler_conceded = self.df_pressure["bowler_conceded_runs"].sum()
        self.assertEqual(bowler_conceded, 279649)

        fielding_extras = total_team_runs - bowler_conceded
        self.assertEqual(fielding_extras, 4608)

        # Reconcile fielding extras components
        byes_runs = self.df_raw[self.df_raw["extras_type"] == "byes"]["extras1_runs"].sum()
        legbyes_runs = self.df_raw[self.df_raw["extras_type"] == "legbyes"]["extras1_runs"].sum()
        penalty_runs = self.df_raw[self.df_raw["extras_type"] == "Penalty"]["extras1_runs"].sum()
        self.assertEqual(byes_runs, 1000)
        self.assertEqual(legbyes_runs, 3603)
        self.assertEqual(penalty_runs, 5)
        self.assertEqual(byes_runs + legbyes_runs + penalty_runs, 4608)

    def test_anomalous_deliveries_investigation(self):
        """Verify the exact records of the 3 source-level anomalous deliveries."""
        # Row 113765: Tagged 'legbyes', but bat run = 1, extras = 0
        r_lb = self.df_raw.loc[113765]
        self.assertEqual(r_lb["match_id"], 37099)
        self.assertEqual(r_lb["extras_type"], "legbyes")
        self.assertEqual(r_lb["runs"], 1)
        self.assertEqual(r_lb["extras1_runs"], 0)
        self.assertEqual(r_lb["extras_2_runs"], 0)

        # Total deliveries labeled 'legbyes' is 2,748
        # Deliveries with leg-byes extras > 0 is 2,747
        lb_labeled = (self.df_raw["extras_type"] == "legbyes").sum()
        lb_extras_conceded = ((self.df_raw["extras_type"] == "legbyes") & (self.df_raw["extras1_runs"] > 0)).sum()
        self.assertEqual(lb_labeled, 2748)
        self.assertEqual(lb_extras_conceded, 2747)

        # Rows 36854 & 107489: Unclassified extras (extras_type is NaN, but extras > 0)
        r_nan1 = self.df_raw.loc[36854]
        self.assertTrue(pd.isna(r_nan1["extras_type"]))
        self.assertEqual(r_nan1["extras_2_runs"], 1)

        r_nan2 = self.df_raw.loc[107489]
        self.assertTrue(pd.isna(r_nan2["extras_type"]))
        self.assertEqual(r_nan2["extras1_runs"], 1)

    def test_dot_ball_bifurcation(self):
        """Verify True Team Dots vs Bowler Scoreless Balls on legal deliveries."""
        legal = self.df_pressure["is_legal_ball"] == True
        true_team_dots = (legal & (self.df_pressure["total_runs"] == 0)).sum()
        bowler_scoreless = (legal & (self.df_pressure["bowler_conceded_runs"] == 0)).sum()

        self.assertEqual(true_team_dots, 68027)
        self.assertEqual(bowler_scoreless, 71304)
        # Difference is exactly the 3,277 fielding extra deliveries (byes/legbyes/penalty)
        self.assertEqual(bowler_scoreless - true_team_dots, 3277)

    def test_wickets_breakdown(self):
        """Verify bowler-credited wickets, individual dismissal modes, run-outs, and total dismissals."""
        caught = (self.df_pressure["dismissal_type"] == "Caught").sum()
        bowled = (self.df_pressure["dismissal_type"] == "Bowled").sum()
        lbw = (self.df_pressure["dismissal_type"] == "LBW").sum()
        stump = (self.df_pressure["dismissal_type"] == "Stump").sum()
        hit_wicket = (self.df_pressure["dismissal_type"] == "Hit Wicket").sum()

        # Exact delivery counts for bowler-credited dismissals
        self.assertEqual(caught, 7557, "Caught wickets must be exactly 7,557 (not 7,577)")
        self.assertEqual(bowled, 1775, "Bowled wickets must be exactly 1,775")
        self.assertEqual(lbw, 709, "LBW wickets must be exactly 709")
        self.assertEqual(stump, 214, "Stumped wickets must be exactly 214")
        self.assertEqual(hit_wicket, 17, "Hit Wicket dismissals must be exactly 17")

        bowler_wkts = caught + bowled + lbw + stump + hit_wicket
        self.assertEqual(bowler_wkts, 10272, "Total bowler-credited wickets must be exactly 10,272")

        run_outs = (self.df_pressure["dismissal_type"] == "RunOut").sum()
        self.assertEqual(run_outs, 600)

        retire_outs = (self.df_pressure["dismissal_type"] == "Retire Out").sum()
        self.assertEqual(retire_outs, 6)

        obstructing = self.df_pressure["dismissal_type"].str.lower().str.contains("obstr", na=False).sum()
        self.assertEqual(obstructing, 3)

        total_dismissals = self.df_pressure["is_wicket"].sum()
        self.assertEqual(total_dismissals, 10881)
        self.assertEqual(bowler_wkts + run_outs + retire_outs + obstructing, total_dismissals)

    def test_eligibility_and_ranking_integrity(self):
        """Verify eligible batter and bowler counts, uniqueness of player IDs, and sorting."""
        # Eligible batters count: 304
        self.assertEqual(len(self.df_batter_ranks), 304)
        # Check no duplicate player IDs
        self.assertEqual(self.df_batter_ranks["player_id"].nunique(), 304)
        # Check rank is strictly ascending 1..304
        self.assertEqual(list(self.df_batter_ranks["rank"]), list(range(1, 305)))
        # Check performance_rating is monotonically non-increasing
        self.assertTrue((self.df_batter_ranks["performance_rating"].diff().dropna() <= 0.001).all())

        # Eligible bowlers count: 290
        self.assertEqual(len(self.df_bowler_ranks), 290)
        # Check no duplicate player IDs
        self.assertEqual(self.df_bowler_ranks["player_id"].nunique(), 290)
        # Check rank is strictly ascending 1..290
        self.assertEqual(list(self.df_bowler_ranks["rank"]), list(range(1, 291)))
        # Check performance_rating is monotonically non-increasing
        self.assertTrue((self.df_bowler_ranks["performance_rating"].diff().dropna() <= 0.001).all())

    def test_sensitivity_metrics(self):
        """Verify sensitivity ranges, Spearman rho bounds, and Top 20 retention."""
        self.assertEqual(len(self.df_sensitivity), 6)
        # All Spearman correlations >= 0.9635
        self.assertTrue((self.df_sensitivity["Spearman_Rho"] >= 0.9635).all())

        # Top 20 retention ranges from 70% (14/20) to 90% (18/20)
        retentions = self.df_sensitivity["Top20_Retention"].tolist()
        self.assertIn("14/20", retentions)
        self.assertIn("18/20", retentions)
        self.assertIn("15/20", retentions)
        self.assertIn("17/20", retentions)

    def test_bowling_model_formula_verification(self):
        """Verify that exported bowler ratings were generated strictly by Model A (6 dimensions)."""
        df_bw = pd.read_parquet("data/processed/bowler_player_ratings.parquet")
        
        # Sub-scores for Model A (6 dimensions):
        sub_rc = np.clip((df_bw["delta_econ_phase_adj"] - (-3.0)) / (3.0 - (-3.0)) * 100.0, 0.0, 100.0)
        sub_dots = np.clip((df_bw["true_dot_pct_clutch"] - 15.0) / (50.0 - 15.0) * 100.0, 0.0, 100.0)
        sub_wkts = np.clip(df_bw["wkt_pct_clutch"] / 12.0 * 100.0, 0.0, 100.0)
        sub_bnd = np.clip((30.0 - df_bw["bnd_pct_clutch"]) / (30.0 - 10.0) * 100.0, 0.0, 100.0)
        sub_ovr = np.clip((11.0 - df_bw["economy_overall"]) / (11.0 - 6.0) * 100.0, 0.0, 100.0)
        sub_clutch = np.clip(df_bw["bowling_clutch_index"] * 10.0, 0.0, 100.0)
        
        model_a = np.round(
            0.25 * sub_rc + 0.20 * sub_dots + 0.20 * sub_wkts +
            0.15 * sub_bnd + 0.10 * sub_ovr + 0.10 * sub_clutch, 2
        )
        
        max_diff_a = np.abs(df_bw["performance_rating"] - model_a).max()
        self.assertLess(max_diff_a, 0.001, "Exported bowler rating must match Model A (6 dimensions) with 0 error")
        
        # Verify that Model B (5 dimensions) does NOT match
        sub_econ_inv = np.clip((12.0 - df_bw["economy_clutch"]) / (12.0 - 6.0) * 100.0, 0.0, 100.0)
        sub_bnd_b = np.clip((30.0 - df_bw["bnd_pct_clutch"]) / (30.0 - 8.0) * 100.0, 0.0, 100.0)
        sub_wkt_b = np.clip((df_bw["wkt_pct_clutch"] - 2.0) / (14.0 - 2.0) * 100.0, 0.0, 100.0)
        model_b = np.round(
            0.30 * sub_rc + 0.20 * sub_econ_inv + 0.20 * sub_dots +
            0.15 * sub_bnd_b + 0.15 * sub_wkt_b, 2
        )
        max_diff_b = np.abs(df_bw["performance_rating"] - model_b).max()
        self.assertGreater(max_diff_b, 10.0, "Model B (5 dimensions) must not match exported ratings")

    def test_sub_20_clutch_deliveries_exclusion(self):
        """Verify that players with 5-19 clutch deliveries are strictly excluded from rankings."""
        df_b = pd.read_parquet("data/processed/batter_player_ratings.parquet")
        df_bw = pd.read_parquet("data/processed/bowler_player_ratings.parquet")
        
        # Batters with 5 <= bf_clutch < 20 and ERS >= 20: exactly 44 players
        b_sub20 = df_b[(df_b["bf_clutch"] >= 5) & (df_b["bf_clutch"] < 20) & (df_b["evidence_reliability_score"] >= 20.0)]
        self.assertEqual(len(b_sub20), 44)
        self.assertTrue((b_sub20["is_eligible_for_ranking"] == False).all())
        self.assertTrue(b_sub20["evidence_tier"].isin(["Insufficient Evidence", "Not Eligible"]).all())
        
        # Bowlers with 5 <= legal_balls_clutch < 20 and ERS >= 20: exactly 29 players
        bw_sub20 = df_bw[(df_bw["legal_balls_clutch"] >= 5) & (df_bw["legal_balls_clutch"] < 20) & (df_bw["evidence_reliability_score"] >= 20.0)]
        self.assertEqual(len(bw_sub20), 29)
        self.assertTrue((bw_sub20["is_eligible_for_ranking"] == False).all())
        self.assertTrue(bw_sub20["evidence_tier"].isin(["Insufficient Evidence", "Not Eligible"]).all())

    def test_ers_targets_and_tier_reconciliation(self):
        """Verify linear ERS saturation targets (120, 300, 25, 3) and exact evidence tier distributions."""
        df_b = pd.read_parquet("data/processed/batter_player_ratings.parquet")
        df_bw = pd.read_parquet("data/processed/bowler_player_ratings.parquet")

        # Batter evidence tiers
        b_tiers = df_b["evidence_tier"].value_counts().to_dict()
        self.assertEqual(b_tiers.get("Strong Evidence", 0), 201)
        self.assertEqual(b_tiers.get("Moderate Evidence", 0), 103)
        self.assertEqual(b_tiers.get("Insufficient Evidence", 0), 163)
        self.assertEqual(b_tiers.get("Not Eligible", 0), 421)
        self.assertEqual(len(df_b), 888)
        self.assertEqual(df_b["is_eligible_for_ranking"].sum(), 304)

        # Bowler evidence tiers
        bw_tiers = df_bw["evidence_tier"].value_counts().to_dict()
        self.assertEqual(bw_tiers.get("Strong Evidence", 0), 206)
        self.assertEqual(bw_tiers.get("Moderate Evidence", 0), 84)
        self.assertEqual(bw_tiers.get("Insufficient Evidence", 0), 156)
        self.assertEqual(bw_tiers.get("Not Eligible", 0), 201)
        self.assertEqual(len(df_bw), 647)
        self.assertEqual(df_bw["is_eligible_for_ranking"].sum(), 290)

        # Verify linear ERS formulation on top batter
        top_b = df_b[df_b["striker_name"] == "Yashasvi Jaiswal"].iloc[0]
        s_clutch = min(top_b["bf_clutch"] / 120.0 * 100.0, 100.0)
        s_overall = min(top_b["bf_overall"] / 300.0 * 100.0, 100.0)
        s_matches = min(top_b["matches_played"] / 25.0 * 100.0, 100.0)
        s_comps = min(top_b["comps_played"] / 3.0 * 100.0, 100.0)
        expected_ers = round(0.40 * s_clutch + 0.25 * s_overall + 0.20 * s_matches + 0.15 * s_comps, 2)
        self.assertAlmostEqual(top_b["evidence_reliability_score"], expected_ers, places=2)


if __name__ == "__main__":
    unittest.main()
