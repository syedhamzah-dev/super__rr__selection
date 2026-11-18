/**
 * SupeRR Selector - Interactive Chart Engine (Reconciled & Audited)
 * Built with Chart.js, fully branded in Rajasthan Royals colors.
 */

const ChartManager = {
  charts: {},

  // Global Chart.js styling defaults
  applyGlobalTheme() {
    if (typeof Chart === "undefined") return;
    
    Chart.defaults.color = "#94a3b8";
    Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    Chart.defaults.font.size = 11.5;
    Chart.defaults.plugins.tooltip.backgroundColor = "#161e2e";
    Chart.defaults.plugins.tooltip.titleColor = "#f8fafc";
    Chart.defaults.plugins.tooltip.bodyColor = "#cbd5e1";
    Chart.defaults.plugins.tooltip.borderColor = "#2b3547";
    Chart.defaults.plugins.tooltip.borderWidth = 1;
    Chart.defaults.plugins.tooltip.padding = 10;
    Chart.defaults.plugins.tooltip.cornerRadius = 6;
  },

  destroyChart(id) {
    if (this.charts[id]) {
      this.charts[id].destroy();
      delete this.charts[id];
    }
  },

  /**
   * 1. Scatter Chart: Batter PR vs ERS (Authoritative Module 5 Tiers)
   */
  renderBatterPRvsERS(canvasId, batters) {
    if (typeof Chart === "undefined") return;
    this.destroyChart(canvasId);

    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    // Split by authoritative Module 5 tier
    const strong = batters.filter(b => b.evidence_tier === "Strong");
    const moderate = batters.filter(b => b.evidence_tier === "Moderate");

    const formatData = list => list.map(b => ({
      x: b.evidence_reliability_score,
      y: b.performance_rating,
      player: b
    }));

    this.charts[canvasId] = new Chart(ctx, {
      type: "scatter",
      data: {
        datasets: [
          {
            label: `Strong Evidence (ERS ≥ 60, Clutch ≥ 40, Matches ≥ 10; n=${strong.length})`,
            data: formatData(strong),
            backgroundColor: "#10b981",
            borderColor: "#059669",
            pointRadius: 5.5,
            pointHoverRadius: 8
          },
          {
            label: `Moderate Evidence (ERS ≥ 35, Clutch ≥ 20, Matches ≥ 5; n=${moderate.length})`,
            data: formatData(moderate),
            backgroundColor: "#3b82f6",
            borderColor: "#2563eb",
            pointRadius: 4.5,
            pointHoverRadius: 7
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "top", labels: { boxWidth: 12 } },
          tooltip: {
            callbacks: {
              title: items => items[0].raw.player.player_name,
              label: item => {
                const p = item.raw.player;
                return [
                  `Role: ${p.tactical_role} (${p.country})`,
                  `Performance Rating (PR): ${p.performance_rating.toFixed(2)}`,
                  `Evidence Reliability (ERS): ${p.evidence_reliability_score.toFixed(2)} (${p.evidence_tier_label})`,
                  `Clutch SR: ${p.sr_clutch.toFixed(1)} | Runs: ${p.runs_clutch}`,
                  `Category: ${p.candidate_category}`
                ];
              }
            }
          }
        },
        scales: {
          x: {
            title: { display: true, text: "Evidence Reliability Score (ERS, 0–100; Linear Saturation)" },
            grid: { color: "rgba(255, 255, 255, 0.05)" },
            min: 20,
            max: 100
          },
          y: {
            title: { display: true, text: "Performance Rating (PR, 0–100; Empirical Bayes Shrinkage)" },
            grid: { color: "rgba(255, 255, 255, 0.05)" },
            min: 30,
            max: 100
          }
        }
      }
    });
  },

  /**
   * 2. Scatter Chart: Bowler PR vs ERS (Authoritative Module 5 Tiers)
   */
  renderBowlerPRvsERS(canvasId, bowlers) {
    if (typeof Chart === "undefined") return;
    this.destroyChart(canvasId);

    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const strong = bowlers.filter(b => b.evidence_tier === "Strong");
    const moderate = bowlers.filter(b => b.evidence_tier === "Moderate");

    const formatData = list => list.map(b => ({
      x: b.evidence_reliability_score,
      y: b.performance_rating,
      player: b
    }));

    this.charts[canvasId] = new Chart(ctx, {
      type: "scatter",
      data: {
        datasets: [
          {
            label: `Strong Evidence (ERS ≥ 60, Clutch ≥ 40, Matches ≥ 10; n=${strong.length})`,
            data: formatData(strong),
            backgroundColor: "#10b981",
            borderColor: "#059669",
            pointRadius: 5.5,
            pointHoverRadius: 8
          },
          {
            label: `Moderate Evidence (ERS ≥ 35, Clutch ≥ 20, Matches ≥ 5; n=${moderate.length})`,
            data: formatData(moderate),
            backgroundColor: "#3b82f6",
            borderColor: "#2563eb",
            pointRadius: 4.5,
            pointHoverRadius: 7
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "top", labels: { boxWidth: 12 } },
          tooltip: {
            callbacks: {
              title: items => items[0].raw.player.player_name,
              label: item => {
                const p = item.raw.player;
                return [
                  `Role: ${p.tactical_role} (${p.country})`,
                  `Performance Rating (PR): ${p.performance_rating.toFixed(2)}`,
                  `Evidence Reliability (ERS): ${p.evidence_reliability_score.toFixed(2)} (${p.evidence_tier_label})`,
                  `Clutch Econ: ${p.economy_clutch.toFixed(2)} | Wkts: ${p.wickets_clutch}`,
                  `Category: ${p.candidate_category}`
                ];
              }
            }
          }
        },
        scales: {
          x: {
            title: { display: true, text: "Evidence Reliability Score (ERS, 0–100; Linear Saturation)" },
            grid: { color: "rgba(255, 255, 255, 0.05)" },
            min: 20,
            max: 100
          },
          y: {
            title: { display: true, text: "Performance Rating (PR, 0–100; Phase-Adjusted Shrinkage)" },
            grid: { color: "rgba(255, 255, 255, 0.05)" },
            min: 30,
            max: 100
          }
        }
      }
    });
  },

  /**
   * 3. Candidate PR vs SSS (Top-Tier Impact Retention Index)
   */
  renderPRvsSSS(canvasId, candidates) {
    if (typeof Chart === "undefined") return;
    this.destroyChart(canvasId);

    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const viable = candidates.filter(c => c.candidate_category === "Viable Auction Target");
    const benchmarks = candidates.filter(c => c.candidate_category !== "Viable Auction Target");

    const formatData = list => list.map(c => ({
      x: c.performance_rating,
      y: c.statistical_stability_score,
      player: c
    }));

    this.charts[canvasId] = new Chart(ctx, {
      type: "scatter",
      data: {
        datasets: [
          {
            label: "Viable Auction Targets (Actionable)",
            data: formatData(viable),
            backgroundColor: "#ff2a85",
            borderColor: "#e01e73",
            pointRadius: 6,
            pointHoverRadius: 9
          },
          {
            label: "Strategic Benchmarks & Internal Assets (Non-Auction)",
            data: formatData(benchmarks),
            backgroundColor: "#f59e0b",
            borderColor: "#d97706",
            pointRadius: 5,
            pointHoverRadius: 8
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "top", labels: { boxWidth: 12 } },
          tooltip: {
            callbacks: {
              title: items => items[0].raw.player.player_name,
              label: item => {
                const p = item.raw.player;
                return [
                  `${p.discipline}: ${p.tactical_role} (${p.country})`,
                  `Performance Rating (PR): ${p.performance_rating.toFixed(2)}`,
                  `Stability Score (SSS - Top-Tier Impact Retention): ${p.statistical_stability_score.toFixed(2)}`,
                  `Decision Score (RDH): ${p.recruitment_decision_score.toFixed(2)} / 90.0`,
                  `Status: ${p.candidate_category}`
                ];
              }
            }
          }
        },
        scales: {
          x: {
            title: { display: true, text: "Performance Rating (PR, 0–100)" },
            grid: { color: "rgba(255, 255, 255, 0.05)" },
            min: 50,
            max: 100
          },
          y: {
            title: { display: true, text: "Statistical Stability Score (SSS, 0–100; Top-Tier Impact Retention Index)" },
            grid: { color: "rgba(255, 255, 255, 0.05)" },
            min: 15,
            max: 100
          }
        }
      }
    });
  },

  /**
   * 4. Horizontal Bar: RR Squad Role Depth vs Safe Minimum
   */
  renderRoleDepthCoverage(canvasId, gapEvaluations, selectedScenario = "Scenario A") {
    if (typeof Chart === "undefined") return;
    this.destroyChart(canvasId);

    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const filtered = gapEvaluations.filter(g => g.scenario.includes(selectedScenario));
    const labels = filtered.map(g => g.tactical_role);
    const domesticCounts = filtered.map(g => g.squad_count_domestic);
    const overseasCounts = filtered.map(g => g.squad_count_overseas);

    this.charts[canvasId] = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Domestic Retained Depth",
            data: domesticCounts,
            backgroundColor: "#1e88e5"
          },
          {
            label: "Overseas Retained Depth",
            data: overseasCounts,
            backgroundColor: "#ff2a85"
          }
        ]
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            stacked: true,
            title: { display: true, text: "Squad Count (Players in Role)" },
            grid: { color: "rgba(255, 255, 255, 0.05)" },
            suggestedMax: 4
          },
          y: {
            stacked: true,
            grid: { display: false }
          }
        },
        plugins: {
          legend: { position: "top" },
          tooltip: {
            callbacks: {
              afterBody: items => {
                const idx = items[0].dataIndex;
                const row = filtered[idx];
                return [
                  `Status: ${row.depth_status}`,
                  `Severity: ${row.gap_severity}`,
                  `Players: ${row.players_in_role}`
                ];
              }
            }
          }
        }
      }
    });
  },

  /**
   * 5. Tactical Gap Matrix: Criticality & Severity
   */
  renderTacticalGaps(canvasId, gapEvaluations, selectedScenario = "Scenario A") {
    if (typeof Chart === "undefined") return;
    this.destroyChart(canvasId);

    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const filtered = gapEvaluations.filter(g => g.scenario.includes(selectedScenario));
    const labels = filtered.map(g => g.tactical_role);
    const criticality = filtered.map(g => g.gap_criticality_weight);
    
    const severityScores = filtered.map(g => {
      if (g.gap_severity === "Critical") return 90;
      if (g.gap_severity === "High") return 75;
      if (g.gap_severity === "Moderate") return 50;
      return 25;
    });

    this.charts[canvasId] = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Tactical Gap Criticality Weight",
            data: criticality,
            backgroundColor: "rgba(255, 42, 133, 0.7)",
            borderColor: "#ff2a85",
            borderWidth: 1
          },
          {
            label: "Gap Severity Score",
            data: severityScores,
            backgroundColor: "rgba(245, 158, 11, 0.7)",
            borderColor: "#f59e0b",
            borderWidth: 1
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            grid: { display: false },
            ticks: { maxRotation: 45, minRotation: 45 }
          },
          y: {
            title: { display: true, text: "Evaluation Score (0–100)" },
            grid: { color: "rgba(255, 255, 255, 0.05)" },
            max: 100
          }
        },
        plugins: {
          legend: { position: "top" }
        }
      }
    });
  },

  /**
   * 6 & 7. Shortlist Candidate Squad Fit (PR, SSS, TFS)
   */
  renderShortlistFit(canvasId, shortlist, titleLabel = "Batting") {
    if (typeof Chart === "undefined") return;
    this.destroyChart(canvasId);

    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const topCandidates = shortlist.slice(0, 8);
    const labels = topCandidates.map(c => c.player_name);
    const prs = topCandidates.map(c => c.performance_rating);
    const ssss = topCandidates.map(c => c.statistical_stability_score);
    const tfss = topCandidates.map(c => c.tactical_squad_fit_score);

    this.charts[canvasId] = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Performance Rating (PR)",
            data: prs,
            backgroundColor: "#ff2a85"
          },
          {
            label: "Statistical Stability (SSS - Impact Retention)",
            data: ssss,
            backgroundColor: "#1e88e5"
          },
          {
            label: "Tactical Squad Fit (TFS)",
            data: tfss,
            backgroundColor: "#10b981"
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { display: false } },
          y: {
            title: { display: true, text: "Component Score (0–100)" },
            grid: { color: "rgba(255, 255, 255, 0.05)" },
            max: 100
          }
        },
        plugins: {
          legend: { position: "top" }
        }
      }
    });
  },

  /**
   * 8. Scatter: Acquisition Risk (ARS) vs Tactical Squad Fit (TFS)
   */
  renderRiskVsFit(canvasId, matrix) {
    if (typeof Chart === "undefined") return;
    this.destroyChart(canvasId);

    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const viable = matrix.filter(c => c.candidate_category === "Viable Auction Target");
    const benchmarks = matrix.filter(c => c.candidate_category !== "Viable Auction Target");

    const formatData = list => list.map(c => ({
      x: c.tactical_squad_fit_score,
      y: c.acquisition_risk_score,
      player: c
    }));

    this.charts[canvasId] = new Chart(ctx, {
      type: "scatter",
      data: {
        datasets: [
          {
            label: "Viable Auction Candidates (Actionable)",
            data: formatData(viable),
            backgroundColor: "#10b981",
            borderColor: "#059669",
            pointRadius: 6,
            pointHoverRadius: 9
          },
          {
            label: "Benchmarks & Internal Assets (Non-Auction)",
            data: formatData(benchmarks),
            backgroundColor: "#64748b",
            borderColor: "#475569",
            pointRadius: 5,
            pointHoverRadius: 8
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "top" },
          tooltip: {
            callbacks: {
              title: items => items[0].raw.player.player_name,
              label: item => {
                const p = item.raw.player;
                return [
                  `Role: ${p.tactical_role} (${p.country})`,
                  `Tactical Fit (TFS): ${p.tactical_squad_fit_score.toFixed(2)}`,
                  `Acquisition Risk (ARS): ${p.acquisition_risk_score.toFixed(2)}`,
                  `Decision Score (RDH): ${p.recruitment_decision_score.toFixed(2)} / 90.0`,
                  `Category: ${p.candidate_category}`
                ];
              }
            }
          }
        },
        scales: {
          x: {
            title: { display: true, text: "Tactical Squad Fit Score (TFS, Higher = Better Fit)" },
            grid: { color: "rgba(255, 255, 255, 0.05)" },
            min: 50,
            max: 95
          },
          y: {
            title: { display: true, text: "Acquisition Risk Score (ARS, Lower = Safer Acquisition)" },
            grid: { color: "rgba(255, 255, 255, 0.05)" },
            min: 5,
            max: 30
          }
        }
      }
    });
  },

  /**
   * 9. Stacked Bar: Auction Scenarios Budget Allocations (100 BAU)
   */
  renderAuctionScenarios(canvasId, scenarios) {
    if (typeof Chart === "undefined") return;
    this.destroyChart(canvasId);

    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const labels = scenarios.map(s => s.scenario_name);
    
    const batting = [];
    const bowling = [];
    const multiRole = [];
    const contingency = [];

    scenarios.forEach(s => {
      const getUnits = cat => {
        const found = s.budget_allocations.find(a => a.allocation_category.toLowerCase().includes(cat));
        return found ? found.budget_units : 0;
      };
      batting.push(getUnits("batting"));
      bowling.push(getUnits("bowling"));
      multiRole.push(getUnits("multi"));
      contingency.push(getUnits("contingency") || getUnits("reserve"));
    });

    this.charts[canvasId] = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          { label: "Batting Reinforcement", data: batting, backgroundColor: "#ff2a85" },
          { label: "Bowling Reinforcement", data: bowling, backgroundColor: "#1e88e5" },
          { label: "Multi-Role / All-Rounders", data: multiRole, backgroundColor: "#10b981" },
          { label: "Contingency / Dynamic Bids", data: contingency, backgroundColor: "#f59e0b" }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { stacked: true, grid: { display: false } },
          y: {
            stacked: true,
            title: { display: true, text: "Budget Allocation Units (Total: 100 BAU)" },
            grid: { color: "rgba(255, 255, 255, 0.05)" },
            max: 100
          }
        },
        plugins: {
          legend: { position: "top" }
        }
      }
    });
  }
};
