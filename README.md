# SupeRR Selector — Cricket Player Performance Intelligence System
### Advanced High-Pressure Performance Modeling, Uncertainty Quantification & Tactical Recruitment Architecture for IPL 2027

[![Live Platform](https://img.shields.io/badge/Live%20Platform-superrrselection.netlify.app-ff2a85.svg?style=for-the-badge&logo=netlify)](https://superrrselection.netlify.app/)
[![Tests](https://img.shields.io/badge/Automated%20Tests-51%20Passed-10b981.svg?style=for-the-badge&logo=pytest)](tests/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3b82f6.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Author](https://img.shields.io/badge/Author-Syed%20Mohammad%20Hamzah-f59e0b.svg?style=for-the-badge&logo=github)](https://github.com/syedhamzah-dev)

> 🌐 **Live Web Application:** [**https://superrrselection.netlify.app/**](https://superrrselection.netlify.app/)  
> 📄 **Official Final PDF Report:** [`reports/SupeRR_Selector_Competition_Report.pdf`](reports/SupeRR_Selector_Competition_Report.pdf)  
> 💡 *SupeRR Intelligence: Discover Talent. Decode Performance. Make Smarter Decisions Under Pressure.*

---

## 1. Project Overview & Objectives

**SupeRR Selector** is a sports performance intelligence and player recruitment system engineered by **Syed Mohammad Hamzah** ([@syedhamzah-dev](https://github.com/syedhamzah-dev)).

Built for the **Rajasthan Royals Sports Analytics Challenge (Season 2)**, the platform addresses a core deficiency in traditional cricket analytics: standard statistics (batting averages, strike rates, economy rates) treat all match moments equally, disguising clutch execution failures, inflating low-leverage run accumulators, and obscuring genuine match-winning specialists.

By reconstructing **200,999 ball-by-ball delivery events** across **883 matches** (2022–2026), SupeRR Selector establishes:
1. A delivery-level, mathematically continuous **Pressure Index (0.00–10.00 scale)** isolating **50,713 clutch deliveries**.
2. Decoupled **Performance Ratings (PR: 0–100)** with Empirical Bayes credibility shrinkage to avoid small-sample distortions.
3. Multi-tournament **Evidence Reliability Scores (ERS: 0–90)** categorizing qualified candidates into Strong vs. Moderate evidence tiers.
4. **1,000-iteration cluster bootstrap resampling** generating 95% confidence intervals and a **Statistical Stability Score (SSS: 0–100)**.
5. An audited 27-player baseline evaluation identifying Rajasthan Royals' critical tactical voids (**Death-Overs Bowling** and **Lower-Order Finishing**).
6. Multi-criteria recruitment optimization via the **Recruitment Decision Heuristic (RDH: 0–90 scale)** and a flexible **100 Budget Allocation Units (BAU)** auction framework.
7. Strict recruitment data governance isolating **35 Viable Auction Targets** from non-auction assets and conditional scenarios.

---

## 2. Author & Project Ownership

* **Author & Lead Analytics Engineer:** **Syed Mohammad Hamzah**
* **GitHub Profile:** [@syedhamzah-dev](https://github.com/syedhamzah-dev)
* **Repository:** [`syedhamzah-dev/super__rr__selection`](https://github.com/syedhamzah-dev/super__rr__selection)
* **Academic Background:** B.Tech Computer Science & Engineering (Data Analytics)

> **Attribution Note:** This system, analytical models, codebase, interactive dashboard, and final report are the original work of **Syed Mohammad Hamzah**. Rajasthan Royals is acknowledged solely as the organizer of the sports analytics challenge and the provider of the underlying competition data pack.

---

## 3. Challenge Context & Problem Statement

In modern franchise T20 cricket, matches are decided in narrow, high-leverage margins:
* **Overall batting averages disguise clutch failures:** A top-order batter averaging 42.0 may accumulate runs in low-leverage dead rubbers or early powerplay overs, but collapse when required run rates exceed 11.0 RPO.
* **Traditional economy rates ignore phase context:** A bowler conceding 8.0 RPO exclusively in the low-risk middle overs appears artificially economical, whereas a death bowler conceding 8.8 RPO in overs 18–20 is delivering elite match-winning execution.
* **Small-sample volatility causes bidding traps:** An emerging player who executes one match-winning boundary in a playoff game often attracts severe bidding inflation, despite having insufficient evidence of repeatability.
* **Subjective recruitment vs. tactical voids:** Franchises frequently enter mega-auctions with speculative rupee targets, resulting in roster imbalances and budget exhaustion on redundant roles.

SupeRR Selector replaces subjective intuition with an empirical, end-to-end mathematical pipeline that identifies, stress-tests, and prioritizes actionable match-winners.

---

## 4. Audited Multi-Tournament Dataset Scope

The analytical models are derived strictly from audited ball-by-ball competition records spanning **2022 to 2026**:

| Metric | Audited Scope Value | Analytical Interpretation |
|---|---:|---|
| **Matches in Metadata** | **883** | Complete fixture universe across all three target competition tiers. |
| **Matches with Deliveries** | **867** | Fixtures with ball-by-ball event records (16 weather abandonments excluded). |
| **Deliveries Analysed** | **200,999** | Complete delivery events reconstructed with pre- and post-delivery state. |
| **Legal Balls Faced** | **193,285** | Scorecard convention (excludes wides; includes balls faced on no-balls). |
| **Total Batter Runs** | **269,550** | Off-the-bat runs accredited to individual batters. |
| **Total Bowler Wickets** | **10,272** | Bowler-credited dismissals (bowled, caught, lbw, stumped, hit wicket). |
| **Wides / No-Balls** | **7,714 / 840** | Full extra event tracking with ball re-bowling accounting. |
| **Clutch Deliveries** | **50,713** | Deliveries under extreme pressure ($\text{Pressure Index} \ge 6.0$, 25.23% of pool). |

### Competitions Covered (2022–2026)
1. **Indian Premier League (IPL):** 371 matches across seasons 2022, 2023, 2024, 2025, and 2026.
2. **International T20s (T20I):** 486 fixtures across ICC Full Member and Associate T20I matches (2022–2026).
3. **Emerging Teams & Rising Stars Asia Cups:** 26 fixtures (2024, 2025).

---

## 5. Technical Architecture & Technology Stack

```
┌────────────────────────────────────────────────────────────────────────┐
│                        SUPERR SELECTOR PIPELINE                        │
├────────────────────────────────────────────────────────────────────────┤
│  1. Ingestion & Match State    --> 883 Matches | 200,999 Deliveries    │
│  2. Delivery Pressure Index    --> Equation-Driven 0–10 Scale (50,713) │
│  3. Empirical Bayes Ratings    --> Decoupled Batting & Bowling PR      │
│  4. Scorecard Corrections      --> True Dot Bifurcation & Wides        │
│  5. Evidence Reliability (ERS) --> Linear Saturation Tiers (Strong/Mod)│
│  6. Uncertainty & Stability    --> 1,000 Bootstrap Resamples (SSS)    │
│  7. Squad Fit & Auction Model  --> 27-Player RR Audit | 100 BAU Purse │
│  8. Interactive Dashboard      --> Power BI Cockpit | Netlify CDN      │
└────────────────────────────────────────────────────────────────────────┘
```

* **Core Analytics & Modeling:** Python 3.10+, Pandas, NumPy, SciPy, Scikit-learn, PyArrow (Parquet & CSV).
* **Statistical Frameworks:** Empirical Bayes Shrinkage, 1,000-iteration Cluster Match Bootstrap, Herfindahl-Hirschman Volume Concentration Index (HHI), Leave-One-Match-Out (LOMO) Resilience.
* **Automated Testing Suite:** Pytest (51 passing unit, regression, governance, and headless DOM execution tests).
* **Frontend Web Application:** Semantic HTML5, CSS3 (Custom Responsive Dark Sports Analytics Theme), Vanilla ES6+ JavaScript, Chart.js 4.4.1 (Zero external heavyweight framework overhead).
* **Report Compilation:** Headless Google Chrome PDF rendering pipeline generating publication-grade documentation (`reports/SupeRR_Selector_Competition_Report.pdf`).
* **Cloud Infrastructure & Hosting:** Continuous deployment on Netlify with offline caching (`OFFLINE_DATA_BUNDLE`).

---

## 6. Analytical Modules 1–8

The project is structured into eight sequential modules:

### Module 1: Data Cleaning & Match-State Reconstruction
* Reconstructs delivery-level match states across 883 matches.
* Tracks dynamic match context: innings score, balls remaining, wickets in hand, target chase delta, and current required run rate (RRR).
* Cleans player entity IDs, aliases, and playing eleven line-ups.

### Module 2: Delivery-Level Pressure Index (0–10 Scale)
* Develops a mathematical continuous Pressure Index ($\text{PI} \in [0.0, 10.0]$).
* Calibrates match leverage using Win Probability swings, match phase multipliers (Powerplay 0.85, Middle 1.00, Death 1.35), required run rate escalation, and exponential resource decay based on wickets lost.
* Isolates **50,713 clutch deliveries** ($\text{PI} \ge 6.0$).

### Module 3: Performance Rating (PR) via Empirical Bayes
* Evaluates delivery execution under pressure using Bayesian credibility weighting toward tournament baselines.
* Batting PR ($\in [0, 100]$) combines clutch strike rate, boundary percentage, and dot-ball mitigation.
* Bowling PR ($\in [0, 100]$) combines phase-adjusted economy suppression, true dot-ball percentage, and clutch wicket threat.

### Module 4: Scorecard Conventions & True Dot-Ball Bifurcation
* Enforces MCC/IPL official scorecard conventions: batters are credited with balls faced on no-balls, while wides do not count as balls faced.
* Bifurcates dot balls: batter dots (deliveries resulting in 0 off-the-bat runs) vs. bowler dots (legal deliveries conceding 0 runs including extras).
* Adjusts bowling metrics for match phase scoring baselines.

### Module 5: Evidence Reliability Scoring (ERS) & Historical Rankings
* Quantifies supporting sample breadth ($\text{ERS} \in [0, 90]$) using linear saturation targets across clutch balls, total deliveries, matches played, and multi-tournament exposure.
* Enforces authoritative qualification tiers:
  * **Strong Evidence:** $\text{ERS} \ge 60.0$, $\ge 40$ clutch deliveries, $\ge 10$ matches.
  * **Moderate Evidence:** $\text{ERS} \ge 35.0$, $\ge 20$ clutch deliveries, $\ge 5$ matches.
* Produces baseline historical rankings for **304 qualified batters** and **290 qualified bowlers**.

### Module 6: Robustness Checks, Uncertainty & Statistical Stability (SSS)
* Executes **1,000 cluster-preserving match bootstrap iterations** to quantify rating uncertainty (95% confidence intervals).
* Calculates Top-20 ranking frequency across resamples, match volume concentration ($1 - \text{HHI}$), and Leave-One-Match-Out (LOMO) rating shifts.
* Synthesizes these metrics into the **Statistical Stability Score (SSS: 0–100)**, serving as a Top-Tier Impact Retention Index.

### Module 7: Squad Gap Analysis, Tactical Fit, ARS & 100 BAU Auction Strategy
* Audits Rajasthan Royals' 2026 baseline roster (27 registered players, 20 active rotation, 6 bench, 1 admin).
* Identifies critical squad voids: **Death-Overs Specialist Bowling** (Criticality 90.0) and **Lower-Order Finisher** (Criticality 87.5).
* Formulates Tactical Fit Score ($\text{TFS} \in [0, 100]$), Acquisition Risk Score ($\text{ARS} \in [0, 100]$), and the composite **Recruitment Decision Heuristic ($\text{RDH} \in [0, 90]$)**.
* Simulates five flexible **100 Budget Allocation Units (BAU)** auction capital allocation scenarios.

### Module 8: Interactive Dashboard & Governance Reconciliation
* Deploys the public **SupeRR Intelligence** platform with Power BI-style Cockpit, 5-dimension analytical Slicer Bar, interactive charts, and player profile compare trays.
* Establishes candidate governance isolating 35 viable auction targets from non-auction assets and conditional trade watches.

---

## 7. Key Analytical Metric Definitions

| Metric | Full Expansion | Scale | Direction | Formula & Definition |
|---|---|:---:|:---:|---|
| **PI** | **Pressure Index** | $0.00 - 10.00$ | Higher = Greater Tension | Continuous situational difficulty combining Leverage Index, required run rate, match phase, and wicket resources. $\text{PI} \ge 6.0$ defines **Clutch**. |
| **PR** | **Performance Rating** | $0.00 - 100.00$ | Higher is better | Empirical Bayes credibility rating measuring run scoring/suppression under pressure shrunk toward global tournament mean. |
| **ERS** | **Evidence Reliability Score** | $0.00 - 90.00$ | Higher = Greater Confidence | Sample depth score combining clutch balls, total deliveries, matches, and multi-competition exposure. Tiers: Strong ($\ge 60$) vs. Moderate ($35-59$). |
| **SSS** | **Statistical Stability Score** | $0.00 - 100.00$ | Higher = Greater Resilience | Top-Tier Impact Retention Index from 1,000 cluster bootstrap iterations: $0.35 \cdot \text{Top20Freq} + 0.25 \cdot \text{CI\_Stability} + 0.25 \cdot (1 - \text{HHI}) + 0.15 \cdot \text{LOMO}$. |
| **TFS** | **Tactical Fit Score** | $0.00 - 100.00$ | Higher = Better Alignment | Capability alignment with Rajasthan Royals' critical tactical voids (death bowling, finishing power, middle-overs spin). |
| **ARS** | **Acquisition Risk Score** | $0.00 - 100.00$ | Lower is safer | Expected auction bidding inflation (star-power premium) plus overseas roster slot friction penalty ($+6.0$ surcharge). |
| **RDH** | **Recruitment Decision Heuristic** | $0.00 - 90.00$ | Higher = Priority Target | $\text{RDH} = \text{clip}(0.30 \cdot \text{PR} + 0.20 \cdot \text{ERS} + 0.20 \cdot \text{SSS} + 0.20 \cdot \text{TFS} - 0.10 \cdot \text{ARS}, 0.0, 90.0)$. Positive weights sum to $0.90$. Never displayed as a percentage. |

---

## 8. Player Selection vs. Recruitment Governance

SupeRR Selector enforces a strict structural distinction between **Historical Performance Rankings** and **Actionable Recruitment Recommendations**:

```
50-PLAYER CANDIDATE RECRUITMENT MATRIX
├── 35 Viable Auction Targets (Actionable Bidding Candidates)
├──  1 Conditional Trade Watch (Marcus Stoinis — Retained by Punjab Kings)
├──  4 RR Core Internal Assets (Jurel, Jadeja, Parag, Bishnoi)
├──  5 Strategic Benchmarks — BCCI Ineligible (Muqeem, Wasim, Rauf, Afridi, Mir)
├──  4 Strategic Benchmarks — Rival Core (Bumrah, Suryakumar, Narine, Rinku Singh)
└──  1 Historical Reference — Retired (Dinesh Karthik)
```

### Critical Governance Rules
1. **Separation of Performance from Actionability:** An elite historical performer (e.g. Jasprit Bumrah $\text{PR} = 88.54$ or Heinrich Klaasen) is not an actionable recruitment target because they are retained franchise cornerstones. They are classified as **Strategic Benchmarks**.
2. **BCCI Policy Compliance:** Under long-standing BCCI regulatory policy, Pakistani players cannot register for the IPL auction. Elite performers like **Sufiyan Muqeem** ($\text{PR} = 88.28$, $\text{RDH} = 68.32$) and **Imad Wasim** ($\text{PR} = 81.42$) are retained strictly as comparative international benchmarks.
3. **Marcus Stoinis Governance Invariant:**
   * **Verified Status:** Punjab Kings (PBKS) officially retained Marcus Stoinis for IPL 2027 per the official announcement dated 18 November 2026.
   * **Classification:** Classified strictly as **`"Conditional Trade Watch — Currently Retained by Punjab Kings"`**.
   * **Availability:** Excluded from the open auction pool. Accessible to Rajasthan Royals only through a potential bilateral player trade subject to mutual franchise agreement and IPL trading rules. Clearly, **no trade has been confirmed**.
   * **Metric Integrity:** His historical metrics ($\text{PR} = 71.32$, $\text{ERS} = 90.0$, $\text{SSS} = 61.75$, $\text{TFS} = 69.65$, $\text{ARS} = 17.48$, $\text{RDH} = 63.93$) are preserved without modification.

---

## 9. Top Actionable Recruitment Recommendations

Ranked by Recruitment Decision Heuristic ($\text{RDH} \in [0.0, 90.0]$) to solve Rajasthan Royals' primary tactical voids:

### Top 10 Actionable Batters
| Rank | Player Name | Tactical Role | Country | PR (0–100) | ERS (0–90) | SSS (0–100) | TFS (0–100) | ARS (0–100) | RDH (0–90) | Primary Tactical Fit |
|:---:|---|---|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **1** | **Tim David** | Finisher | Australia | 80.98 | 90.0 | 74.73 | 83.84 | 13.58 | **72.65** | Elite death boundary striker (179.3 clutch SR). Direct fix for RR #1 void. |
| **2** | **Naman Dhir** | Batting All-Rounder | India | 84.48 | 90.0 | 72.54 | 74.45 | 11.08 | **72.54** | High-ceiling domestic versatility (168.2 clutch SR), saves overseas slot. |
| **3** | **Matthew Wade** | Wk-Finisher | Australia | 81.39 | 90.0 | 69.96 | 77.06 | 12.82 | **69.82** | Dual-role depth: reliable backup wicketkeeper + death finisher. |
| **4** | **Ashutosh Sharma** | Finisher | India | 74.65 | 90.0 | 68.74 | 82.25 | 11.45 | **66.09** | Domestic boundary enforcer (188.7 clutch SR) in crisis run chases. |
| **5** | **Mahipal Lomror** | Middle-Order Batter | India | 85.26 | 60.5 | 60.18 | 74.52 | 10.74 | **65.98** | Proven high-pressure spin-hitter (190.5 clutch SR) for middle overs. |
| **6** | **Abhishek Sharma** | Top-Order Batter | India | 79.52 | 90.0 | 66.86 | 65.02 | 11.41 | **65.08** | Explosive powerplay accelerator with bowling overs utility. |
| **7** | **Ayush Badoni** | Middle-Order Batter | India | 76.54 | 90.0 | 63.81 | 71.05 | 10.45 | **64.40** | High-leverage crisis accumulator with proven IPL match-finishing poise. |
| **8** | **Shai Hope** | Top-Order Batter | West Indies | 80.45 | 76.5 | 62.45 | 68.25 | 13.05 | **63.91** | Adaptable anchor capable of stabilizing collapse scenarios. |
| **9** | **Sanju Samson** | Top-Order / Wk | India | 75.82 | 90.0 | 64.12 | 70.15 | 10.82 | **63.69** | Existing RR asset benchmark representing elite top-order baseline. |
| **10** | **Sherfane Rutherford** | Finisher | West Indies | 72.48 | 84.2 | 60.52 | 80.12 | 13.85 | **63.53** | High-leverage boundary hitter with demonstrated death-overs power. |

### Top 10 Actionable Bowlers
| Rank | Player Name | Tactical Role | Country | PR (0–100) | ERS (0–90) | SSS (0–100) | TFS (0–100) | ARS (0–100) | RDH (0–90) | Primary Tactical Fit |
|:---:|---|---|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **1** | **Benjamin Sears** | Death-Overs Specialist | New Zealand | 75.30 | 87.6 | 70.52 | 79.84 | 14.85 | **65.27** | High-pace enforcer (15 clutch wickets, 145+ km/h) to close tight games. |
| **2** | **Liam Dawson** | Middle-Overs Spinner | England | 72.68 | 87.6 | 71.25 | 78.52 | 13.92 | **65.26** | Elite spin containment (6.42 clutch economy) + lower-order batting. |
| **3** | **Eshan Malinga** | Death-Overs Specialist | Sri Lanka | 71.85 | 82.4 | 67.45 | 78.12 | 14.25 | **63.07** | Slinging yorker specialist providing death-overs run suppression. |
| **4** | **George Linde** | Middle-Overs Spinner | South Africa | 74.18 | 71.5 | 66.82 | 74.25 | 13.15 | **62.85** | Multi-competition control spinner with power-hitting capabilities. |
| **5** | **Ottniel Baartman** | Death-Overs Specialist | South Africa | 70.42 | 81.0 | 66.12 | 79.52 | 14.05 | **62.58** | Heavy-ball specialist with deceptive changes of pace in overs 17–20. |
| **6** | **Dunith Wellalage** | Middle-Overs Spinner | Sri Lanka | 71.25 | 75.2 | 64.85 | 72.84 | 12.85 | **61.85** | Young multi-format left-arm orthodox spinner with tactical poise. |
| **7** | **Akeal Hosein** | Middle-Overs Spinner | West Indies | 69.85 | 85.0 | 65.12 | 72.15 | 13.95 | **61.82** | Elite new-ball and middle-overs spin with stingy boundary containment. |
| **8** | **Fazalhaq Farooqi** | New-Ball / Death Pacer | Afghanistan | 71.50 | 79.2 | 64.25 | 71.85 | 14.15 | **61.78** | Left-arm swing angle with high-speed yorker execution. |
| **9** | **Riley Meredith** | Death-Overs Specialist | Australia | 69.12 | 78.5 | 63.85 | 76.45 | 14.52 | **60.67** | Raw hit-the-deck pace supporting Jofra Archer in closing overs. |
| **10** | **Nathan Ellis** | Death-Overs Specialist | Australia | 68.45 | 82.0 | 64.12 | 77.25 | 14.88 | **60.55** | T20 specialist renowned for dipping slower balls and wide yorkers. |

---

## 10. Rajasthan Royals Squad Fit & 100 BAU Auction Strategy

### Audited Roster Baseline (27 Registered Players)
* **Active Playing XI / Rotation:** 20 players (16 matches played in 2026).
* **Bench Reserve Specialists:** 6 players (squad depth).
* **Administrative Registration:** 1 non-participant registration (Yuzvendra Chahal — 0 appearances).
* **Composition:** 19 Domestic players, 8 Overseas players.

### 100 Budget Allocation Units (BAU) Auction Model
Rather than fabricating fragile rupee prices (e.g. predicting a player at ₹14.5 Crore), SupeRR Selector employs a normalized **100 BAU model** where $1.0\text{ BAU} = 1.0\%$ of available purse:

| Scenario | Strategic Focus | Death Bowling (BAU) | Finisher Batting (BAU) | Spin & Multi-Role (BAU) | Dynamic Reserve (BAU) | Max Overseas Slots |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **Scenario A** | Balanced Roster Reinforcement | 40 BAU | 35 BAU | 15 BAU | 10 BAU | 3 Slots |
| **Scenario B** | Elite Pace Dominance | 45 BAU | 30 BAU | 15 BAU | 10 BAU | 3 Slots |
| **Scenario C** | Lower-Order Firepower First | 35 BAU | 40 BAU | 15 BAU | 10 BAU | 4 Slots |
| **Scenario D** | Domestic Core Value Max | 35 BAU | 35 BAU | 20 BAU | 10 BAU | 2 Slots |
| **Scenario E** | High-Flexibility Counter-Bidding | 30 BAU | 30 BAU | 20 BAU | 20 BAU | 3 Slots |

---

## 11. Dashboard Overview (SupeRR Intelligence)

The interactive dashboard is live at [**https://superrrselection.netlify.app/**](https://superrrselection.netlify.app/) and includes:

* **Executive Cockpit (Overview):** Power BI-style KPI tiles, delivery pressure distribution doughnut, Bayesian PR vs. SSS scatter chart, and Module 5 top-10 leaderboards.
* **Interactive Slicer Bar:** Live cross-filters across Competition, Season, Tactical Role, Candidate Affiliation, and Evidence Tier with instant empty-state handling.
* **Dedicated Top 10 Picks:** Showcase views for actionable batting and bowling targets with tactical gap tags and *"Why this player?"* scouting rationales.
* **Batter & Bowler Explorers:** Multi-attribute filtering across 304 batters and 290 bowlers with overall vs. clutch splits.
* **Side-by-Side Compare Tray:** Pin up to 3 candidates simultaneously across PR, ERS, SSS, TFS, and ARS.
* **Squad Gap Matrix:** Interactive role depth coverage and void criticality across Scenarios A, B, and C.
* **Auction Strategy Simulator:** Interactive capital allocation bar charts across 5 BAU scenarios.
* **Metric Accessibility Glossary:** Searchable definitions, equations, interpretations, and caveats for all metrics.

---

## 12. Repository Structure

```
Rajhstan royals/
├── dashboard/                  # Production Interactive Dashboard (Module 8)
│   ├── index.html              # Single-page Power BI-inspired web application
│   ├── css/
│   │   └── style.css           # Responsive sports-tech dark theme (RR Pink & Royal Blue)
│   ├── js/
│   │   ├── app.js              # Application controller, navigation, and slicer logic
│   │   ├── charts.js           # Chart.js visualization engine (Scatter, Doughnut, Bars)
│   │   ├── data.js             # DataManager with asynchronous fetching & offline fallback
│   │   └── data_bundle.js      # Bundled offline data for zero-network execution
│   └── data/                   # Production JSON feeds exported from verified models
│       ├── batters_data.json   # 304 eligible batters with PR, ERS, and bootstrap metrics
│       ├── bowlers_data.json   # 290 eligible bowlers with phase adjustments
│       ├── recruitment_matrix.json # Authoritative 50-player candidate decision matrix
│       ├── rr_squad_data.json  # 27 registered RR baseline players
│       ├── squad_gaps_data.json# 36 tactical role depth evaluations
│       ├── auction_scenarios.json # 5 dynamic 100 BAU auction scenarios
│       ├── overview_stats.json # Global KPI summaries and scope records
│       └── methodology_data.json # Governance rules, formulas, and assumptions register
├── data/
│   └── processed/              # Authoritative Parquet & CSV analytical tables
├── notebooks/                  # Step-by-step Jupyter research notebooks (Modules 1–7)
├── reports/                    # Competition deliverable generation scripts & documents
│   ├── generate_competition_report.py # Automated report generation pipeline
│   ├── SupeRR_Selector_Competition_Report.html # Publication HTML source
│   ├── SupeRR_Selector_Competition_Report.md   # Executive markdown report
│   └── SupeRR_Selector_Competition_Report.pdf  # 23-page verified competition PDF
├── src/                        # Core Python analytical library
│   ├── batter_pressure_analysis.py  # Batting pressure metrics & role classification
│   ├── bowler_pressure_analysis.py  # Bowling phase adjustments & true dot bifurcation
│   ├── reliability_scoring.py       # Empirical Bayes shrinkage & ERS calibration
│   ├── bootstrap_validation.py      # 1,000 cluster match bootstrap resampling & SSS
│   ├── squad_context.py             # Squad gap arithmetic, TFS, ARS, and RDH
│   ├── generate_module6_outputs.py  # Module 6 processing runner
│   ├── generate_module7_outputs.py  # Module 7 recommendation matrix runner
│   └── export_dashboard_data.py     # Authoritative dashboard JSON & bundle exporter
├── tests/                      # Automated test suite (51 tests, 100% pass rate)
│   ├── test_audit_reconciliation.py # Scope, delivery count, and formula identity checks
│   ├── test_module4_corrections.py  # Scorecard convention & dot ball tests
│   ├── test_module5_ratings.py      # Bayes shrinkage & ERS tier validation
│   ├── test_module6_robustness.py   # Bootstrap CI bounds, HHI, and ranking stability
│   ├── test_module7_squad_fit.py    # TFS bounds, budget conservation, and limits
│   ├── test_module8_dashboard.py    # JSON schema, DOM elements, and headless execution
│   └── test_homepage_logic.js       # Node.js mock DOM runtime execution test
├── index.html                  # Root landing page with auto-redirect to dashboard
├── requirements.txt            # Python dependencies
└── README.md                   # Authoritative repository documentation
```

---

## 13. Installation, Execution & Testing Instructions

### 1. Prerequisites
* Python 3.10 or higher
* Node.js v18+ (for headless DOM unit tests)
* Modern web browser (Chrome, Edge, Firefox, Safari)

### 2. Environment Setup
Clone the repository:
```bash
git clone https://github.com/syedhamzah-dev/super__rr__selection.git
cd super__rr__selection
```

Create and activate a virtual environment:
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Run Automated Tests
Execute the complete 51-test validation suite:
```bash
python -m pytest tests/ -v
```
*Expected Result:* `51 passed in ~6.5s` (100% pass rate).

### 4. Regenerate Analytical Models & Exports
To regenerate all processed datasets, models, and dashboard JSON feeds:
```bash
python src/generate_module6_outputs.py
python src/generate_module7_outputs.py
python src/export_dashboard_data.py
```

### 5. Launch the Dashboard Locally
Serve the dashboard via local HTTP server:
```bash
python -m http.server 8000 --directory dashboard
```
Open your browser and navigate to:
```
http://localhost:8000/
```
*(Alternatively, simply open `dashboard/index.html` directly in any web browser — the application includes an offline memory bundle fallback that functions without network access).*

### 6. Generate the Competition PDF Report
To recompile the official 23-page PDF report:
```bash
python reports/generate_competition_report.py
```
Outputs: `reports/SupeRR_Selector_Competition_Report.pdf`.

---

## 14. Limitations & Future Scope

### Analytical Limitations
1. **Historical Evidence vs. Future Guarantees:** High performance ratings reflect empirical delivery-level execution in 2022–2026. They do not constitute an unconditional guarantee of future IPL performance.
2. **Auction Registration Conditionality:** All actionable candidates are potential targets whose actual availability depends on official BCCI player registration lists for the IPL 2027 auction.
3. **Pitch & Environmental Micro-Variables:** While the Pressure Index incorporates required run rate and phase pressure, it does not explicitly adjust for extreme pitch wear, dew factors, or ground dimension asymmetries.
4. **Normalized Auction Units vs. Live Bidding Wars:** The 100 BAU model provides strategic capital allocation guidelines; actual auction prices can deviate due to multi-team bidding escalations.

### Future Research Directions
* **Computer Vision Biomechanics Integration:** Incorporating release speed, ball tracking deviation, and seam presentation into bowling acquisition risk models.
* **Matchup Matrix (Ball-Type vs. Batter Sub-Archetype):** Deepening tactical fit evaluation by assessing candidate performance against specific bowling variations (e.g., left-arm wrist spin, hard-length pace).
* **Dynamic Live Auction In-Game Optimizer:** Integrating live auction purse tracking to adjust remaining BAU targets dynamically as bidding unfolds.

---

## 15. Author Attribution & Acknowledgements

### Project Author
* **Lead Analytics Engineer & Author:** **Syed Mohammad Hamzah**
* **GitHub:** [@syedhamzah-dev](https://github.com/syedhamzah-dev)
* **Live Dashboard:** [https://superrrselection.netlify.app/](https://superrrselection.netlify.app/)

### Acknowledgements
* **Rajasthan Royals:** For hosting the **Sports Analytics Challenge (Season 2)** and supplying the comprehensive competition data pack (2022–2026).
* **Cricket Analytics Community:** For pioneering research into Win Probability Added (WPA), Leverage Index (LI), and Empirical Bayes credibility shrinkage in sports performance modeling.

---

*SupeRR Selector is an independent sports analytics project developed by Syed Mohammad Hamzah for the Rajasthan Royals Sports Analytics Challenge 2026.*
