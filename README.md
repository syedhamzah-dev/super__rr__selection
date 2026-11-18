# SupeRR Selector: Cricket Player Performance Intelligence System

**Project:** SupeRR Selector — Cricket Player Performance Intelligence System  
**Competition:** Rajasthan Royals Sports Analytics Challenge (Season 2)  
**Author:** Syed Mohammad Hamzah (B.Tech CSE - Data Analytics)  
**Evaluator Reference:** Sports Analytics Research & Technical Submission  

---

## 1. Project Title and Description

SupeRR Selector is a cricket analytics intelligence system developed for the Rajasthan Royals Sports Analytics Challenge (Season 2). The system evaluates and ranks professional cricket player performance under high-pressure situations across Indian Premier League (IPL) and Men's T20 International matches from 2022 to 2026.

Traditional cricket statistics treat every run and wicket equally. A boundary scored during a low-leverage powerplay in a dead rubber counts identically on an unweighted scorecard to a boundary hit when needing 12 runs off the final 4 deliveries of a knockout match. SupeRR Selector reconstructs ball-by-ball match states, computes a dynamic delivery-level Pressure Index ($PI \in [0.0, 10.0]$), and measures player performance in clutch situations while statistically separating performance quality from sample-size evidence confidence.

---

## 2. Rajasthan Royals Challenge Context

The Rajasthan Royals Sports Analytics Challenge tasks participants with identifying reliable, battle-tested players who perform dependably when matches are on the line. The objective is to provide actionable intelligence for franchise recruitment and auction strategy ahead of the IPL 2027 cycle.

Franchise auctions represent high-stakes capital allocation decisions. Overpaying for players whose aggregate career metrics are inflated by low-pressure stat-padding creates substantial downside risk. Conversely, under-valuing specialized death-overs finishers or defensive enforcers due to modest aggregate volume leads to missed opportunities. SupeRR Selector addresses this problem by grounding player evaluations in situational leverage and statistical evidence reliability.

---

## 3. Problem Statement

Evaluating cricket players using aggregate career averages introduces three critical failure modes:
1. **Leverage Blindness:** Career strike rates and economy rates fail to distinguish between low-stakes consolidation and high-stakes crisis execution.
2. **Phase Confounding in Bowling:** Directly comparing clutch economy rates across bowlers penalizes death-overs specialists who bowl in the most expensive phase of T20 cricket (averaging 10.52 runs per over) compared to powerplay or middle-overs specialists.
3. **Conflating Performance with Statistical Evidence:** Treating an emerging player with 15 clutch balls and a 200 strike rate identically to a veteran with 400 clutch balls and a 175 strike rate introduces severe sample-size variance and regression risk.

---

## 4. Project Objectives

1. **Reconstruct Situational Match State:** Vectorize cumulative match context before and after each delivery, tracking runs required, balls remaining, wickets in hand, current run rate (CRR), and required run rate (RRR).
2. **Model Delivery-Level Pressure ($PI$):** Formulate an empirical, resource-based Pressure Index scaled from 0.0 to 10.0 for first innings target-setting, second innings chases, and bowling defense.
3. **Quantify Player Clutch Differentials:** Measure individual player performance across discrete pressure tiers against their own baseline and role benchmarks, adjusting for phase confounding and applying credibility-weighted shrinkage.
4. **Decouple Performance from Evidence Reliability:** Engineer independent evaluation scores for Performance Rating ($0.0$ to $100.0$) and Evidence Reliability ($0.0$ to $100.0$) to insulate main auction boards from small-sample noise while surfacing emerging talent on a watchlist.
5. **Ensure Reproducibility and Audit Integrity:** Reconcile delivery records, scorecard rules, and run identities to 100% precision across all 200,999 deliveries.

---

## 5. Analytical Workflow

The project is structured into modular stages:

