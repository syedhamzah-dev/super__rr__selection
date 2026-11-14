"""
src/bowler_pressure_analysis.py
SupeRR Selector - Bowler Performance Under Pressure Module

This module evaluates bowling performance across pressure tiers.
Key Rules:
1. Legal Balls: Only deliveries where is_legal_ball == True advance overs bowled.
2. Bowler Conceded Runs: Excludes byes, leg-byes, and penalty extras.
3. Bowler Wickets: Excludes run-outs, retire-outs, and obstructing the field.
   Only Bowled, Caught, LBW, Stumped, and Hit Wicket count.
4. Dot Balls: Deliveries where bowler_conceded_runs == 0.
5. Boundaries Conceded: Deliveries with a four or six off the bowler.
6. Pressure Tiers: Low (<3.5), Medium (3.5-6.0), High (6.0-8.0), Extreme (>=8.0), Clutch (>=6.0).
   Evaluated strictly using bowling_pressure_index.
"""

import numpy as np
import pandas as pd


BOWLER_WICKET_TYPES = ["Caught", "Bowled", "LBW", "Stump", "Hit Wicket"]


def classify_bowling_role(pct_pp: float, pct_death: float, pct_mid: float) -> str:
    """Classifies bowler phase specialization based on delivery distribution."""
    if pct_pp >= 45.0:
        return "Powerplay Specialist"
    elif pct_death >= 30.0:
        return "Death Specialist"
    elif pct_mid >= 55.0:
        return "Middle Enforcer"
    else:
        return "All-Phase Bowler"


def _aggregate_bowler_subset(subset: pd.DataFrame, prefix: str = "") -> pd.DataFrame:
    """Helper to aggregate bowling volume, economy, dot%, and wickets for a slice."""
    if len(subset) == 0:
        return pd.DataFrame(columns=[
            "bowler_id", f"legal_balls_{prefix}", f"total_balls_{prefix}",
            f"runs_conceded_{prefix}", f"economy_{prefix}", f"dot_pct_{prefix}",
            f"bnd_pct_{prefix}", f"wickets_{prefix}", f"bowling_sr_{prefix}"
        ])

    grouped = subset.groupby("bowler_id")
    agg = grouped.agg(
        legal_balls=("is_legal_ball", "sum"),
        total_balls=("is_legal_ball", "count"),
        runs_conceded=("bowler_conceded_runs", "sum"),
        dot_balls=("is_dot_bowler", "sum"),
        boundary_balls=("is_boundary_conceded", "sum"),
        wickets=("is_bowler_wicket", "sum")
    ).reset_index()

    agg[f"legal_balls_{prefix}"] = agg["legal_balls"]
    agg[f"total_balls_{prefix}"] = agg["total_balls"]
    agg[f"runs_conceded_{prefix}"] = agg["runs_conceded"]
    agg[f"economy_{prefix}"] = np.round((agg["runs_conceded"] / np.maximum(agg["legal_balls"], 1)) * 6.0, 2)
    agg[f"dot_pct_{prefix}"] = np.round((agg["dot_balls"] / np.maximum(agg["total_balls"], 1)) * 100.0, 2)
    agg[f"bnd_pct_{prefix}"] = np.round((agg["boundary_balls"] / np.maximum(agg["total_balls"], 1)) * 100.0, 2)
    agg[f"wickets_{prefix}"] = agg["wickets"]
    agg[f"bowling_sr_{prefix}"] = np.round(agg["legal_balls"] / np.maximum(agg["wickets"], 1), 2)

    keep_cols = [
        "bowler_id", f"legal_balls_{prefix}", f"total_balls_{prefix}",
        f"runs_conceded_{prefix}", f"economy_{prefix}", f"dot_pct_{prefix}",
        f"bnd_pct_{prefix}", f"wickets_{prefix}", f"bowling_sr_{prefix}"
    ]
    return agg[keep_cols]


