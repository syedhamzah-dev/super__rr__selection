/**
 * SupeRR Selector - Data Manager
 * Handles asynchronous data loading, filtering, sorting, and comparison state.
 * Supports both HTTP fetch() and offline window.DASHBOARD_DATA fallback.
 */

const DataManager = {
  data: {
    overview: null,
    batters: [],
    bowlers: [],
    rrSquad: [],
    squadGaps: [],
    recruitmentMatrix: [],
    auctionScenarios: [],
    methodology: null
  },
  
  comparisonList: [], // Array of player objects (up to 3)

  /**
   * Determine data directory path
   */
  getBasePath() {
    return "./data/";
  },

  /**
   * Load all datasets asynchronously with offline fallback
   */
  async loadAllData() {
    // 1. Check if offline pre-bundled data exists (e.g. running via file://)
    if (typeof window !== "undefined" && window.DASHBOARD_DATA) {
      console.log("Loading datasets from bundled memory feed (Offline/file:// mode)...");
      this.data.overview = window.DASHBOARD_DATA.overview;
      this.data.batters = window.DASHBOARD_DATA.batters;
      this.data.bowlers = window.DASHBOARD_DATA.bowlers;
      this.data.rrSquad = window.DASHBOARD_DATA.rrSquad;
      this.data.squadGaps = window.DASHBOARD_DATA.squadGaps;
      this.data.recruitmentMatrix = window.DASHBOARD_DATA.recruitmentMatrix;
      this.data.auctionScenarios = window.DASHBOARD_DATA.auctionScenarios;
      this.data.methodology = window.DASHBOARD_DATA.methodology;
      return this.data;
    }

    // 2. Otherwise load via fetch (Web server mode / Netlify / GitHub Pages)
    const basePath = this.getBasePath();
    const files = [
      { key: "overview", path: `${basePath}overview_stats.json` },
      { key: "batters", path: `${basePath}batters_data.json` },
      { key: "bowlers", path: `${basePath}bowlers_data.json` },
      { key: "rrSquad", path: `${basePath}rr_squad_data.json` },
      { key: "squadGaps", path: `${basePath}squad_gaps_data.json` },
      { key: "recruitmentMatrix", path: `${basePath}recruitment_matrix.json` },
      { key: "auctionScenarios", path: `${basePath}auction_scenarios.json` },
      { key: "methodology", path: `${basePath}methodology_data.json` }
    ];

    const results = await Promise.allSettled(
      files.map(f => fetch(f.path).then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status} on ${f.path}`);
        return res.json();
      }))
    );

    files.forEach((file, idx) => {
      if (results[idx].status === "fulfilled") {
        this.data[file.key] = results[idx].value;
      } else {
        console.warn(`Failed loading ${file.path}:`, results[idx].reason);
      }
    });

    return this.data;
  },

  /**
   * Filter and sort batter dataset
   */
  filterBatters(filters = {}) {
    let list = [...(this.data.batters || [])];

    // Search query
    if (filters.search && filters.search.trim() !== "") {
      const q = filters.search.toLowerCase().trim();
      list = list.filter(b => b.player_name.toLowerCase().includes(q) || b.country.toLowerCase().includes(q));
    }

    // Tactical Role
    if (filters.role && filters.role !== "ALL") {
      list = list.filter(b => b.tactical_role === filters.role);
    }

    // Country
    if (filters.country && filters.country !== "ALL") {
      list = list.filter(b => b.country === filters.country);
    }

    // Authoritative Evidence Tier (Strong / Moderate)
    if (filters.tier && filters.tier !== "ALL") {
      list = list.filter(b => b.evidence_tier === filters.tier);
    }

    // Governance Category
    if (filters.category && filters.category !== "ALL") {
      list = list.filter(b => b.candidate_category === filters.category);
    }

    // Actionable Only Toggle (Independent of Tier)
    if (filters.actionableOnly) {
      list = list.filter(b => b.candidate_category === "Viable Auction Target");
    }

    // Sorting
    const sortKey = filters.sortKey || "recruitment_decision_score";
    const sortDir = filters.sortDir || "desc";

    list.sort((a, b) => {
      let valA = a[sortKey];
      let valB = b[sortKey];
      if (valA === null || valA === undefined) valA = -999999;
      if (valB === null || valB === undefined) valB = -999999;

      if (typeof valA === "string") {
        return sortDir === "asc" ? valA.localeCompare(valB) : valB.localeCompare(valA);
      }
      return sortDir === "asc" ? valA - valB : valB - valA;
    });

    return list;
  },

  /**
   * Filter and sort bowler dataset
   */
  filterBowlers(filters = {}) {
    let list = [...(this.data.bowlers || [])];

    // Search query
    if (filters.search && filters.search.trim() !== "") {
      const q = filters.search.toLowerCase().trim();
      list = list.filter(b => b.player_name.toLowerCase().includes(q) || b.country.toLowerCase().includes(q));
    }

    // Tactical Role
    if (filters.role && filters.role !== "ALL") {
      list = list.filter(b => b.tactical_role === filters.role || b.primary_bowling_role === filters.role);
    }

    // Country
    if (filters.country && filters.country !== "ALL") {
      list = list.filter(b => b.country === filters.country);
    }

    // Authoritative Evidence Tier (Strong / Moderate)
    if (filters.tier && filters.tier !== "ALL") {
      list = list.filter(b => b.evidence_tier === filters.tier);
    }

    // Governance Category
    if (filters.category && filters.category !== "ALL") {
      list = list.filter(b => b.candidate_category === filters.category);
    }

    // Actionable Only Toggle (Independent of Tier)
    if (filters.actionableOnly) {
      list = list.filter(b => b.candidate_category === "Viable Auction Target");
    }

    // Sorting
    const sortKey = filters.sortKey || "recruitment_decision_score";
    const sortDir = filters.sortDir || "desc";

    list.sort((a, b) => {
      let valA = a[sortKey];
      let valB = b[sortKey];
      if (valA === null || valA === undefined) valA = -999999;
      if (valB === null || valB === undefined) valB = -999999;

      if (typeof valA === "string") {
        return sortDir === "asc" ? valA.localeCompare(valB) : valB.localeCompare(valA);
      }
      return sortDir === "asc" ? valA - valB : valB - valA;
    });

    return list;
  },

  /**
   * Filter recruitment recommendation matrix (50 candidates)
   */
  filterRecruitmentMatrix(categoryFilter = "ALL", disciplineFilter = "ALL", actionableOnly = false) {
    let list = [...(this.data.recruitmentMatrix || [])];

    if (actionableOnly) {
      list = list.filter(p => p.candidate_category === "Viable Auction Target");
    } else if (categoryFilter !== "ALL") {
      list = list.filter(p => p.candidate_category === categoryFilter);
    }

    if (disciplineFilter !== "ALL") {
      list = list.filter(p => p.discipline === disciplineFilter);
    }

    return list;
  },

  /**
   * Add player to side-by-side comparison (max 3)
   */
  addToComparison(player) {
    if (this.comparisonList.length >= 3) {
      return { success: false, message: "Maximum 3 players can be compared simultaneously." };
    }
    if (this.comparisonList.some(p => p.player_id === player.player_id && p.discipline === player.discipline)) {
      return { success: false, message: "Player already in comparison tray." };
    }
    this.comparisonList.push(player);
    return { success: true, count: this.comparisonList.length };
  },

  /**
   * Remove player from comparison
   */
  removeFromComparison(playerId) {
    this.comparisonList = this.comparisonList.filter(p => p.player_id !== playerId);
    return this.comparisonList.length;
  },

  /**
   * Clear comparison
   */
  clearComparison() {
    this.comparisonList = [];
  },

  /**
   * Find player by ID across datasets
   */
  findPlayer(playerId, discipline = "Batting") {
    if (discipline === "Batting") {
      return this.data.batters.find(b => b.player_id === playerId);
    } else {
      return this.data.bowlers.find(b => b.player_id === playerId);
    }
  },

  /**
   * Get Authoritative Top 10 Actionable Batting Picks with optional sub-filters
   */
  getTop10Batters(filter = "all") {
    let top10 = [];
    if (this.data.overview && this.data.overview.top_10_actionable_batters) {
      top10 = [...this.data.overview.top_10_actionable_batters];
    } else {
      top10 = this.filterBatters({ actionableOnly: true, sortKey: "recruitment_decision_score", sortDir: "desc" }).slice(0, 10);
    }

    if (!filter || filter === "all") return top10;
    if (filter === "domestic") return top10.filter(p => !p.is_overseas);
    if (filter === "overseas") return top10.filter(p => p.is_overseas);
    return top10.filter(p => p.tactical_role === filter);
  },

  /**
   * Get Authoritative Top 10 Actionable Bowling Picks with optional sub-filters
   */
  getTop10Bowlers(filter = "all") {
    let top10 = [];
    if (this.data.overview && this.data.overview.top_10_actionable_bowlers) {
      top10 = [...this.data.overview.top_10_actionable_bowlers];
    } else {
      top10 = this.filterBowlers({ actionableOnly: true, sortKey: "recruitment_decision_score", sortDir: "desc" }).slice(0, 10);
    }

    if (!filter || filter === "all") return top10;
    if (filter === "domestic") return top10.filter(p => !p.is_overseas);
    if (filter === "overseas") return top10.filter(p => p.is_overseas);
    return top10.filter(p => p.tactical_role === filter);
  },

  /**
   * Get Module 5 Top 10 Historical Batting Performers (Ranked by PR)
   */
  getHistoricalBatters(filter = "all") {
    let top10 = [];
    if (this.data.overview && this.data.overview.top_10_historical_batters) {
      top10 = [...this.data.overview.top_10_historical_batters];
    } else {
      top10 = [...(this.data.batters || [])].sort((a, b) => b.performance_rating - a.performance_rating).slice(0, 10);
    }

    if (!filter || filter === "all") return top10;
    if (filter === "domestic") return top10.filter(p => !p.is_overseas);
    if (filter === "overseas") return top10.filter(p => p.is_overseas);
    return top10.filter(p => p.tactical_role === filter);
  },

  /**
   * Get Module 5 Top 10 Historical Bowling Performers (Ranked by PR)
   */
  getHistoricalBowlers(filter = "all") {
    let top10 = [];
    if (this.data.overview && this.data.overview.top_10_historical_bowlers) {
      top10 = [...this.data.overview.top_10_historical_bowlers];
    } else {
      top10 = [...(this.data.bowlers || [])].sort((a, b) => b.performance_rating - a.performance_rating).slice(0, 10);
    }

    if (!filter || filter === "all") return top10;
    if (filter === "domestic") return top10.filter(p => !p.is_overseas);
    if (filter === "overseas") return top10.filter(p => p.is_overseas);
    return top10.filter(p => p.tactical_role === filter);
  },

  /**
   * Get Strategic Comparative Benchmarks
   */
  getStrategicBenchmarks(discipline = "ALL") {
    let list = [];
    if (this.data.overview && this.data.overview.strategic_benchmarks) {
      list = [...this.data.overview.strategic_benchmarks];
    } else {
      list = (this.data.recruitmentMatrix || []).filter(p => p.candidate_category.includes("Benchmark"));
    }

    if (discipline !== "ALL") {
      list = list.filter(p => p.discipline === discipline);
    }
    return list;
  }
};