```
[Raw Competition Data: 6 CSVs]
         |
         v
[Module 1: Data Understanding & Exploratory Data Analysis]
         |  - Relational key validation, schema audit, and cricket rule verification
         v
[Module 2: Cleaning, Integration & Match-State Reconstruction]
         |  - Deduplication, scorecard compliance, cumulative state engine (ball_by_ball_state.parquet)
         v
[Module 3: Pressure Index Mathematical Modelling]
         |  - GroupKFold empirical resource surfaces, pressure calibration (ball_by_ball_pressure.parquet)
         v
[Module 4: Player Performance Under Pressure]
         |  - Scorecard balls faced, dot bifurcation, phase-adjusted bowling, credibility shrinkage
         v
[Module 5: Reliability Scoring & Evidence-Based Rankings]
         |  - Decoupled ratings & ERS, eligibility filtering, role boards, sensitivity testing
         v
[Future Work: Modules 6 to 9]
            - Statistical robustness, RR squad fit, HTML/CSS/JS dashboard, final defense
```

---

## 6. Dataset Overview

The project is built on the official proprietary dataset provided for the challenge, covering Men's T20 cricket from 2022 to 2026:

| Dataset File | File Size | Record Count | Description |
| :--- | :---: | :---: | :--- |
| `Data Pack/ball_by_ball.csv` | 39.17 MB | 200,999 | Granular delivery-level records including ball, batsman, bowler, runs, extras, and wickets. |
| `Data Pack/matches.csv` | 0.12 MB | 883 | Match outcome records, dates, venues, toss decisions, and winning margins. |
| `Data Pack/competitions.csv` | 0.01 MB | 141 | Tournament metadata covering IPL editions and Men's T20 Internationals. |
| `Data Pack/playing_eleven.csv` | 0.92 MB | 28,381 | Player match participation and lineup records. |
| `Data Pack/teams.csv` | 0.01 MB | 353 | Team names and franchise identifiers. |
| `Data Pack/competition_team_player_mapping.csv` | 0.44 MB | 6,413 | Player-team-tournament roster mappings. |

---

## 7. Repository Structure

