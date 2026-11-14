"""
Data ingestion module for SupeRR Selector.

Provides centralized path resolution and loading for the six raw cricket CSV datasets
while guaranteeing original raw files are preserved untouched.
"""

import os
from typing import Dict
import pandas as pd


def get_data_dir() -> str:
    """Resolve the raw data directory path dynamically.
    
    Notebooks in notebooks/ and scripts in the repository root run with different
    working directories. Checking both levels avoids hardcoded paths.
    """
    if os.path.exists("Data Pack"):
        return "Data Pack"
    elif os.path.exists(os.path.join("..", "Data Pack")):
        return os.path.join("..", "Data Pack")
    raise FileNotFoundError("Could not locate 'Data Pack' directory. Please verify repository structure.")


def load_raw_datasets() -> Dict[str, pd.DataFrame]:
    """Load all six raw CSV datasets without altering original files.
    
    Uses low_memory=False on delivery and lineup tables because mixed historical types
    in optional columns can trigger chunking warnings during automated loading.
    """
    data_dir = get_data_dir()
    return {
        "competitions": pd.read_csv(os.path.join(data_dir, "competitions.csv")),
        "teams": pd.read_csv(os.path.join(data_dir, "teams.csv")),
        "matches": pd.read_csv(os.path.join(data_dir, "matches.csv")),
        "playing_eleven": pd.read_csv(os.path.join(data_dir, "playing_eleven.csv"), low_memory=False),
        "player_mapping": pd.read_csv(os.path.join(data_dir, "competition_team_player_mapping.csv")),
        "ball_by_ball": pd.read_csv(os.path.join(data_dir, "ball_by_ball.csv"), low_memory=False)
    }
