/**
 * SupeRR Selector - Main Interactive Application (Audited & Reconciled)
 * Orchestrates navigation, filtering, rendering, modals, and user events.
 */

const App = {
  activeTab: "overview",
  
  // State for Batters Explorer
  batterFilters: {
    search: "",
    role: "ALL",
    country: "ALL",
    tier: "ALL",
    category: "ALL",
    actionableOnly: false,
    sortKey: "recruitment_decision_score",
    sortDir: "desc",
    page: 1,
    pageSize: 15
  },

  // State for Bowlers Explorer
  bowlerFilters: {
    search: "",
    role: "ALL",
    country: "ALL",
    tier: "ALL",
    category: "ALL",
    actionableOnly: false,
    sortKey: "recruitment_decision_score",
    sortDir: "desc",
    page: 1,
    pageSize: 15
  },

  // State for Recruitment Shortlist
  recruitmentFilters: {
    tab: "all",
    actionableOnly: false
  },

  // State for Squad Analysis
  selectedSquadScenario: "Scenario A",

  // State for Auction Strategy
  selectedAuctionScenarioIndex: 0,

  /**
   * Bootstraps the dashboard application
   */
  async init() {
    console.log("Initializing SupeRR Selector Interactive Dashboard...");
    ChartManager.applyGlobalTheme();

    try {
      await DataManager.loadAllData();
      console.log("Datasets successfully loaded into memory.");

      this.setupNavigation();
      this.setupEventListeners();
      this.populateFilterDropdowns();

      // Render Initial Views
      this.renderOverview();
      this.renderBatterExplorer();
      this.renderBowlerExplorer();
      this.renderRRSquadAnalysis();
      this.renderRecruitmentShortlists();
      this.renderAuctionStrategy();
      this.renderMethodology();

      // Activate default tab
      this.switchTab("overview");

    } catch (err) {
      console.error("Dashboard initialization error:", err);
      const main = document.querySelector(".main-content");
      if (main) {
        main.innerHTML = `<div class="governance-alert" style="border-left-color: #ef4444;">
          <div class="alert-icon">⚠️</div>
          <div class="alert-content">
            <strong>Data Loading Notice:</strong> Failed to initialize dashboard datasets via fetch.
            <p>If you are opening this file locally (via file://), please serve this folder using a local web server:</p>
            <pre style="margin-top: 8px; background: #0f172a; padding: 8px; border-radius: 4px; font-family: monospace;">python -m http.server 8000 --bind 127.0.0.1</pre>
            <p style="margin-top: 6px;">Then open: <a href="http://127.0.0.1:8000/dashboard/index.html" style="color: #38bdf8;">http://127.0.0.1:8000/dashboard/index.html</a></p>
          </div>
        </div>`;
      }
    }
  },

  /**
   * Tab Navigation handler
   */
  setupNavigation() {
    const navButtons = document.querySelectorAll(".nav-tab");
    navButtons.forEach(btn => {
      btn.addEventListener("click", () => {
        const tabId = btn.getAttribute("data-tab");
        this.switchTab(tabId);
      });
    });

    document.addEventListener("click", e => {
      const jumpTarget = e.target.closest("[data-jump]");
      if (jumpTarget) {
        const targetTab = jumpTarget.getAttribute("data-jump");
        this.switchTab(targetTab);
      }
    });
  },

  switchTab(tabId) {
    this.activeTab = tabId;

    document.querySelectorAll(".nav-tab").forEach(b => {
      b.classList.toggle("active", b.getAttribute("data-tab") === tabId);
    });

    document.querySelectorAll(".tab-pane").forEach(pane => {
      pane.classList.toggle("active", pane.id === `pane-${tabId}`);
    });

    window.scrollTo({ top: 0, behavior: "smooth" });
    this.refreshActiveCharts(tabId);
  },

  refreshActiveCharts(tabId) {
    setTimeout(() => {
      if (tabId === "overview") {
        if (DataManager.data.recruitmentMatrix.length > 0) {
          ChartManager.renderPRvsSSS("chart-overview-pr-sss", DataManager.data.recruitmentMatrix);
        }
      } else if (tabId === "batters") {
        ChartManager.renderBatterPRvsERS("chart-batters-scatter", DataManager.data.batters);
      } else if (tabId === "bowlers") {
        ChartManager.renderBowlerPRvsERS("chart-bowlers-scatter", DataManager.data.bowlers);
      } else if (tabId === "squad") {
        ChartManager.renderRoleDepthCoverage("chart-squad-depth", DataManager.data.squadGaps, this.selectedSquadScenario);
        ChartManager.renderTacticalGaps("chart-squad-gaps", DataManager.data.squadGaps, this.selectedSquadScenario);
      } else if (tabId === "recruitment") {
        const topB = DataManager.data.recruitmentMatrix.filter(c => c.discipline === "Batting");
        const topBw = DataManager.data.recruitmentMatrix.filter(c => c.discipline === "Bowling");
        ChartManager.renderShortlistFit("chart-shortlist-batting", topB, "Batting Targets");
        ChartManager.renderShortlistFit("chart-shortlist-bowling", topBw, "Bowling Targets");
        ChartManager.renderRiskVsFit("chart-risk-vs-fit", DataManager.data.recruitmentMatrix);
      } else if (tabId === "auction") {
        ChartManager.renderAuctionScenarios("chart-auction-allocations", DataManager.data.auctionScenarios);
      }
    }, 50);
  },

  /**
   * Populate Filter Dropdowns dynamically
   */
  populateFilterDropdowns() {
    // 1. Batters Filters
    const bRoles = [...new Set(DataManager.data.batters.map(b => b.tactical_role))].sort();
    const bCountries = [...new Set(DataManager.data.batters.map(b => b.country))].sort();
    
    const bRoleSelect = document.getElementById("batter-role-filter");
    if (bRoleSelect) {
      bRoleSelect.innerHTML = `<option value="ALL">All Roles (${bRoles.length})</option>` +
        bRoles.map(r => `<option value="${r}">${r}</option>`).join("");
    }

    const bCountrySelect = document.getElementById("batter-country-filter");
    if (bCountrySelect) {
      bCountrySelect.innerHTML = `<option value="ALL">All Countries (${bCountries.length})</option>` +
        bCountries.map(c => `<option value="${c}">${c}</option>`).join("");
    }

    // 2. Bowlers Filters
    const bwRoles = [...new Set(DataManager.data.bowlers.map(bw => bw.tactical_role))].sort();
    const bwCountries = [...new Set(DataManager.data.bowlers.map(bw => bw.country))].sort();

    const bwRoleSelect = document.getElementById("bowler-role-filter");
    if (bwRoleSelect) {
      bwRoleSelect.innerHTML = `<option value="ALL">All Bowling Roles (${bwRoles.length})</option>` +
        bwRoles.map(r => `<option value="${r}">${r}</option>`).join("");
    }

    const bwCountrySelect = document.getElementById("bowler-country-filter");
    if (bwCountrySelect) {
      bwCountrySelect.innerHTML = `<option value="ALL">All Countries (${bwCountries.length})</option>` +
        bwCountries.map(c => `<option value="${c}">${c}</option>`).join("");
    }
  },

  /**
   * Setup Event Listeners for Filters, Sorting, Modals
   */
  setupEventListeners() {
    // --- Batters Controls ---
    const bSearch = document.getElementById("batter-search");
    if (bSearch) {
      bSearch.addEventListener("input", e => {
        this.batterFilters.search = e.target.value;
        this.batterFilters.page = 1;
        this.renderBatterTable();
      });
    }

    const bRole = document.getElementById("batter-role-filter");
    if (bRole) {
      bRole.addEventListener("change", e => {
        this.batterFilters.role = e.target.value;
        this.batterFilters.page = 1;
        this.renderBatterTable();
      });
    }

    const bCountry = document.getElementById("batter-country-filter");
    if (bCountry) {
      bCountry.addEventListener("change", e => {
        this.batterFilters.country = e.target.value;
        this.batterFilters.page = 1;
        this.renderBatterTable();
      });
    }

    const bTier = document.getElementById("batter-tier-filter");
    if (bTier) {
      bTier.addEventListener("change", e => {
        this.batterFilters.tier = e.target.value;
        this.batterFilters.page = 1;
        this.renderBatterTable();
      });
    }

    const bCat = document.getElementById("batter-category-filter");
    if (bCat) {
      bCat.addEventListener("change", e => {
        this.batterFilters.category = e.target.value;
        this.batterFilters.page = 1;
        this.renderBatterTable();
      });
    }

    const bActionable = document.getElementById("batter-actionable-toggle");
    if (bActionable) {
      bActionable.addEventListener("change", e => {
        this.batterFilters.actionableOnly = e.target.checked;
        this.batterFilters.page = 1;
        this.renderBatterTable();
      });
    }

    const bReset = document.getElementById("batter-reset-btn");
    if (bReset) {
      bReset.addEventListener("click", () => {
        this.batterFilters = {
          search: "", role: "ALL", country: "ALL", tier: "ALL", category: "ALL",
          actionableOnly: false, sortKey: "recruitment_decision_score", sortDir: "desc",
          page: 1, pageSize: 15
        };
        if (bSearch) bSearch.value = "";
        if (bRole) bRole.value = "ALL";
        if (bCountry) bCountry.value = "ALL";
        if (bTier) bTier.value = "ALL";
        if (bCat) bCat.value = "ALL";
        if (bActionable) bActionable.checked = false;
        this.renderBatterTable();
      });
    }

    // --- Bowlers Controls ---
    const bwSearch = document.getElementById("bowler-search");
    if (bwSearch) {
      bwSearch.addEventListener("input", e => {
        this.bowlerFilters.search = e.target.value;
        this.bowlerFilters.page = 1;
        this.renderBowlerTable();
      });
    }

    const bwRole = document.getElementById("bowler-role-filter");
    if (bwRole) {
      bwRole.addEventListener("change", e => {
        this.bowlerFilters.role = e.target.value;
        this.bowlerFilters.page = 1;
        this.renderBowlerTable();
      });
    }

    const bwCountry = document.getElementById("bowler-country-filter");
    if (bwCountry) {
      bwCountry.addEventListener("change", e => {
        this.bowlerFilters.country = e.target.value;
        this.bowlerFilters.page = 1;
        this.renderBowlerTable();
      });
    }

    const bwTier = document.getElementById("bowler-tier-filter");
    if (bwTier) {
      bwTier.addEventListener("change", e => {
        this.bowlerFilters.tier = e.target.value;
        this.bowlerFilters.page = 1;
        this.renderBowlerTable();
      });
    }

    const bwCat = document.getElementById("bowler-category-filter");
    if (bwCat) {
      bwCat.addEventListener("change", e => {
        this.bowlerFilters.category = e.target.value;
        this.bowlerFilters.page = 1;
        this.renderBowlerTable();
      });
    }

    const bwActionable = document.getElementById("bowler-actionable-toggle");
    if (bwActionable) {
      bwActionable.addEventListener("change", e => {
        this.bowlerFilters.actionableOnly = e.target.checked;
        this.bowlerFilters.page = 1;
        this.renderBowlerTable();
      });
    }

    const bwReset = document.getElementById("bowler-reset-btn");
    if (bwReset) {
      bwReset.addEventListener("click", () => {
        this.bowlerFilters = {
          search: "", role: "ALL", country: "ALL", tier: "ALL", category: "ALL",
          actionableOnly: false, sortKey: "recruitment_decision_score", sortDir: "desc",
          page: 1, pageSize: 15
        };
        if (bwSearch) bwSearch.value = "";
        if (bwRole) bwRole.value = "ALL";
        if (bwCountry) bwCountry.value = "ALL";
        if (bwTier) bwTier.value = "ALL";
        if (bwCat) bwCat.value = "ALL";
        if (bwActionable) bwActionable.checked = false;
        this.renderBowlerTable();
      });
    }

    // Modal close listeners
    document.querySelectorAll(".modal-close, .modal-backdrop").forEach(el => {
      el.addEventListener("click", e => {
        if (e.target === el) {
          document.querySelectorAll(".modal-backdrop").forEach(m => m.classList.remove("active"));
        }
      });
    });

    // Comparison Trigger Button
    const cmpTrigger = document.getElementById("compare-tray-trigger");
    if (cmpTrigger) {
      cmpTrigger.addEventListener("click", () => this.openComparisonModal());
    }

    // Squad Scenario Switcher
    document.querySelectorAll(".squad-scenario-btn").forEach(btn => {
      btn.addEventListener("click", e => {
        document.querySelectorAll(".squad-scenario-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        this.selectedSquadScenario = btn.getAttribute("data-scenario");
        this.renderRRSquadAnalysis();
      });
    });

    // Auction Scenario Switcher
    document.addEventListener("click", e => {
      const scenBtn = e.target.closest(".scenario-btn");
      if (scenBtn) {
        document.querySelectorAll(".scenario-btn").forEach(b => b.classList.remove("active"));
        scenBtn.classList.add("active");
        this.selectedAuctionScenarioIndex = parseInt(scenBtn.getAttribute("data-index"), 10);
        this.renderAuctionStrategy();
      }
    });

    // Shortlist Subtab Switcher
    document.querySelectorAll(".shortlist-tab-btn").forEach(btn => {
      btn.addEventListener("click", e => {
        document.querySelectorAll(".shortlist-tab-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        this.recruitmentFilters.tab = btn.getAttribute("data-filter");
        this.renderRecruitmentShortlists();
      });
    });
  },

  /**
   * Helper to format badges
   */
  getCategoryBadge(category) {
    if (category.includes("Viable")) {
      return `<span class="badge badge-viable">✓ Potential Target</span>`;
    } else if (category.includes("Ineligible")) {
      return `<span class="badge badge-ineligible">⚠ Non-Actionable (BCCI Ineligible)</span>`;
    } else if (category.includes("Rival")) {
      return `<span class="badge badge-rival">🔒 Non-Actionable (Rival Core)</span>`;
    } else if (category.includes("Internal") || category.includes("RR")) {
      return `<span class="badge badge-internal">★ RR Internal Asset</span>`;
    } else if (category.includes("Retired")) {
      return `<span class="badge badge-retired">Historical Reference (Retired)</span>`;
    }
    return `<span class="badge badge-role">${category}</span>`;
  },

  getTierBadge(tierCode, tierLabel) {
    if (tierCode === "Strong" || (tierLabel && tierLabel.includes("Strong"))) {
      return `<span class="badge badge-tier-1">Strong Evidence</span>`;
    }
    return `<span class="badge badge-tier-2">Moderate Evidence</span>`;
  },

  // ---------------------------------------------------------------------------
  // PAGE 1: Overview
  // ---------------------------------------------------------------------------
  renderOverview() {
    const stats = DataManager.data.overview;
    if (!stats) return;

    // Set Reconciled KPI cards
    const elMatches = document.getElementById("kpi-matches");
    if (elMatches) elMatches.textContent = `${stats.dataset_scope.total_matches_in_metadata} (${stats.dataset_scope.total_matches_with_deliveries} Enriched)`;

    const elBalls = document.getElementById("kpi-deliveries");
    if (elBalls) elBalls.textContent = stats.dataset_scope.total_deliveries_analyzed.toLocaleString();

    const elBatters = document.getElementById("kpi-batters");
    if (elBatters) elBatters.textContent = `${stats.candidate_pool.eligible_batters_count} / ${stats.candidate_pool.total_batters_evaluated}`;

    const elBowlers = document.getElementById("kpi-bowlers");
    if (elBowlers) elBowlers.textContent = `${stats.candidate_pool.eligible_bowlers_count} / ${stats.candidate_pool.total_bowlers_evaluated}`;

    const elRoster = document.getElementById("kpi-rr-roster");
    if (elRoster) elRoster.textContent = `${stats.rr_squad_baseline.total_registered_players} (${stats.rr_squad_baseline.active_playing_xi_rotation} Active)`;

    // Top Actionable Targets preview table
    const topRecruitsBody = document.getElementById("overview-top-recruits-body");
    if (topRecruitsBody) {
      const topB = stats.top_actionable_targets.batting.slice(0, 3);
      const topBw = stats.top_actionable_targets.bowling.slice(0, 3);
      const combined = [
        ...topB.map(b => ({ ...b, discipline: "Batting" })),
        ...topBw.map(bw => ({ ...bw, discipline: "Bowling" }))
      ];

      topRecruitsBody.innerHTML = combined.map(p => `
        <tr>
          <td><strong style="color: #fff;">${p.name}</strong> <span class="badge badge-role">${p.country}</span></td>
          <td><span class="badge ${p.discipline === 'Batting' ? 'badge-internal' : 'badge-tier-2'}">${p.discipline}</span></td>
          <td>${p.role}</td>
          <td class="metric-pill font-mono">${p.pr.toFixed(2)}</td>
          <td class="metric-pill font-mono">${p.tfs.toFixed(2)}</td>
          <td class="metric-pill font-mono" style="color: #f87171;">${p.ars.toFixed(2)}</td>
          <td class="metric-pill highlight font-mono">${p.rdh.toFixed(2)}</td>
        </tr>
      `).join("");
    }
  },

  // ---------------------------------------------------------------------------
  // PAGE 2: Batter Explorer
  // ---------------------------------------------------------------------------
  renderBatterExplorer() {
    this.renderBatterTable();
  },

  renderBatterTable() {
    const list = DataManager.filterBatters(this.batterFilters);
    const tbody = document.getElementById("batters-table-body");
    if (!tbody) return;

    // Pagination
    const total = list.length;
    const totalPages = Math.ceil(total / this.batterFilters.pageSize) || 1;
    if (this.batterFilters.page > totalPages) this.batterFilters.page = 1;
    const startIdx = (this.batterFilters.page - 1) * this.batterFilters.pageSize;
    const pageItems = list.slice(startIdx, startIdx + this.batterFilters.pageSize);

    const counterEl = document.getElementById("batters-count-display");
    if (counterEl) {
      counterEl.textContent = `Showing ${pageItems.length} of ${total} eligible batters`;
    }

    if (pageItems.length === 0) {
      tbody.innerHTML = `<tr><td colspan="12" style="text-align:center; padding: 24px; color: var(--text-muted);">No batters matched the active filter criteria.</td></tr>`;
      return;
    }

    tbody.innerHTML = pageItems.map((b, idx) => {
      const inComp = DataManager.comparisonList.some(p => p.player_id === b.player_id && p.discipline === "Batting");
      return `
        <tr>
          <td class="table-rank ${b.rank <= 10 ? 'top-10' : ''}">${b.rank}</td>
          <td>
            <div class="player-cell">
              <div>
                <span class="player-cell-name" onclick="App.openPlayerModal(${b.player_id}, 'Batting')">${b.player_name}</span>
                <div class="player-cell-sub">${b.country} • ${b.is_overseas ? 'Overseas' : 'Domestic'}</div>
              </div>
            </div>
          </td>
          <td><span class="badge badge-role">${b.tactical_role}</span></td>
          <td>${this.getCategoryBadge(b.candidate_category)}</td>
          <td>${this.getTierBadge(b.evidence_tier, b.evidence_tier_label)}</td>
          <td class="metric-pill font-mono">${b.performance_rating.toFixed(2)}</td>
          <td class="metric-pill font-mono blue">${b.evidence_reliability_score.toFixed(1)}</td>
          <td class="metric-pill font-mono" title="Top-Tier Impact Retention Index">${b.statistical_stability_score.toFixed(1)}</td>
          <td class="metric-pill font-mono">${b.tactical_squad_fit_score.toFixed(1)}</td>
          <td class="metric-pill font-mono" style="color: #f87171;">${b.acquisition_risk_score.toFixed(1)}</td>
          <td class="metric-pill highlight font-mono">${b.recruitment_decision_score.toFixed(2)}</td>
          <td style="text-align: right;">
            <button class="btn btn-sm ${inComp ? 'btn-primary' : ''}" onclick="App.toggleCompare(${b.player_id}, 'Batting')">
              ${inComp ? '✓ In Compare' : '+ Compare'}
            </button>
            <button class="btn btn-sm" onclick="App.openPlayerModal(${b.player_id}, 'Batting')">Details</button>
          </td>
        </tr>
      `;
    }).join("");

    this.renderPagination("batters-pagination", this.batterFilters.page, totalPages, newPage => {
      this.batterFilters.page = newPage;
      this.renderBatterTable();
    });
  },

  // ---------------------------------------------------------------------------
  // PAGE 3: Bowler Explorer
  // ---------------------------------------------------------------------------
  renderBowlerExplorer() {
    this.renderBowlerTable();
  },

  renderBowlerTable() {
    const list = DataManager.filterBowlers(this.bowlerFilters);
    const tbody = document.getElementById("bowlers-table-body");
    if (!tbody) return;

    const total = list.length;
    const totalPages = Math.ceil(total / this.bowlerFilters.pageSize) || 1;
    if (this.bowlerFilters.page > totalPages) this.bowlerFilters.page = 1;
    const startIdx = (this.bowlerFilters.page - 1) * this.bowlerFilters.pageSize;
    const pageItems = list.slice(startIdx, startIdx + this.bowlerFilters.pageSize);

    const counterEl = document.getElementById("bowlers-count-display");
    if (counterEl) {
      counterEl.textContent = `Showing ${pageItems.length} of ${total} eligible bowlers`;
    }

    if (pageItems.length === 0) {
      tbody.innerHTML = `<tr><td colspan="12" style="text-align:center; padding: 24px; color: var(--text-muted);">No bowlers matched the active filter criteria.</td></tr>`;
      return;
    }

    tbody.innerHTML = pageItems.map((bw, idx) => {
      const inComp = DataManager.comparisonList.some(p => p.player_id === bw.player_id && p.discipline === "Bowling");
      return `
        <tr>
          <td class="table-rank ${bw.rank <= 10 ? 'top-10' : ''}">${bw.rank}</td>
          <td>
            <div class="player-cell">
              <div>
                <span class="player-cell-name" onclick="App.openPlayerModal(${bw.player_id}, 'Bowling')">${bw.player_name}</span>
                <div class="player-cell-sub">${bw.country} • ${bw.is_overseas ? 'Overseas' : 'Domestic'}</div>
              </div>
            </div>
          </td>
          <td><span class="badge badge-role">${bw.tactical_role}</span></td>
          <td>${this.getCategoryBadge(bw.candidate_category)}</td>
          <td>${this.getTierBadge(bw.evidence_tier, bw.evidence_tier_label)}</td>
          <td class="metric-pill font-mono">${bw.performance_rating.toFixed(2)}</td>
          <td class="metric-pill font-mono blue">${bw.evidence_reliability_score.toFixed(1)}</td>
          <td class="metric-pill font-mono" title="Top-Tier Impact Retention Index">${bw.statistical_stability_score.toFixed(1)}</td>
          <td class="metric-pill font-mono">${bw.tactical_squad_fit_score.toFixed(1)}</td>
          <td class="metric-pill font-mono" style="color: #f87171;">${bw.acquisition_risk_score.toFixed(1)}</td>
          <td class="metric-pill highlight font-mono">${bw.recruitment_decision_score.toFixed(2)}</td>
          <td style="text-align: right;">
            <button class="btn btn-sm ${inComp ? 'btn-primary' : ''}" onclick="App.toggleCompare(${bw.player_id}, 'Bowling')">
              ${inComp ? '✓ In Compare' : '+ Compare'}
            </button>
            <button class="btn btn-sm" onclick="App.openPlayerModal(${bw.player_id}, 'Bowling')">Details</button>
          </td>
        </tr>
      `;
    }).join("");

    this.renderPagination("bowlers-pagination", this.bowlerFilters.page, totalPages, newPage => {
      this.bowlerFilters.page = newPage;
      this.renderBowlerTable();
    });
  },

  // ---------------------------------------------------------------------------
  // PAGE 4: RR Squad Analysis
  // ---------------------------------------------------------------------------
  renderRRSquadAnalysis() {
    const baseline = DataManager.data.rrSquad || [];
    const gaps = DataManager.data.squadGaps || [];
    const scenario = this.selectedSquadScenario;

    const rosterTbody = document.getElementById("rr-roster-table-body");
    if (rosterTbody) {
      rosterTbody.innerHTML = baseline.map(p => `
        <tr>
          <td><strong style="color: #fff;">${p.player_name}</strong></td>
          <td><span class="badge badge-role">${p.country}</span> ${p.is_overseas ? '<span class="badge badge-rival">OS</span>' : '<span class="badge badge-tier-2">IND</span>'}</td>
          <td><span class="badge badge-role">${p.bat_role}</span></td>
          <td><span class="badge badge-role">${p.bowl_role}</span></td>
          <td>${p.roster_status}</td>
          <td class="metric-pill font-mono">${p.bat_rating ? p.bat_rating.toFixed(2) : '—'}</td>
          <td class="metric-pill font-mono">${p.bowl_rating ? p.bowl_rating.toFixed(2) : '—'}</td>
        </tr>
      `).join("");
    }

    const gapTbody = document.getElementById("rr-gap-table-body");
    if (gapTbody) {
      const filteredGaps = gaps.filter(g => g.scenario.includes(scenario));
      gapTbody.innerHTML = filteredGaps.map(g => {
        let severityClass = "gap-low";
        if (g.gap_severity === "Critical") severityClass = "gap-critical";
        else if (g.gap_severity === "High") severityClass = "gap-high";
        else if (g.gap_severity === "Moderate") severityClass = "gap-moderate";

        return `
          <tr>
            <td><strong style="color: #fff;">${g.tactical_role}</strong></td>
            <td><span class="badge ${g.discipline === 'Batting' ? 'badge-internal' : 'badge-tier-2'}">${g.discipline}</span></td>
            <td class="font-mono" style="text-align: center;">${g.squad_count_total}</td>
            <td class="font-mono" style="text-align: center;">${g.squad_count_domestic} / ${g.squad_count_overseas}</td>
            <td><span class="gap-tag ${severityClass}">${g.depth_status}</span></td>
            <td class="metric-pill font-mono" style="text-align: center;">${g.gap_criticality_weight.toFixed(1)}</td>
            <td><span class="gap-tag ${severityClass}">${g.gap_severity}</span></td>
          </tr>
        `;
      }).join("");
    }

    ChartManager.renderRoleDepthCoverage("chart-squad-depth", gaps, scenario);
    ChartManager.renderTacticalGaps("chart-squad-gaps", gaps, scenario);
  },

  // ---------------------------------------------------------------------------
  // PAGE 5: Recruitment Shortlists
  // ---------------------------------------------------------------------------
  renderRecruitmentShortlists() {
    const matrix = DataManager.data.recruitmentMatrix || [];
    const tbody = document.getElementById("recruitment-table-body");
    if (!tbody) return;

    let filtered = [...matrix];
    const tab = this.recruitmentFilters.tab;

    if (tab === "batting") {
      filtered = filtered.filter(p => p.discipline === "Batting");
    } else if (tab === "bowling") {
      filtered = filtered.filter(p => p.discipline === "Bowling");
    } else if (tab === "benchmarks") {
      filtered = filtered.filter(p => p.candidate_category.includes("Benchmark"));
    } else if (tab === "internal") {
      filtered = filtered.filter(p => p.candidate_category.includes("Internal") || p.candidate_category.includes("RR"));
    } else if (tab === "viable") {
      filtered = filtered.filter(p => p.candidate_category === "Viable Auction Target");
    }

    if (this.recruitmentFilters.actionableOnly) {
      filtered = filtered.filter(p => p.candidate_category === "Viable Auction Target");
    }

    tbody.innerHTML = filtered.map(p => `
      <tr>
        <td>
          <div class="player-cell">
            <div>
              <span class="player-cell-name" onclick="App.openPlayerModal(${p.player_id}, '${p.discipline}')">${p.player_name}</span>
              <div class="player-cell-sub">${p.country} • ${p.is_overseas ? 'Overseas' : 'Domestic'}</div>
            </div>
          </div>
        </td>
        <td><span class="badge ${p.discipline === 'Batting' ? 'badge-internal' : 'badge-tier-2'}">${p.discipline}</span></td>
        <td><span class="badge badge-role">${p.tactical_role}</span></td>
        <td>${this.getCategoryBadge(p.candidate_category)}</td>
        <td><span class="badge ${p.recommendation_priority.includes('High') ? 'badge-priority-high' : (p.recommendation_priority.includes('Medium') ? 'badge-priority-med' : 'badge-priority-low')}">${p.recommendation_priority}</span></td>
        <td class="metric-pill font-mono">${p.performance_rating.toFixed(2)}</td>
        <td class="metric-pill font-mono blue">${p.evidence_reliability_score.toFixed(1)}</td>
        <td class="metric-pill font-mono" title="Top-Tier Impact Retention Index">${p.statistical_stability_score.toFixed(1)}</td>
        <td class="metric-pill font-mono">${p.tactical_squad_fit_score.toFixed(1)}</td>
        <td class="metric-pill font-mono" style="color: #f87171;">${p.acquisition_risk_score.toFixed(1)}</td>
        <td class="metric-pill highlight font-mono">${p.recruitment_decision_score.toFixed(2)}</td>
        <td><small style="color: var(--text-muted);">${p.squad_gap_addressed}</small></td>
      </tr>
    `).join("");

    const topB = matrix.filter(c => c.discipline === "Batting");
    const topBw = matrix.filter(c => c.discipline === "Bowling");
    ChartManager.renderShortlistFit("chart-shortlist-batting", topB, "Batting Targets");
    ChartManager.renderShortlistFit("chart-shortlist-bowling", topBw, "Bowling Targets");
    ChartManager.renderRiskVsFit("chart-risk-vs-fit", matrix);
  },

  // ---------------------------------------------------------------------------
  // PAGE 6: Auction Strategy
  // ---------------------------------------------------------------------------
  renderAuctionStrategy() {
    const scenarios = DataManager.data.auctionScenarios || [];
    if (scenarios.length === 0) return;

    const scen = scenarios[this.selectedAuctionScenarioIndex] || scenarios[0];

    const titleEl = document.getElementById("auction-scenario-title");
    if (titleEl) titleEl.textContent = scen.scenario_name;

    const focusEl = document.getElementById("auction-scenario-focus");
    if (focusEl) focusEl.textContent = scen.strategic_focus;

    const osEl = document.getElementById("auction-overseas-demand");
    if (osEl) osEl.textContent = `${scen.overseas_slots_demanded} Overseas Slots`;

    const advEl = document.getElementById("auction-scenario-advantages");
    if (advEl) advEl.textContent = scen.main_advantages;

    const riskEl = document.getElementById("auction-scenario-risks");
    if (riskEl) riskEl.textContent = scen.main_risks;

    const balanceEl = document.getElementById("auction-scenario-balance");
    if (balanceEl) balanceEl.textContent = scen.squad_balance_impact;

    const barEl = document.getElementById("auction-budget-bar");
    if (barEl) {
      const colors = ["#ff2a85", "#1e88e5", "#10b981", "#f59e0b"];
      barEl.innerHTML = scen.budget_allocations.map((a, i) => `
        <div class="budget-seg" style="width: ${a.pct_of_budget}%; background: ${colors[i % colors.length]};" title="${a.allocation_category}: ${a.budget_units} BAU (${a.pct_of_budget}%)">
          ${a.budget_units} BAU
        </div>
      `).join("");
    }

    const allocTbody = document.getElementById("auction-allocations-tbody");
    if (allocTbody) {
      allocTbody.innerHTML = scen.budget_allocations.map(a => `
        <tr>
          <td><strong style="color: #fff;">${a.allocation_category}</strong></td>
          <td class="font-mono" style="text-align: right;">${a.budget_units} BAU</td>
          <td class="font-mono text-pink" style="text-align: right;">${a.pct_of_budget.toFixed(1)}%</td>
        </tr>
      `).join("");
    }

    const targetsEl = document.getElementById("auction-candidate-targets-list");
    if (targetsEl && scen.key_candidate_targets) {
      const roles = Object.keys(scen.key_candidate_targets);
      targetsEl.innerHTML = roles.map(role => `
        <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 8px; padding: 12px; margin-bottom: 10px;">
          <div style="font-weight: 700; color: #60a5fa; margin-bottom: 6px;">${role.replace(/_/g, ' ')}:</div>
          <div style="display: flex; flex-wrap: wrap; gap: 6px;">
            ${scen.key_candidate_targets[role].map(name => `<span class="badge badge-viable">${name}</span>`).join("")}
          </div>
        </div>
      `).join("");
    }

    ChartManager.renderAuctionScenarios("chart-auction-allocations", scenarios);
  },

  // ---------------------------------------------------------------------------
  // PAGE 7: Methodology & Register
  // ---------------------------------------------------------------------------
  renderMethodology() {
    const meth = DataManager.data.methodology;
    if (!meth) return;

    const regTbody = document.getElementById("methodology-register-tbody");
    if (regTbody && meth.assumptions_register) {
      regTbody.innerHTML = meth.assumptions_register.map(item => `
        <tr>
          <td class="font-mono" style="font-weight: 700; color: #38bdf8;">${item.item_id}</td>
          <td><span class="badge badge-role">${item.category}</span></td>
          <td style="color: #fff;">${item.description}</td>
          <td><small style="color: var(--text-muted);">${item.source}</small></td>
          <td><span class="badge badge-tier-1">${item.status}</span></td>
          <td><small style="color: var(--text-secondary);">${item.impact_on_model}</small></td>
        </tr>
      `).join("");
    }
  },

  // ---------------------------------------------------------------------------
  // Modals & Side-by-Side Comparison
  // ---------------------------------------------------------------------------
  openPlayerModal(playerId, discipline = "Batting") {
    const p = DataManager.findPlayer(playerId, discipline);
    if (!p) return;

    const titleEl = document.getElementById("modal-player-title");
    if (titleEl) {
      titleEl.innerHTML = `${p.player_name} <span class="badge ${p.is_overseas ? 'badge-rival' : 'badge-tier-2'}">${p.country}</span> ${this.getCategoryBadge(p.candidate_category)}`;
    }

    const bodyEl = document.getElementById("modal-player-body");
    if (!bodyEl) return;

    const isBat = discipline === "Batting";

    bodyEl.innerHTML = `
      <div class="metrics-summary-banner">
        <div class="metric-box">
          <div class="label">Performance Rating</div>
          <div class="val text-pink">${p.performance_rating.toFixed(2)}</div>
          <div class="sub">Rank #${p.rank} (0-100)</div>
        </div>
        <div class="metric-box">
          <div class="label">Evidence Reliability</div>
          <div class="val text-blue">${p.evidence_reliability_score.toFixed(1)}</div>
          <div class="sub">${p.evidence_tier_label}</div>
        </div>
        <div class="metric-box">
          <div class="label">Statistical Stability (SSS)</div>
          <div class="val text-gold">${p.statistical_stability_score.toFixed(1)}</div>
          <div class="sub">Top-Tier Retention Index</div>
        </div>
        <div class="metric-box">
          <div class="label">Tactical Squad Fit</div>
          <div class="val text-emerald">${p.tactical_squad_fit_score.toFixed(1)}</div>
          <div class="sub">${p.tactical_role}</div>
        </div>
        <div class="metric-box">
          <div class="label">Acquisition Risk</div>
          <div class="val text-rose">${p.acquisition_risk_score.toFixed(1)}</div>
          <div class="sub">${p.is_overseas ? '+6.0 OS Penalty' : 'Domestic Base'}</div>
        </div>
        <div class="metric-box" style="border-color: var(--rr-pink);">
          <div class="label" style="color: var(--rr-pink);">Decision Score (RDH)</div>
          <div class="val text-pink">${p.recruitment_decision_score.toFixed(2)}</div>
          <div class="sub">Scale: 0.00 to 90.00</div>
        </div>
      </div>

      <div class="grid-2" style="margin-bottom: 20px;">
        <div class="dashboard-card" style="margin-bottom: 0;">
          <div class="card-header"><span class="card-title">Overall vs. Clutch Performance</span></div>
          <div class="card-body">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Condition</th>
                  <th>${isBat ? 'Balls Faced' : 'Legal Balls'}</th>
                  <th>${isBat ? 'Runs Scored' : 'Wickets Taken'}</th>
                  <th>${isBat ? 'Strike Rate' : 'Economy Rate'}</th>
                  <th>${isBat ? 'Dot %' : 'True Dot %'}</th>
                  <th>Boundary %</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Overall</strong></td>
                  <td class="font-mono">${isBat ? p.bf_overall : p.legal_balls_overall}</td>
                  <td class="font-mono">${isBat ? p.runs_overall : p.wickets_overall}</td>
                  <td class="font-mono">${isBat ? p.sr_overall.toFixed(1) : p.economy_overall.toFixed(2)}</td>
                  <td class="font-mono">—</td>
                  <td class="font-mono">—</td>
                </tr>
                <tr style="background: rgba(255, 42, 133, 0.06);">
                  <td><strong class="text-pink">Clutch (LI ≥ 1.0)</strong></td>
                  <td class="font-mono">${isBat ? p.bf_clutch : p.legal_balls_clutch}</td>
                  <td class="font-mono">${isBat ? p.runs_clutch : p.wickets_clutch}</td>
                  <td class="font-mono text-pink">${isBat ? p.sr_clutch.toFixed(1) : p.economy_clutch.toFixed(2)}</td>
                  <td class="font-mono">${isBat ? p.dot_pct_clutch.toFixed(1) : p.true_dot_pct_clutch.toFixed(1)}%</td>
                  <td class="font-mono">${p.bnd_pct_clutch.toFixed(1)}%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="dashboard-card" style="margin-bottom: 0;">
          <div class="card-header"><span class="card-title">Module 6 Robustness & Stability</span></div>
          <div class="card-body" style="font-size: 13px;">
            <p><strong>Bootstrap 95% CI:</strong> [${p.rating_p025.toFixed(1)}, ${p.rating_p975.toFixed(1)}] (Width: ${p.rating_ci_width.toFixed(1)} pts)</p>
            <p style="margin-top: 6px;"><strong>Bootstrap Mean Rank:</strong> #${p.bootstrap_mean_rank.toFixed(1)} (± ${p.rank_std.toFixed(1)})</p>
            <p style="margin-top: 6px;"><strong>Top-20 Frequency:</strong> ${p.top20_freq_pct.toFixed(1)}% across 1,000 resamples</p>
            <p style="margin-top: 6px;"><strong>Clutch Volume HHI:</strong> ${p.clutch_volume_hhi.toFixed(4)} (Concentration index)</p>
            <p style="margin-top: 6px;"><strong>Leave-One-Match-Out Shift:</strong> ${p.lomo_rating_shift.toFixed(2)} pts rating change</p>
            <p style="margin-top: 6px;"><strong>Resilience Category:</strong> <span class="badge ${p.resilience_category.includes('Resilient') ? 'badge-viable' : 'badge-rival'}">${p.resilience_category}</span></p>
          </div>
        </div>
      </div>

      <div style="background: var(--bg-surface); padding: 16px; border-radius: 8px; border: 1px solid var(--border-color);">
        <strong style="color: #60a5fa;">Recruitment Governance & Availability:</strong>
        <p style="margin-top: 4px; color: var(--text-secondary); font-size: 12.5px;">${p.availability_status}</p>
        <p style="margin-top: 6px; font-size: 11.5px; color: var(--text-muted);">
          * Note: Auction registration for IPL 2027 is unconfirmed. Recommendations are model-derived priority targets based on historical high-pressure performance.
        </p>
      </div>
    `;

    document.getElementById("modal-player-detail").classList.add("active");
  },

  toggleCompare(playerId, discipline = "Batting") {
    const p = DataManager.findPlayer(playerId, discipline);
    if (!p) return;

    p.discipline = discipline;
    const exists = DataManager.comparisonList.some(item => item.player_id === playerId && item.discipline === discipline);

    if (exists) {
      DataManager.removeFromComparison(playerId);
    } else {
      const res = DataManager.addToComparison(p);
      if (!res.success) {
        alert(res.message);
        return;
      }
    }

    this.updateCompareTray();
    if (discipline === "Batting") this.renderBatterTable();
    else this.renderBowlerTable();
  },

  updateCompareTray() {
    const btn = document.getElementById("compare-tray-trigger");
    const countSpan = document.getElementById("compare-tray-count");
    if (!btn || !countSpan) return;

    const count = DataManager.comparisonList.length;
    countSpan.textContent = count;
    btn.style.display = count > 0 ? "inline-flex" : "none";
  },

  openComparisonModal() {
    const players = DataManager.comparisonList;
    if (players.length === 0) return;

    const container = document.getElementById("modal-compare-grid");
    if (!container) return;

    const rows = [
      { label: "Player Name", render: p => `<strong>${p.player_name}</strong>` },
      { label: "Discipline & Role", render: p => `<span class="badge badge-role">${p.discipline}</span> • ${p.tactical_role}` },
      { label: "Country & Origin", render: p => `${p.country} (${p.is_overseas ? 'Overseas' : 'Domestic'})` },
      { label: "Governance Category", render: p => this.getCategoryBadge(p.candidate_category) },
      { label: "Performance Rating (PR)", render: p => `<span class="metric-pill text-pink">${p.performance_rating.toFixed(2)}</span>` },
      { label: "Evidence Reliability (ERS)", render: p => `<span class="metric-pill text-blue">${p.evidence_reliability_score.toFixed(1)}</span> (${p.evidence_tier_label})` },
      { label: "Stability (SSS - Impact Retention)", render: p => `<span class="metric-pill text-gold">${p.statistical_stability_score.toFixed(1)}</span>` },
      { label: "Tactical Squad Fit (TFS)", render: p => `<span class="metric-pill text-emerald">${p.tactical_squad_fit_score.toFixed(1)}</span>` },
      { label: "Acquisition Risk (ARS)", render: p => `<span class="metric-pill text-rose">${p.acquisition_risk_score.toFixed(1)}</span>` },
      { label: "Decision Score (RDH)", render: p => `<span class="metric-pill highlight">${p.recruitment_decision_score.toFixed(2)} / 90.0</span>` },
      { label: "Bootstrap 95% CI", render: p => `[${p.rating_p025.toFixed(1)}, ${p.rating_p975.toFixed(1)}]` },
      { label: "Clutch Volume HHI", render: p => `${p.clutch_volume_hhi.toFixed(4)}` },
      { label: "Recommendation Priority", render: p => `<span class="badge badge-viable">${p.recommendation_priority}</span>` },
      { label: "Action", render: p => `<button class="btn btn-sm btn-reset" onclick="App.removeAndRefreshCompare(${p.player_id})">Remove</button>` }
    ];

    container.innerHTML = `
      <table class="data-table" style="width: 100%;">
        <thead>
          <tr>
            <th style="width: 220px;">Attribute</th>
            ${players.map(p => `<th>${p.player_name}</th>`).join("")}
          </tr>
        </thead>
        <tbody>
          ${rows.map(r => `
            <tr>
              <td><strong>${r.label}</strong></td>
              ${players.map(p => `<td>${r.render(p)}</td>`).join("")}
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;

    document.getElementById("modal-compare-players").classList.add("active");
  },

  removeAndRefreshCompare(playerId) {
    DataManager.removeFromComparison(playerId);
    this.updateCompareTray();
    if (DataManager.comparisonList.length === 0) {
      document.getElementById("modal-compare-players").classList.remove("active");
    } else {
      this.openComparisonModal();
    }
    this.renderBatterTable();
    this.renderBowlerTable();
  },

  renderPagination(containerId, currentPage, totalPages, onPageChange) {
    const el = document.getElementById(containerId);
    if (!el) return;

    if (totalPages <= 1) {
      el.innerHTML = "";
      return;
    }

    let buttons = `
      <button class="btn btn-sm" ${currentPage === 1 ? 'disabled style="opacity:0.4;"' : ''} onclick="App.paginate('${containerId}', ${currentPage - 1})">Prev</button>
      <span style="font-size: 12px; color: var(--text-muted); align-self: center; margin: 0 4px;">Page ${currentPage} of ${totalPages}</span>
      <button class="btn btn-sm" ${currentPage === totalPages ? 'disabled style="opacity:0.4;"' : ''} onclick="App.paginate('${containerId}', ${currentPage + 1})">Next</button>
    `;

    el.innerHTML = buttons;
    el._onPageChange = onPageChange;
  },

  paginate(containerId, newPage) {
    const el = document.getElementById(containerId);
    if (el && el._onPageChange) {
      el._onPageChange(newPage);
    }
  }
};

document.addEventListener("DOMContentLoaded", () => {
  App.init();
});