```text
Rajhstan royals/
│
├── Data Pack/                               # Original competition CSV datasets
│   ├── ball_by_ball.csv                     # 200,999 deliveries
│   ├── matches.csv                          # 883 matches
│   ├── competitions.csv                     # 141 tournaments
│   ├── playing_eleven.csv                   # 28,381 participation entries
│   ├── teams.csv                            # 353 team records
│   └── competition_team_player_mapping.csv   # 6,413 roster records
│
├── notebooks/                               # Research and analytical notebooks
│   ├── 01_data_understanding.ipynb          # Module 1: EDA, schema checks, and relational integrity
│   ├── 02_data_cleaning_and_integration.ipynb # Module 2: Match-state reconstruction & cleaning
│   ├── 03_pressure_index_framework.ipynb    # Module 3: Pressure Index modeling and calibration
│   ├── 04_player_performance_under_pressure.ipynb # Module 4: Batter & bowler clutch evaluation
│   └── 05_player_reliability_and_rankings.ipynb   # Module 5: Decoupled ratings, evidence tiers & rankings
│
├── data/
│   └── processed/                           # Verified Parquet and CSV processed datasets
│       ├── playing_eleven_clean.parquet     # Deduplicated lineups (28,341 rows)
│       ├── ball_by_ball_state.parquet       # Cumulative match-state deliveries (200,999 rows, 58 cols)
│       ├── ball_by_ball_pressure.parquet    # Pressure-labeled deliveries (200,999 rows, 68 cols)
│       ├── batter_pressure_metrics.parquet  # Batter pressure tier metrics (888 players, 77 cols)
│       ├── bowler_pressure_metrics.parquet  # Bowler pressure tier metrics (647 players, 102 cols)
│       ├── batter_player_ratings.parquet    # Multi-dimensional batter ratings & ERS (888 players)
│       ├── bowler_player_ratings.parquet    # Multi-dimensional bowler ratings & ERS (647 players)
│       ├── batter_player_rankings.csv       # Official eligible batter leaderboard (304 players)
│       ├── bowler_player_rankings.csv       # Official eligible bowler leaderboard (290 players)
│       └── player_ranking_sensitivity.csv   # Robustness, rank shift & sensitivity outputs
│
├── src/                                     # Production Python analytical modules
│   ├── __init__.py
│   ├── data_loader.py                       # Ingestion, validation, and path resolution
│   ├── data_cleaner.py                      # Deduplication and anomaly cleaning
│   ├── match_state.py                       # Vectorized live match-state reconstruction engine
│   ├── pressure_calibration.py              # Out-of-fold baseline resource surface calibration
│   ├── pressure_model.py                    # Multi-component Pressure Index calculation engine
│   ├── batter_pressure_analysis.py          # Scorecard-compliant batter metrics across pressure tiers
│   ├── bowler_pressure_analysis.py          # Bowler metrics across pressure tiers with dot bifurcation
│   ├── clutch_analysis.py                   # Clutch differentials, phase adjustments & credibility weighting
│   ├── reliability_scoring.py               # Multi-factor Evidence Reliability Score (ERS) engine
│   ├── player_rating.py                     # Multi-dimensional batting and bowling performance ratings
│   ├── player_ranking.py                    # Stratified rankings, role boards & specialized cohorts
│   ├── ranking_validation.py                # Sensitivity auditing, rank shift & Spearman stability engine
│   └── data_validator.py                    # Automated data integrity and invariant test suite
│
├── tests/                                   # Automated unit and regression test suite (pytest)
│   ├── test_audit_reconciliation.py         # Forensic run, extras, dots, wickets, and ranking tests
│   ├── test_module4_corrections.py          # Scorecard balls-faced, dot-ball & run preservation tests
│   └── test_module5_ratings.py              # ERS bounds, rating monotonicity & sensitivity tests
│
├── reports/                                 # Handover documentation & technical reports
│   ├── module_01_completion_summary.md
│   ├── module_02_completion_summary.md
│   ├── module_02_data_quality_report.md
│   ├── module_03_completion_summary.md
│   ├── module_03_pressure_methodology_report.md
│   ├── module_04_completion_summary.md
│   ├── module_04_methodology_report.md
│   ├── module_05_completion_summary.md
│   ├── module_05_methodology_report.md
│   ├── project_correction_audit.md          # Forensic defect catalog and verification evidence
│   └── final_project_readiness_report.md    # Multi-gate competition readiness audit
│
└── .gitignore                               # Clean git tracking policy
```

---

## 8. Technology Stack

* **Core Analytical Environment:** Python 3.10+ (tested on Python 3.10 to 3.14)
* **Data Processing & Analytics:** pandas, NumPy, PyArrow (Parquet engine)
* **Statistical Modeling & ML:** scikit-learn (GroupKFold cross-validation, non-linear regression baselines), SciPy (Spearman rho, Kendall tau rank statistics)
* **Visualization (Research):** Matplotlib, Seaborn
* **Interactive Dashboard Architecture (Planned):** Pure HTML5, CSS3, modern JavaScript (ES6+), Chart.js / Plotly.js, hosted on Netlify (planned for Module 8; Streamlit is not used for final production deployment)
* **Testing & Quality Assurance:** pytest, unittest

---

## 9. Module 1 — Data Understanding and EDA

* **Scope:** Forensic schema inspection, missing-value audit, primary key validation, and relational key consistency across all six raw CSV tables.
* **Key Findings:**
  * Confirmed 200,999 delivery rows across 883 matches and 141 tournaments.
  * Identified 40 duplicate participation records in `playing_eleven.csv` (specifically within match ID 13613), which were resolved in Module 2.
  * Verified that player identifiers (`striker_id`, `bowler_id`) link cleanly to `competition_team_player_mapping.csv`.

---

## 10. Module 2 — Cleaning, Integration and Match-State Reconstruction

