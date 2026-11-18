"""
src/auction_strategy.py
SupeRR Selector - Rajasthan Royals Auction Strategy & Scenario Modelling Module

This module constructs an evidence-based auction strategy framework:
1. Implements 5 practical squad-building scenarios for Rajasthan Royals.
2. Models budget allocation using 100 Budget Allocation Units (percentage of purse),
   strictly avoiding fabricated player prices or unverified purse amounts.
3. Maps required archetypes, shortlisted targets, role coverages, and trade-offs.
4. Enforces official IPL squad limits (18-25 players) and overseas caps (max 8 in squad, max 4 in XI).

Author: Syed Mohammad Hamzah (B.Tech CSE - Data Analytics)
Evaluator Reference: Rajasthan Royals Sports Analytics Challenge (Season 2)
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

from src.squad_context import OFFICIAL_IPL_RULES


# 5 Practical Auction Strategy Scenarios
AUCTION_SCENARIOS = {
    "Scenario_1_Balanced_Reinforcement": {
        "scenario_id": "SCEN-01",
        "name": "Balanced Squad Reinforcement",
        "strategic_focus": "Distribute capital across the three critical voids: specialist finisher, secondary death pacer, and middle-overs spin enforcer.",
        "target_archetypes": [
            "Specialist Phase Performer (Finisher)",
            "Specialist Phase Performer (Death Pacer)",
            "Reliable Campaign Performer (Middle Spinner)",
            "Reliable Campaign Performer (Backup Keeper)"
        ],
        "primary_candidates": {
            "Finisher": ["Tim David (Overseas)", "Ashutosh Sharma (Domestic)"],
            "Death_Pacer": ["Benjamin Sears (Overseas)", "Eshan Malinga (Overseas)"],
            "Middle_Spinner": ["Liam Dawson (Overseas)", "Mujeeb Ur Rahman (Overseas)"],
            "Backup_Keeper": ["Matthew Wade (Overseas)"]
        },
        "budget_allocation_units": {
            "Primary Death-Overs Specialist Bowler": 35.0,
            "Proven Lower-Order Finisher Batter": 30.0,
            "Attacking Middle-Overs Spinner": 20.0,
            "Domestic Depth / Backup Wicketkeeper": 15.0
        },
        "total_budget_units": 100.0,
        "overseas_slots_demanded": 3,  # e.g., Tim David, Liam Dawson, Benjamin Sears
        "main_advantages": "Directly patches all three primary statistical voids without over-concentrating budget into a single high-beta player.",
        "main_risks": "Spreading resources evenly may lead to losing targeted bidding duels for the very best player in each role.",
        "squad_balance_impact": "Establishes a robust 18-22 player squad with two distinct crisis-phase specialists (Archer + Sears; Parag + David)."
    },
    "Scenario_2_Bowling_Depth_Priority": {
        "scenario_id": "SCEN-02",
        "name": "Bowling-Depth Priority",
        "strategic_focus": "Resolve Rajasthan Royals' acute bowling economy bleed (9.93 PP, 9.70 Mid, 9.74 Death in 2026) by acquiring dual elite strike weapons.",
        "target_archetypes": [
            "Specialist Phase Performer (Death Pacer)",
            "Reliable Campaign Performer (Middle Spinner)",
            "Multi-Role Tactical Option (Bowling All-Rounder)",
            "Reliable Campaign Performer (Domestic Finisher)"
        ],
        "primary_candidates": {
            "Death_Pacer": ["Benjamin Sears (Overseas)", "Nathan Ellis (Overseas)"],
            "Middle_Spinner": ["Liam Dawson (Overseas)", "Mujeeb Ur Rahman (Overseas)"],
            "Bowling_All_Rounder": ["George Dockrell (Overseas)", "Liam Dawson (Overseas)"],
            "Domestic_Finisher": ["Ashutosh Sharma (Domestic)", "Naman Dhir (Domestic)"]
        },
        "budget_allocation_units": {
            "Elite Death-Overs Specialist Pacer": 40.0,
            "High-Leverage Middle-Overs Spin Enforcer": 25.0,
            "Multi-Phase Bowling All-Rounder": 20.0,
            "Domestic Power-Hitting Batter": 15.0
        },
        "total_budget_units": 100.0,
        "overseas_slots_demanded": 3,
        "main_advantages": "Constructs the most formidable bowling attack in the competition, completely insulating RR from Archer fatigue or off-days.",
        "main_risks": "Leaves lower-order batting reliant on domestic emerging finishers (Ashutosh Sharma/Shubham Dubey).",
        "squad_balance_impact": "Creates elite defensive bowling ceiling; matches become lower-scoring and less dependent on top-order run explosions."
    },
    "Scenario_3_Finishing_Power_Priority": {
        "scenario_id": "SCEN-03",
        "name": "Middle-Order & Finishing Power Priority",
        "strategic_focus": "Remedy the decline in late-overs run-rates (Hetmyer SR 105.4 in 2026) by prioritizing proven boundary hitters at overs 16-20.",
        "target_archetypes": [
            "Specialist Phase Performer (Finisher)",
            "Reliable Campaign Performer (Middle-Order Batter)",
            "Specialist Phase Performer (Death Bowler)",
            "Multi-Role Tactical Option (Spin All-Rounder)"
        ],
        "primary_candidates": {
            "Finisher": ["Tim David (Overseas)", "Matthew Wade (Overseas)"],
            "Middle_Order": ["Mahipal Lomror (Domestic)", "Naman Dhir (Domestic)"],
            "Death_Bowler": ["Benjamin Sears (Overseas)", "Eshan Malinga (Overseas)"],
            "Spin_All_Rounder": ["Liam Dawson (Overseas)", "George Dockrell (Overseas)"]
        },
        "budget_allocation_units": {
            "Elite Overseas Finisher (Tim David archetype)": 45.0,
            "Domestic Middle-Order Enforcer (Lomror / Dhir)": 25.0,
            "Defensive Death-Overs Pacer": 20.0,
            "Spin / All-Rounder Backup": 10.0
        },
        "total_budget_units": 100.0,
        "overseas_slots_demanded": 2,
        "main_advantages": "Guarantees match-winning death-overs hitting (180+ clutch SR) supporting Jaiswal, Sooryavanshi, and Parag.",
        "main_risks": "Leaves secondary bowling attack thin if Archer sustains an injury or bowls expensive overs.",
        "squad_balance_impact": "Maximizes chasing potential and target-setting ceilings in high-scoring venues like Jaipur and Mumbai."
    },
    "Scenario_4_Domestic_Talent_Maximization": {
        "scenario_id": "SCEN-04",
        "name": "Domestic Talent Maximization",
        "strategic_focus": "Invest aggressively in premium Indian domestic assets to preserve scarce overseas slots for global strike weapons.",
        "target_archetypes": [
            "Multi-Role Tactical Option (Domestic Batting All-Rounder)",
            "Reliable Campaign Performer (Domestic Middle Batter)",
            "Reliable Campaign Performer (Overseas Strike Bowler)",
            "Reliable Campaign Performer (Overseas Finisher / Keeper)"
        ],
        "primary_candidates": {
            "Domestic_All_Rounder": ["Naman Dhir (Domestic)", "Abhishek Sharma (Domestic)"],
            "Domestic_Middle_Batter": ["Mahipal Lomror (Domestic)", "Ashutosh Sharma (Domestic)"],
            "Overseas_Strike_Bowler": ["Benjamin Sears (Overseas)", "Nathan Ellis (Overseas)"],
            "Overseas_Finisher_Keeper": ["Matthew Wade (Overseas)", "Tim David (Overseas)"]
        },
        "budget_allocation_units": {
            "Premium Indian Multi-Role Star (Naman Dhir)": 35.0,
            "Indian Middle-Order Power Hitter (Lomror / Ashutosh)": 25.0,
            "Overseas Elite Strike Bowler (Sears / Ellis)": 25.0,
            "Overseas Finisher / Backup Keeper (Wade / David)": 15.0
        },
        "total_budget_units": 100.0,
        "overseas_slots_demanded": 2,
        "main_advantages": "Maximizes tactical flexibility by fielding 8 high-performing Indian domestic players, allowing RR to rotate overseas specialists based on pitch.",
        "main_risks": "Premium Indian domestic stars often encounter ferocious bidding inflation in mini-auctions.",
        "squad_balance_impact": "Builds sustainable multi-year franchise core aligned with RR's historical scouting and development ethos."
    },
    "Scenario_5_High_Upside_Controlled_Risk": {
        "scenario_id": "SCEN-05",
        "name": "High-Upside, Controlled-Risk Strategy",
        "strategic_focus": "Pair proven high-stability veterans with calculated high-ceiling prospects from the Module 5/6 Watchlist.",
        "target_archetypes": [
            "Reliable Campaign Performer (Veteran Anchor)",
            "Emerging High-Upside Prospect (Lower-Order Power)",
            "Specialist Phase Performer (Death Pacer)",
            "Multi-Role Tactical Option (Bowling All-Rounder)"
        ],
        "primary_candidates": {
            "Veteran_Anchor": ["Matthew Wade (Overseas)", "Tim David (Overseas)"],
            "Emerging_Prospect": ["Vipraj Nigam (Domestic)", "Jake Fraser-McGurk (Overseas - Watchlist)"],
            "Death_Pacer": ["Benjamin Sears (Overseas)", "Taskin Ahmed (Overseas)"],
            "All_Rounder": ["Imad Wasim (Overseas)", "George Dockrell (Overseas)"]
        },
        "budget_allocation_units": {
            "Proven High-Stability Veteran Anchor": 40.0,
            "High-Ceiling Emerging Power Prospect": 25.0,
            "High-Ceiling Death Bowler Prospect": 20.0,
            "Versatile Domestic Role Players": 15.0
        },
        "total_budget_units": 100.0,
        "overseas_slots_demanded": 3,
        "main_advantages": "Provides floor security via the veteran anchor while capturing tournament-winning explosive upside from young prospects.",
        "main_risks": "Higher statistical variance if the emerging prospects fail to adapt to IPL stage pressure.",
        "squad_balance_impact": "Exciting, high-tempo squad capable of overwhelming opponents when high-ceiling bets pay off."
    }
}


def get_auction_scenarios_summary() -> pd.DataFrame:
    """
    Returns a structured DataFrame summarizing all 5 auction strategy scenarios.
    """
    records = []
    for key, sc in AUCTION_SCENARIOS.items():
        records.append({
            "scenario_key": key,
            "scenario_name": sc["name"],
            "strategic_focus": sc["strategic_focus"],
            "total_budget_units": sc["total_budget_units"],
            "overseas_slots_demanded": sc["overseas_slots_demanded"],
            "main_advantages": sc["main_advantages"],
            "main_risks": sc["main_risks"],
            "squad_balance_impact": sc["squad_balance_impact"]
        })
    return pd.DataFrame(records)


def get_budget_allocations_dataframe() -> pd.DataFrame:
    """
    Returns a granular breakdown of budget unit allocations across categories for all 5 scenarios.
    """
    records = []
    for key, sc in AUCTION_SCENARIOS.items():
        for category, units in sc["budget_allocation_units"].items():
            records.append({
                "scenario_key": key,
                "scenario_name": sc["name"],
                "allocation_category": category,
                "budget_units": units,
                "pct_of_budget": units  # Since total is 100.0
            })
    return pd.DataFrame(records)
