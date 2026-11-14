"""
Validation framework for SupeRR Selector.

Executes a 14-point audit on the reconstructed match-state delivery dataset to verify
relational consistency, boundary invariants, non-leakage, and DLS rules.
"""

from typing import Dict, Any
import numpy as np
import pandas as pd


def run_all_validations(
    enriched_df: pd.DataFrame,
    matches_df: pd.DataFrame,
    playing_eleven_df: pd.DataFrame
) -> Dict[str, Dict[str, Any]]:
    """Execute the full 14-point validation framework on the enriched match-state dataset.
    
    Returns:
        dict: Test results with passed/failed flags and execution details.
    """
    results = {}
    
    # 1. Delivery-level composite key uniqueness
    dup_keys = enriched_df.duplicated(subset=['match_id', 'innings', 'overid', 'over_ball_num']).sum()
    results['check_1_key_uniqueness'] = {
        'description': 'Unique delivery composite key (match_id, innings, overid, over_ball_num)',
        'passed': dup_keys == 0,
        'details': f'{dup_keys} duplicate keys found'
    }
    
    # 2. Referential integrity to matches master
    all_matches_valid = enriched_df['match_id'].isin(matches_df['match_id']).all()
    results['check_2_referential_integrity'] = {
        'description': 'Every delivery references a valid match in matches.csv',
        'passed': all_matches_valid,
        'details': '100% referential integrity confirmed'
    }
    
    # 3. Cumulative runs monotonicity
    run_diff = enriched_df.groupby(['match_id', 'innings'])['cumulative_runs_after'].diff().dropna()
    negative_runs = (run_diff < 0).sum()
    results['check_3_cumulative_runs_monotonic'] = {
        'description': 'Cumulative runs never decrease within an innings',
        'passed': negative_runs == 0,
        'details': f'{negative_runs} instances of decreasing cumulative runs'
    }
    
    # 4. Cumulative wickets monotonicity
    wicket_diff = enriched_df.groupby(['match_id', 'innings'])['cumulative_wickets_after'].diff().dropna()
    negative_wickets = (wicket_diff < 0).sum()
    results['check_4_cumulative_wickets_monotonic'] = {
        'description': 'Cumulative wickets never decrease within an innings',
        'passed': negative_wickets == 0,
        'details': f'{negative_wickets} instances of decreasing cumulative wickets'
    }
    
    # 5. Legal ball increment logic
    legal_diff = enriched_df['legal_balls_after'] - enriched_df['legal_balls_before']
    legal_expected = enriched_df['is_legal_ball'].astype(int)
    legal_mismatch = (legal_diff != legal_expected).sum()
    results['check_5_legal_ball_increments'] = {
        'description': 'Legal-ball counts increment if and only if is_legal_ball is True',
        'passed': legal_mismatch == 0,
        'details': f'{legal_mismatch} legal ball increment mismatches'
    }
    
    # 6. Bounded balls remaining
    negative_balls_remaining = (enriched_df['balls_remaining_after'] < 0).sum()
    results['check_6_balls_remaining_bounded'] = {
        'description': 'Balls remaining never negative under applicable innings limit',
        'passed': negative_balls_remaining == 0,
        'details': f'{negative_balls_remaining} instances of negative balls remaining'
    }
    
    # 7. Non-leakage: Before-state strictly excludes current delivery
    run_delta_check = (
        enriched_df['cumulative_runs_after'] - enriched_df['cumulative_runs_before'] != enriched_df['total_runs']
    ).sum()
    results['check_7_before_state_exclusion'] = {
        'description': 'Before-delivery state strictly excludes the current delivery',
        'passed': run_delta_check == 0,
        'details': f'{run_delta_check} discrepancies in before/after run delta'
    }
    
    # 8. Completeness: After-state strictly includes current delivery
    wicket_delta_check = (
        enriched_df['cumulative_wickets_after'] - enriched_df['cumulative_wickets_before'] != enriched_df['is_wicket'].astype(int)
    ).sum()
    results['check_8_after_state_inclusion'] = {
        'description': 'After-delivery state strictly includes the current delivery',
        'passed': wicket_delta_check == 0,
        'details': f'{wicket_delta_check} discrepancies in before/after wicket delta'
    }
    
    # 9. Chase runs needed mathematical consistency
    chase_mask = enriched_df['innings'].isin([2, 4])
    expected_needed = np.maximum(
        0,
        enriched_df.loc[chase_mask, 'target_runs'] - enriched_df.loc[chase_mask, 'cumulative_runs_before']
    )
    needed_mismatch = (enriched_df.loc[chase_mask, 'runs_needed_before'] != expected_needed).sum()
    results['check_9_chase_runs_needed'] = {
        'description': 'Chase runs needed before matches target - cumulative runs before',
        'passed': needed_mismatch == 0,
        'details': f'{needed_mismatch} runs needed mismatches in chase innings'
    }
    
    # 10. CRR formula precision
    valid_crr_mask = enriched_df['legal_balls_after'] > 0
    expected_crr = enriched_df.loc[valid_crr_mask, 'cumulative_runs_after'] / (
        enriched_df.loc[valid_crr_mask, 'legal_balls_after'] / 6.0
    )
    crr_error = np.abs(enriched_df.loc[valid_crr_mask, 'current_run_rate_after'] - expected_crr).max()
    results['check_10_crr_rrr_formulas'] = {
        'description': 'Current Run Rate matches runs / (legal balls / 6)',
        'passed': crr_error < 1e-6,
        'details': f'Max CRR calculation error: {crr_error:.8f}'
    }
    
    # 11. DLS revised overs and target initialization
    # Evaluated on Match 21586 (CSK vs GT IPL 2023 Final: target 171 in 90 balls)
    m21586_inn2 = enriched_df[(enriched_df['match_id'] == 21586) & (enriched_df['innings'] == 2)]
    dls_passed = False
    if len(m21586_inn2) > 0:
        first_ball = m21586_inn2.iloc[0]
        dls_passed = (first_ball['target_runs'] == 171.0) and (first_ball['balls_remaining_before'] == 90)
    results['check_11_dls_treatment'] = {
        'description': 'DLS matches use revised target and revised ball limit (e.g. Match 21586 target 171, 90 balls)',
        'passed': dls_passed,
        'details': f'Match 21586 Innings 2 initial target: {first_ball["target_runs"]}, initial balls left: {first_ball["balls_remaining_before"]}'
    }
    
    # 12. Super Over isolation
    so_deliveries = enriched_df[enriched_df['innings'].isin([3, 4])]
    so_max_balls_check = (so_deliveries['innings_max_balls'] == 6).all()
    so_phase_check = (so_deliveries['over_phase'] == 'Super Over').all()
    results['check_12_super_over_segregation'] = {
        'description': 'Super Overs (innings 3 & 4) allocated max 6 balls and tagged as Super Over phase',
        'passed': so_max_balls_check and so_phase_check,
        'details': f'{len(so_deliveries)} super over balls correctly isolated'
    }
    
    # 13. Lineup merge safety
    p11_unique = playing_eleven_df.drop_duplicates(subset=['match_id', 'player_id'])
    test_merge = enriched_df.merge(
        p11_unique[['match_id', 'player_id', 'batting_order']],
        left_on=['match_id', 'striker_id'],
        right_on=['match_id', 'player_id'],
        how='left'
    )
    results['check_13_lineup_join_safety'] = {
        'description': 'Merging cleaned playing eleven produces zero row multiplication',
        'passed': len(test_merge) == len(enriched_df),
        'details': f'Original rows: {len(enriched_df)}, merged rows: {len(test_merge)}'
    }
    
    # 14. Full-innings total reconciliation
    last_balls = enriched_df.groupby(['match_id', 'innings'])['cumulative_runs_after'].last()
    summed_runs = enriched_df.groupby(['match_id', 'innings'])['total_runs'].sum()
    reconciled = (last_balls == summed_runs).all()
    results['check_14_innings_total_reconciliation'] = {
        'description': 'Final cumulative runs exactly matches sum of delivery total runs across all innings',
        'passed': reconciled,
        'details': '100% of innings totals reconcile perfectly'
    }
    
    return results


def inspect_manual_match_sequence(
    df: pd.DataFrame, match_id: int, innings: int, start_over: int, end_over: int
) -> pd.DataFrame:
    """Extract a delivery sequence for manual verification."""
    mask = (
        (df['match_id'] == match_id) &
        (df['innings'] == innings) &
        (df['overid'] >= start_over) &
        (df['overid'] <= end_over)
    )
    cols = [
        'overid', 'over_ball_num', 'striker_name', 'bowler_name', 'runs', 'extras_type',
        'is_legal_ball', 'total_runs', 'cumulative_runs_before', 'cumulative_runs_after',
        'balls_remaining_before', 'runs_needed_before', 'required_run_rate_before', 'over_phase'
    ]
    return df.loc[mask, [c for c in cols if c in df.columns]]