* **Scope:** Deduplication, dismissal alignment, and vectorized live match-state reconstruction.
* **Engine Deliverables (`src/match_state.py`):**
  * Computed pre-delivery and post-delivery match state for all 200,999 balls.
  * Invariant tracking: cumulative innings runs, balls elapsed, legal balls remaining, wickets in hand (10 down to 0), Current Run Rate (CRR), and Required Run Rate (RRR).
  * Legal ball flagging (`is_legal_ball`): exactly 192,445 legal balls (excluding 7,714 wides and 840 no-balls).
  * Exports: `playing_eleven_clean.parquet` (28,341 rows) and `ball_by_ball_state.parquet` (200,999 rows, 58 columns).

---

## 11. Module 3 — Pressure Index Modelling

* **Scope:** Mathematical formulation and empirical calibration of delivery-level pressure ($PI \in [0.0, 10.0]$).
* **Framework Design (`src/pressure_model.py`, `src/pressure_calibration.py`):**
  * **Chasing Innings ($PI_{\text{chase}}$):** Compares required run rate against an empirical resource baseline surface calibrated via GroupKFold out-of-fold cross-validation on match IDs to prevent data leakage ($R^2 > 0.83$).
  * **First Innings ($PI_{\text{1st}}$):** Measures deviation from par projected score based on balls remaining and wickets fallen.
  * **Pressure Tiers:** Low ($PI < 3.5$), Medium ($3.5 \le PI < 6.0$), High ($6.0 \le PI < 8.0$), Extreme ($PI \ge 8.0$), and Clutch ($PI \ge 6.0$).
  * Export: `ball_by_ball_pressure.parquet` (200,999 rows, 68 columns).

---

## 12. Module 4 — Player Performance Under Pressure

* **Scope:** Aggregating batter and bowler metrics across pressure tiers and computing clutch differentials.
* **Cricket Scorecard Compliance:**
  * Excluded wides (7,714) from batter balls faced while including no-balls (840), byes (529), leg-byes (2,748), and standard deliveries, establishing exactly **193,285 balls faced**.
  * Preserved all **269,550 runs off the bat**, including 1,264 runs scored on no-balls.
  * Bifurcated dot balls into True Team Dots (`total_runs == 0`, 68,027 balls) and Bowler Scoreless Balls (`bowler_conceded_runs == 0`, 71,304 balls).
  * Phase-adjusted bowling clutch comparison against Powerplay (9.18 RPO), Middle (9.01 RPO), and Death (10.52 RPO) baselines.
  * Applied credibility-weighted shrinkage heuristic ($w = n / (n + 30.0)$).
  * Exports: `batter_pressure_metrics.parquet` (888 rows, 77 cols) and `bowler_pressure_metrics.parquet` (647 rows, 102 cols).

---

## 13. Module 5 — Reliability Scoring and Evidence-Based Rankings

* **Scope:** Decoupled multi-dimensional performance ratings and evidence reliability scores.
* **Core Outputs:**
  * Evaluated 888 batters and 647 bowlers across independent disciplines.
  * Computed Evidence Reliability Score ($ERS$) across 4 exposure dimensions.
  * Enforced eligibility criteria ($\ge 20$ clutch balls AND $ERS \ge 20.0$), qualifying **304 eligible batters** and **290 eligible bowlers**.
  * Generated stratified role boards, Standout Performers, High-Upside Watchlist, and Regression Risks.
  * Exports: `batter_player_ratings.parquet` (888 rows), `bowler_player_ratings.parquet` (647 rows), `batter_player_rankings.csv` (304 rows), `bowler_player_rankings.csv` (290 rows), `player_ranking_sensitivity.csv` (6 scenarios).

---

## 14. Methodology and Mathematical Framework

### 14.1 Evidence Reliability Score ($ERS$)

The Evidence Reliability Score ($ERS \in [0.0, 100.0]$) quantifies statistical exposure and sample adequacy:

$$ERS = 0.40 \cdot S_{\text{clutch}} + 0.25 \cdot S_{\text{overall}} + 0.20 \cdot S_{\text{matches}} + 0.15 \cdot S_{\text{comps}}$$

Where each sub-score uses linear saturation benchmarks calibrated to professional T20 exposure distributions:

