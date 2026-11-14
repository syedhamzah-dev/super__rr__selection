# SupeRR Selector – Cricket Player Performance Intelligence System
**Rajasthan Royals Sports Analytics Hackathon (Season 2)**

An end-to-end, data-driven sports analytics intelligence platform designed to identify, quantify, and rank the **Most Reliable Cricket Players Under Pressure** across the Indian Premier League (IPL) and T20 Internationals (T20Is) from 2022 to 2026.

---

## 📌 Project Overview
In modern T20 cricket, aggregate statistics like raw batting average or total wickets fail to separate baseline accumulators from true match-winners. A run scored when chasing 120 at 6.0 RRR does not carry the same competitive weight as a boundary scored when needing 14 off 6 balls with 6 wickets down. 

**SupeRR Selector** constructs a rigorous, mathematical framework to:
1. **Reconstruct Live Match States:** Track cumulative runs, wickets, legal balls, CRR, and RRR on a ball-by-ball level.
2. **Formulate a Contextual Pressure Index ($PI$):** Model high-leverage situations across both setting (1st innings) and chasing (2nd innings) contexts.
3. **Evaluate Clutch Performance vs. Baseline:** Quantify deviation from player baseline metrics under pressure.
4. **Mitigate Sample-Size Bias:** Employ Empirical Bayes shrinkage and competition weighting (IPL vs T20I tiers).
5. **Deliver Actionable Intelligence:** Generate the Top 10 Clutch Batters and Bowlers supported by an interactive Streamlit intelligence suite and an empirical methodology report.

---

## 🏗️ Repository Architecture

```text
Rajhstan royals/
│
├── Data Pack/                     # Raw datasets provided by Rajasthan Royals (Preserved untouched)
│   ├── ball_by_ball.csv           # 200,999 delivery event records
│   ├── matches.csv                # 883 match records & outcomes
│   ├── competitions.csv           # 141 tournaments (IPL 2022-2026 + T20Is)
│   ├── playing_eleven.csv         # 28,381 player appearance records (incl. Impact Players)
│   ├── teams.csv                  # 353 team-competition records
│   └── competition_team_player_mapping.csv # 6,413 player lookup records
│
├── notebooks/                     # Educational & analytical research notebooks
│   ├── 01_data_understanding.ipynb# Module 1: Comprehensive EDA & Schema Audit
│   ├── 02_match_state.ipynb       # Module 2: State reconstruction (CRR, RRR, Resources)
│   ├── 03_pressure_index.ipynb    # Module 3: Mathematical Pressure Index modeling
│   └── 04_ranking_engine.ipynb    # Module 4 & 5: Clutch evaluation & ranking
│
├── data/
│   ├── processed/                 # Feature-engineered state tables (derived)
│   └── results/                   # Final Top-10 leaderboards and exports
│
├── src/                           # Modular production Python package
│   ├── __init__.py
│   ├── data_loader.py             # Data ingestion and schema validation
│   ├── match_state.py             # Match state reconstruction engine
│   ├── pressure_model.py          # Pressure index computation algorithms
│   ├── player_metrics.py          # Baseline vs pressure metrics calculator
│   └── ranking_engine.py          # Bayesian shrinkage & composite scoring
│
├── tests/                         # Unit tests and invariant assertions
│   └── test_data_integrity.py
│
├── reports/                       # Formal Hackathon Submission Documentation
│   └── methodology_report.md
│
├── app/                           # Interactive Streamlit Web Application
│   └── app.py
│
└── .gitignore                     # Repository hygiene configuration
```

---

## 🤖 AI-Assisted Development & Transparency

AI tools were used as development assistants throughout this project.

### Tools Used:
- **Google Antigravity:** AI-assisted coding, project structuring, debugging, and development support.
- **ChatGPT:** Analytical brainstorming, methodology discussions, learning support, code review guidance, and documentation assistance.

### Areas where AI assistance was used:
- Project architecture and module planning.
- Python code development and debugging assistance.
- Exploratory Data Analysis workflow guidance.
- Feature engineering implementation support.
- Dashboard design and development assistance.
- Documentation and README preparation.

### Student Contributions & Responsibilities:
AI tools were used as assistive accelerators rather than treating their outputs as automatically correct. Core human responsibilities included:
- Understanding the datasets and their underlying relational relationships.
- Evaluating analytical approaches and selecting appropriate statistical techniques.
- Reviewing and mathematically validating calculations and domain invariants.
- Investigating data-quality issues (e.g. ghost abandoned matches, lineup duplicates).
- Interpreting statistical results from a cricket perspective.
- Making critical methodological decisions (e.g. defining Pressure Index parameters).
- Rigorously testing the application, unit assertions, and outputs.

> All final analytical findings and player rankings are grounded strictly in the supplied datasets and verified calculations.

### Learning Objective:
This project is an intensive, practical learning journey in Data Analytics, Python programming, cricket domain modeling, statistical reasoning, Bayesian methods, and interactive data visualization.

---

## 📊 Development Roadmap

- [x] **Module 0:** Environment Setup, Raw Data Preservation & Repository Hygiene
- [x] **Module 1:** Data Understanding, Schema Audit, Forensic Verification & Baseline EDA
- [ ] **Module 2:** Dynamic Match-State Reconstruction (Cumulative scores, CRR, RRR, Resource calculations)
- [ ] **Module 3:** Pressure Index ($PI$) Mathematical Modeling (Chase dynamics, Collapse hazards, Death acceleration)
- [ ] **Module 4:** Pressure Performance vs. Player Baseline Evaluation
- [ ] **Module 5:** Bayesian Shrinkage, Composite Scoring & Definitive Top-10 Rankings
- [ ] **Module 6:** Statistical Validation, Sensitivity Testing & Hackathon Report
- [ ] **Module 7:** Interactive SupeRR Selector Streamlit Intelligence Suite

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Recommended virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

### Installation
```bash
pip install pandas numpy matplotlib seaborn scikit-learn streamlit plotly nbformat
```

### Running Module 1 Notebook
```bash
jupyter notebook notebooks/01_data_understanding.ipynb
```
