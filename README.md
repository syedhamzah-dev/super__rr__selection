# SupeRR Selector

### A Cricket Player Intelligence System for Identifying Reliable Match-Winners Under Pressure

[![Tests](https://img.shields.io/badge/tests-38%20passed-brightgreen.svg)](tests/)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

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

An interactive scouting dashboard (Module 8) is being built to make these insights intuitive and easy to explore in a web browser:

* **Player Scouting Cards:** Search and filter over 300 batters and 290 bowlers by role, origin (Domestic vs. Overseas), and performance level.
* **Performance vs. Reliability Quadrants:** Quickly spot proven core targets, emerging high-potential picks, and volatile performers.
* **Squad Gap Explorer:** Review Rajasthan Royals' current depth chart across 12 specific on-field roles.
* **Auction Strategy Simulator:** Explore different squad-building scenarios to see how capital can be allocated across priority positions.

> **Live Dashboard Status:** The interactive web dashboard is currently in active development for Module 8 and will be hosted live on Netlify. In the meantime, all charts and outputs can be viewed in the `reports/figures/` folder or explored interactively using the notebooks in `notebooks/`.

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
* **Top Bowling Target (Overseas):** **Sufiyan Muqeem** (Middle-Overs Spinner). Elite middle-overs run containment with a 5.71 clutch economy rate across 25 matches.
* **Defensive Bowling Anchor:** **Imad Wasim** (Bowling All-Rounder). Outstanding economy under pressure combined with reliable lower-order batting.
* **Primary Death Pacer:** **Benjamin Sears** (Death Specialist). High-pace enforcer with 15 clutch wickets to partner Jofra Archer in closing out innings.
* **Smart Redundancy Avoidance:** Outstanding openers like **Finn Allen** are deprioritized because Rajasthan Royals already has elite young opening talent in Yashasvi Jaiswal and Vaibhav Sooryavanshi.
* **Volatility Warnings:** High-rated players whose numbers depend heavily on a single match (such as **Chris Woakes**) are clearly flagged for caution.

---

## 7. Technology Used

* **Language:** Python 3.10+
* **Data Processing:** pandas, NumPy, PyArrow (Parquet format)
* **Statistical Modeling:** scikit-learn, SciPy
* **Automated Testing:** pytest (38 unit and governance tests, 100% pass rate)
* **Visualizations & Notebooks:** Matplotlib, Seaborn, Jupyter Notebook

---

## 8. Project Structure

```
Rajhstan royals/
├── Data Pack/            # Original competition CSV files (deliveries, matches, lineups)
├── data/processed/       # Verified clean datasets, ratings, and squad models (Parquet & CSV)
├── notebooks/            # Seven step-by-step Jupyter notebooks covering Modules 1 to 7
├── src/                  # Core Python modules for data processing, scoring, and strategy
├── tests/                # Automated test suite ensuring 100% data and logic accuracy
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

### 3. Run Automated Tests
Verify that all 38 data integrity, logic, and governance tests pass:

```powershell
python -m pytest tests/ -v
```

### 4. Run Analysis Scripts
Generate all analytical datasets and figures directly from the command line:

```powershell
python src/generate_module6_outputs.py
python src/generate_module7_outputs.py
```

### 5. Explore Research Notebooks
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