def calculate_bowler_pressure_metrics(df_deliveries: pd.DataFrame) -> pd.DataFrame:
    """
    Computes complete bowler metrics across all pressure tiers:
    Overall, Low (<3.5), Medium (3.5-6.0), High (6.0-8.0), Extreme (>=8.0), and Clutch (>=6.0).
    """
    df = df_deliveries.copy()

    # Cricket delivery flags
    df["is_dot_bowler"] = df["bowler_conceded_runs"] == 0
    df["is_boundary_conceded"] = df["is_four"] | df["is_six"]
    df["is_bowler_wicket"] = (df["is_wicket"] == True) & (df["dismissal_type"].isin(BOWLER_WICKET_TYPES))

    # Phase allocation flags
    df["is_pp"] = df["over_phase"] == "Powerplay"
    df["is_mid"] = df["over_phase"] == "Middle"
    df["is_death"] = df["over_phase"] == "Death"

    # Player profile metadata
    player_meta = df.groupby("bowler_id").agg(
        bowler_name=("bowler_name", "last"),
        bowling_type=("bowling_type", "last"),
        pace_or_spin=("pace_or_spin", "last"),
        matches_played=("match_id", "nunique"),
        comps_played=("comp_id", "nunique") if "comp_id" in df.columns else ("match_id", lambda x: 1),
        pp_balls=("is_pp", "sum"),
        mid_balls=("is_mid", "sum"),
        death_balls=("is_death", "sum"),
        total_legal=("is_legal_ball", "sum")
    ).reset_index()

    # Compute phase proportions
    player_meta["pct_powerplay"] = np.round((player_meta["pp_balls"] / np.maximum(player_meta["total_legal"], 1)) * 100.0, 1)
    player_meta["pct_middle"] = np.round((player_meta["mid_balls"] / np.maximum(player_meta["total_legal"], 1)) * 100.0, 1)
    player_meta["pct_death"] = np.round((player_meta["death_balls"] / np.maximum(player_meta["total_legal"], 1)) * 100.0, 1)

    # Classify bowling role
    roles = []
    for _, row in player_meta.iterrows():
        roles.append(classify_bowling_role(row["pct_powerplay"], row["pct_death"], row["pct_middle"]))
    player_meta["primary_bowling_role"] = roles

    # Overall metrics
    overall_agg = _aggregate_bowler_subset(df, prefix="overall")

    # Pressure tier slices (using bowling_pressure_index)
    pib = df["bowling_pressure_index"]
    low_agg = _aggregate_bowler_subset(df[pib < 3.5], prefix="low")
    med_agg = _aggregate_bowler_subset(df[(pib >= 3.5) & (pib < 6.0)], prefix="med")
    high_agg = _aggregate_bowler_subset(df[(pib >= 6.0) & (pib < 8.0)], prefix="high")
    ext_agg = _aggregate_bowler_subset(df[pib >= 8.0], prefix="ext")
    clutch_agg = _aggregate_bowler_subset(df[pib >= 6.0], prefix="clutch")

    # Combine all slices
    meta_cols = [
        "bowler_id", "bowler_name", "bowling_type", "pace_or_spin",
        "primary_bowling_role", "pct_powerplay", "pct_middle", "pct_death",
        "matches_played", "comps_played"
    ]
    merged = player_meta[meta_cols].merge(overall_agg, on="bowler_id", how="left")
    merged = merged.merge(low_agg, on="bowler_id", how="left")
    merged = merged.merge(med_agg, on="bowler_id", how="left")
    merged = merged.merge(high_agg, on="bowler_id", how="left")
    merged = merged.merge(ext_agg, on="bowler_id", how="left")
    merged = merged.merge(clutch_agg, on="bowler_id", how="left")

    # Fill NaN for tiers where bowler bowled 0 balls
    fill_zero_cols = [c for c in merged.columns if c.startswith(("legal_balls_", "total_balls_", "runs_conceded_", "wickets_"))]
    merged[fill_zero_cols] = merged[fill_zero_cols].fillna(0).astype(int)

    fill_nan_cols = [c for c in merged.columns if c.startswith(("economy_", "dot_pct_", "bnd_pct_", "bowling_sr_"))]
    merged[fill_nan_cols] = merged[fill_nan_cols].fillna(0.0)

    # Sort by total legal balls bowled
    merged = merged.sort_values(by="legal_balls_overall", ascending=False).reset_index(drop=True)
    return merged
