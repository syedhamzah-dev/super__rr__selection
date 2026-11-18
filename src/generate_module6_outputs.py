"""
src/generate_module6_outputs.py
SupeRR Selector - Module 6 Execution & Artifact Generation Script

This script runs the complete Module 6 statistical validation pipeline:
1. 1,000-replicate stratified match-cluster bootstrap for batters and bowlers.
2. Player rating uncertainty intervals (mean, median, std, 95% CI).
3. Ranking stability distributions and Top 5/10/20 retention frequencies.
4. Eligibility stability across bootstrap replicates.
5. Sample-size evidence threshold sensitivity testing across 6 scenarios.
6. Match influence, volume concentration (HHI), and Leave-One-Match-Out (LOMO) analysis.
7. Role and phase cohort robustness breakdowns.
8. Exports all processed data tables to data/processed/.
9. Generates all 6 publication-grade figures in reports/figures/.
"""

import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.bootstrap_validation import (
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


def run_pipeline():
    print("=" * 70)
    print("SupeRR Selector — Module 6: Statistical Validation & Robustness Pipeline")
    print("=" * 70)

    # 1. Load inputs
    print("\n[Step 1/6] Loading Module 4 and Module 5 processed inputs...")
    df_deliv = pd.read_parquet("data/processed/ball_by_ball_pressure.parquet")
    df_b_ratings = pd.read_parquet("data/processed/batter_player_ratings.parquet")
    df_bw_ratings = pd.read_parquet("data/processed/bowler_player_ratings.parquet")
    df_b_rankings = pd.read_csv("data/processed/batter_player_rankings.csv")
    df_bw_rankings = pd.read_csv("data/processed/bowler_player_rankings.csv")
    print(f"Loaded: {len(df_deliv)} deliveries, {len(df_b_ratings)} batters, {len(df_bw_ratings)} bowlers.")

    # 2. Run 1,000-replicate stratified match-cluster bootstrap
    print("\n[Step 2/6] Executing 1,000-replicate stratified match-cluster bootstrap (seed=42)...")
    t0 = time.time()
    boot_res = run_match_cluster_bootstrap(
        df_deliv, df_b_ratings, df_bw_ratings,
        n_replicates=1000, random_seed=42, stratify=True
    )
    t_boot = time.time() - t0
    print(f"Bootstrap complete: {boot_res['metadata']['successful_replicates']} replicates in {t_boot:.2f}s.")

    # 3. Summarize bootstrap uncertainty, ranking, and eligibility
    print("\n[Step 3/6] Computing uncertainty intervals, ranking stability, and eligibility...")
    b_uncertainty = summarize_player_rating_uncertainty(boot_res, df_b_ratings, discipline="batter")
    bw_uncertainty = summarize_player_rating_uncertainty(boot_res, df_bw_ratings, discipline="bowler")

    b_ranking_stab = summarize_ranking_stability(boot_res, df_b_rankings, discipline="batter")
    bw_ranking_stab = summarize_ranking_stability(boot_res, df_bw_rankings, discipline="bowler")

    b_elig_stab = summarize_eligibility_stability(boot_res, discipline="batter")
    bw_elig_stab = summarize_eligibility_stability(boot_res, discipline="bowler")

    # 4. Sensitivity, Influence, and Cohort Robustness
    print("\n[Step 4/6] Evaluating threshold sensitivity, match concentration, and LOMO...")
    sensitivity_df = evaluate_evidence_threshold_sensitivity(df_b_ratings, df_bw_ratings)
    
    b_conc = calculate_batter_match_concentration(df_deliv, df_b_rankings)
    bw_conc = calculate_bowler_match_concentration(df_deliv, df_bw_rankings)

    b_lomo, bw_lomo = evaluate_leave_one_match_out_sensitivity(
        df_deliv, df_b_ratings, df_bw_ratings, top_n=25
    )

    # Combine influence outputs
    b_lomo["discipline"] = "Batting"
    bw_lomo["discipline"] = "Bowling"
    b_lomo_renamed = b_lomo.rename(columns={"excluded_match_runs": "excluded_match_metric"})
    bw_lomo_renamed = bw_lomo.rename(columns={"excluded_match_wkts": "excluded_match_metric"})
    influence_lomo_df = pd.concat([b_lomo_renamed, bw_lomo_renamed], ignore_index=True)

    roles_dict = analyze_role_and_phase_robustness(df_b_ratings, df_bw_ratings)
    b_roles_df = roles_dict["batting_roles"]
    bw_roles_df = roles_dict["bowling_roles"]
    b_roles_df["discipline"] = "Batting"
    bw_roles_df["discipline"] = "Bowling"
    cohort_df = pd.concat([b_roles_df, bw_roles_df], ignore_index=True)

    # 5. Export processed datasets
    print("\n[Step 5/6] Exporting processed datasets to data/processed/...")
    exports = {
        "batter_rating_uncertainty": b_uncertainty,
        "bowler_rating_uncertainty": bw_uncertainty,
        "batter_ranking_stability": b_ranking_stab,
        "bowler_ranking_stability": bw_ranking_stab,
        "batter_eligibility_stability": b_elig_stab,
        "bowler_eligibility_stability": bw_elig_stab,
        "evidence_threshold_sensitivity": sensitivity_df,
        "match_influence_analysis": influence_lomo_df,
        "role_phase_robustness": cohort_df
    }

    for name, df_exp in exports.items():
        pq_path = f"data/processed/{name}.parquet"
        csv_path = f"data/processed/{name}.csv"
        df_exp.to_parquet(pq_path, index=False)
        df_exp.to_csv(csv_path, index=False)
        print(f"  - Exported {name}: {len(df_exp)} rows -> {pq_path} and {csv_path}")

    # 6. Generate Figures in reports/figures/
    print("\n[Step 6/6] Generating 6 publication-grade figures in reports/figures/...")
    os.makedirs("reports/figures", exist_ok=True)
    sns.set_theme(style="whitegrid", font="sans-serif")
    plt.rcParams.update({"font.size": 11, "axes.labelsize": 12, "axes.titlesize": 13})

    # Figure 1: Batter Rating Uncertainty Intervals
    fig, ax = plt.subplots(figsize=(10, 7))
    top_b = b_uncertainty[b_uncertainty["baseline_eligible"]].head(15).iloc[::-1]
    y_pos = np.arange(len(top_b))
    ax.errorbar(
        top_b["bootstrap_mean_rating"], y_pos,
        xerr=[top_b["bootstrap_mean_rating"] - top_b["rating_p025"], top_b["rating_p975"] - top_b["bootstrap_mean_rating"]],
        fmt='o', color="#1f77b4", ecolor="#aec7e8", elinewidth=3, capsize=4, label="Bootstrap Mean & 95% Percentile Interval"
    )
    ax.scatter(top_b["baseline_rating"], y_pos, color="#d62728", marker="s", s=40, zorder=5, label="Original Module 5 Rating")
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"{name} ({w:.1f})" for name, w in zip(top_b["player_name"], top_b["rating_ci_width"])])
    ax.set_xlabel("Batting Performance Rating (0.0 to 100.0)")
    ax.set_title("Figure 1: Batting Performance Rating 95% Bootstrap Uncertainty Intervals\n(Top 15 Eligible Batters, Values in Parentheses = 95% Interval Width)")
    ax.legend(loc="lower right")
    ax.set_xlim(30, 105)
    plt.tight_layout()
    plt.savefig("reports/figures/batter_rating_uncertainty_intervals.png", dpi=300)
    plt.close()
    print("  - Saved reports/figures/batter_rating_uncertainty_intervals.png")

    # Figure 2: Bowler Rating Uncertainty Intervals
    fig, ax = plt.subplots(figsize=(10, 7))
    top_bw = bw_uncertainty[bw_uncertainty["baseline_eligible"]].head(15).iloc[::-1]
    y_pos = np.arange(len(top_bw))
    ax.errorbar(
        top_bw["bootstrap_mean_rating"], y_pos,
        xerr=[top_bw["bootstrap_mean_rating"] - top_bw["rating_p025"], top_bw["rating_p975"] - top_bw["bootstrap_mean_rating"]],
        fmt='o', color="#2ca02c", ecolor="#98df8a", elinewidth=3, capsize=4, label="Bootstrap Mean & 95% Percentile Interval"
    )
    ax.scatter(top_bw["baseline_rating"], y_pos, color="#d62728", marker="s", s=40, zorder=5, label="Original Module 5 Rating")
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"{name} ({w:.1f})" for name, w in zip(top_bw["player_name"], top_bw["rating_ci_width"])])
    ax.set_xlabel("Bowling Performance Rating (0.0 to 100.0)")
    ax.set_title("Figure 2: Bowling Performance Rating 95% Bootstrap Uncertainty Intervals\n(Top 15 Eligible Bowlers, Values in Parentheses = 95% Interval Width)")
    ax.legend(loc="lower right")
    ax.set_xlim(30, 105)
    plt.tight_layout()
    plt.savefig("reports/figures/bowler_rating_uncertainty_intervals.png", dpi=300)
    plt.close()
    print("  - Saved reports/figures/bowler_rating_uncertainty_intervals.png")

    # Figure 3: Ranking Stability Distribution
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    top_b_stab = b_ranking_stab.head(12).iloc[::-1]
    y_pos1 = np.arange(len(top_b_stab))
    ax1.errorbar(
        top_b_stab["bootstrap_median_rank"], y_pos1,
        xerr=[top_b_stab["bootstrap_median_rank"] - top_b_stab["rank_p025"], top_b_stab["rank_p975"] - top_b_stab["bootstrap_median_rank"]],
        fmt='o', color="#1f77b4", ecolor="#aec7e8", elinewidth=2.5, capsize=4, label="Median & 95% Range"
    )
    ax1.scatter(top_b_stab["baseline_rank"], y_pos1, color="#d62728", marker="x", s=60, linewidths=2, label="Baseline Rank")
    ax1.set_yticks(y_pos1)
    ax1.set_yticklabels(top_b_stab["player_name"])
    ax1.set_xlabel("Eligible Leaderboard Rank")
    ax1.set_title("A: Leading Batters Rank Range")
    ax1.legend(loc="lower right")
    ax1.set_xlim(0, 100)

    top_bw_stab = bw_ranking_stab.head(12).iloc[::-1]
    y_pos2 = np.arange(len(top_bw_stab))
    ax2.errorbar(
        top_bw_stab["bootstrap_median_rank"], y_pos2,
        xerr=[top_bw_stab["bootstrap_median_rank"] - top_bw_stab["rank_p025"], top_bw_stab["rank_p975"] - top_bw_stab["bootstrap_median_rank"]],
        fmt='o', color="#2ca02c", ecolor="#98df8a", elinewidth=2.5, capsize=4, label="Median & 95% Range"
    )
    ax2.scatter(top_bw_stab["baseline_rank"], y_pos2, color="#d62728", marker="x", s=60, linewidths=2, label="Baseline Rank")
    ax2.set_yticks(y_pos2)
    ax2.set_yticklabels(top_bw_stab["player_name"])
    ax2.set_xlabel("Eligible Leaderboard Rank")
    ax2.set_title("B: Leading Bowlers Rank Range")
    ax2.legend(loc="lower right")
    ax2.set_xlim(0, 100)

    plt.suptitle("Figure 3: Leaderboard Ranking Stability Across 1,000 Historical Match Resamples", fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig("reports/figures/ranking_stability_distribution.png", dpi=300)
    plt.close()
    print("  - Saved reports/figures/ranking_stability_distribution.png")

    # Figure 4: Top Retention Comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    top10_b = b_ranking_stab.head(10)
    x = np.arange(len(top10_b))
    width = 0.25
    ax1.bar(x - width, top10_b["top5_freq_pct"], width, label="Top 5 Freq %", color="#1f77b4")
    ax1.bar(x, top10_b["top10_freq_pct"], width, label="Top 10 Freq %", color="#43a2ca")
    ax1.bar(x + width, top10_b["top20_freq_pct"], width, label="Top 20 Freq %", color="#a8ddb5")
    ax1.set_xticks(x)
    ax1.set_xticklabels(top10_b["player_name"], rotation=40, ha="right")
    ax1.set_ylabel("Replicate Appearance Frequency (%)")
    ax1.set_ylim(0, 105)
    ax1.set_title("A: Top 10 Batters Tier Retention")
    ax1.legend(loc="upper right")

    top10_bw = bw_ranking_stab.head(10)
    x2 = np.arange(len(top10_bw))
    ax2.bar(x2 - width, top10_bw["top5_freq_pct"], width, label="Top 5 Freq %", color="#2ca02c")
    ax2.bar(x2, top10_bw["top10_freq_pct"], width, label="Top 10 Freq %", color="#74c476")
    ax2.bar(x2 + width, top10_bw["top20_freq_pct"], width, label="Top 20 Freq %", color="#bae4b3")
    ax2.set_xticks(x2)
    ax2.set_xticklabels(top10_bw["player_name"], rotation=40, ha="right")
    ax2.set_ylabel("Replicate Appearance Frequency (%)")
    ax2.set_ylim(0, 105)
    ax2.set_title("B: Top 10 Bowlers Tier Retention")
    ax2.legend(loc="upper right")

    plt.suptitle("Figure 4: Frequency of Top-Tier Leaderboard Placement Across 1,000 Resamples", fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig("reports/figures/top_retention_comparison.png", dpi=300)
    plt.close()
    print("  - Saved reports/figures/top_retention_comparison.png")

    # Figure 5: Sample-Size Sensitivity Comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    sc_order = [
        "Low_Exposure_Probe", "Relaxed_Clutch_15", "Baseline",
        "High_Match_Breadth", "Strict_Clutch_30", "Strong_Evidence_Only"
    ]
    b_sens = sensitivity_df[sensitivity_df["Discipline"] == "Batting"].set_index("Scenario").loc[sc_order].reset_index()
    bw_sens = sensitivity_df[sensitivity_df["Discipline"] == "Bowling"].set_index("Scenario").loc[sc_order].reset_index()

    x = np.arange(len(sc_order))
    ax1.bar(x - 0.2, b_sens["Eligible_Count"], 0.4, label="Eligible Batters", color="#1f77b4")
    ax1.bar(x + 0.2, bw_sens["Eligible_Count"], 0.4, label="Eligible Bowlers", color="#2ca02c")
    ax1.set_xticks(x)
    ax1.set_xticklabels([s.replace("_", "\n") for s in sc_order], fontsize=10)
    ax1.set_ylabel("Number of Eligible Players")
    ax1.set_title("A: Eligible Cohort Size Across Evidence Thresholds")
    ax1.legend()

    # Top 20 retention
    b_top20_vals = [int(v.split("/")[0]) for v in b_sens["Top20_Retention"]]
    bw_top20_vals = [int(v.split("/")[0]) for v in bw_sens["Top20_Retention"]]
    ax2.plot(x, b_top20_vals, marker="o", linewidth=2.5, markersize=8, color="#1f77b4", label="Batting Top 20 Retention")
    ax2.plot(x, bw_top20_vals, marker="s", linewidth=2.5, markersize=8, color="#2ca02c", label="Bowling Top 20 Retention")
    ax2.set_xticks(x)
    ax2.set_xticklabels([s.replace("_", "\n") for s in sc_order], fontsize=10)
    ax2.set_ylabel("Retained Players (out of 20)")
    ax2.set_ylim(8, 21)
    ax2.set_title("B: Baseline Top 20 Retention in Candidate Pool")
    ax2.legend()

    plt.suptitle("Figure 5: Sensitivity of Eligible Cohorts and Top 20 Retention to Evidence Thresholds", fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig("reports/figures/sample_size_sensitivity.png", dpi=300)
    plt.close()
    print("  - Saved reports/figures/sample_size_sensitivity.png")

    # Figure 6: Match Influence and Volume Concentration
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Batter concentration
    sc1 = ax1.scatter(
        b_conc["clutch_volume_hhi"], b_conc["performance_rating"],
        s=b_conc["clutch_bf_total"] * 0.8, c=b_conc["top_match_run_share"],
        cmap="coolwarm", alpha=0.7, edgecolors="grey", linewidth=0.5
    )
    cbar1 = plt.colorbar(sc1, ax=ax1)
    cbar1.set_label("Top Match Clutch Run Share (%)")
    ax1.set_xlabel("Clutch Delivery Herfindahl-Hirschman Index (HHI)")
    ax1.set_ylabel("Batting Performance Rating")
    ax1.set_title("A: Batting Rating vs Clutch Match Concentration\n(Bubble Size = Clutch Balls Faced)")
    ax1.axvline(0.30, color="grey", linestyle="--", alpha=0.6, label="HHI = 0.30 Threshold")
    
    # Annotate key batters
    notable_b = ["Yashasvi Jaiswal", "Finn Allen", "Vipraj Nigam", "Naman Dhir", "Mahipal Lomror", "Tim David"]
    for _, row in b_conc[b_conc["player_name"].isin(notable_b)].iterrows():
        ax1.annotate(
            row["player_name"], (row["clutch_volume_hhi"], row["performance_rating"]),
            xytext=(6, 4), textcoords="offset points", fontsize=9, fontweight="bold"
        )
    ax1.legend(loc="lower left")

    # Bowler concentration
    sc2 = ax2.scatter(
        bw_conc["clutch_volume_hhi"], bw_conc["performance_rating"],
        s=bw_conc["clutch_lb_total"] * 0.8, c=bw_conc["top_match_wkt_share"],
        cmap="viridis", alpha=0.7, edgecolors="grey", linewidth=0.5
    )
    cbar2 = plt.colorbar(sc2, ax=ax2)
    cbar2.set_label("Top Match Clutch Wicket Share (%)")
    ax2.set_xlabel("Clutch Delivery Herfindahl-Hirschman Index (HHI)")
    ax2.set_ylabel("Bowling Performance Rating")
    ax2.set_title("B: Bowling Rating vs Clutch Match Concentration\n(Bubble Size = Clutch Legal Balls)")
    ax2.axvline(0.30, color="grey", linestyle="--", alpha=0.6, label="HHI = 0.30 Threshold")

    notable_bw = ["Chris Woakes", "Sufiyan Muqeem", "George Dockrell", "Imad Wasim", "Matthew Humphreys", "Jasprit Bumrah"]
    for _, row in bw_conc[bw_conc["player_name"].isin(notable_bw)].iterrows():
        ax2.annotate(
            row["player_name"], (row["clutch_volume_hhi"], row["performance_rating"]),
            xytext=(6, 4), textcoords="offset points", fontsize=9, fontweight="bold"
        )
    ax2.legend(loc="lower left")

    plt.suptitle("Figure 6: Match Concentration Diagnostics and Outlier Influence Mapping", fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig("reports/figures/match_influence_concentration.png", dpi=300)
    plt.close()
    print("  - Saved reports/figures/match_influence_concentration.png")

    print("\n" + "=" * 70)
    print("Module 6 Pipeline Execution Successfully Completed!")
    print("=" * 70)


if __name__ == "__main__":
    run_pipeline()
