"""
Match-state reconstruction engine.

Transforms static delivery-level records into a dynamic timeline with live
cumulative scoreboards, legal ball tracking, resources remaining, and chase rates.
"""

import numpy as np
import pandas as pd


def compute_legal_deliveries(df: pd.DataFrame) -> pd.Series:
    """Identify legal deliveries that count towards the 6-ball over limit.
    
    In cricket rules, wides and no-balls must be re-bowled and do not consume a legal delivery:
    - 'wide' indicates wide deliveries.
    - 'Overstep' indicates front-foot no-balls.
    - 'other' indicates non-overstep no-balls (e.g. waist-high full tosses).
    Byes, leg-byes, and penalty runs are legal deliveries that consume balls.
    """
    return ~df['extras_type'].isin(['wide', 'Overstep', 'other'])


def compute_run_components(df: pd.DataFrame) -> pd.DataFrame:
    """Separate ball runs into total runs, batter runs, and bowler-conceded runs.
    
    - total_runs: all runs scored on the delivery (runs off bat + all extras).
    - batter_runs: only runs struck directly off the bat.
    - bowler_conceded_runs: excludes fielding extras (byes, leg-byes, and penalties),
      which are team fielding errors rather than bowling performance flaws.
    """
    df = df.copy()
    df['total_runs'] = df['runs'] + df['extras1_runs'] + df['extras_2_runs']
    df['batter_runs'] = df['runs']
    
    fielding_extras_mask = df['extras_type'].isin(['byes', 'legbyes', 'Penalty'])
    df['bowler_conceded_runs'] = np.where(
        fielding_extras_mask,
        df['runs'],
        df['runs'] + df['extras1_runs'] + df['extras_2_runs']
    )
    return df


