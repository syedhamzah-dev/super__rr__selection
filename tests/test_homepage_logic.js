/**
 * Test homepage rendering and data filtering in Node.js
 */
const fs = require('fs');
const path = require('path');

// 1. Create Mock DOM
class MockElement {
  constructor(tagName = 'div', id = '') {
    this.tagName = tagName;
    this.id = id;
    this.children = [];
    this.classList = {
      classes: new Set(),
      add: (c) => this.classList.classes.add(c),
      remove: (c) => this.classList.classes.delete(c),
      toggle: (c, force) => {
        if (force === undefined) {
          if (this.classList.classes.has(c)) {
            this.classList.classes.delete(c);
            return false;
          } else {
            this.classList.classes.add(c);
            return true;
          }
        } else if (force) {
          this.classList.classes.add(c);
          return true;
        } else {
          this.classList.classes.delete(c);
          return false;
        }
      },
      contains: (c) => this.classList.classes.has(c)
    };
    this.style = {};
    this.attributes = {};
    this.listeners = {};
    this._innerHTML = '';
    this._textContent = '';
  }

  get innerHTML() { return this._innerHTML; }
  set innerHTML(val) {
    this._innerHTML = val;
    this._textContent = val.replace(/<[^>]+>/g, '');
  }

  get textContent() { return this._textContent; }
  set textContent(val) {
    this._textContent = val;
    this._innerHTML = val;
  }

  setAttribute(k, v) { this.attributes[k] = v; }
  getAttribute(k) { return this.attributes[k]; }
  addEventListener(event, fn) {
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event].push(fn);
  }
  dispatchEvent(event) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(fn => fn({ target: this }));
    }
  }
  querySelector(sel) { return new MockElement(); }
  querySelectorAll(sel) { return []; }
  closest(sel) { return null; }
  getBoundingClientRect() { return { left: 100, top: 100, bottom: 120, right: 200, width: 100, height: 20 }; }
}

const elementsById = {};
const getOrCreateElement = (id) => {
  if (!elementsById[id]) {
    elementsById[id] = new MockElement('div', id);
  }
  return elementsById[id];
};

global.window = {
  location: { hash: '#overview', search: '' },
  scrollTo: () => {},
  addEventListener: () => {},
  scrollX: 0,
  scrollY: 0,
  innerWidth: 1440,
  innerHeight: 900
};

global.document = {
  getElementById: (id) => getOrCreateElement(id),
  querySelector: (sel) => new MockElement(),
  querySelectorAll: (sel) => [],
  addEventListener: () => {},
  documentElement: { scrollWidth: 1440 }
};

// Mock Chart.js
global.Chart = class {
  constructor(ctx, config) {
    this.ctx = ctx;
    this.config = config;
  }
  destroy() {}
};
global.Chart.defaults = {
  plugins: { tooltip: {} },
  font: {}
};

const vm = require('vm');

// 2. Load Dashboard Scripts in Global Context
const dataBundleCode = fs.readFileSync('dashboard/js/data_bundle.js', 'utf8');
vm.runInThisContext(dataBundleCode.replace(/const\s+OFFLINE_DATA_BUNDLE/g, 'global.OFFLINE_DATA_BUNDLE'));

const dataJsCode = fs.readFileSync('dashboard/js/data.js', 'utf8');
vm.runInThisContext(dataJsCode.replace(/const\s+DataManager/g, 'global.DataManager'));

const chartsJsCode = fs.readFileSync('dashboard/js/charts.js', 'utf8');
vm.runInThisContext(chartsJsCode.replace(/const\s+ChartManager/g, 'global.ChartManager'));

const appJsCode = fs.readFileSync('dashboard/js/app.js', 'utf8');
vm.runInThisContext(appJsCode.replace(/const\s+METRIC_GLOSSARY/g, 'global.METRIC_GLOSSARY').replace(/const\s+App/g, 'global.App'));

