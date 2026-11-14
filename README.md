# SupeRR Selector: Cricket Player Performance Intelligence System

**Competition:** Rajasthan Royals Sports Analytics Hackathon (Season 2)  
**Author:** Syed Mohammad Hamzah  

SupeRR Selector is a cricket analytics project designed to evaluate and rank player performance under pressure across the Indian Premier League (IPL) and T20 Internationals from 2022 to 2026.

---

## Project Overview

In T20 cricket, traditional summary statistics like batting average or overall economy rate treat all match situations equally. A boundary hit when a team needs 10 runs off 30 balls is counted the same as a boundary hit when needing 14 runs off the final over with four wickets down.

This project builds an empirical framework to:
1. Reconstruct delivery-level match situations, tracking cumulative score, wickets fallen, balls remaining, current run rate (CRR), and required run rate (RRR).
2. Define a mathematical Pressure Index ($PI \in [0.0, 10.0]$) for both first-innings target setting and second-innings run chases.
3. Compare how batters and bowlers perform in high-pressure situations relative to their overall baseline.
4. Apply credibility-weighted shrinkage (Bühlmann model) and sample-size thresholds so player rankings are not distorted by small samples.
5. Provide transparent rankings for the top 10 batters and top 10 bowlers under pressure, supported by an interactive Streamlit application and an analytical report.

---

## Repository Structure

```text
Rajhstan royals/
│
├── Data Pack/                               # Original CSV datasets provided for the hackathon
│   ├── ball_by_ball.csv                     # 200,999 delivery-level records
│   ├── matches.csv                          # 883 match records and outcomes
│   ├── competitions.csv                     # 141 tournaments across IPL and T20Is
│   ├── playing_eleven.csv                   # 28,381 player appearance records
│   ├── teams.csv                            # 353 team participation records
│   └── competition_team_player_mapping.csv   # 6,413 player name and ID mappings
│
├── notebooks/                               # Analytical research notebooks
│   ├── 01_data_understanding.ipynb          # Module 1: Exploratory data analysis and schema audit
│   ├── 02_data_cleaning_and_integration.ipynb # Module 2: Match-state reconstruction & cleaning
│   ├── 03_pressure_index_framework.ipynb    # Module 3: Pressure Index mathematical modeling
│   └── 04_player_performance_under_pressure.ipynb # Module 4: Batter & bowler clutch evaluation
│
├── data/
│   └── processed/                           # Processed Parquet & CSV analytical datasets
│       ├── playing_eleven_clean.parquet     # Deduplicated 11s (28,341 rows)
│       ├── ball_by_ball_state.parquet       # Match-state reconstructed deliveries (200,999 rows)
│       ├── ball_by_ball_pressure.parquet    # Pressure-labeled deliveries (200,999 rows, 68 cols)
│       ├── batter_pressure_metrics.parquet  # Batter pressure tier metrics (888 players, 77 metrics)
│       └── bowler_pressure_metrics.parquet  # Bowler pressure tier metrics (647 players, 85 metrics)
│
├── src/                                     # Production Python modules
│   ├── __init__.py
│   ├── data_loader.py                       # Ingestion and path resolution
│   ├── data_cleaner.py                      # Deduplication and anomaly cleaning
│   ├── match_state.py                       # Vectorized live match-state engine
│   ├── pressure_calibration.py              # Empirical baseline calibration & cross-validation
│   ├── pressure_model.py                    # Multi-component Pressure Index calculation
│   ├── batter_pressure_analysis.py          # Batter metrics across pressure tiers (MCC Law 24 compliant)
│   ├── bowler_pressure_analysis.py          # Bowler metrics across pressure tiers (bifurcated dot balls)
│   ├── clutch_analysis.py                   # Multi-dimensional clutch differentials, phase adjustments & credibility shrinkage
│   └── data_validator.py                    # 24-point automated validation framework
│
├── reports/                                 # Private handover documentation & technical notes (Git ignored)
│   ├── module_01_completion_summary.md
│   ├── module_02_completion_summary.md
│   ├── module_02_data_quality_report.md
│   ├── module_03_pressure_methodology_report.md
│   ├── module_03_completion_summary.md
│   ├── module_04_methodology_report.md
│   └── module_04_completion_summary.md
│
└── .gitignore                               # Git configuration ignoring cache and temporary files
```