$$S_{\text{clutch}} = \text{clip}\left(\frac{n_{\text{clutch}}}{120.0} \times 100.0, 0.0, 100.0\right) \quad [\text{Target: 120 clutch balls, top-quartile exposure}]$$
$$S_{\text{overall}} = \text{clip}\left(\frac{n_{\text{overall}}}{300.0} \times 100.0, 0.0, 100.0\right) \quad [\text{Target: 300 total balls, ~15-20 T20 innings}]$$
$$S_{\text{matches}} = \text{clip}\left(\frac{m}{25.0} \times 100.0, 0.0, 100.0\right) \quad [\text{Target: 25 matches, multi-season presence}]$$
$$S_{\text{comps}} = \text{clip}\left(\frac{c}{3.0} \times 100.0, 0.0, 100.0\right) \quad [\text{Target: 3 competitions, cross-league versatility}]$$

**Critical Conceptual Boundary:** ERS is an exposure coverage index. It is **not** a probability that a player is good, **not** a confidence interval, **not** a Bayesian posterior, and **not** a future performance guarantee.

---

## 15. Final Batter and Bowler Ranking Methodology

### 15.1 Batting Performance Rating ($BPR \in [0.0, 100.0]$)

Every batter is evaluated across six traceable dimensions:

$$BPR = 0.30 \cdot S_{\text{scoring}} + 0.20 \cdot S_{\text{boundary}} + 0.15 \cdot S_{\text{rotation}} + 0.15 \cdot S_{\text{preservation}} + 0.10 \cdot S_{\text{clutch}} + 0.10 \cdot S_{\text{overall}}$$

* $S_{\text{scoring}}$: Clutch SR normalized $[70.0, 200.0]$ (Domain reasoning / design choice).
* $S_{\text{boundary}}$: Clutch Boundary % normalized $[0.0\%, 35.0\%]$ (Domain reasoning / design choice).
* $S_{\text{rotation}}$: Clutch Non-Dot % normalized $[20.0\%, 70.0\%]$ (Domain reasoning / design choice).
* $S_{\text{preservation}}$: Clutch Runs per Dismissal normalized $[0.0, 50.0]$ (Domain reasoning / design choice).
* $S_{\text{clutch}}$: Batting Clutch Index normalized $[0.0, 10.0]$ scaled to $[0.0, 100.0]$ (Model scale design).
* $S_{\text{overall}}$: Career SR Baseline normalized $[80.0, 180.0]$ (Domain reasoning / design choice).

### 15.2 Bowling Performance Rating ($BPR_{\text{bowl}} \in [0.0, 100.0]$)

Every bowler is evaluated across six traceable dimensions:

$$BPR_{\text{bowl}} = 0.25 \cdot S_{\text{run\_control}} + 0.20 \cdot S_{\text{dot\_creation}} + 0.20 \cdot S_{\text{wicket\_taking}} + 0.15 \cdot S_{\text{bnd\_supp}} + 0.10 \cdot S_{\text{overall}} + 0.10 \cdot S_{\text{clutch}}$$

* $S_{\text{run\_control}}$: Phase-adjusted delta economy normalized $[-3.0, +3.0]$ RPO (Domain reasoning / design choice).
* $S_{\text{dot\_creation}}$: True team dot % in clutch normalized $[15.0\%, 50.0\%]$ (Domain reasoning / design choice).
* $S_{\text{wicket\_taking}}$: Clutch wicket % normalized $[0.0\%, 12.0\%]$ (Domain reasoning / design choice).
* $S_{\text{bnd\_supp}}$: Inverted clutch boundary % normalized $[10.0\%, 30.0\%]$ (Domain reasoning / design choice).
* $S_{\text{overall}}$: Inverted overall career economy normalized $[6.0, 11.0]$ RPO (Domain reasoning / design choice).
* $S_{\text{clutch}}$: Bowling Clutch Index normalized $[0.0, 10.0]$ scaled to $[0.0, 100.0]$ (Model scale design).

---

## 16. Reliability and Eligibility Framework

Players are segmented into discrete evidence tiers based on their $ERS$ and conjunctional sample floors:

| Evidence Tier | Criteria | Batters Count | Bowlers Count | Treatment in Recruitment Strategy |
| :--- | :--- | :---: | :---: | :--- |
| **Strong Evidence** | $ERS \ge 60.0$ AND $n_{\text{clutch}} \ge 40$ AND $\text{matches} \ge 10$ | **201** | **206** | Core auction targets with extensive multi-tournament proof. |
| **Moderate Evidence** | $ERS \ge 35.0$ AND $n_{\text{clutch}} \ge 20$ AND $\text{matches} \ge 5$ | **103** | **84** | Viable targets with role-specific contextualization. |
| **Insufficient Evidence** | $n_{\text{overall}} \ge 30$ AND $n_{\text{clutch}} \ge 10$ (not Strong/Mod) | **163** | **156** | Emerging talents; isolated on Watchlist if performance is high. |
| **Not Eligible** | $n_{\text{overall}} < 30$ OR $n_{\text{clutch}} < 10$ | **421** | **201** | Excluded from player rankings due to negligible exposure. |

**Sub-20 Clutch Deliveries Classification:** Exactly 44 batters and 29 bowlers have between 5 and 19 clutch deliveries and $ERS \ge 20.0$. Because Moderate Evidence strictly enforces $n_{\text{clutch}} \ge 20$, 100% of these players have `is_eligible_for_ranking == False`. High-upside talents among them are monitored on the Watchlist.

**Official Leaderboard Cutoff:** Players must have `is_eligible_for_ranking == True` (`Strong Evidence` or `Moderate Evidence`), satisfying $n_{\text{clutch}} \ge 20$. This establishes **304 eligible batters** and **290 eligible bowlers**.

---

## 17. Sensitivity and Robustness Testing

To ensure rankings are not artifacts of specific weight choices, the models were stress-tested against 6 alternative weighting scenarios ($\pm 15\%$ variations) in `data/processed/player_ranking_sensitivity.csv`:

| Discipline | Scenario | Weight Shift Description | Spearman $\rho$ | Kendall $\tau$ | Mean Shift | Max Shift | Top 20 Retention |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Batting** | `Clutch_Heavy` | Clutch Scoring 40%, Clutch Index 25% | **0.9936** | 0.9352 | 7.05 | 37 | **18 / 20 (90%)** |
| **Batting** | `Baseline_Heavy` | Wicket Preservation 25%, Non-Dot 25% | **0.9925** | 0.9320 | 7.47 | 53 | **18 / 20 (90%)** |
| **Batting** | `Power_Hitting_Bias` | Boundary % 35%, Clutch Scoring 35% | **0.9755** | 0.8719 | 13.97 | 70 | **15 / 20 (75%)** |
| **Bowling** | `Clutch_Heavy` | Delta Economy 40%, Absolute Econ 25% | **0.9932** | 0.9324 | 7.08 | 34 | **18 / 20 (90%)** |
| **Bowling** | `Baseline_Heavy` | Absolute Econ 35%, True Dot % 30% | **0.9805** | 0.8828 | 12.37 | 67 | **17 / 20 (85%)** |
| **Bowling** | `Wicket_Attacking_Bias` | Wicket % 35%, Boundary Supp 25% | **0.9635** | 0.8394 | 16.38 | 85 | **14 / 20 (70%)** |

**Robustness Findings:**
* High relative rank stability: all Spearman correlations exceed **0.9635**.
* Top 20 retention ranges from **70% to 90%**, with lower retention in aggressive stress scenarios reflecting expected tactical divergence (strike bowlers advancing over run-containment spinners) rather than mathematical instability.
* **Scope Boundary:** These scenarios test parameter specification robustness; full statistical uncertainty quantification (bootstrapping and Bayesian posteriors) will be conducted in Module 6.

---

## 18. Validation and Testing

The repository includes an automated test suite executed via `pytest`:

```powershell
python -m pytest tests/ -v
```

