"""
src/create_module7_notebook.py
Script to generate notebooks/07_rr_squad_fit_auction_strategy.ipynb
"""

import os
import nbformat as nbf

def build_notebook():
    nb = nbf.v4.new_notebook()

    # Markdown Cell 1: Header
    nb.cells.append(nbf.v4.new_markdown_cell("""# Module 7: Rajasthan Royals Squad Fit & Auction Strategy
## SupeRR Selector | Rajasthan Royals Sports Analytics Challenge - Season 2

**Author:** Syed Mohammad Hamzah (B.Tech CSE - Data Analytics)  
**Role:** Senior Cricket Data Scientist & Sports Analytics Researcher  
**Evaluator Reference:** Technical Submission & Strategy Deck  
**Status:** Completed and Validated  

---

### Executive Summary & Research Goal

Module 7 translates the statistical evidence and uncertainty bounds established in Modules 1-6 into practical recruitment intelligence for Rajasthan Royals ahead of IPL 2027.

The central inquiry is:
> **Which players from the analysed player pool offer the strongest combination of pressure performance, evidence reliability, statistical stability, tactical role fit, and squad need for Rajasthan Royals?**

Key Governance Constraints:
* Separate batting and bowling evaluations (no invented combined rating).
* Decoupled 5-dimension evaluation framework: Performance Rating (PR), Evidence Reliability (ERS), Statistical Stability (SSS), Tactical Squad Fit (TFS), and Acquisition Risk (ARS).
* Zero price fabrication: Budget allocation modeled using 100 Budget Allocation Units / percentage shares.
* Transparent Source & Assumptions Register separating confirmed historical facts from provisional scenario models.
"""))

    # Code Cell 1: Imports
    nb.cells.append(nbf.v4.new_code_cell("""import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, os.path.abspath(".."))

from src.squad_context import (
    get_rr_2026_baseline_squad,
    get_squad_retention_scenarios,
    get_source_and_assumptions_register,
    OFFICIAL_IPL_RULES
)
from src.squad_gap_analysis import (
    audit_rr_squad_by_roles,
    evaluate_squad_gaps,
    RR_TACTICAL_GAP_WEIGHTS,
    TACTICAL_BATTING_ROLES,
    TACTICAL_BOWLING_ROLES
)
from src.player_squad_fit import (
    build_candidate_recruitment_pool,
    calculate_candidate_squad_fit_scores,
    run_alternative_weight_scenarios
)
from src.auction_strategy import (
    get_auction_scenarios_summary,
    get_budget_allocations_dataframe,
    AUCTION_SCENARIOS
)

print("Environment initialized successfully. Pandas version:", pd.__version__)
"""))

    # Markdown Cell 2: Squad Context
    nb.cells.append(nbf.v4.new_markdown_cell("""## 1. Rajasthan Royals Squad Context & Governance Register

We extract the authoritative Rajasthan Royals roster from IPL 2026 (competition ID: 3298), verify match appearances, and document official IPL squad governance constraints.
"""))

    # Code Cell 2: Baseline Squad
    nb.cells.append(nbf.v4.new_code_cell("""rr_raw_squad = get_rr_2026_baseline_squad("../Data Pack") if os.path.exists("../Data Pack") else get_rr_2026_baseline_squad("Data Pack")
data_pack_dir = "../Data Pack" if os.path.exists("../Data Pack") else "Data Pack"
rr_audited_squad = audit_rr_squad_by_roles(rr_raw_squad, data_pack_dir)

print(f"Total Registered RR Players (2026): {len(rr_audited_squad)}")
print(f"Domestic Players: {(~rr_audited_squad['is_overseas']).sum()} | Overseas Players: {rr_audited_squad['is_overseas'].sum()}")
rr_audited_squad[["player_name", "country", "is_overseas", "matches_played", "tactical_bat_role", "tactical_bowl_role"]].head(15)
"""))

    # Code Cell 3: Register
    nb.cells.append(nbf.v4.new_code_cell("""register_df = get_source_and_assumptions_register()
register_df[["item_id", "category", "description", "status", "verification_date"]]
"""))

    # Markdown Cell 3: Gap Analysis
    nb.cells.append(nbf.v4.new_markdown_cell("""## 2. Squad Role Depth & Tactical Gap Analysis

We evaluate squad depth across the 12 tactical roles under three retention scenarios:
* **Scenario A (Core Continuity Baseline):** Retain 8 core players (Jaiswal, Sooryavanshi, Jurel, Parag, Jadeja, Bishnoi, Sandeep Sharma, Archer - 7 domestic, 1 overseas).
* **Scenario B (Balanced Depth):** Retain 10 players (includes Burger and Ferreira).
* **Scenario C (Open Rebuild):** Retain 5 young Indian pillars.
"""))

    # Code Cell 4: Gaps
    nb.cells.append(nbf.v4.new_code_cell("""gaps_a = evaluate_squad_gaps(rr_audited_squad, "Scenario_A_Core_Continuity")
gaps_a[["discipline", "tactical_role", "squad_count_total", "depth_status", "gap_criticality_weight", "gap_severity", "players_in_role"]]
"""))

    # Markdown Cell 4: Recruitment Pool & Scoring
    nb.cells.append(nbf.v4.new_markdown_cell("""## 3. Candidate Recruitment Pool & 5-Dimension Evaluation

Candidates from Modules 5 and 6 (304 eligible batters, 290 eligible bowlers) are evaluated across five transparent, decoupled dimensions:
1. **Historical Performance Rating ($PR$):** Multi-dimensional tactical execution under pressure.
2. **Evidence Reliability Score ($ERS$):** Exposure-based sample adequacy.
3. **Statistical Stability Score ($SSS$):** Cluster-bootstrap interval precision, rank stability, and LOMO resilience.
4. **Tactical Squad Fit Score ($TFS$):** Match against RR role voids and phase needs.
5. **Acquisition Risk Score ($ARS$):** Downside volatility and slot constraints.
"""))

    # Code Cell 5: Batting Evaluations
    nb.cells.append(nbf.v4.new_code_cell("""b_pool = build_candidate_recruitment_pool("Batting", data_pack_dir)
b_eval = calculate_candidate_squad_fit_scores(b_pool, "Batting")
b_scen = run_alternative_weight_scenarios(b_eval)

print(f"Evaluated Batters: {len(b_eval)}")
cols = ["player_name", "tactical_role", "performance_rating", "evidence_reliability_score", "statistical_stability_score", "tactical_squad_fit_score", "acquisition_risk_score", "recruitment_decision_score", "player_archetype", "recommendation_priority"]
b_eval[cols].head(10)
"""))

    # Code Cell 6: Bowling Evaluations
    nb.cells.append(nbf.v4.new_code_cell("""bw_pool = build_candidate_recruitment_pool("Bowling", data_pack_dir)
bw_eval = calculate_candidate_squad_fit_scores(bw_pool, "Bowling")
bw_scen = run_alternative_weight_scenarios(bw_eval)

print(f"Evaluated Bowlers: {len(bw_eval)}")
bw_eval[cols].head(10)
"""))

    # Markdown Cell 5: Recommendation Matrix
    nb.cells.append(nbf.v4.new_markdown_cell("""## 4. Master Recruitment Recommendation Matrix

Combining the top shortlisted targets into an executive recruitment matrix.
"""))

    # Code Cell 7: Matrix
    nb.cells.append(nbf.v4.new_code_cell("""matrix_path = "../data/processed/recruitment_recommendation_matrix.parquet" if os.path.exists("../data/processed/recruitment_recommendation_matrix.parquet") else "data/processed/recruitment_recommendation_matrix.parquet"
matrix_df = pd.read_parquet(matrix_path)

display_cols = ["player_name", "discipline", "country", "tactical_role", "performance_rating", "statistical_stability_score", "tactical_squad_fit_score", "acquisition_risk_score", "recruitment_decision_score", "player_archetype", "recommendation_priority"]
matrix_df[display_cols].head(15)
"""))

    # Markdown Cell 6: Auction Strategy
    nb.cells.append(nbf.v4.new_markdown_cell("""## 5. Auction Strategy & Budget Allocation Scenarios

Models 5 practical squad-building scenarios conserving exactly 100 Budget Allocation Units without fabricated currency prices.
"""))

    # Code Cell 8: Scenarios
    nb.cells.append(nbf.v4.new_code_cell("""scen_df = get_auction_scenarios_summary()
alloc_df = get_budget_allocations_dataframe()

print("Auction Strategy Scenarios Summary:")
print(scen_df[["scenario_name", "strategic_focus", "total_budget_units", "overseas_slots_demanded"]].to_string())

print("Budget Allocations Sample:")
print(alloc_df.head(8).to_string())
"""))

    # Markdown Cell 7: Visualizations
    nb.cells.append(nbf.v4.new_markdown_cell("""## 6. Publication Figures & Visual Insights
"""))

    # Code Cell 9: Display figures
    nb.cells.append(nbf.v4.new_code_cell("""from IPython.display import Image, display

fig_dir = "../reports/figures" if os.path.exists("../reports/figures") else "reports/figures"

print("Figure 1: Squad Role Coverage")
display(Image(filename=f"{fig_dir}/rr_squad_role_coverage.png"))

print("Figure 2: Tactical Gap Criticality Matrix")
display(Image(filename=f"{fig_dir}/rr_tactical_gap_matrix.png"))

print("Figure 5: Batting Shortlist Squad Fit")
display(Image(filename=f"{fig_dir}/batting_shortlist_squad_fit.png"))

print("Figure 6: Bowling Shortlist Squad Fit")
display(Image(filename=f"{fig_dir}/bowling_shortlist_squad_fit.png"))

print("Figure 7: Candidate Risk vs Tactical Squad Fit")
display(Image(filename=f"{fig_dir}/candidate_risk_vs_tactical_fit.png"))

print("Figure 8: Auction Scenario Capital Allocations")
display(Image(filename=f"{fig_dir}/auction_scenario_allocation.png"))
"""))

    os.makedirs("notebooks", exist_ok=True)
    out_path = "notebooks/07_rr_squad_fit_auction_strategy.ipynb"
    with open(out_path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"Successfully generated {out_path} with {len(nb.cells)} cells.")

if __name__ == "__main__":
    build_notebook()