---

## AI-Assisted Development and Transparency

AI tools were used as development assistants throughout this project.

### Tools used:
* Google Antigravity: AI-assisted coding, project structuring, debugging and development support.
* ChatGPT: Analytical brainstorming, methodology discussions, learning support, code review guidance and documentation assistance.

### Areas where AI assistance was used:
* Project architecture and module planning.
* Python code development and debugging assistance.
* Exploratory Data Analysis workflow guidance.
* Feature engineering implementation support.
* Dashboard design and development assistance.
* Documentation and README preparation.

### My Contributions and Responsibilities:
I used these tools as assistants rather than treating their outputs as automatically correct. My responsibilities included:
* Understanding the datasets and their relationships.
* Evaluating analytical approaches.
* Reviewing and validating calculations.
* Investigating data-quality issues.
* Interpreting statistical results.
* Making methodological decisions.
* Testing the application and its outputs.

All final analytical findings and player rankings must be based on the supplied datasets and verified calculations. AI-generated suggestions and code were reviewed and tested before being accepted into the project.

### Learning Objective:
This project is also a practical learning journey in Data Analytics, Python, cricket statistics, statistical reasoning and interactive data visualization.

---

## Development Roadmap

- [x] **Module 1 — Data Understanding & Exploratory Data Analysis:** Schema audit, invariant checks, relational key validation, and baseline cricket distributions.
- [x] **Module 2 — Data Cleaning, Integration & Match-State Reconstruction:** Deduplicated lineups (match 13613), corrected dismissal edge cases, and vectorized live cumulative match states before and after each delivery.
- [x] **Module 3 — Pressure Index ($PI$) Mathematical Modelling:** Built format-aware Duckworth-Lewis style empirical resource baselines ($R^2 > 0.83$) with GroupKFold cross-validation, evaluating pre-delivery tension for chases, 1st innings, bowling, and Super Overs.
- [x] **Module 4 — Player Performance Under Pressure:** Granular performance metrics across 5 pressure tiers, MCC Law 24 scorecard compliance, bifurcated team dots vs bowler scoreless deliveries, phase-adjusted bowling clutch economy, and Bühlmann credibility-weighted shrinkage.
- [ ] **Module 5 — Player Reliability Scores & Rankings:** Develop transparent, statistically defensible player reliability scores using pressure-performance metrics, sample-size controls and appropriate shrinkage.
- [ ] **Module 6 — Statistical Validation & Robustness:** Test ranking stability, sensitivity to thresholds and weights, format differences, role effects and sample-size assumptions.
- [ ] **Module 7 — Rajasthan Royals Squad Fit & Auction Strategy:** Evaluate player suitability against RR's squad composition, role requirements, team balance and IPL 2027 auction strategy.
- [ ] **Module 8 — Interactive Streamlit Dashboard:** Build a dashboard for exploring pressure metrics, player comparisons, reliability scores and squad-fit insights.
- [ ] **Module 9 — Final Report & Presentation:** Prepare the final methodology report, analytical findings, player recommendations, auction strategy and presentation for the competition.

---

## Getting Started

### Prerequisites
* Python 3.10 or higher
* Recommended virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Installation
```powershell
pip install pandas numpy matplotlib seaborn scikit-learn streamlit plotly nbformat pyarrow
```

### Running the Notebooks
```powershell
jupyter notebook notebooks/01_data_understanding.ipynb
jupyter notebook notebooks/02_data_cleaning_and_integration.ipynb
jupyter notebook notebooks/03_pressure_index_framework.ipynb
jupyter notebook notebooks/04_player_performance_under_pressure.ipynb
```