### Test Suite Coverage:
* `tests/test_audit_reconciliation.py` (9 tests): Run reconciliation identities, balls-faced counts, dot-ball bifurcations, anomalous deliveries, wicket breakdowns, eligibility counts, 6-dimension bowling model verification, sub-20 clutch exclusions, and sensitivity ranges.
* `tests/test_module4_corrections.py` (6 tests): Scorecard balls faced, bat runs on no-balls, dot definitions, phase adjustment, and credibility weighting bounds.
* `tests/test_module5_ratings.py` (5 tests): ERS calculation bounds, performance rating monotonicity, role filtering, and rank sensitivity.
* **Test Outcome:** **20 passed in 4.06s** (100% pass rate).

---

## 19. Key Analytical Findings

### 19.1 Top 10 Eligible Batters
1. **Yashasvi Jaiswal** (Rank 1, Rating: 96.90, ERS: 63.00, Clutch SR: 225.64, 39 clutch balls)
2. **Finn Allen** (Rank 2, Rating: 93.48, ERS: 63.67, Clutch SR: 212.20, 41 clutch balls)
3. **Vipraj Nigam** (Rank 3, Rating: 92.52, ERS: 44.42, Clutch SR: 187.50, 72 clutch balls)
4. **Mahipal Lomror** (Rank 4, Rating: 85.26, ERS: 60.50, Clutch SR: 205.88, 51 clutch balls)
5. **Naman Dhir** (Rank 5, Rating: 84.48, ERS: 90.00, Clutch SR: 182.87, 216 clutch balls)
6. **Phil Salt** (Rank 6, Rating: 84.42, ERS: 78.33, Clutch SR: 190.59, 85 clutch balls)
7. **Matthew Wade** (Rank 7, Rating: 81.39, ERS: 90.00, Clutch SR: 171.97, 157 clutch balls)
8. **Asif Khan** (Rank 8, Rating: 81.20, ERS: 52.40, Clutch SR: 190.16, 61 clutch balls)
9. **Tim David** (Rank 9, Rating: 80.98, ERS: 90.00, Clutch SR: 179.25, 400 clutch balls)
10. **Shamar Springer** (Rank 10, Rating: 80.79, ERS: 37.02, Clutch SR: 172.58, 62 clutch balls)

### 19.2 Top 10 Eligible Bowlers
1. **Chris Woakes** (Rank 1, Rating: 90.22, ERS: 38.13, Clutch Econ: 6.56, Delta Econ: +2.91, 32 clutch balls)
2. **Sufiyan Muqeem** (Rank 2, Rating: 88.28, ERS: 90.00, Clutch Econ: 5.71, Delta Econ: +3.54, 126 clutch balls)
3. **George Dockrell** (Rank 3, Rating: 83.05, ERS: 52.17, Clutch Econ: 5.29, Delta Econ: +3.90, 59 clutch balls)
4. **Imad Wasim** (Rank 4, Rating: 81.42, ERS: 74.70, Clutch Econ: 6.00, Delta Econ: +3.19, 114 clutch balls)
5. **Matthew Humphreys** (Rank 5, Rating: 77.56, ERS: 64.87, Clutch Econ: 6.68, Delta Econ: +2.60, 71 clutch balls)
6. **Ehsan Khan** (Rank 6, Rating: 77.15, ERS: 60.20, Clutch Econ: 7.37, Delta Econ: +3.01, 57 clutch balls)
7. **Dushan Hemantha** (Rank 7, Rating: 76.76, ERS: 49.73, Clutch Econ: 7.50, Delta Econ: +1.84, 68 clutch balls)
8. **Benjamin Sears** (Rank 8, Rating: 75.30, ERS: 87.60, Clutch Econ: 7.91, Delta Econ: +1.62, 129 clutch balls, 15 wkts)
9. **George Linde** (Rank 9, Rating: 74.18, ERS: 71.52, Clutch Econ: 7.57, Delta Econ: +1.74, 88 clutch balls)
10. **Liam Dawson** (Rank 10, Rating: 72.68, ERS: 87.60, Clutch Econ: 7.05, Delta Econ: +2.13, 131 clutch balls, 12 wkts)