async function runTests() {
  console.log('--- 1. Testing DataManager Loading ---');
  await DataManager.loadAllData();
  console.log('DataManager loaded successfully:');
  console.log('  Batters count:', DataManager.data.batters.length);
  console.log('  Bowlers count:', DataManager.data.bowlers.length);
  console.log('  Recruitment targets:', DataManager.data.recruitmentMatrix.length);
  console.log('  Overview stats present:', !!DataManager.data.overview);

  if (DataManager.data.batters.length !== 304) throw new Error('Expected 304 batters');
  if (DataManager.data.bowlers.length !== 290) throw new Error('Expected 290 bowlers');
  if (DataManager.data.recruitmentMatrix.length !== 50) throw new Error('Expected 50 targets');

  console.log('--- 2. Testing App.renderOverview ---');
  App.renderOverview();

  // Verify KPI values
  const kpiDeliveries = elementsById['kpi-deliveries'].textContent;
  const kpiMatches = elementsById['kpi-matches'].textContent;
  const kpiMatchesData = elementsById['kpi-matches-deliveries'].textContent;
  const kpiBatters = elementsById['kpi-batters'].textContent;
  const kpiBowlers = elementsById['kpi-bowlers'].textContent;

  console.log('  KPI Deliveries:', kpiDeliveries);
  console.log('  KPI Matches:', kpiMatches);
  console.log('  KPI Matches with Data:', kpiMatchesData);
  console.log('  KPI Eligible Batters:', kpiBatters);
  console.log('  KPI Eligible Bowlers:', kpiBowlers);

  if (kpiDeliveries !== '200,999') throw new Error('Deliveries KPI mismatch');
  if (kpiMatches !== '883') throw new Error('Matches KPI mismatch');
  if (kpiMatchesData !== '867') throw new Error('Matches with data KPI mismatch');
  if (kpiBatters !== '304') throw new Error('Batters KPI mismatch');
  if (kpiBowlers !== '290') throw new Error('Bowlers KPI mismatch');

  // Verify Leaderboard population
  const battersHtml = elementsById['overview-top-batters-body'].innerHTML;
  const bowlersHtml = elementsById['overview-top-bowlers-body'].innerHTML;

  if (!battersHtml.includes('Yashasvi Jaiswal')) throw new Error('Expected Yashasvi Jaiswal in Top Batters');
  if (!battersHtml.includes('Tim David')) throw new Error('Expected Tim David in Top Batters');
  if (!bowlersHtml.includes('Chris Woakes')) throw new Error('Expected Chris Woakes in Top Bowlers');
  if (!bowlersHtml.includes('Benjamin Sears')) throw new Error('Expected Benjamin Sears in Top Bowlers');
  console.log('  Authoritative Top 10 Leaderboards populated successfully!');

  console.log('--- 3. Testing Analytical Slicers / Filters ---');
  // Filter by Role = 'Finisher'
  App.overviewFilters.role = 'Finisher';
  App.updateOverviewFilteredViews();
  const finisherBatters = elementsById['overview-top-batters-body'].innerHTML;
  console.log('  Finisher filter applied: Batters table updated.');
  if (!finisherBatters.includes('Tim David')) throw new Error('Expected Tim David in Finisher list');

  // Filter by Tier = 'Strong'
  App.overviewFilters.tier = 'Strong';
  App.updateOverviewFilteredViews();
  console.log('  Strong tier filter applied successfully.');

  // Reset Filters
  App.resetOverviewFilters();
  if (App.overviewFilters.role !== 'all' || App.overviewFilters.tier !== 'all') {
    throw new Error('Reset filters did not restore default all');
  }
  console.log('  Reset filters restored default all state.');

  console.log('--- 4. Testing Metric Tooltip Accessibility ---');
  ['PR', 'ERS', 'SSS', 'TFS', 'ARS', 'RDH', 'DELIVERIES', 'MATCHES_SCOPE'].forEach(key => {
    const entry = METRIC_GLOSSARY[key];
    if (!entry || !entry.what || !entry.interpretation || !entry.limitation) {
      throw new Error(`Glossary entry for ${key} is incomplete!`);
    }
  });
  console.log('  All Metric Glossary entries have full definitions, interpretation, and limitations!');

  console.log('\n=== ALL HOMEPAGE RUNTIME INTEGRITY CHECKS PASSED WITH 0 ERRORS! ===');
}

runTests().catch(err => {
  console.error('FATAL TEST ERROR:', err);
  process.exit(1);
});