def reconstruct_match_state(ball_by_ball_df: pd.DataFrame, matches_df: pd.DataFrame) -> pd.DataFrame:
    """Reconstruct live match situation before and after every delivery.
    
    Calculates cumulative scores, resources remaining, run rates, and chase dynamics
    while respecting DLS rain adjustments and Super Over rules.
    """
    df = ball_by_ball_df.copy()
    df = df.sort_values(['match_id', 'innings', 'overid', 'over_ball_num']).reset_index(drop=True)
    
    df['is_legal_ball'] = compute_legal_deliveries(df)
    df = compute_run_components(df)
    
    # Merge match context for rain-revised overs and DLS targets
    match_cols = ['match_id', 'first_inn_revised_overs', 'second_inn_revised_overs', 'revised_target']
    df = df.merge(matches_df[match_cols], on='match_id', how='left')
    
    # Cumulative progression within (match_id, innings)
    grouped = df.groupby(['match_id', 'innings'])
    
    # Subtracting current delivery ensures the 'before' state strictly excludes current-ball events
    df['cumulative_runs_after'] = grouped['total_runs'].cumsum()
    df['cumulative_runs_before'] = df['cumulative_runs_after'] - df['total_runs']
    
    df['cumulative_wickets_after'] = grouped['is_wicket'].cumsum()
    df['cumulative_wickets_before'] = df['cumulative_wickets_after'] - df['is_wicket'].astype(int)
    
    df['legal_balls_after'] = grouped['is_legal_ball'].cumsum()
    df['legal_balls_before'] = df['legal_balls_after'] - df['is_legal_ball'].astype(int)
    
    # Maximum legal balls allowed for the innings (B_max)
    # In this dataset, revised overs columns store ball counts (e.g. 90.0 balls = 15 overs)
    inn1_limit = np.where(
        df['first_inn_revised_overs'].notnull() & (df['first_inn_revised_overs'] > 0),
        df['first_inn_revised_overs'],
        120.0
    )
    inn2_limit = np.where(
        df['second_inn_revised_overs'].notnull() & (df['second_inn_revised_overs'] > 0),
        df['second_inn_revised_overs'],
        120.0
    )
    
    max_balls = np.where(
        df['innings'] == 1, inn1_limit,
        np.where(df['innings'] == 2, inn2_limit,
        np.where(df['innings'].isin([3, 4]), 6.0, 120.0))
    )
    df['innings_max_balls'] = max_balls.astype(int)
    
    # Remaining legal balls and wickets in hand
    df['balls_remaining_before'] = np.maximum(0, df['innings_max_balls'] - df['legal_balls_before'])
    df['balls_remaining_after'] = np.maximum(0, df['innings_max_balls'] - df['legal_balls_after'])
    
    max_wickets = np.where(df['innings'].isin([3, 4]), 2, 10)  # Super Over permits only 2 dismissals
    df['wickets_in_hand_before'] = np.maximum(0, max_wickets - df['cumulative_wickets_before'])
    df['wickets_in_hand_after'] = np.maximum(0, max_wickets - df['cumulative_wickets_after'])
    
    # Current Run Rate (runs per 6 legal balls bowled)
    df['current_run_rate_before'] = np.where(
        df['legal_balls_before'] > 0,
        df['cumulative_runs_before'] / (df['legal_balls_before'] / 6.0),
        0.0
    )
    df['current_run_rate_after'] = np.where(
        df['legal_balls_after'] > 0,
        df['cumulative_runs_after'] / (df['legal_balls_after'] / 6.0),
        0.0
    )
    
    # Second innings chase dynamics
    inn1_totals = df[df['innings'] == 1].groupby('match_id')['total_runs'].sum().rename('first_innings_total')
    df = df.merge(inn1_totals, on='match_id', how='left')
    
    inn3_totals = df[df['innings'] == 3].groupby('match_id')['total_runs'].sum().rename('super_over_inn3_total')
    df = df.merge(inn3_totals, on='match_id', how='left')
    
    # In standard chases, target is 1st innings total + 1; in DLS matches, revised_target overrides
    inn2_target = np.where(
        df['revised_target'].notnull() & (df['revised_target'] > 0),
        df['revised_target'],
        df['first_innings_total'] + 1
    )
    inn4_target = df['super_over_inn3_total'] + 1
    
    df['target_runs'] = np.where(
        df['innings'] == 2, inn2_target,
        np.where(df['innings'] == 4, inn4_target, np.nan)
    )
    
    # Runs needed in chase
    is_chase = df['innings'].isin([2, 4])
    df['runs_needed_before'] = np.where(
        is_chase,
        np.maximum(0, df['target_runs'] - df['cumulative_runs_before']),
        np.nan
    )
    df['runs_needed_after'] = np.where(
        is_chase,
        np.maximum(0, df['target_runs'] - df['cumulative_runs_after']),
        np.nan
    )
    
    # Required Run Rate (runs required per 6 legal balls remaining)
    # When target is reached, RRR is 0. When 0 balls remain with runs needed, RRR is undefined (NaN)
    df['required_run_rate_before'] = np.where(
        ~is_chase, np.nan,
        np.where(df['runs_needed_before'] <= 0, 0.0,
        np.where(df['balls_remaining_before'] > 0,
                 df['runs_needed_before'] / (df['balls_remaining_before'] / 6.0),
                 np.nan))
    )
    df['required_run_rate_after'] = np.where(
        ~is_chase, np.nan,
        np.where(df['runs_needed_after'] <= 0, 0.0,
        np.where(df['balls_remaining_after'] > 0,
                 df['runs_needed_after'] / (df['balls_remaining_after'] / 6.0),
                 np.nan))
    )
    
    # Run rate pressure differential (positive values indicate batting team is behind required rate)
    df['run_rate_difference'] = np.where(
        is_chase,
        df['required_run_rate_before'] - df['current_run_rate_before'],
        np.nan
    )
    
    # Tactical over phase classification
    df['over_phase'] = np.where(
        df['innings'].isin([3, 4]), 'Super Over',
        np.where(df['overid'] <= 6, 'Powerplay',
        np.where(df['overid'] <= 15, 'Middle', 'Death'))
    )
    
    # Drop intermediate calculation columns
    drop_cols = ['first_inn_revised_overs', 'second_inn_revised_overs', 'revised_target', 'super_over_inn3_total']
    return df.drop(columns=[c for c in drop_cols if c in df.columns])