### 19.3 Specialized Analytical Cohorts
* **Standout Clutch Performers (High Rating + Strong Evidence):** Tim David, Matthew Wade, Phil Salt, Sufiyan Muqeem, Imad Wasim, Benjamin Sears, Taskin Ahmed, Jasprit Bumrah (541 clutch balls, +1.73 delta econ).
* **High-Upside Watchlist (High Rating + Low Evidence):** Jake Fraser-McGurk (Rating: 95.15, Clutch SR: 316.67, 12 balls), Vaibhav Sooryavanshi (Rating: 95.63, Clutch SR: 261.11, 18 balls), Kushal Bhurtel (Rating: 95.46, Clutch Econ: 4.74, 19 balls).
* **High-Volume Regression Risks (High Evidence + Poor Clutch Performance):** Romario Shepherd (Rating: 54.05, Clutch SR drops to 140.43 across 423 balls), Arshad Khan (Rating: 16.79, Concedes 14.05 RPO across 111 clutch balls), Mayank Markande (Rating: 15.79, Concedes 12.48 RPO across 150 clutch balls).

---

## 20. Limitations

1. **Phase Adjustment Residuals:** While phase baselines mitigate over-phase bias, residual confounding remains regarding opposition batter quality and venue pitch conditions.
2. **Cross-Tournament Standardisation:** Regional franchise leagues (CPL, BPL, SA20) possess differing competitive baselines from the IPL.
3. **No Direct Auction Recommendations in Module 5:** Module 5 delivers objective performance evidence. Auction price estimation, budget allocation, and team squad balance are strictly reserved for Module 7.

---

## 21. Instructions to Reproduce the Analysis

### Step 1: Environment Setup
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install pandas numpy scikit-learn pyarrow pytest nbformat matplotlib seaborn
```

### Step 2: Run Automated Test Suite
```powershell
python -m pytest tests/ -v
```

### Step 3: Execute Research Notebooks in Sequence
```powershell
jupyter notebook notebooks/01_data_understanding.ipynb
jupyter notebook notebooks/02_data_cleaning_and_integration.ipynb
jupyter notebook notebooks/03_pressure_index_framework.ipynb
jupyter notebook notebooks/04_player_performance_under_pressure.ipynb
jupyter notebook notebooks/05_player_reliability_and_rankings.ipynb
```

---

## 22. Current Project Status

* [x] **Module 1 — Data Understanding & Exploratory Data Analysis:** Completed and verified.
* [x] **Module 2 — Data Cleaning, Integration & Match-State Reconstruction:** Completed and verified.
* [x] **Module 3 — Pressure Index ($PI$) Mathematical Modelling:** Completed and verified.
* [x] **Module 4 — Player Performance Under Pressure:** Completed and verified (scorecard compliant, bifurcated dots, phase adjusted).
* [x] **Module 5 — Reliability Scoring & Evidence-Based Rankings:** Completed and verified (decoupled ratings, 304 eligible batters, 290 eligible bowlers, sensitivity verified).
* [ ] **Module 6 — Statistical Validation & Robustness:** Pending development.
* [ ] **Module 7 — Rajasthan Royals Squad Fit & Auction Strategy:** Pending development.
* [ ] **Module 8 — Interactive Dashboard:** Pending development (planned HTML/CSS/JS architecture on Netlify).
* [ ] **Module 9 — Final Competition Report & Presentation:** Pending development.

---

## 23. Future Work: Dashboard Development and Presentation

* **Interactive Scouting Dashboard:** Development of a high-performance web dashboard built in HTML5, CSS3, and modern JavaScript, featuring interactive player cards, scatter plots, role filters, and radar charts. The dashboard will be hosted on Netlify.
* **Squad Optimization Engine:** Implementation of an auction purse simulation model tailored to the Rajasthan Royals' retention sheet and role vacancies for IPL 2027.
* **Executive Presentation:** Preparation of an analytical slide deck and technical defense document summarizing methodology, findings, and strategic recruitment targets.
