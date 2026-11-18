"""
src/reliability_scoring.py
SupeRR Selector - Evidence Reliability Scoring Module

This module calculates the Evidence Reliability Score (ERS in [0.0, 100.0]) and
categorizes players into evidence tiers based on sample volume, match breadth,
and competition coverage.

Key Philosophy:
- Performance Rating measures HOW WELL a player performed.
- Evidence Reliability measures HOW MUCH CONFIDENCE we have in that rating.
These two concepts must remain strictly distinct.
"""

import numpy as np
import pandas as pd


def calculate_batter_evidence_reliability(df_batter: pd.DataFrame) -> pd.DataFrame:
    """
    Computes Evidence Reliability Score (ERS) for batters.
    
    Dimensions:
    1. Clutch Sample Volume (40%): Saturation benchmark at 120 clutch balls faced.
    2. Overall Sample Volume (25%): Saturation benchmark at 300 total balls faced.
    3. Match Breadth (20%): Saturation benchmark at 25 matches played.
    4. Competition Depth (15%): Saturation benchmark at 3 distinct competitions.
    
    ERS in [0.0, 100.0].
    
    Evidence Tiers:
    - Strong Evidence: ERS >= 60.0 AND bf_clutch >= 40 AND matches_played >= 10
    - Moderate Evidence: ERS >= 35.0 AND bf_clutch >= 20 AND matches_played >= 5
    - Insufficient Evidence: bf_overall >= 30 AND bf_clutch >= 10 (sample too noisy)
    - Not Eligible: bf_overall < 30 OR bf_clutch < 10 (fringe appearances)
    """
    df = df_batter.copy()
    
    # Volume and coverage saturation functions
    f_clutch = np.clip(df["bf_clutch"] / 120.0 * 100.0, 0.0, 100.0)
    f_overall = np.clip(df["bf_overall"] / 300.0 * 100.0, 0.0, 100.0)
    f_matches = np.clip(df["matches_played"] / 25.0 * 100.0, 0.0, 100.0)
    f_comps = np.clip(df["comps_played"] / 3.0 * 100.0, 0.0, 100.0)
    
    ers = 0.40 * f_clutch + 0.25 * f_overall + 0.20 * f_matches + 0.15 * f_comps
    df["evidence_reliability_score"] = np.round(ers, 2)
    
    # Assign discrete evidence tiers
    tiers = []
    for _, row in df.iterrows():
        s = row["evidence_reliability_score"]
        c = row["bf_clutch"]
        o = row["bf_overall"]
        m = row["matches_played"]
        
        if s >= 60.0 and c >= 40 and m >= 10:
            tiers.append("Strong Evidence")
        elif s >= 35.0 and c >= 20 and m >= 5:
            tiers.append("Moderate Evidence")
        elif o >= 30 and c >= 10:
            tiers.append("Insufficient Evidence")
        else:
            tiers.append("Not Eligible")
            
    df["evidence_tier"] = tiers
    df["is_eligible_for_ranking"] = df["evidence_tier"].isin(["Strong Evidence", "Moderate Evidence"])
    return df


def calculate_bowler_evidence_reliability(df_bowler: pd.DataFrame) -> pd.DataFrame:
    """
    Computes Evidence Reliability Score (ERS) for bowlers.
    
    Dimensions:
    1. Clutch Sample Volume (40%): Saturation benchmark at 120 clutch legal balls bowled.
    2. Overall Sample Volume (25%): Saturation benchmark at 300 total legal balls bowled.
    3. Match Breadth (20%): Saturation benchmark at 25 matches played.
    4. Competition Depth (15%): Saturation benchmark at 3 distinct competitions.
    
    ERS in [0.0, 100.0].
    
    Evidence Tiers:
    - Strong Evidence: ERS >= 60.0 AND legal_balls_clutch >= 40 AND matches_played >= 10
    - Moderate Evidence: ERS >= 35.0 AND legal_balls_clutch >= 20 AND matches_played >= 5
    - Insufficient Evidence: legal_balls_overall >= 30 AND legal_balls_clutch >= 10
    - Not Eligible: legal_balls_overall < 30 OR legal_balls_clutch < 10
    """
    df = df_bowler.copy()
    
    f_clutch = np.clip(df["legal_balls_clutch"] / 120.0 * 100.0, 0.0, 100.0)
    f_overall = np.clip(df["legal_balls_overall"] / 300.0 * 100.0, 0.0, 100.0)
    f_matches = np.clip(df["matches_played"] / 25.0 * 100.0, 0.0, 100.0)
    f_comps = np.clip(df["comps_played"] / 3.0 * 100.0, 0.0, 100.0)
    
    ers = 0.40 * f_clutch + 0.25 * f_overall + 0.20 * f_matches + 0.15 * f_comps
    df["evidence_reliability_score"] = np.round(ers, 2)
    
    tiers = []
    for _, row in df.iterrows():
        s = row["evidence_reliability_score"]
        c = row["legal_balls_clutch"]
        o = row["legal_balls_overall"]
        m = row["matches_played"]
        
        if s >= 60.0 and c >= 40 and m >= 10:
            tiers.append("Strong Evidence")
        elif s >= 35.0 and c >= 20 and m >= 5:
            tiers.append("Moderate Evidence")
        elif o >= 30 and c >= 10:
            tiers.append("Insufficient Evidence")
        else:
            tiers.append("Not Eligible")
            
    df["evidence_tier"] = tiers
    df["is_eligible_for_ranking"] = df["evidence_tier"].isin(["Strong Evidence", "Moderate Evidence"])
    return df
