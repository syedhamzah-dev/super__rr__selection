"""
src/pressure_model.py
SupeRR Selector - Pressure Index Mathematical Modelling

This module implements the delivery-level Pressure Index (PI) engine.
It evaluates match pressure strictly before each ball is bowled, combining:
1. Chasing Pressure: Demand-to-Capacity ratio, RRR intensity, wicket fragility, and late urgency.
2. First-Innings Pressure: Projected score par deficit, collapse severity, and death-over demands.
3. Bowling-Side Pressure: Contestability in chases, defending thin margins, and death-over assault defense.
4. Super Over Pressure: Separate physical constraints (6 legal balls, max 2 wickets).

All metrics are continuous, normalized between 0.0 and 10.0, and free from outcome leakage.
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional
from src.pressure_calibration import parametric_resource_function


def _sigmoid(x: np.ndarray) -> np.ndarray:
    """Stable logistic sigmoid function for non-linear saturation."""
    return 1.0 / (1.0 + np.exp(-x))


def calculate_chasing_pressure(
    runs_needed: np.ndarray,
    balls_rem: np.ndarray,
    wickets_hand: np.ndarray,
    rrr: np.ndarray,
    e_rem: np.ndarray
) -> np.ndarray:
    """
    Computes chasing batting pressure (Innings 2 & Innings 4).
    
    Cricket Logic:
    - Pressure is NOT just RRR. A team needing 12 RPO with 8 wickets in hand
      has vastly more resources than a team needing 12 RPO with 2 wickets in hand.
    - We compare scoring demand (runs_needed) against empirical capacity (e_rem).
    - If runs_needed <= 0 (target achieved), pressure is strictly 0.0.
    
    Mathematical Formulation:
    Demand Ratio: D = runs_needed / max(e_rem, 1.0)
    RRR Component: RRR_norm = clip(rrr / 16.0, 0.0, 1.25)
    Wicket Depletion: W_dep = (10 - wickets_hand) / 9.0
    Balls Elapsed: B_elap = 1.0 - (balls_rem / 120.0)
    
    PI_chase = 4.5 * sigmoid(2.2 * (D - 1.0)) + 3.2 * RRR_norm + 2.3 * (W_dep * B_elap)
    """
    safe_demand = np.maximum(runs_needed, 0.0)
    d_ratio = np.clip(safe_demand / np.maximum(e_rem, 1.0), 0.0, 3.0)
    rrr_norm = np.clip(rrr / 16.0, 0.0, 1.25)
    w_dep = (10.0 - wickets_hand) / 9.0
    b_elap = 1.0 - np.clip(balls_rem / 120.0, 0.0, 1.0)

    score = (
        4.5 * _sigmoid(2.2 * (d_ratio - 1.0))
        + 3.2 * rrr_norm
        + 2.3 * (w_dep * b_elap)
    )

    # Physical boundary: if target already achieved before this delivery, pressure is 0.0
    score = np.where(runs_needed <= 0, 0.0, score)
    return np.clip(score, 0.0, 10.0)


def calculate_first_innings_pressure(
    cum_runs_before: np.ndarray,
    balls_rem: np.ndarray,
    wickets_hand: np.ndarray,
    e_rem: np.ndarray,
    par_total: np.ndarray,
    over_phase: np.ndarray
) -> np.ndarray:
    """
    Computes first-innings batting pressure (Innings 1).
    
    Cricket Logic:
    - There is no fixed target in the first innings, so we must not fabricate an artificial RRR.
    - Instead, pressure is driven by:
      1. Par Deficit: Projected final score vs historical format par total (~183 for IPL, ~167 for T20I).
      2. Collapse Severity: Losing early wickets severely constrains batting freedom and risks all-out.
      3. Death Overs Acceleration: The tactical demand to score at 10.5+ RPO in overs 16-20.
    
    Mathematical Formulation:
    Projected Total: P = cum_runs_before + e_rem
    Par Gap: Delta_Par = par_total - P
    Collapse Severity: C_sev = ((10 - wickets_hand) / 9.0) * (balls_rem / 120.0)^0.75
    Death Demand: A_death = 1.5 if Phase == 'Death' else 0.0
    
    PI_inn1 = 4.0 + 3.5 * clip(Delta_Par / 35.0, -1.2, 1.5) + 2.5 * C_sev + A_death
    """
    proj_total = cum_runs_before + e_rem
    par_gap = par_total - proj_total
    norm_par_gap = np.clip(par_gap / 35.0, -1.2, 1.5)

    w_lost = (10.0 - wickets_hand) / 9.0
    b_frac = np.clip(balls_rem / 120.0, 0.0, 1.0)
    c_sev = w_lost * (b_frac ** 0.75)

    # Death overs acceleration incentive (overs 16-20)
    death_mask = (over_phase == "Death")
    death_progress = np.clip((120.0 - balls_rem - 90.0) / 30.0, 0.0, 1.0)
    a_death = np.where(death_mask, death_progress * 1.5, 0.0)

    score = 4.0 + 3.5 * norm_par_gap + 2.5 * c_sev + a_death
    return np.clip(score, 0.0, 10.0)


def calculate_bowling_pressure(
    innings: np.ndarray,
    runs_needed: np.ndarray,
    balls_rem: np.ndarray,
    wickets_hand: np.ndarray,
    rrr: np.ndarray,
    e_rem: np.ndarray,
    par_gap: np.ndarray,
    over_phase: np.ndarray,
    batting_pi: np.ndarray
) -> np.ndarray:
    """
    Computes bowling-side pressure (Fielding team).
    
    Cricket Logic:
    - Bowling pressure is NOT simply (10 - batting_pressure).
    - When batting pressure is 10 (e.g. needing 40 off 6 balls), bowling pressure is ~0 (comfortable defense).
    - When batting pressure is 0 (needing 5 off 40 balls with 9 wickets), bowling pressure is also low (game lost).
    - Bowling pressure PEAKS when:
      1. In a chase: The match is tight / contestable (runs_needed ~ e_rem), RRR is in striking distance (7-14),
         and balls remaining are few (defending narrow margins).
      2. In first innings: The opponent is scoring heavily above par (negative par_gap) and launching
         a death overs assault with wickets in hand.
    """
    # Innings 2 Chasing Bowling Pressure
    safe_demand = np.maximum(runs_needed, 0.0)
    d_ratio = np.clip(safe_demand / np.maximum(e_rem, 1.0), 0.0, 3.0)
    b_elap = 1.0 - np.clip(balls_rem / 120.0, 0.0, 1.0)

    # Contestability curve: peaks around D = 1.0 (50/50 balance)
    contestability = np.exp(-((d_ratio - 1.0) ** 2) / 0.5)

    # Death-overs defensive stakes (defending with balls running out)
    stakes = b_elap * np.clip(wickets_hand / 7.0, 0.4, 1.2)

    # RRR sweet spot for bowler anxiety (run rate between 6 and 14 is dangerous)
    rrr_sweet_spot = np.clip((rrr - 5.0) / 8.0, 0.0, 1.0) * (1.0 - np.clip((rrr - 16.0) / 10.0, 0.0, 1.0))

    bowl_chase = (
        4.5 * contestability * (0.4 + 0.6 * b_elap)
        + 3.5 * rrr_sweet_spot
        + 2.0 * stakes
    )
    bowl_chase = np.where(runs_needed <= 0, 0.0, bowl_chase)

    # Innings 1 Bowling Pressure: Defending against above-par totals
    norm_par_gap = np.clip(par_gap / 35.0, -1.2, 1.5)
    death_mask = (over_phase == "Death")
    death_progress = np.clip((120.0 - balls_rem - 90.0) / 30.0, 0.0, 1.0)
    a_death = np.where(death_mask, death_progress * 1.5, 0.0)

    # Negative par gap means opponent is above par -> higher bowling pressure
    bowl_inn1 = (
        4.0
        - 3.2 * norm_par_gap
        + 1.8 * (wickets_hand / 10.0)
        + a_death
    )

    # Super over bowling pressure (high intensity mirror)
    bowl_so = np.clip(batting_pi * 0.95 + 0.5, 7.5, 10.0)

    bowl_score = np.where(
        innings == 1, bowl_inn1,
        np.where(innings == 2, bowl_chase, bowl_so)
    )
    return np.clip(bowl_score, 0.0, 10.0)


def calculate_super_over_pressure(
    innings: np.ndarray,
    cum_wickets_before: np.ndarray,
    balls_rem: np.ndarray,
    runs_needed: np.ndarray
) -> np.ndarray:
    """
    Computes Super Over pressure respecting physical constraints:
    - Exactly 6 legal balls.
    - Exactly 2 wickets maximum.
    - Every delivery is an inherently High to Extreme pressure situation ([7.5, 10.0]).
    """
    # Innings 3 (1st Super Over): Maximize score, 2 wickets capacity
    w_lost = np.clip(cum_wickets_before / 2.0, 0.0, 1.0)
    b_used = np.clip((6.0 - balls_rem) / 6.0, 0.0, 1.0)
    so_inn3 = 7.5 + 1.5 * w_lost + 1.0 * b_used

    # Innings 4 (2nd Super Over chase): Target chase in 6 balls
    so_inn4 = 7.5 + 2.5 * np.clip(runs_needed / np.maximum(balls_rem * 2.5, 1.0), 0.0, 1.0)

    return np.where(innings == 3, so_inn3, so_inn4)


def calculate_delivery_pressure(
    df: pd.DataFrame,
    calibrated_params: Optional[Dict[str, Dict[str, float]]] = None
) -> pd.DataFrame:
    """
    Master pipeline function that calculates the complete delivery-level Pressure Index.
    
    Enriches the input DataFrame with:
    - expected_remaining_runs: Empirical scoring capacity based on match state.
    - projected_final_score: Projected 1st innings total.
    - par_score_gap: Difference against format par score.
    - chase_demand_ratio: Required runs / Expected capacity (innings 2).
    - batting_pressure_index: Continuous PI [0.0, 10.0] for batting side.
    - bowling_pressure_index: Continuous PI [0.0, 10.0] for bowling side.
    - pressure_index: Primary context-aware PI (batting PI for batters).
    - pressure_category: Categorical classification (Low, Medium, High, Extreme).
    - pressure_category_bowl: Categorical classification for bowlers.
    """
    df_out = df.copy()

    # Default calibrated parameters if not supplied
    if calibrated_params is None:
        calibrated_params = {
            "T20": {"a": 184.9, "beta": 0.688, "gamma": 0.608, "par_total": 183.0},
            "T20I": {"a": 171.7, "beta": 0.704, "gamma": 0.476, "par_total": 167.0}
        }

    # Ensure match_format exists
    if "match_format" not in df_out.columns:
        df_out["match_format"] = "T20"

    is_t20 = (df_out["match_format"] == "T20").values
    p_t20 = calibrated_params.get("T20", {"a": 184.9, "beta": 0.688, "gamma": 0.608, "par_total": 183.0})
    p_t20i = calibrated_params.get("T20I", {"a": 171.7, "beta": 0.704, "gamma": 0.476, "par_total": 167.0})

    a = np.where(is_t20, p_t20["a"], p_t20i["a"])
    beta = np.where(is_t20, p_t20["beta"], p_t20i["beta"])
    gamma = np.where(is_t20, p_t20["gamma"], p_t20i["gamma"])
    par_total = np.where(is_t20, p_t20["par_total"], p_t20i["par_total"])

    balls_rem = np.maximum(df_out["balls_remaining_before"].values, 0.0)
    wickets_hand = np.maximum(df_out["wickets_in_hand_before"].values, 0.0)
    innings = df_out["innings"].values
    runs_needed = np.maximum(df_out["runs_needed_before"].fillna(0.0).values, 0.0)
    rrr = np.maximum(df_out["required_run_rate_before"].fillna(0.0).values, 0.0)
    cum_runs_before = df_out["cumulative_runs_before"].values
    cum_wickets_before = df_out["cumulative_wickets_before"].values
    over_phase = df_out["over_phase"].values

    # 1. Expected remaining runs
    e_rem = parametric_resource_function(balls_rem, wickets_hand, a, beta, gamma)
    df_out["expected_remaining_runs"] = np.round(e_rem, 2)

    # 2. Projected 1st innings total and par gap
    proj_total = cum_runs_before + e_rem
    par_gap = par_total - proj_total
    df_out["projected_final_score"] = np.where(innings == 1, np.round(proj_total, 1), np.nan)
    df_out["par_score_gap"] = np.where(innings == 1, np.round(par_gap, 1), np.nan)

    # 3. Chase demand ratio
    d_ratio = np.where(
        innings == 2,
        np.round(runs_needed / np.maximum(e_rem, 1.0), 3),
        np.nan
    )
    df_out["chase_demand_ratio"] = d_ratio

    # 4. Batting Pressure Calculation
    p_chase = calculate_chasing_pressure(runs_needed, balls_rem, wickets_hand, rrr, e_rem)
    p_inn1 = calculate_first_innings_pressure(cum_runs_before, balls_rem, wickets_hand, e_rem, par_total, over_phase)
    p_so = calculate_super_over_pressure(innings, cum_wickets_before, balls_rem, runs_needed)

    bat_pi = np.where(
        innings == 1, p_inn1,
        np.where(innings == 2, p_chase, p_so)
    )
    df_out["batting_pressure_index"] = np.round(np.clip(bat_pi, 0.0, 10.0), 2)

    # 5. Bowling Pressure Calculation
    bowl_pi = calculate_bowling_pressure(
        innings, runs_needed, balls_rem, wickets_hand, rrr, e_rem,
        np.nan_to_num(par_gap, nan=0.0), over_phase, bat_pi
    )
    df_out["bowling_pressure_index"] = np.round(np.clip(bowl_pi, 0.0, 10.0), 2)

    # Unified primary pressure index
    df_out["pressure_index"] = df_out["batting_pressure_index"]

    # 6. Categorical classifications
    def _categorize(p_vals):
        return np.where(
            p_vals < 3.5, "Low",
            np.where(
                p_vals < 6.0, "Medium",
                np.where(p_vals < 8.0, "High", "Extreme")
            )
        )

    df_out["pressure_category"] = _categorize(df_out["pressure_index"].values)
    df_out["pressure_category_bowl"] = _categorize(df_out["bowling_pressure_index"].values)

    return df_out
