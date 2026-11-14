# SupeRR Selector: Cricket Player Performance Intelligence System

**Competition:** Rajasthan Royals Sports Analytics Hackathon (Season 2)  
**Author:** Syed Mohammad Hamzah  

SupeRR Selector is a cricket analytics project designed to evaluate and rank player performance under pressure across the Indian Premier League (IPL) and T20 Internationals from 2022 to 2026.

---

## Project Overview

In T20 cricket, traditional summary statistics like batting average or overall economy rate treat all match situations equally. A boundary hit when a team needs 10 runs off 30 balls is counted the same as a boundary hit when needing 14 runs off the final over with four wickets down.

This project builds an empirical framework to:
1. Reconstruct delivery-level match situations, tracking cumulative score, wickets fallen, balls remaining, current run rate (CRR), and required run rate (RRR).
2. Define a mathematical Pressure Index ($PI$) for both first-innings target setting and second-innings run chases.
3. Compare how batters and bowlers perform in high-pressure situations relative to their overall baseline.
4. Apply Bayesian shrinkage and sample-size thresholds so player rankings are not distorted by small samples.
5. Provide transparent rankings for the top 10 batters and top 10 bowlers under pressure, supported by an interactive Streamlit application and an analytical report.

---

## Repository Structure

```text
Rajhstan royals/
│
├── Data Pack/                     # Original CSV datasets provided for the hackathon
│   ├── ball_by_ball.csv           # 200,999 delivery-level records
│   ├── matches.csv                # 883 match records and outcomes
│   ├── competitions.csv           # 141 tournaments across IPL and T20Is
│   ├── playing_eleven.csv         # 28,381 player appearance records
│   ├── teams.csv                  # 353 team participation records
│   └── competition_team_player_mapping.csv # 6,413 player name and ID mappings
│
├── notebooks/                     # Analytical research notebooks
│   ├── 01_data_understanding.ipynb# Module 1: Exploratory data analysis and schema audit
│   ├── 02_match_state.ipynb       # Module 2: Live match-state reconstruction
│   ├── 03_pressure_index.ipynb    # Module 3: Mathematical pressure index modeling
│   └── 04_ranking_engine.ipynb    # Module 4 and 5: Performance analysis and rankings
│
├── data/
│   ├── processed/                 # Processed tables with reconstructed match states
│   └── results/                   # Final leaderboards and metrics exports
│
├── src/                           # Reusable Python modules
│   ├── __init__.py
│   ├── data_loader.py             # Data loading and schema validation
│   ├── match_state.py             # State reconstruction logic
│   ├── pressure_model.py          # Pressure index calculations
│   ├── player_metrics.py          # Player baseline and pressure metrics
│   └── ranking_engine.py          # Bayesian shrinkage and scoring functions
│
├── tests/                         # Unit tests and invariant assertions
│   └── test_data_integrity.py
│
├── reports/                       # Hackathon methodology documentation
│   └── methodology_report.md
│
├── app/                           # Streamlit interactive application
│   └── app.py
│
└── .gitignore                     # Git configuration ignoring cache and temporary files
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

- [x] Module 1: Data Understanding and Exploratory Data Analysis
- [ ] Module 2: Dynamic Match-State Reconstruction (Cumulative scores, CRR, RRR, resource calculations)
- [ ] Module 3: Pressure Index ($PI$) Mathematical Modeling
- [ ] Module 4: Player Performance Under Pressure vs Baseline
- [ ] Module 5: Bayesian Shrinkage, Composite Scoring, and Top 10 Rankings
- [ ] Module 6: Statistical Validation, Sensitivity Analysis, and Submission Report
- [ ] Module 7: Interactive Streamlit Intelligence Dashboard

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
pip install pandas numpy matplotlib seaborn scikit-learn streamlit plotly nbformat
```

### Running the Notebooks
```powershell
jupyter notebook notebooks/01_data_understanding.ipynb
```
