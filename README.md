# SupeRR Selector

### A Cricket Player Intelligence System for Identifying Reliable Match-Winners Under Pressure

[![Tests](https://img.shields.io/badge/tests-45%20passed-brightgreen.svg)](tests/)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Dashboard](https://img.shields.io/badge/dashboard-live-ff2a85.svg)](dashboard/index.html)

---

## 1. About the Project

**SupeRR Selector** is a cricket analytics system that evaluates how T20 players perform when matches are on the line. 

Developed for the **Rajasthan Royals Sports Analytics Challenge (Season 2)**, the project analyzes ball-by-ball data from major Men's T20 competitions between 2022 and 2026. Its goal is to move beyond standard averages and help cricket teams discover players who consistently deliver in difficult, high-pressure match situations.

---

## 2. The Problem

Traditional cricket statistics often tell an incomplete story:

* **Overall averages can hide clutch failures:** A batter with a 40+ average might score most of their runs in low-pressure situations when victory is already assured, but struggle during tight chases.
* **Economy rates ignore match phase:** A bowler with an 8.0 economy rate who bowls mostly in the middle overs may actually be more expensive than average, while a bowler with an 8.5 rate in the death overs is performing exceptionally well.
* **Small samples create misleading spikes:** An emerging player who hits two boundaries in one close game can briefly look like a superstar, but may lack the consistency to repeat it across a full season.

Teams need an objective way to ask: **Who can we trust when the pressure is at its highest?**

---

## 3. What Does It Do?

SupeRR Selector provides four core analytical capabilities:

* **Measures Match Pressure Ball by Ball:** Tracks wickets in hand, balls remaining, and required run rates for every delivery to score how tense each moment is on a 0 to 10 scale.
* **Separates Performance from Sample Size:** Evaluates player skill under pressure while separately measuring their total volume of experience. This ensures experienced, proven performers are ranked fairly against promising newcomers.
* **Checks Ranking Stability:** Tests whether a player's standing is steady across multiple games or heavily driven by a single standout performance.
* **Guides Squad and Auction Planning:** Compares candidate profiles directly against Rajasthan Royals' specific squad gaps (such as death-overs bowling and lower-order finishing) using a 100-unit budget allocation framework without making up unrealistic player prices.

---

## 4. Explore the Dashboard

An interactive cricket analytics dashboard (**Module 8**) is built directly in the repository using clean HTML5, CSS3, and Vanilla JavaScript with Chart.js:

* **Batter & Bowler Explorers:** Search, filter, and inspect 304 eligible batters and 290 eligible bowlers by role, origin (Domestic vs. Overseas), and evidence tier, with full overall vs. clutch metric splits.
* **Side-by-Side Player Comparison:** Compare up to 3 candidates simultaneously across Performance Rating (PR), Evidence Reliability (ERS), Statistical Stability (SSS), Tactical Squad Fit (TFS), and Acquisition Risk (ARS).
* **Rajasthan Royals Squad Analysis:** Review Rajasthan Royals' audited 2026 baseline roster (27 registered players) and evaluate tactical depth gaps across Scenarios A, B, and C.
* **Recruitment Recommendation Matrix:** Authoritative 50-player candidate decision matrix clearly separating actionable auction targets from non-actionable strategic benchmarks (Pakistani stars, rival franchise core retentions, and retired veterans).
* **Auction Strategy Simulator:** Interactive 100 Budget Allocation Units (BAU) scenario simulator across 5 squad-building strategies with candidate buy lists and overseas slot demand.

> **How to Run the Dashboard Locally:**
> ```powershell
> python -m http.server 8000
> ```
> Then navigate your web browser to: **`http://localhost:8000/dashboard/index.html`** (or `http://localhost:8000/`).

---

## 5. How It Works

The system processes and evaluates players through five clear steps:

1. **Match-State Reconstruction:** Cleans and processes over 200,000 deliveries from 883 matches, calculating live game context (such as required run rate and balls remaining) before and after every ball.
2. **Pressure Index Calculation:** Measures situational difficulty for both first-innings target setting and second-innings chases, grouping deliveries into Low, Medium, High, and Clutch pressure.
3. **Clutch Performance Scoring:** Evaluates how batters handle rising run rates and dot balls, and measures how bowlers contain boundaries in high-scoring phases compared to league baselines.
4. **Reliability and Stability Auditing:** Resamples tournament matches to confirm that top rankings hold up over time and are not simply the result of one lucky day.
5. **Squad Fit and Role Allocation:** Identifies Rajasthan Royals' primary needs ahead of IPL 2027 and matches players to those voids while respecting squad size and overseas player limits.

---

## 6. Key Strategic Findings at a Glance

* **Top Batting Target (Overseas):** **Tim David** (Finisher). Proven multi-match death-overs boundary hitter with 400 pressure balls of experience and high statistical stability.
* **Top Batting Target (Domestic):** **Naman Dhir** (Batting All-Rounder). Combines high-pressure scoring power with useful bowling overs, saving a valuable overseas roster spot.
* **Dual-Role Depth:** **Matthew Wade** (Wicketkeeper-Finisher). Solves Rajasthan Royals' backup wicketkeeping need while adding experienced lower-order finishing power.
* **Top Bowling Target (Overseas):** **Benjamin Sears** (Death-Overs Specialist). High-pace enforcer with 15 clutch wickets to partner Jofra Archer in closing out tight innings.
* **Strategic Spin Target:** **Liam Dawson** (Middle-Overs Control Spinner). Elite containment spinner with high tournament pedigree and lower-order batting capability.
* **International Tactical Benchmarks:** Players like **Sufiyan Muqeem** (5.71 clutch economy) and **Imad Wasim** are retained strictly as global comparative benchmarks; under BCCI regulatory policy, Pakistani players are ineligible for IPL auction recruitment.
* **Smart Redundancy Avoidance:** Outstanding openers like **Finn Allen** are deprioritized because Rajasthan Royals already possesses elite opening talent in Yashasvi Jaiswal and Vaibhav Sooryavanshi.
* **Volatility Warnings:** High-rated players whose numbers depend heavily on a single match (such as **Chris Woakes**) are clearly flagged for caution.

---

## 7. Technology Used

* **Languages:** Python 3.10+, HTML5, CSS3, Vanilla JavaScript (ES6+)
* **Interactive Dashboard:** HTML5, CSS3 (Responsive Dark Sports Analytics Theme), Chart.js 4.4.1 (No heavy JS frameworks)
* **Data Processing:** pandas, NumPy, PyArrow (Parquet & CSV formats)
* **Statistical Modeling:** scikit-learn, SciPy (Empirical Bayes Credibility Shrinkage, 1,000 Bootstrap Resampling)
* **Automated Testing:** pytest (45 unit, governance, and dashboard tests, 100% pass rate)
* **Visualizations & Notebooks:** Matplotlib, Seaborn, Jupyter Notebook

---

## 8. Project Structure

```
Rajhstan royals/
├── dashboard/            # Interactive Web Dashboard (Module 8)
│   ├── index.html        # Single-page dashboard application with 7 tabbed views
│   ├── css/style.css     # Responsive sports analytics dark theme (RR Pink & Royal Blue)
│   ├── js/               # Modular application scripts (app.js, data.js, charts.js)
│   └── data/             # Lightweight JSON feeds exported from verified analytical models
├── index.html            # Root web entrypoint with auto-redirect to dashboard
├── Data Pack/            # Original competition CSV files (deliveries, matches, lineups)
├── data/processed/       # Verified clean datasets, ratings, and squad models (Parquet & CSV)
├── notebooks/            # Seven step-by-step Jupyter notebooks covering Modules 1 to 7
├── src/                  # Core Python modules for data processing, scoring, and strategy
├── tests/                # Automated test suite ensuring 100% data and logic accuracy (45 tests)
└── reports/              # Methodology reports, documentation summaries, and visual figures
    └── figures/          # High-resolution publication charts and analytical plots
```

---

## 9. How to Run Locally

### 1. Prerequisites
Ensure you have Python 3.10 or higher installed on your machine.

### 2. Set Up Environment
Clone or navigate to the project directory:

```powershell
cd "c:\Users\mohdh\Desktop\Projects\Rajhstan royals"
```

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\activate
```

Install the project dependencies:

```powershell
pip install pandas numpy scikit-learn pyarrow pytest nbformat matplotlib seaborn
```

### 3. Launch the Interactive Dashboard (Module 8)
Start a lightweight local web server from the project root:

```powershell
python -m http.server 8000
```

Open your browser and navigate to:
* **`http://localhost:8000/dashboard/index.html`** (or `http://localhost:8000/`)

To re-export or update the dashboard JSON feeds from processed analytical tables:

```powershell
python src/export_dashboard_data.py
```

### 4. Run Automated Tests
Verify that all 45 data integrity, logic, governance, and dashboard tests pass:

```powershell
python -m pytest tests/ -v
```

### 5. Run Analytical Generation Scripts
Regenerate all processed datasets, models, and publication figures directly:

```powershell
python src/generate_module6_outputs.py
python src/generate_module7_outputs.py
```

### 6. Explore Research Notebooks
Launch Jupyter to inspect any research module interactively:

```powershell
jupyter notebook notebooks/
```

---

## 10. Limitations

* **Past Performance vs. Future Results:** Strong past performance under pressure is a helpful guide, but it does not guarantee future success under new match conditions, pitches, or team dynamics.
* **Sample Size Realities:** Players with very few high-pressure deliveries are placed on a watchlist rather than ranked on primary auction leaderboards.
* **Tournament Context:** Playing conditions and competition standards differ across international matches and regional T20 leagues.
* **Auction Dynamics:** The 100-unit budget allocation model represents strategic squad priority. It does not attempt to predict exact rupee bids or erratic bidding wars during live auctions.

---

## 11. Acknowledgements

This project was built for the **Rajasthan Royals Sports Analytics Challenge (Season 2)**, using the official competition data pack covering T20 cricket from 2022 to 2026.

Special thanks to the sports analytics community for open research into win probability, run-rate pressure modeling, and cricket performance metrics.
