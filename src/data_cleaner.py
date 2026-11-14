"""
Data cleaning and anomaly resolution module.

Addresses verified data quality anomalies identified during exploratory analysis:
1. Deduplicating player entries in match 13613.
2. Correcting non-wicket false-positive and missing dismissal targets.
3. Extracting a unique team lookup to prevent cartesian join products.
"""

import numpy as np
import pandas as pd


def clean_playing_eleven(df: pd.DataFrame) -> pd.DataFrame:
    """Resolve duplicate player records in playing_eleven.csv.
    
    Match 13613 (Australia vs Sri Lanka, 2022-02-13 at Sydney) was a tied fixture decided
    by a Super Over. The raw data appended Super Over batting orders alongside regulation
    batting orders, causing 12 players to appear twice.
    
    We retain the first occurrence for each (match_id, player_id) pair to preserve the
    canonical regulation 11-player lineup and eliminate cartesian row multiplication during merges.
    """
    cleaned_df = df.copy()
    return cleaned_df.drop_duplicates(subset=['match_id', 'player_id'], keep='first')


def clean_ball_by_ball(df: pd.DataFrame) -> pd.DataFrame:
    # Resolve dismissal column inconsistencies in delivery records.
    
    
    
    cleaned_df = df.copy()
    
    # Reset phantom dismissal targets on deliveries where no wicket fell
    non_wicket_mask = (cleaned_df['is_wicket'] == False) & (cleaned_df['dismissal_type'].isnull())
    cleaned_df.loc[non_wicket_mask, 'dismissed_player_id'] = np.nan
    
    # Fill missing dismissed_player_id for the verified Retire Out delivery
    retire_out_mask = (cleaned_df['dismissal_type'].str.lower() == 'retire out') & (cleaned_df['dismissed_player_id'].isnull())
    cleaned_df.loc[retire_out_mask, 'dismissed_player_id'] = cleaned_df.loc[retire_out_mask, 'striker_id']
    
    return cleaned_df


def build_team_lookup(teams_df: pd.DataFrame) -> pd.DataFrame:
    """Extract a unique team_id to team_name mapping.
    
    teams.csv tracks team participation per tournament with a composite key on
    (comp_id, team_id). Joining matches on team_id alone causes many-to-many row
    multiplication. Deduplicating creates a safe 1:1 dimension lookup table.
    """
    return teams_df[['team_id', 'team_name']].drop_duplicates().reset_index(drop=True)
