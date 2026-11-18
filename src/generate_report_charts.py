"""
src/generate_report_charts.py
Generates 8 high-resolution publication-grade charts for the SupeRR Selector Competition Report.
Theme: Professional sports analytics consultancy (Clean editorial layout, navy/royal blue/RR pink palette).
Outputs saved directly to reports/figures/
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

# Create output dir
os.makedirs('reports/figures', exist_ok=True)

# Styling Constants
NAVY = '#0E1726'
ROYAL_BLUE = '#1D4ED8'
RR_PINK = '#FF2A85'
CYAN = '#0284C7'
GOLD = '#D97706'
EMERALD = '#059669'
SLATE = '#64748B'
LIGHT_BG = '#F8FAFC'
BORDER_COLOR = '#E2E8F0'

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 13,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'figure.titlesize': 14,
    'figure.dpi': 200,
    'savefig.dpi': 250,
    'axes.edgecolor': '#CBD5E1',
    'axes.linewidth': 0.8,
    'grid.color': '#F1F5F9',
    'grid.linestyle': '--',
    'grid.alpha': 0.8
})

def fig1_dataset_scope():
    """Figure 1: Dataset Scope & Tournament Coverage (883 matches, 200,999 deliveries)"""
    matches = pd.read_csv('Data Pack/matches.csv')
    comps = pd.read_csv('Data Pack/competitions.csv')
    m_c = matches.merge(comps, on='comp_id', how='left')

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2))
    fig.patch.set_facecolor('#FFFFFF')

    # Subplot 1: IPL vs T20I Breakdown
    m_c['is_ipl'] = m_c['comp_name'].str.contains('IPL', na=False)
    ipl_count = m_c['is_ipl'].sum()
    intl_count = len(m_c) - ipl_count

    colors = [ROYAL_BLUE, CYAN]
    wedges, texts, autotexts = ax1.pie(
        [ipl_count, intl_count],
        labels=['IPL (2022–2026)', 'International T20Is & Bilaterals'],
        autopct='%1.1f%%',
        colors=colors,
        startangle=140,
        pctdistance=0.75,
        wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2)
    )
    for at in autotexts:
        at.set_color('white')
        at.set_weight('bold')
    ax1.set_title(f'Match Coverage by Competition\n(Total: {len(m_c):,} Matches)', weight='bold', pad=15)
    ax1.text(0, 0, f'{len(m_c)}\nMatches', ha='center', va='center', fontsize=13, weight='bold', color=NAVY)

    # Subplot 2: Matches per Season (2022–2026)
    m_c['season'] = pd.to_numeric(m_c['season'], errors='coerce')
    season_counts = m_c['season'].value_counts().sort_index()

    bars = ax2.bar(
        [str(int(s)) for s in season_counts.index],
        season_counts.values,
        color=ROYAL_BLUE,
        width=0.55,
        edgecolor=NAVY,
        linewidth=0.5
    )
    for bar in bars:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., h + 3, f'{int(h)}', ha='center', va='bottom', fontsize=9, weight='bold')

    ax2.set_title('Matches Analyzed by Calendar Season (2022–2026)', weight='bold', pad=15)
    ax2.set_xlabel('Season')
    ax2.set_ylabel('Number of Matches')
    ax2.set_ylim(0, max(season_counts.values) * 1.15)
    ax2.grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig('reports/figures/fig1_dataset_scope.png', bbox_inches='tight')
    plt.close()
    print("Generated fig1_dataset_scope.png")

def fig2_leverage_distribution():
    """Figure 2: Pressure Index Distribution across 200,999 deliveries"""
    pbp = pd.read_parquet('data/processed/ball_by_ball_pressure.parquet')

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2))
    fig.patch.set_facecolor('#FFFFFF')

    # Subplot 1: Distribution of Pressure Index
    counts, bins, patches = ax1.hist(pbp['pressure_index'], bins=30, color=CYAN, edgecolor=NAVY, alpha=0.85, linewidth=0.5)
    ax1.axvline(6.0, color=RR_PINK, linestyle='--', linewidth=1.8, label=r'Clutch Threshold ($\geq$ 6.0)')
    ax1.axvline(pbp['pressure_index'].mean(), color=GOLD, linestyle='-', linewidth=1.5, label=f'Mean = {pbp["pressure_index"].mean():.2f}')

    ax1.set_title('Pressure Index Distribution (200,999 Deliveries)', weight='bold', pad=15)
    ax1.set_xlabel('Pressure Index (0.0 to 10.0 scale)')
    ax1.set_ylabel('Number of Deliveries')
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{int(x):,}'))
    ax1.legend(frameon=True, facecolor=LIGHT_BG)
    ax1.grid(True, linestyle='--', alpha=0.5)

    # Subplot 2: Delivery Breakdown by Pressure Category
    cats = pbp['pressure_category'].value_counts()[['Low', 'Medium', 'High', 'Extreme']]
    cat_colors = ['#94A3B8', CYAN, '#F97316', RR_PINK]
    bars = ax2.bar(cats.index, cats.values, color=cat_colors, edgecolor=NAVY, width=0.55, linewidth=0.5)

    total = len(pbp)
    for bar in bars:
        h = bar.get_height()
        pct = (h / total) * 100
        ax2.text(bar.get_x() + bar.get_width()/2., h + 1500, f'{int(h):,}\n({pct:.1f}%)', ha='center', va='bottom', fontsize=9, weight='bold')

    ax2.set_title('Deliveries by Pressure Category', weight='bold', pad=15)
    ax2.set_xlabel('Pressure Category')
    ax2.set_ylabel('Deliveries')
    ax2.set_ylim(0, max(cats.values) * 1.18)
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{int(x):,}'))
    ax2.grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig('reports/figures/fig2_leverage_distribution.png', bbox_inches='tight')
    plt.close()
    print("Generated fig2_leverage_distribution.png")

def fig3_batting_credibility():
    """Figure 3: Batting Performance Rating vs. Evidence Reliability Score"""
    b_rat = pd.read_parquet('data/processed/batter_player_ratings.parquet')
    eligible = b_rat[b_rat['is_eligible_for_ranking'] == 1].copy()

    fig, ax = plt.subplots(figsize=(10, 6.2))
    fig.patch.set_facecolor('#FFFFFF')

    # Scatter by Evidence Tier
    strong = eligible[eligible['evidence_tier'] == 'Strong Evidence']
    mod = eligible[eligible['evidence_tier'] == 'Moderate Evidence']

    ax.scatter(mod['evidence_reliability_score'], mod['performance_rating'],
               color=CYAN, alpha=0.6, s=45, label=f'Moderate Evidence (n={len(mod)})', edgecolors='none')
    ax.scatter(strong['evidence_reliability_score'], strong['performance_rating'],
               color=ROYAL_BLUE, alpha=0.85, s=65, label=f'Strong Evidence (n={len(strong)})', edgecolors=NAVY, linewidth=0.4)

    # Key callouts
    callouts = ['Yashasvi Jaiswal', 'Finn Allen', 'Tim David', 'Naman Dhir', 'Matthew Wade', 'Sanju Samson', 'Rinku Singh']
    for name in callouts:
        row = eligible[eligible['striker_name'] == name]
        if not row.empty:
            x = row['evidence_reliability_score'].values[0]
            y = row['performance_rating'].values[0]
            ax.scatter(x, y, color=RR_PINK, s=90, zorder=5, edgecolors=NAVY, linewidth=1)
            ax.annotate(name, (x, y), xytext=(6, 4), textcoords='offset points', fontsize=9, weight='bold', color=NAVY)

    ax.axhline(50, color=SLATE, linestyle=':', alpha=0.7)
    ax.axvline(50, color=SLATE, linestyle=':', alpha=0.7)
    ax.set_title('Batting Performance Rating vs. Evidence Reliability Score (304 Eligible Batters)', weight='bold', pad=15)
    ax.set_xlabel('Evidence Reliability Score (ERS, 0–100 Scale)')
    ax.set_ylabel('Performance Rating (PR, 0–100 Scale)')
    ax.set_xlim(15, 105)
    ax.set_ylim(20, 105)
    ax.legend(loc='lower right', frameon=True, facecolor=LIGHT_BG)
    ax.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig('reports/figures/fig3_batting_credibility.png', bbox_inches='tight')
    plt.close()
    print("Generated fig3_batting_credibility.png")

def fig4_bowling_credibility():
    """Figure 4: Bowling Performance Rating vs. Evidence Reliability Score"""
    bw_rat = pd.read_parquet('data/processed/bowler_player_ratings.parquet')
    eligible = bw_rat[bw_rat['is_eligible_for_ranking'] == 1].copy()

    fig, ax = plt.subplots(figsize=(10, 6.2))
    fig.patch.set_facecolor('#FFFFFF')

    strong = eligible[eligible['evidence_tier'] == 'Strong Evidence']
    mod = eligible[eligible['evidence_tier'] == 'Moderate Evidence']

    ax.scatter(mod['evidence_reliability_score'], mod['performance_rating'],
               color=CYAN, alpha=0.6, s=45, label=f'Moderate Evidence (n={len(mod)})', edgecolors='none')
    ax.scatter(strong['evidence_reliability_score'], strong['performance_rating'],
               color=ROYAL_BLUE, alpha=0.85, s=65, label=f'Strong Evidence (n={len(strong)})', edgecolors=NAVY, linewidth=0.4)

    # Key callouts
    callouts = ['Chris Woakes', 'Benjamin Sears', 'Liam Dawson', 'Sikandar Raza', 'George Dockrell', 'Sufiyan Muqeem', 'Yuzvendra Chahal']
    for name in callouts:
        row = eligible[eligible['bowler_name'] == name]
        if not row.empty:
            x = row['evidence_reliability_score'].values[0]
            y = row['performance_rating'].values[0]
            ax.scatter(x, y, color=RR_PINK, s=90, zorder=5, edgecolors=NAVY, linewidth=1)
            ax.annotate(name, (x, y), xytext=(6, 4), textcoords='offset points', fontsize=9, weight='bold', color=NAVY)

    ax.axhline(50, color=SLATE, linestyle=':', alpha=0.7)
    ax.axvline(50, color=SLATE, linestyle=':', alpha=0.7)
    ax.set_title('Bowling Performance Rating vs. Evidence Reliability Score (290 Eligible Bowlers)', weight='bold', pad=15)
    ax.set_xlabel('Evidence Reliability Score (ERS, 0–100 Scale)')
    ax.set_ylabel('Performance Rating (PR, 0–100 Scale)')
    ax.set_xlim(15, 105)
    ax.set_ylim(20, 105)
    ax.legend(loc='lower right', frameon=True, facecolor=LIGHT_BG)
    ax.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig('reports/figures/fig4_bowling_credibility.png', bbox_inches='tight')
    plt.close()
    print("Generated fig4_bowling_credibility.png")

def fig5_bootstrap_stability():
    """Figure 5: 95% Bootstrap Confidence Intervals for Top Recommendations"""
    b_unc = pd.read_parquet('data/processed/batter_rating_uncertainty.parquet')
    bw_unc = pd.read_parquet('data/processed/bowler_rating_uncertainty.parquet')

    top_bat = ['Tim David', 'Naman Dhir', 'Matthew Wade', 'Ashutosh Sharma', 'Mahipal Lomror']
    top_bowl = ['Benjamin Sears', 'Liam Dawson', 'Eshan Malinga', 'Sikandar Raza', 'Taskin Ahmed']

    bat_df = b_unc[b_unc['player_name'].isin(top_bat)].copy()
    bowl_df = bw_unc[bw_unc['player_name'].isin(top_bowl)].copy()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2), sharex=True)
    fig.patch.set_facecolor('#FFFFFF')

    # Batters CI
    y_pos = np.arange(len(bat_df))
    ax1.errorbar(
        bat_df['baseline_rating'], y_pos,
        xerr=[bat_df['baseline_rating'] - bat_df['rating_p025'], bat_df['rating_p975'] - bat_df['baseline_rating']],
        fmt='o', color=ROYAL_BLUE, ecolor=CYAN, elinewidth=2, capsize=4, markersize=7, label='Rating & 95% CI'
    )
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(bat_df['player_name'], weight='bold')
    ax1.set_title('Top Actionable Batters: 95% Uncertainty CI', weight='bold', pad=15)
    ax1.set_xlabel('Performance Rating (0–100 Scale)')
    ax1.set_xlim(40, 95)
    ax1.grid(axis='x', linestyle='--', alpha=0.5)

    # Bowlers CI
    y_pos_bw = np.arange(len(bowl_df))
    ax2.errorbar(
        bowl_df['baseline_rating'], y_pos_bw,
        xerr=[bowl_df['baseline_rating'] - bowl_df['rating_p025'], bowl_df['rating_p975'] - bowl_df['baseline_rating']],
        fmt='o', color=RR_PINK, ecolor='#FB7185', elinewidth=2, capsize=4, markersize=7, label='Rating & 95% CI'
    )
    ax2.set_yticks(y_pos_bw)
    ax2.set_yticklabels(bowl_df['player_name'], weight='bold')
    ax2.set_title('Top Actionable Bowlers: 95% Uncertainty CI', weight='bold', pad=15)
    ax2.set_xlabel('Performance Rating (0–100 Scale)')
    ax2.grid(axis='x', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig('reports/figures/fig5_bootstrap_stability.png', bbox_inches='tight')
    plt.close()
    print("Generated fig5_bootstrap_stability.png")

def fig6_rr_squad_gaps():
    """Figure 6: Rajasthan Royals Tactical Role Depth vs. Target Squad Voids"""
    gaps = pd.read_parquet('data/processed/rr_squad_gap_analysis.parquet')
    scen_b = gaps[gaps['scenario'].str.contains('Scenario B')].copy()

    fig, ax = plt.subplots(figsize=(10, 5.5))
    fig.patch.set_facecolor('#FFFFFF')

    roles = scen_b['tactical_role'].tolist()
    y_pos = np.arange(len(roles))
    current_depth = scen_b['squad_count_total'].values
    weights = scen_b['gap_criticality_weight'].values

    # Bar chart of current squad depth
    bars = ax.barh(y_pos, current_depth, height=0.55, color=ROYAL_BLUE, edgecolor=NAVY, label='Current Squad Depth')

    # Annotate criticality
    for i, (bar, w) in enumerate(zip(bars, weights)):
        width = bar.get_width()
        crit_label = 'CRITICAL VOID' if w >= 0.25 else ('Moderate Need' if w >= 0.15 else 'Sufficient Depth')
        color = RR_PINK if w >= 0.25 else (GOLD if w >= 0.15 else EMERALD)
        ax.text(width + 0.15, bar.get_y() + bar.get_height()/2., f'{int(width)} players | {crit_label}',
                va='center', fontsize=9, weight='bold', color=color)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(roles, weight='bold')
    ax.invert_yaxis()
    ax.set_title('Rajasthan Royals Squad Depth & Tactical Gaps (Scenario B Model)', weight='bold', pad=15)
    ax.set_xlabel('Number of Retained Players in Role')
    ax.set_xlim(0, max(current_depth) + 4)
    ax.grid(axis='x', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig('reports/figures/fig6_rr_squad_gaps.png', bbox_inches='tight')
    plt.close()
    print("Generated fig6_rr_squad_gaps.png")

def fig7_auction_scenarios():
    """Figure 7: 5 Budget Allocation Scenarios (100 BAU model)"""
    allocs = pd.read_parquet('data/processed/auction_budget_allocations.parquet')

    pivot = allocs.pivot(index='scenario_name', columns='allocation_category', values='budget_units').fillna(0)

    fig, ax = plt.subplots(figsize=(11, 5.8))
    fig.patch.set_facecolor('#FFFFFF')

    category_colors = {
        'Death Overs Specialist Bowling': RR_PINK,
        'Lower-Order Finishing Power': ROYAL_BLUE,
        'Top-Order Powerplay Batting': CYAN,
        'Specialist Spin / Utility': GOLD,
        'Flexible Squad Depth Reserve': SLATE
    }

    # Plot stacked bar chart
    bottom = np.zeros(len(pivot))
    for col in pivot.columns:
        color = category_colors.get(col, '#94A3B8')
        ax.barh(pivot.index, pivot[col], left=bottom, label=col, color=color, edgecolor='white', height=0.55)
        bottom += pivot[col].values

    ax.set_title('Auction Strategy: 100 Budget Allocation Units (BAU) Across 5 Scenarios', weight='bold', pad=15)
    ax.set_xlabel('Budget Allocation Units (BAU, Total = 100)')
    ax.set_xlim(0, 105)
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.28), ncol=2, frameon=True, facecolor=LIGHT_BG)
    ax.grid(axis='x', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig('reports/figures/fig7_auction_scenarios.png', bbox_inches='tight')
    plt.close()
    print("Generated fig7_auction_scenarios.png")

def fig8_recruitment_matrix():
    """Figure 8: Candidate Governance Quadrant (PR vs. TFS with RDH bubble sizes)"""
    rec = pd.read_parquet('data/processed/recruitment_recommendation_matrix.parquet')

    fig, ax = plt.subplots(figsize=(11, 6.8))
    fig.patch.set_facecolor('#FFFFFF')

    cat_map = {
        'Viable Auction Target': (ROYAL_BLUE, 'Viable Auction Target (Actionable)'),
        'Existing RR Player (Internal Asset)': (RR_PINK, 'Existing RR Player (Internal Asset)'),
        'Strategic Benchmark (BCCI Ineligible)': ('#64748B', 'Strategic Benchmark (BCCI Ineligible)'),
        'Strategic Benchmark (Rival Core)': ('#0284C7', 'Strategic Benchmark (Rival Franchise Core)'),
        'Strategic Benchmark (Retired)': ('#D97706', 'Strategic Benchmark (Retired Veteran)')
    }

    for cat, (color, label) in cat_map.items():
        sub = rec[rec['candidate_category'] == cat]
        if not sub.empty:
            sizes = (sub['recruitment_decision_score'] - 45) ** 1.8 * 2.5
            ax.scatter(sub['performance_rating'], sub['tactical_squad_fit_score'],
                       s=sizes, color=color, label=f'{label} (n={len(sub)})',
                       alpha=0.8, edgecolors=NAVY, linewidth=0.6)

    # Annotate top actionable targets and benchmarks
    top_labels = ['Tim David', 'Naman Dhir', 'Matthew Wade', 'Benjamin Sears', 'Liam Dawson', 'Sufiyan Muqeem', 'Sanju Samson']
    for name in top_labels:
        row = rec[rec['player_name'] == name]
        if not row.empty:
            x = row['performance_rating'].values[0]
            y = row['tactical_squad_fit_score'].values[0]
            rdh = row['recruitment_decision_score'].values[0]
            ax.annotate(f'{name} (RDH {rdh:.1f})', (x, y), xytext=(6, 5), textcoords='offset points',
                        fontsize=8.5, weight='bold', color=NAVY)

    ax.axvline(70, color=SLATE, linestyle=':', alpha=0.6)
    ax.axhline(70, color=SLATE, linestyle=':', alpha=0.6)
    ax.text(92, 92, 'PRIORITY TARGET\nQUADRANT', ha='center', va='center', fontsize=9, color=ROYAL_BLUE, weight='bold', alpha=0.4)

    ax.set_title('Candidate Decision Matrix: Performance vs. Tactical Fit (Bubble Size = RDH)', weight='bold', pad=15)
    ax.set_xlabel('Performance Rating (PR, 0–100 Scale)')
    ax.set_ylabel('Tactical Squad Fit Score (TFS, 0–100 Scale)')
    ax.set_xlim(55, 102)
    ax.set_ylim(45, 102)
    ax.legend(loc='lower left', frameon=True, facecolor=LIGHT_BG, fontsize=8.5)
    ax.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig('reports/figures/fig8_recruitment_matrix.png', bbox_inches='tight')
    plt.close()
    print("Generated fig8_recruitment_matrix.png")

if __name__ == '__main__':
    fig1_dataset_scope()
    fig2_leverage_distribution()
    fig3_batting_credibility()
    fig4_bowling_credibility()
    fig5_bootstrap_stability()
    fig6_rr_squad_gaps()
    fig7_auction_scenarios()
    fig8_recruitment_matrix()
    print("All 8 publication figures generated successfully!")
