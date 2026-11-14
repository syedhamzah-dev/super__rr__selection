"""
src/batter_pressure_analysis.py
SupeRR Selector - Batter Performance Under Pressure Module

This module evaluates batting performance across pressure tiers.
Key Rules:
1. Balls Faced: Wides are excluded. No-balls, byes, leg-byes, and standard deliveries count.
2. Dot Balls: Balls faced where batter_runs == 0.
3. Boundaries: Balls faced with four or six off the bat.
4. Dismissals: Deliveries where is_wicket == True and dismissed_player_id == striker_id.
5. Pressure Tiers: Low (<3.5), Medium (3.5-6.0), High (6.0-8.0), Extreme (>=8.0), Clutch (>=6.0).
"""

import numpy as np
import pandas as pd


def classify_batting_role(batting_order_series: pd.Series) -> pd.Series:
    """
    Classifies batting order position into tactical roles:
    - Top Order: Batting orders 1, 2, 3
    - Middle Order: Batting orders 4, 5
    - Finisher: Batting orders 6, 7
    - Lower Order: Batting orders 8, 9, 10, 11
    """
    vals = batting_order_series.fillna(5).values
    roles = np.where(
        vals <= 3, "Top Order",
        np.where(
            vals <= 5, "Middle Order",
            np.where(vals <= 7, "Finisher", "Lower Order")
        )
    )
    return pd.Series(roles, index=batting_order_series.index)


def _aggregate_batter_subset(subset: pd.DataFrame, prefix: str = "") -> pd.DataFrame:
    """Helper to aggregate batting volume, scoring, and boundary metrics for a slice."""
    if len(subset) == 0:
        return pd.DataFrame(columns=[
            "striker_id", f"bf_{prefix}", f"runs_{prefix}", f"sr_{prefix}",
            f"dot_pct_{prefix}", f"bnd_pct_{prefix}", f"fours_{prefix}",
            f"sixes_{prefix}", f"dismissals_{prefix}", f"bpd_{prefix}", f"rpd_{prefix}"
        ])

    grouped = subset.groupby("striker_id")
    agg = grouped.agg(
        bf=("is_ball_faced", "sum"),
        runs=("batter_runs", "sum"),
        dot_balls=("is_dot_batter", "sum"),
        boundary_balls=("is_boundary_batter", "sum"),
        fours=("is_four", "sum"),
        sixes=("is_six", "sum"),
        dismissals=("is_batter_dismissed", "sum")
    ).reset_index()

    agg[f"bf_{prefix}"] = agg["bf"]
    agg[f"runs_{prefix}"] = agg["runs"]
    agg[f"sr_{prefix}"] = np.round((agg["runs"] / np.maximum(agg["bf"], 1)) * 100.0, 2)
    agg[f"dot_pct_{prefix}"] = np.round((agg["dot_balls"] / np.maximum(agg["bf"], 1)) * 100.0, 2)
    agg[f"bnd_pct_{prefix}"] = np.round((agg["boundary_balls"] / np.maximum(agg["bf"], 1)) * 100.0, 2)
    agg[f"fours_{prefix}"] = agg["fours"]
    agg[f"sixes_{prefix}"] = agg["sixes"]
    agg[f"dismissals_{prefix}"] = agg["dismissals"]
    agg[f"bpd_{prefix}"] = np.round(agg["bf"] / np.maximum(agg["dismissals"], 1), 2)
    agg[f"rpd_{prefix}"] = np.round(agg["runs"] / np.maximum(agg["dismissals"], 1), 2)

    keep_cols = [
        "striker_id", f"bf_{prefix}", f"runs_{prefix}", f"sr_{prefix}",
        f"dot_pct_{prefix}", f"bnd_pct_{prefix}", f"fours_{prefix}",
        f"sixes_{prefix}", f"dismissals_{prefix}", f"bpd_{prefix}", f"rpd_{prefix}"
    ]
    return agg[keep_cols]


def calculate_batter_pressure_metrics(df_deliveries: pd.DataFrame) -> pd.DataFrame:
    """
    Computes complete batter metrics across all pressure tiers:
    Overall, Low (<3.5), Medium (3.5-6.0), High (6.0-8.0), Extreme (>=8.0), and Clutch (>=6.0).
    """
    df = df_deliveries.copy()

    # Cricket delivery flags
    df["is_ball_faced"] = df["extras_type"] != "wide"
    df["is_dot_batter"] = df["is_ball_faced"] & (df["batter_runs"] == 0)
    df["is_boundary_batter"] = df["is_ball_faced"] & (df["is_four"] | df["is_six"])
    df["is_batter_dismissed"] = (df["is_wicket"] == True) & (df["dismissed_player_id"] == df["striker_id"])

    # Batting role
    df["batting_role"] = classify_batting_role(df["batting_order"])

    # Filter to deliveries faced
    df_faced = df[df["is_ball_faced"]].copy()

    # Player profile metadata
    player_meta = df_faced.groupby("striker_id").agg(
        striker_name=("striker_name", "last"),
        batting_type=("batting_type", "last"),
        primary_role=("batting_role", lambda x: x.mode().iloc[0] if len(x) else "Middle Order"),
        matches_played=("match_id", "nunique"),
        comps_played=("comp_id", "nunique") if "comp_id" in df_faced.columns else ("match_id", lambda x: 1)
    ).reset_index()

    # Overall metrics
    overall_agg = _aggregate_batter_subset(df_faced, prefix="overall")

    # Pressure tier slices (using batting_pressure_index)
    pi = df_faced["batting_pressure_index"]
    low_agg = _aggregate_batter_subset(df_faced[pi < 3.5], prefix="low")
    med_agg = _aggregate_batter_subset(df_faced[(pi >= 3.5) & (pi < 6.0)], prefix="med")
    high_agg = _aggregate_batter_subset(df_faced[(pi >= 6.0) & (pi < 8.0)], prefix="high")
    ext_agg = _aggregate_batter_subset(df_faced[pi >= 8.0], prefix="ext")
    clutch_agg = _aggregate_batter_subset(df_faced[pi >= 6.0], prefix="clutch")

    # Combine all slices
    merged = player_meta.merge(overall_agg, on="striker_id", how="left")
    merged = merged.merge(low_agg, on="striker_id", how="left")
    merged = merged.merge(med_agg, on="striker_id", how="left")
    merged = merged.merge(high_agg, on="striker_id", how="left")
    merged = merged.merge(ext_agg, on="striker_id", how="left")
    merged = merged.merge(clutch_agg, on="striker_id", how="left")

    # Fill NaN for tiers where player had 0 balls
    fill_zero_cols = [c for c in merged.columns if c.startswith(("bf_", "runs_", "fours_", "sixes_", "dismissals_"))]
    merged[fill_zero_cols] = merged[fill_zero_cols].fillna(0).astype(int)

    fill_nan_cols = [c for c in merged.columns if c.startswith(("sr_", "dot_pct_", "bnd_pct_", "bpd_", "rpd_"))]
    merged[fill_nan_cols] = merged[fill_nan_cols].fillna(0.0)

    # Sort by total balls faced
    merged = merged.sort_values(by="bf_overall", ascending=False).reset_index(drop=True)
    return merged
