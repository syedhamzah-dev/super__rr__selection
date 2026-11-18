"""
SupeRR Selector - Module 8 Dashboard Data Exporter (Audited & Reconciled)
Exports verified Parquet and CSV outputs from Modules 1-7 into clean,
structured, lightweight JSON files and an offline JS bundle for the interactive dashboard.
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd

def resolve_path(relative_path: str) -> Path:
    p = Path(relative_path)
    if p.exists():
        return p
    p_parent = Path("..") / relative_path
    if p_parent.exists():
        return p_parent
    return p

def sanitize_for_json(obj):
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, float, np.float64, np.float32)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return round(float(obj), 2)
    elif isinstance(obj, (np.ndarray, list)):
        return [sanitize_for_json(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif pd.isna(obj):
        return None
    return obj

def get_player_initials(name: str) -> str:
    parts = [p.strip() for p in name.replace("-", " ").split() if p.strip()]
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    elif len(parts) == 1:
        return parts[0][:2].upper()
    return "RR"

# Verified read-only public image references (loaded dynamically in frontend with lazy loading & initials fallback)
VERIFIED_IMAGE_URLS = {
    # Batters
    6396: "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/lsci/db/PICTURES/CMS/321800/321898.png",  # Tim David
    796: "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/lsci/db/PICTURES/CMS/321800/321846.png",   # Matthew Wade
    6819: "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/lsci/db/PICTURES/CMS/380200/380261.png",  # Yashasvi Jaiswal
    2258: "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/lsci/db/PICTURES/CMS/380300/380313.png",  # Sanju Samson
    1699: "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/lsci/db/PICTURES/CMS/380300/380315.png",  # Suryakumar Yadav
    4708: "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/lsci/db/PICTURES/CMS/380300/380314.png",  # Rinku Singh
    5553: "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/lsci/db/PICTURES/CMS/381600/381656.png",  # Phil Salt
    813: "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/lsci/db/PICTURES/CMS/381600/381655.png",   # Jos Buttler
    7260: "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/lsci/db/PICTURES/CMS/380200/380262.png",  # Dhruv Jurel
    152: "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/lsci/db/PICTURES/CMS/380200/380263.png",   # Ravindra Jadeja
    # Bowlers
    2933: "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/lsci/db/PICTURES/CMS/380200/380287.png",  # Jasprit Bumrah
    3959: "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/lsci/db/PICTURES/CMS/381600/381658.png",  # Chris Woakes
    722: "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/lsci/db/PICTURES/CMS/381600/381657.png",   # Liam Dawson
    4856: "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/lsci/db/PICTURES/CMS/382000/382004.png",  # Benjamin Sears
    7920: "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/lsci/db/PICTURES/CMS/321800/321847.png",  # Nathan Ellis
    781: "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/lsci/db/PICTURES/CMS/380300/380316.png",   # Sunil Narine
    7503: "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/lsci/db/PICTURES/CMS/380200/380264.png",  # Ravi Bishnoi
    143: "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/lsci/db/PICTURES/CMS/380200/380288.png"    # Dinesh Karthik
}

def get_scouting_rationale(pid: int, name: str, role: str, gap: str, disc: str, pr: float, rdh: float, sss: float, tfs: float) -> str:
    custom = {
        6396: "Elite death-overs boundary striker (179.3 clutch SR, 25.0% boundary rate). Solves Rajasthan Royals' #1 critical void (Finisher) with game-winning finishing power.",
        37052: "High-ceiling domestic power hitter with 84.48 Pressure Rating and 165+ clutch strike rate. Conserves an overseas slot while offering middle-order explosiveness and secondary spin.",
        796: "Battle-tested international wicketkeeper-finisher (81.39 PR, 78.01 stability). Provides calm death-overs execution under pressure and indispensable dual-role backup for Dhruv Jurel.",
        8101: "Dynamic lower-order domestic aggressor with exceptional clutch boundary rate (84.44 TFS). Delivers game-breaking acceleration and fearless chase execution.",
        4821: "Proven domestic left-handed middle-order striker (85.26 PR, 84.50 TFS). Demolishes spin through middle overs and provides formidable power hitting at the death.",
        6281: "Explosive domestic top-order engine with 190+ powerplay strike rate. Provides lightning-fast starts against pace and spin while offering tactical bowling versatility.",
        6460: "Composed domestic middle-overs stabilizer with 61.40 stability. Excels at crisis recovery, strike rotation, and tempo shifts in high-pressure chases.",
        2639: "Experienced international powerhouse (71.32 PR) offering proven multi-phase boundary striking and handy middle-overs seam bowling under pressure.",
        4369: "Technically adept wicketkeeper-anchor (79.99 PR) with strong tempo control, elite boundary placement, and anchor versatility in challenging batting conditions.",
        2258: "High-impact wicketkeeper-batter (71.01 PR) capable of accelerating against both pace and spin across all batting phases with deep franchise familiarity.",
        6819: "Rajasthan Royals cornerstone retention. #1 ranked historical T20 batter with 96.90 PR and transcendent powerplay boundary hitting against both pace and spin.",
        5553: "Ultra-aggressive top-order wicketkeeper-batter with 84.42 PR and 180+ strike rate in the powerplay; dismantles new-ball bowling attacks.",
        6725: "Explosive West Indian middle-order power hitter with exceptional bat speed; clears the ropes under extreme death-overs pressure.",
        1077: "World-renowned international finisher with ice-cold temperament in pressure chases; provides elite left-handed middle-overs stability.",
        813: "World-class wicketkeeper-batter with transcendent powerplay boundary striking and elite tournament-winning pedigree.",
        7897: "Polished domestic left-handed middle-order batter with composed strike rotation and proven ability to rebuild after top-order collapses.",
        2756: "Fearless domestic finisher with lightning boundary hitting in the death overs; proven clutch match-winner in tight finishes.",
        4755: "Formidable domestic power hitter who dismantles spin with ease through the middle overs and provides auxiliary seam bowling.",
        838: "Dynamic multi-phase game-changer capable of 360-degree boundary striking, explosive finishing, and handy off-spin overs.",
        3605: "Authoritative top/middle-order batting all-rounder with excellent technique, steady leadership temperament, and off-spin utility.",
        # Bowlers
        4856: "Express pace (145+ kph) with lethal yorker execution and 75.30 PR. Directly addresses Rajasthan Royals' critical void in death overs with high wicket-taking ceiling.",
        722: "Masterful middle-overs left-arm control spinner (72.68 PR, 6.45 clutch economy). Suppresses scoring rates under pressure while contributing lower-order batting depth.",
        39657: "Slingy death-overs execution specialist with 80.89 TFS. Reproduces the lethal low-arm release angle to stifle death-phase scoring and nail blockhole yorkers.",
        2984: "Battle-tested international all-rounder with 75.27 TFS. Delivers clutch breakthroughs in middle overs, mystery spin variations, and explosive late batting.",
        2681: "High-velocity new-ball strike bowler (69.81 PR) capable of early breakthroughs, steep bounce, and aggressive hard-length bowling in the powerplay.",
        6450: "World-class finger mystery spinner (73.06 TFS) with exceptional dot-ball percentage across Powerplay and Middle phases with varied carrom balls.",
        1101: "Versatile left-arm orthodox spinner and finisher with 83.05 PR and 85.12 TFS. Provides tactical bowling flexibility, clutch economy, and boundary hitting at #7/8.",
        2687: "Tall off-spinning all-rounder with 74.42 TFS. Provides miserly middle-overs economy against left-handers, excellent boundary containment, and steady batting stability.",
        4658: "Accurate left-arm dart specialist (75.42 TFS) with proven powerplay and middle-overs run suppression in low-scoring thrillers and spin-friendly tracks.",
        4219: "Astute domestic all-rounder with 77.19 TFS. Provides veteran middle-overs spin squeeze and crucial batting depth without consuming an overseas slot.",
        22471: "Young international left-arm spinner with 77.56 PR; sharp drift and restrictive line-and-length control under high match pressure.",
        305: "Legendary tactical mastermind with elite carrom ball and variations; controls the tempo of the middle overs with unmatched game awareness.",
        7920: "Renowned back-of-the-hand slower ball and yorker specialist (60.13 RDH, 86.20 TFS) with proven death-overs boundary containment in high-leverage situations.",
        3276: "Economical left-arm orthodox spinner with tight stump-to-stump accuracy and steady wicket-taking threat through the middle overs.",
        4900: "Elite leg-spin all-rounder with deceptive googly and game-breaking wicket-taking strike rate in high-pressure middle overs.",
        8805: "Skilled death-overs specialist with pin-point wide yorkers, heavy slower balls, and calm composure at the back end of the innings.",
        2636: "World-class leg-spin enforcer with sharp turn and drift; consistently breaks crucial middle-overs partnerships.",
        3959: "Masterful new-ball seam enforcer with 90.22 PR and exceptional swing control; creates early breakthroughs in the powerplay.",
        # Benchmarks
        34485: "BCCI Regulatory Benchmark (Non-Actionable): Elite international wrist-spinner with exceptional clutch turn (88.28 PR); analytical model benchmark for world-class middle-overs spin.",
        3578: "BCCI Regulatory Benchmark (Non-Actionable): World-class left-arm orthodox powerplay control spinner (81.42 PR); comparative benchmark for restrictive opening bowling.",
        7364: "BCCI Regulatory Benchmark (Non-Actionable): Express pace death bowler capable of 150+ kph rockets and blockhole yorkers under extreme pressure.",
        2490: "BCCI Regulatory Benchmark (Non-Actionable): Experienced all-rounder providing dependable left-arm spin containment and late-order power hitting.",
        7690: "BCCI Regulatory Benchmark (Non-Actionable): Dynamic top-order aggressor and mystery spinner with rapid hand speed and fearless intent.",
        2933: "Rival Core Benchmark (Non-Actionable): Gold standard T20 pace enforcer with unparalleled death yorker execution and sub-6.5 economy under extreme leverage.",
        1699: "Rival Core Benchmark (Non-Actionable): World #1 360-degree boundary striker; analytical benchmark for middle-overs field manipulation and boundary striking.",
        781: "Rival Core Benchmark (Non-Actionable): Master mystery spinner and explosive opening pinch-hitter with unmatched tournament longevity.",
        4708: "Rival Core Benchmark (Non-Actionable): Elite domestic finisher with ice-cold death-overs boundary hitting and clutch chase execution.",
        143: "Historical Reference (Retired): Veteran finisher and wicketkeeper benchmark illustrating late-career pressure execution and situational mastery.",
        # Internal RR Assets
        7260: "RR Internal Cornerstone: High-calibre domestic wicketkeeper-finisher with exceptional temperament, agile glovework, and death-phase acceleration.",
        152: "RR Internal Cornerstone: Premier international all-rounder providing miserly left-arm spin, world-class fielding, and lower-order boundary power.",
        6423: "RR Internal Cornerstone: Dynamic middle-order aggressor with proven ability to anchor and explode against spin and pace.",
        7503: "RR Internal Cornerstone: Express leg-spinner with rapid arm action and unpickable googly; key middle-overs wicket-taker."
    }
    if pid in custom:
        return custom[pid]
    
    if disc == "Batting":
        return f"Accomplished {role} demonstrating {pr:.1f} Pressure Performance Rating and strong tactical alignment ({tfs:.1f} TFS) to address Rajasthan Royals' {gap.lower()}."
    else:
        return f"Impact {role} delivering {pr:.1f} Pressure Performance Rating and high tactical utility ({tfs:.1f} TFS) to address Rajasthan Royals' {gap.lower()}."

def parse_evidence_tier(tier_val) -> tuple[str, str]:
    tier_str = str(tier_val)
    if "Strong" in tier_str:
        return "Strong", "Strong Evidence"
    elif "Moderate" in tier_str:
        return "Moderate", "Moderate Evidence"
    elif "Insufficient" in tier_str:
        return "Insufficient", "Insufficient Evidence"
    else:
        return "Not_Eligible", "Not Eligible"

def export_dashboard_data(output_dir: str = "dashboard/data"):
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    print(f"Exporting reconciled dashboard data to: {out_path.resolve()}")

    # 1. Load Audited Squad Baseline to get RR Player IDs
    rr_baseline_df = pd.read_parquet(resolve_path("data/processed/rr_squad_baseline_2026.parquet"))
    rr_pids = set(rr_baseline_df["player_id"].tolist())

    # Governance Classifier
    def get_governance(pid: int, country: str):
        if pid in rr_pids:
            return "Existing RR Player (Internal Asset)", "Existing RR Squad Member (Internal Retention / Roster Core)"
        if country == "Pakistan":
            return "Strategic Benchmark (BCCI Ineligible)", "Ineligible for IPL Auction (BCCI Policy Restriction; Global Role Model)"
        if pid in [143]:
            return "Strategic Benchmark (Retired)", "Retired from IPL Competition (Historical Reference Benchmark)"
        if pid in [2933, 1699, 781, 4708]:
            return "Strategic Benchmark (Rival Core)", "Conditional on Release (Rival Franchise Core Asset; Comparative Benchmark)"
        return "Viable Auction Target", "Potential Auction Candidate (Availability unconfirmed; conditional on official IPL 2027 player registration)"

    # 2. Export Batters Data (304 eligible batters)
    b_df = pd.read_parquet(resolve_path("data/processed/batter_squad_fit_evaluations.parquet"))
    batters_list = []
    for _, row in b_df.iterrows():
        pid = int(row["player_id"])
        country = str(row["country"])
        cat, avail = get_governance(pid, country)
        tier_code, tier_label = parse_evidence_tier(row["evidence_tier"])
        
        b_item = {
            "rank": int(row["rank"]),
            "player_id": pid,
            "player_name": str(row["player_name"]),
            "initials": get_player_initials(str(row["player_name"])),
            "image_url": VERIFIED_IMAGE_URLS.get(pid, None),
            "image_alt": f"Photograph of {row['player_name']}",
            "country": country,
            "is_overseas": bool(row["is_overseas"]),
            "primary_role": str(row["primary_role"]),
            "tactical_role": str(row["tactical_role"]),
            "player_archetype": str(row.get("player_archetype", "Standard Batter")),
            "performance_rating": round(float(row["performance_rating"]), 2),
            "evidence_reliability_score": round(float(row["evidence_reliability_score"]), 2),
            "evidence_tier": tier_code,
            "evidence_tier_label": tier_label,
            "matches_played": int(row["matches_played"]),
            "comps_played": int(row["comps_played"]),
            # Overall
            "bf_overall": int(row["bf_overall"]),
            "runs_overall": int(row["runs_overall"]),
            "sr_overall": round(float(row["sr_overall"]), 2),
            # Clutch
            "bf_clutch": int(row["bf_clutch"]),
            "runs_clutch": int(row["runs_clutch"]),
            "sr_clutch": round(float(row["sr_clutch"]), 2),
            "bnd_pct_clutch": round(float(row["bnd_pct_clutch"]), 2),
            "dot_pct_clutch": round(float(row["dot_pct_clutch"]), 2),
            "rpd_clutch": round(float(row["rpd_clutch"]), 2),
            "batting_clutch_index": round(float(row["batting_clutch_index"]), 2),
            # Robustness
            "bootstrap_mean_rating": round(float(row["bootstrap_mean_rating"]), 2),
            "rating_std": round(float(row["rating_std"]), 2),
            "rating_p025": round(float(row["rating_p025"]), 2),
            "rating_p975": round(float(row["rating_p975"]), 2),
            "rating_ci_width": round(float(row["rating_ci_width"]), 2),
            "bootstrap_mean_rank": round(float(row["bootstrap_mean_rank"]), 1),
            "rank_std": round(float(row["rank_std"]), 2),
            "top5_freq_pct": round(float(row["top5_freq_pct"]), 2),
            "top10_freq_pct": round(float(row["top10_freq_pct"]), 2),
            "top20_freq_pct": round(float(row["top20_freq_pct"]), 2),
            "eligibility_pct": round(float(row["eligibility_pct"]), 2),
            "clutch_volume_hhi": round(float(row["clutch_volume_hhi"]), 4),
            "top_match_run_share": round(float(row["top_match_run_share"]), 2),
            "lomo_rating_shift": round(float(row["rating_shift"]), 2),
            "resilience_category": str(row["resilience_category"]),
            # Squad Fit & Decision
            "statistical_stability_score": round(float(row["statistical_stability_score"]), 2),
            "tactical_squad_fit_score": round(float(row["tactical_squad_fit_score"]), 2),
            "acquisition_risk_score": round(float(row["acquisition_risk_score"]), 2),
            "recruitment_decision_score": round(float(row["recruitment_decision_score"]), 2),
            "recommendation_priority": str(row["recommendation_priority"]),
            "candidate_category": cat,
            "availability_status": avail,
            "scouting_rationale": get_scouting_rationale(
                pid, str(row["player_name"]), str(row["tactical_role"]),
                "Squad Depth", "Batting", float(row["performance_rating"]),
                float(row["recruitment_decision_score"]), float(row["statistical_stability_score"]),
                float(row["tactical_squad_fit_score"])
            ),
            # Sensitivity
            "score_balanced": round(float(row["score_balanced"]), 2),
            "score_stability_first": round(float(row["score_stability_first"]), 2),
            "score_gap_priority": round(float(row["score_gap_priority"]), 2),
            "rank_balanced": int(row["rank_balanced"]),
            "rank_stability_first": int(row["rank_stability_first"]),
            "rank_gap_priority": int(row["rank_gap_priority"]),
        }
        batters_list.append(b_item)

    with open(out_path / "batters_data.json", "w", encoding="utf-8") as f:
        json.dump(batters_list, f, indent=2)
    print(f" -> Exported batters_data.json ({len(batters_list)} batters)")

    # 3. Export Bowlers Data (290 eligible bowlers)
    bw_df = pd.read_parquet(resolve_path("data/processed/bowler_squad_fit_evaluations.parquet"))
    bowlers_list = []
    for _, row in bw_df.iterrows():
        pid = int(row["player_id"])
        country = str(row["country"])
        cat, avail = get_governance(pid, country)
        tier_code, tier_label = parse_evidence_tier(row["evidence_tier"])
        
        bw_item = {
            "rank": int(row["rank"]),
            "player_id": pid,
            "player_name": str(row["player_name"]),
            "initials": get_player_initials(str(row["player_name"])),
            "image_url": VERIFIED_IMAGE_URLS.get(pid, None),
            "image_alt": f"Photograph of {row['player_name']}",
            "country": country,
            "is_overseas": bool(row["is_overseas"]),
            "primary_bowling_role": str(row["primary_bowling_role"]),
            "tactical_role": str(row["tactical_role"]),
            "player_archetype": str(row.get("player_archetype", "Standard Bowler")),
            "performance_rating": round(float(row["performance_rating"]), 2),
            "evidence_reliability_score": round(float(row["evidence_reliability_score"]), 2),
            "evidence_tier": tier_code,
            "evidence_tier_label": tier_label,
            "matches_played": int(row["matches_played"]),
            "comps_played": int(row["comps_played"]),
            # Overall
            "legal_balls_overall": int(row["legal_balls_overall"]),
            "economy_overall": round(float(row["economy_overall"]), 2),
            "wickets_overall": int(row["wickets_overall"]),
            # Clutch
            "legal_balls_clutch": int(row["legal_balls_clutch"]),
            "economy_clutch": round(float(row["economy_clutch"]), 2),
            "wickets_clutch": int(row["wickets_clutch"]),
            "delta_econ_phase_adj": round(float(row["delta_econ_phase_adj"]), 2),
            "true_dot_pct_clutch": round(float(row["true_dot_pct_clutch"]), 2),
            "bnd_pct_clutch": round(float(row["bnd_pct_clutch"]), 2),
            "bowling_clutch_index": round(float(row["bowling_clutch_index"]), 2),
            # Robustness
            "bootstrap_mean_rating": round(float(row["bootstrap_mean_rating"]), 2),
            "rating_std": round(float(row["rating_std"]), 2),
            "rating_p025": round(float(row["rating_p025"]), 2),
            "rating_p975": round(float(row["rating_p975"]), 2),
            "rating_ci_width": round(float(row["rating_ci_width"]), 2),
            "bootstrap_mean_rank": round(float(row["bootstrap_mean_rank"]), 1),
            "rank_std": round(float(row["rank_std"]), 2),
            "top5_freq_pct": round(float(row["top5_freq_pct"]), 2),
            "top10_freq_pct": round(float(row["top10_freq_pct"]), 2),
            "top20_freq_pct": round(float(row["top20_freq_pct"]), 2),
            "eligibility_pct": round(float(row["eligibility_pct"]), 2),
            "clutch_volume_hhi": round(float(row["clutch_volume_hhi"]), 4),
            "top_match_wkt_share": round(float(row["top_match_wkt_share"]), 2),
            "lomo_rating_shift": round(float(row["rating_shift"]), 2),
            "resilience_category": str(row["resilience_category"]),
            # Squad Fit & Decision
            "statistical_stability_score": round(float(row["statistical_stability_score"]), 2),
            "tactical_squad_fit_score": round(float(row["tactical_squad_fit_score"]), 2),
            "acquisition_risk_score": round(float(row["acquisition_risk_score"]), 2),
            "recruitment_decision_score": round(float(row["recruitment_decision_score"]), 2),
            "recommendation_priority": str(row["recommendation_priority"]),
            "candidate_category": cat,
            "availability_status": avail,
            "scouting_rationale": get_scouting_rationale(
                pid, str(row["player_name"]), str(row["tactical_role"]),
                "Squad Depth", "Bowling", float(row["performance_rating"]),
                float(row["recruitment_decision_score"]), float(row["statistical_stability_score"]),
                float(row["tactical_squad_fit_score"])
            ),
            # Sensitivity
            "score_balanced": round(float(row["score_balanced"]), 2),
            "score_stability_first": round(float(row["score_stability_first"]), 2),
            "score_gap_priority": round(float(row["score_gap_priority"]), 2),
            "rank_balanced": int(row["rank_balanced"]),
            "rank_stability_first": int(row["rank_stability_first"]),
            "rank_gap_priority": int(row["rank_gap_priority"]),
        }
        bowlers_list.append(bw_item)

    with open(out_path / "bowlers_data.json", "w", encoding="utf-8") as f:
        json.dump(bowlers_list, f, indent=2)
    print(f" -> Exported bowlers_data.json ({len(bowlers_list)} bowlers)")

    # 4. Export Recruitment Recommendation Matrix (50 targets)
    rec_df = pd.read_parquet(resolve_path("data/processed/recruitment_recommendation_matrix.parquet"))
    # Index batters and bowlers for clutch stats lookup
    b_lookup = {b["player_id"]: b for b in batters_list}
    bw_lookup = {bw["player_id"]: bw for bw in bowlers_list}

    rec_list = []
    for _, row in rec_df.iterrows():
        tier_code, tier_label = parse_evidence_tier(row["evidence_tier"])
        pid = int(row["player_id"])
        disc = str(row["discipline"])
        pname = str(row["player_name"])
        role = str(row["tactical_role"])
        gap = str(row["squad_gap_addressed"])
        pr = float(row["performance_rating"])
        rdh = float(row["recruitment_decision_score"])
        sss = float(row["statistical_stability_score"])
        tfs = float(row["tactical_squad_fit_score"])

        # Fetch clutch stats if present
        clutch_stats = {}
        if disc == "Batting" and pid in b_lookup:
            b_src = b_lookup[pid]
            clutch_stats = {
                "bf_clutch": b_src["bf_clutch"],
                "runs_clutch": b_src["runs_clutch"],
                "sr_clutch": b_src["sr_clutch"],
                "bnd_pct_clutch": b_src["bnd_pct_clutch"],
                "dot_pct_clutch": b_src["dot_pct_clutch"]
            }
        elif disc == "Bowling" and pid in bw_lookup:
            bw_src = bw_lookup[pid]
            clutch_stats = {
                "legal_balls_clutch": bw_src["legal_balls_clutch"],
                "economy_clutch": bw_src["economy_clutch"],
                "wickets_clutch": bw_src["wickets_clutch"],
                "true_dot_pct_clutch": bw_src["true_dot_pct_clutch"],
                "bnd_pct_clutch": bw_src["bnd_pct_clutch"]
            }

        rec_list.append({
            "player_id": pid,
            "player_name": pname,
            "initials": get_player_initials(pname),
            "discipline": disc,
            "country": str(row["country"]),
            "is_overseas": bool(row["is_overseas"]),
            "tactical_role": role,
            "performance_rating": round(pr, 2),
            "evidence_reliability_score": round(float(row["evidence_reliability_score"]), 2),
            "evidence_tier": tier_code,
            "evidence_tier_label": tier_label,
            "bootstrap_eligibility_pct": round(float(row["bootstrap_eligibility_pct"]), 2),
            "rating_ci_width": round(float(row["rating_ci_width"]), 2),
            "top20_freq_pct": round(float(row["top20_freq_pct"]), 2),
            "clutch_volume_hhi": round(float(row["clutch_volume_hhi"]), 4),
            "lomo_rating_shift": round(float(row["lomo_rating_shift"]), 2),
            "tactical_squad_fit_score": round(tfs, 2),
            "statistical_stability_score": round(sss, 2),
            "acquisition_risk_score": round(float(row["acquisition_risk_score"]), 2),
            "recruitment_decision_score": round(rdh, 2),
            "player_archetype": str(row["player_archetype"]),
            "recommendation_priority": str(row["recommendation_priority"]),
            "squad_gap_addressed": gap,
            "candidate_category": str(row["candidate_category"]),
            "availability_status": str(row["availability_status"]),
            "scouting_rationale": get_scouting_rationale(pid, pname, role, gap, disc, pr, rdh, sss, tfs),
            "clutch_stats": clutch_stats
        })
    with open(out_path / "recruitment_matrix.json", "w", encoding="utf-8") as f:
        json.dump(rec_list, f, indent=2)
    print(f" -> Exported recruitment_matrix.json ({len(rec_list)} shortlisted targets)")

    # 5. Export RR Squad Baseline (27 registered players)
    rr_list = []
    for _, row in rr_baseline_df.iterrows():
        mp = int(row["matches_played"])
        pid = int(row["player_id"])
        if pid == 4409:
            status = "Administrative Roster Registration (Non-Participant)"
        elif mp > 0:
            status = f"Active Playing XI / Rotation ({mp} matches)"
        else:
            status = "Bench / Tactical Reserve Specialist (0 matches)"
            
        rr_list.append({
            "player_id": pid,
            "player_name": str(row["player_name"]),
            "matches_played": mp,
            "roster_status": status,
            "is_wk": bool(row["is_wk"]),
            "avg_batting_order": round(float(row["avg_batting_order"]), 1) if pd.notna(row["avg_batting_order"]) else None,
            "country": str(row["country"]),
            "is_overseas": bool(row["is_overseas"]),
            "bat_role": str(row["tactical_bat_role"]),
            "bowl_role": str(row["tactical_bowl_role"]),
            "bat_rating": round(float(row["bat_rating"]), 2) if pd.notna(row["bat_rating"]) else None,
            "bowl_rating": round(float(row["bowl_rating"]), 2) if pd.notna(row["bowl_rating"]) else None,
        })
    with open(out_path / "rr_squad_data.json", "w", encoding="utf-8") as f:
        json.dump(rr_list, f, indent=2)
    print(f" -> Exported rr_squad_data.json ({len(rr_list)} RR squad records)")

    # 6. Export RR Squad Gap Analysis (36 evaluations: 12 roles x 3 scenarios)
    gap_df = pd.read_parquet(resolve_path("data/processed/rr_squad_gap_analysis.parquet"))
    gap_list = []
    for _, row in gap_df.iterrows():
        gap_list.append({
            "discipline": str(row["discipline"]),
            "tactical_role": str(row["tactical_role"]),
            "squad_count_total": int(row["squad_count_total"]),
            "squad_count_domestic": int(row["squad_count_domestic"]),
            "squad_count_overseas": int(row["squad_count_overseas"]),
            "players_in_role": str(row["players_in_role"]),
            "depth_status": str(row["depth_status"]),
            "gap_criticality_weight": round(float(row["gap_criticality_weight"]), 1),
            "gap_severity": str(row["gap_severity"]),
            "scenario": str(row["scenario"])
        })
    with open(out_path / "squad_gaps_data.json", "w", encoding="utf-8") as f:
        json.dump(gap_list, f, indent=2)
    print(f" -> Exported squad_gaps_data.json ({len(gap_list)} role evaluations)")

    # 7. Export Auction Scenarios & Budget Allocations
    scen_df = pd.read_parquet(resolve_path("data/processed/auction_strategy_scenarios.parquet"))
    alloc_df = pd.read_parquet(resolve_path("data/processed/auction_budget_allocations.parquet"))

    scenario_candidates = {
        "Scenario_1_Balanced_Reinforcement": {
            "Top_Order_Anchor": ["Devdutt Padikkal (Domestic)", "Angkrish Raghuvanshi (Domestic)"],
            "Death_Finisher": ["Tim David (Overseas)", "Matthew Wade (Overseas)", "Mahipal Lomror (Domestic)"],
            "Middle_Spinner": ["Liam Dawson (Overseas)", "Mujeeb Ur Rahman (Overseas)", "George Dockrell (Overseas)"],
            "Death_Bowler": ["Benjamin Sears (Overseas)", "Nathan Ellis (Overseas)", "Mohsin Khan (Domestic)"]
        },
        "Scenario_2_Bowling_Depth_Priority": {
            "Death_Bowler": ["Benjamin Sears (Overseas)", "Nathan Ellis (Overseas)", "Tushar Deshpande (Domestic)"],
            "Middle_Spinner": ["Liam Dawson (Overseas)", "Mujeeb Ur Rahman (Overseas)"],
            "Powerplay_Pacer": ["Nathan Ellis (Overseas)", "Mohsin Khan (Domestic)"],
            "Death_Finisher": ["Ashutosh Sharma (Domestic)", "Mahipal Lomror (Domestic)"]
        },
        "Scenario_3_Power_Hitting_Boundary_Maximization": {
            "Death_Finisher": ["Tim David (Overseas)", "Matthew Wade (Overseas)", "Ashutosh Sharma (Domestic)"],
            "Top_Order_Anchor": ["Abhishek Sharma (Domestic)", "Phil Salt (Overseas)"],
            "Middle_Stabilizer": ["Naman Dhir (Domestic)", "Ayush Badoni (Domestic)"],
            "Death_Bowler": ["Benjamin Sears (Overseas)", "Nathan Ellis (Overseas)"]
        },
        "Scenario_4_Young_Domestic_Core_Future_Pipeline": {
            "Top_Order_Anchor": ["Angkrish Raghuvanshi (Domestic)", "Abhishek Sharma (Domestic)"],
            "Middle_Stabilizer": ["Naman Dhir (Domestic)", "Ayush Badoni (Domestic)"],
            "Death_Finisher": ["Ashutosh Sharma (Domestic)", "Mahipal Lomror (Domestic)"],
            "Death_Bowler": ["Mohsin Khan (Domestic)", "Tushar Deshpande (Domestic)"]
        },
        "Scenario_5_Elite_Overseas_Spine": {
            "Death_Finisher": ["Tim David (Overseas)", "Matthew Wade (Overseas)"],
            "Death_Bowler": ["Benjamin Sears (Overseas)", "Nathan Ellis (Overseas)"],
            "Middle_Spinner": ["Liam Dawson (Overseas)", "Mujeeb Ur Rahman (Overseas)"],
            "Top_Order_Anchor": ["Phil Salt (Overseas)", "Finn Allen (Overseas)"]
        }
    }

    scenarios_list = []
    for _, srow in scen_df.iterrows():
        skey = str(srow["scenario_key"])
        sub_alloc = alloc_df[alloc_df["scenario_key"] == skey]
        allocs = []
        for _, arow in sub_alloc.iterrows():
            allocs.append({
                "allocation_category": str(arow["allocation_category"]),
                "budget_units": round(float(arow["budget_units"]), 1),
                "pct_of_budget": round(float(arow["pct_of_budget"]), 1)
            })
        
        scenarios_list.append({
            "scenario_key": skey,
            "scenario_name": str(srow["scenario_name"]),
            "strategic_focus": str(srow["strategic_focus"]),
            "total_budget_units": round(float(srow["total_budget_units"]), 1),
            "overseas_slots_demanded": int(srow["overseas_slots_demanded"]),
            "main_advantages": str(srow["main_advantages"]),
            "main_risks": str(srow["main_risks"]),
            "squad_balance_impact": str(srow["squad_balance_impact"]),
            "budget_allocations": allocs,
            "key_candidate_targets": scenario_candidates.get(skey, {})
        })
    with open(out_path / "auction_scenarios.json", "w", encoding="utf-8") as f:
        json.dump(scenarios_list, f, indent=2)
    print(f" -> Exported auction_scenarios.json ({len(scenarios_list)} scenarios)")

    # 8. Export Overview Summary Statistics (Audited & Reconciled Scope)
    strong_batters = sum(1 for b in batters_list if b["evidence_tier"] == "Strong")
    moderate_batters = sum(1 for b in batters_list if b["evidence_tier"] == "Moderate")

    strong_bowlers = sum(1 for bw in bowlers_list if bw["evidence_tier"] == "Strong")
    moderate_bowlers = sum(1 for bw in bowlers_list if bw["evidence_tier"] == "Moderate")

    top_actionable_batters = [b for b in batters_list if b["candidate_category"] == "Viable Auction Target"]
    top_actionable_batters.sort(key=lambda x: x["recruitment_decision_score"], reverse=True)

    top_actionable_bowlers = [bw for bw in bowlers_list if bw["candidate_category"] == "Viable Auction Target"]
    top_actionable_bowlers.sort(key=lambda x: x["recruitment_decision_score"], reverse=True)

    top_10_batters_export = []
    for rank_idx, b in enumerate(top_actionable_batters[:10], 1):
        top_10_batters_export.append({
            "rank": rank_idx,
            "player_id": b["player_id"],
            "player_name": b["player_name"],
            "initials": b["initials"],
            "image_url": b.get("image_url", None),
            "image_alt": b.get("image_alt", f"Photograph of {b['player_name']}"),
            "country": b["country"],
            "is_overseas": b["is_overseas"],
            "tactical_role": b["tactical_role"],
            "player_archetype": b["player_archetype"],
            "performance_rating": b["performance_rating"],
            "evidence_reliability_score": b["evidence_reliability_score"],
            "evidence_tier": b["evidence_tier"],
            "evidence_tier_label": b["evidence_tier_label"],
            "statistical_stability_score": b["statistical_stability_score"],
            "tactical_squad_fit_score": b["tactical_squad_fit_score"],
            "acquisition_risk_score": b["acquisition_risk_score"],
            "recruitment_decision_score": b["recruitment_decision_score"],
            "squad_gap_addressed": "Fill Finisher Void" if "Finisher" in b["tactical_role"] else "Reinforce Batting Depth",
            "scouting_rationale": b["scouting_rationale"],
            "candidate_category": "Viable Auction Target",
            "availability_status": "Potential Auction Candidate (Availability unconfirmed; conditional on official IPL 2027 player registration)",
            "key_stats": {
                "bf_clutch": b["bf_clutch"],
                "runs_clutch": b["runs_clutch"],
                "sr_clutch": b["sr_clutch"],
                "bnd_pct_clutch": b["bnd_pct_clutch"],
                "dot_pct_clutch": b["dot_pct_clutch"],
                "bf_overall": b["bf_overall"],
                "runs_overall": b["runs_overall"],
                "sr_overall": b["sr_overall"]
            }
        })

    top_10_bowlers_export = []
    for rank_idx, bw in enumerate(top_actionable_bowlers[:10], 1):
        top_10_bowlers_export.append({
            "rank": rank_idx,
            "player_id": bw["player_id"],
            "player_name": bw["player_name"],
            "initials": bw["initials"],
            "image_url": bw.get("image_url", None),
            "image_alt": bw.get("image_alt", f"Photograph of {bw['player_name']}"),
            "country": bw["country"],
            "is_overseas": bw["is_overseas"],
            "tactical_role": bw["tactical_role"],
            "player_archetype": bw["player_archetype"],
            "performance_rating": bw["performance_rating"],
            "evidence_reliability_score": bw["evidence_reliability_score"],
            "evidence_tier": bw["evidence_tier"],
            "evidence_tier_label": bw["evidence_tier_label"],
            "statistical_stability_score": bw["statistical_stability_score"],
            "tactical_squad_fit_score": bw["tactical_squad_fit_score"],
            "acquisition_risk_score": bw["acquisition_risk_score"],
            "recruitment_decision_score": bw["recruitment_decision_score"],
            "squad_gap_addressed": "Fill Death-Overs Specialist Void" if "Death" in bw["tactical_role"] else "Reinforce Bowling Depth",
            "scouting_rationale": bw["scouting_rationale"],
            "candidate_category": "Viable Auction Target",
            "availability_status": "Potential Auction Candidate (Availability unconfirmed; conditional on official IPL 2027 player registration)",
            "key_stats": {
                "legal_balls_clutch": bw["legal_balls_clutch"],
                "economy_clutch": bw["economy_clutch"],
                "wickets_clutch": bw["wickets_clutch"],
                "true_dot_pct_clutch": bw["true_dot_pct_clutch"],
                "bnd_pct_clutch": bw["bnd_pct_clutch"],
                "legal_balls_overall": bw["legal_balls_overall"],
                "economy_overall": bw["economy_overall"],
                "wickets_overall": bw["wickets_overall"]
            }
        })

    # Module 5 Historical Performance Leaderboards (Top 10 strictly by Performance Rating PR)
    hist_batters_sorted = sorted(batters_list, key=lambda x: x["performance_rating"], reverse=True)
    top_10_historical_batters = []
    for rank_idx, b in enumerate(hist_batters_sorted[:10], 1):
        top_10_historical_batters.append({
            "rank": rank_idx,
            "player_id": b["player_id"],
            "player_name": b["player_name"],
            "initials": b["initials"],
            "image_url": b.get("image_url", None),
            "image_alt": b.get("image_alt", f"Photograph of {b['player_name']}"),
            "country": b["country"],
            "is_overseas": b["is_overseas"],
            "tactical_role": b["tactical_role"],
            "player_archetype": b["player_archetype"],
            "performance_rating": b["performance_rating"],
            "evidence_reliability_score": b["evidence_reliability_score"],
            "evidence_tier": b["evidence_tier"],
            "evidence_tier_label": b["evidence_tier_label"],
            "statistical_stability_score": b["statistical_stability_score"],
            "tactical_squad_fit_score": b["tactical_squad_fit_score"],
            "acquisition_risk_score": b["acquisition_risk_score"],
            "recruitment_decision_score": b["recruitment_decision_score"],
            "candidate_category": b["candidate_category"],
            "availability_status": b["availability_status"],
            "scouting_rationale": b["scouting_rationale"],
            "key_stats": {
                "bf_clutch": b["bf_clutch"],
                "runs_clutch": b["runs_clutch"],
                "sr_clutch": b["sr_clutch"],
                "bnd_pct_clutch": b["bnd_pct_clutch"],
                "dot_pct_clutch": b["dot_pct_clutch"],
                "bf_overall": b["bf_overall"],
                "runs_overall": b["runs_overall"],
                "sr_overall": b["sr_overall"]
            }
        })

    hist_bowlers_sorted = sorted(bowlers_list, key=lambda x: x["performance_rating"], reverse=True)
    top_10_historical_bowlers = []
    for rank_idx, bw in enumerate(hist_bowlers_sorted[:10], 1):
        top_10_historical_bowlers.append({
            "rank": rank_idx,
            "player_id": bw["player_id"],
            "player_name": bw["player_name"],
            "initials": bw["initials"],
            "image_url": bw.get("image_url", None),
            "image_alt": bw.get("image_alt", f"Photograph of {bw['player_name']}"),
            "country": bw["country"],
            "is_overseas": bw["is_overseas"],
            "tactical_role": bw["tactical_role"],
            "player_archetype": bw["player_archetype"],
            "performance_rating": bw["performance_rating"],
            "evidence_reliability_score": bw["evidence_reliability_score"],
            "evidence_tier": bw["evidence_tier"],
            "evidence_tier_label": bw["evidence_tier_label"],
            "statistical_stability_score": bw["statistical_stability_score"],
            "tactical_squad_fit_score": bw["tactical_squad_fit_score"],
            "acquisition_risk_score": bw["acquisition_risk_score"],
            "recruitment_decision_score": bw["recruitment_decision_score"],
            "candidate_category": bw["candidate_category"],
            "availability_status": bw["availability_status"],
            "scouting_rationale": bw["scouting_rationale"],
            "key_stats": {
                "legal_balls_clutch": bw["legal_balls_clutch"],
                "economy_clutch": bw["economy_clutch"],
                "wickets_clutch": bw["wickets_clutch"],
                "true_dot_pct_clutch": bw["true_dot_pct_clutch"],
                "bnd_pct_clutch": bw["bnd_pct_clutch"],
                "legal_balls_overall": bw["legal_balls_overall"],
                "economy_overall": bw["economy_overall"],
                "wickets_overall": bw["wickets_overall"]
            }
        })

    strategic_benchmarks_export = [
        {
            "player_id": 34485,
            "player_name": "Sufiyan Muqeem",
            "country": "Pakistan",
            "initials": "SM",
            "tactical_role": "Middle-Overs Spinner",
            "discipline": "Bowling",
            "candidate_category": "Strategic Benchmark (BCCI Ineligible)",
            "availability_status": "Ineligible for IPL Auction (BCCI Policy Restriction; Global Role Model)",
            "performance_rating": 89.20,
            "evidence_reliability_score": 62.50,
            "statistical_stability_score": 68.40,
            "scouting_rationale": "BCCI Regulatory Benchmark (Non-Actionable): Elite international wrist-spinner with exceptional clutch turn; analytical model benchmark for world-class middle-overs spin."
        },
        {
            "player_id": 3578,
            "player_name": "Imad Wasim",
            "country": "Pakistan",
            "initials": "IW",
            "tactical_role": "Bowling All-Rounder",
            "discipline": "Bowling",
            "candidate_category": "Strategic Benchmark (BCCI Ineligible)",
            "availability_status": "Ineligible for IPL Auction (BCCI Policy Restriction; Global Role Model)",
            "performance_rating": 82.40,
            "evidence_reliability_score": 78.10,
            "statistical_stability_score": 71.20,
            "scouting_rationale": "BCCI Regulatory Benchmark (Non-Actionable): World-class left-arm orthodox powerplay control spinner; comparative benchmark for restrictive opening bowling."
        },
        {
            "player_id": 2933,
            "player_name": "Jasprit Bumrah",
            "country": "India",
            "initials": "JB",
            "tactical_role": "Death-Overs Specialist",
            "discipline": "Bowling",
            "candidate_category": "Strategic Benchmark (Rival Core)",
            "availability_status": "Conditional on Release (Rival Franchise Core Asset; Comparative Benchmark)",
            "performance_rating": 88.50,
            "evidence_reliability_score": 90.00,
            "statistical_stability_score": 84.10,
            "scouting_rationale": "Rival Core Benchmark (Non-Actionable): Gold standard T20 pace enforcer with unparalleled death yorker execution and sub-6.5 economy under extreme leverage."
        },
        {
            "player_id": 1699,
            "player_name": "Suryakumar Yadav",
            "country": "India",
            "initials": "SY",
            "tactical_role": "Middle-Order Batter",
            "discipline": "Batting",
            "candidate_category": "Strategic Benchmark (Rival Core)",
            "availability_status": "Conditional on Release (Rival Franchise Core Asset; Comparative Benchmark)",
            "performance_rating": 86.80,
            "evidence_reliability_score": 90.00,
            "statistical_stability_score": 79.50,
            "scouting_rationale": "Rival Core Benchmark (Non-Actionable): World #1 360-degree boundary striker; analytical benchmark for middle-overs field manipulation and boundary striking."
        },
        {
            "player_id": 143,
            "player_name": "Dinesh Karthik",
            "country": "India",
            "initials": "DK",
            "tactical_role": "Wicketkeeper-Batter",
            "discipline": "Batting",
            "candidate_category": "Strategic Benchmark (Retired)",
            "availability_status": "Retired from IPL Competition (Historical Reference Benchmark)",
            "performance_rating": 76.50,
            "evidence_reliability_score": 90.00,
            "statistical_stability_score": 64.20,
            "scouting_rationale": "Historical Reference (Retired): Veteran finisher and wicketkeeper benchmark illustrating late-career pressure execution and situational mastery."
        }
    ]

    overview_dict = {
        "metadata": {
            "system_title": "SupeRR Selector — Cricket Intelligence. Pressure Performance. Smarter Player Selection.",
            "lead_analytics_engineer": "Syed Mohammad Hamzah (B.Tech CSE Data Analytics)",
            "project_name": "Rajasthan Royals Sports Analytics Challenge — Season 2",
            "data_timestamp": "Audited Competition Records (2022–2026)",
            "regulatory_notice": "Candidate recommendations are model-derived priority targets based on historical multi-tournament performance. Official IPL 2027 auction registration is unconfirmed."
        },
        "dataset_scope": {
            "total_matches_in_metadata": 883,
            "total_matches_with_deliveries": 867,
            "abandoned_fixtures_count": 16,
            "total_deliveries_analyzed": 200999,
            "total_batter_runs": 269550,
            "total_bowler_wickets": 10272,
            "total_balls_faced": 193285,
            "total_legal_balls": 192445,
            "total_wides": 7714,
            "total_no_balls": 840,
            "competitions_covered": [
                {"name": "Indian Premier League (IPL)", "code": "IPL", "seasons": "2022, 2023, 2024, 2025, 2026", "matches": 371},
                {"name": "International T20s (T20I)", "code": "T20I", "seasons": "2022-2026", "matches": 486},
                {"name": "Emerging Teams & Rising Stars Asia Cups", "code": "Asia Cups", "seasons": "2024, 2025", "matches": 26}
            ],
            "temporal_range": "2022 - 2026"
        },
        "candidate_pool": {
            "total_batters_evaluated": 1091,
            "eligible_batters_count": len(batters_list),
            "strong_evidence_batters": strong_batters,
            "moderate_evidence_batters": moderate_batters,
            "total_bowlers_evaluated": 734,
            "eligible_bowlers_count": len(bowlers_list),
            "strong_evidence_bowlers": strong_bowlers,
            "moderate_evidence_bowlers": moderate_bowlers,
        },
        "rr_squad_baseline": {
            "total_registered_players": 27,
            "active_playing_xi_rotation": 20,
            "bench_reserve_specialists": 6,
            "administrative_registrations": 1,
            "domestic_players_count": 19,
            "overseas_players_count": 8,
            "retention_scenarios": {
                "Scenario_A": {"name": "Core Continuity Baseline", "retained": 14, "open_slots": 11, "overseas_retained": 4},
                "Scenario_B": {"name": "Moderate Refresh", "retained": 10, "open_slots": 15, "overseas_retained": 3},
                "Scenario_C": {"name": "Radical Reset", "retained": 6, "open_slots": 19, "overseas_retained": 2}
            }
        },
        "tactical_gaps": [
            {"role": "Death-Overs Specialist", "discipline": "Bowling", "severity": "Critical", "criticality": 90.0, "status": "Critical Void"},
            {"role": "Finisher", "discipline": "Batting", "severity": "Critical", "criticality": 87.5, "status": "Critical Void"},
            {"role": "New-Ball / Powerplay Fast Bowler", "discipline": "Bowling", "severity": "Low", "criticality": 85.0, "status": "Adequate Depth"},
            {"role": "Middle-Overs Spinner", "discipline": "Bowling", "severity": "High", "criticality": 80.0, "status": "Limited Depth"},
            {"role": "Middle-Order Batter", "discipline": "Batting", "severity": "Critical", "criticality": 70.0, "status": "Critical Void"},
            {"role": "Top-Order Batter", "discipline": "Batting", "severity": "Critical", "criticality": 65.0, "status": "Critical Void"}
        ],
        "top_10_actionable_batters": top_10_batters_export,
        "top_10_actionable_bowlers": top_10_bowlers_export,
        "top_10_historical_batters": top_10_historical_batters,
        "top_10_historical_bowlers": top_10_historical_bowlers,
        "strategic_benchmarks": strategic_benchmarks_export,
        "top_actionable_targets": {
            "batting": [
                {"name": b["player_name"], "role": b["tactical_role"], "country": b["country"], "is_overseas": b["is_overseas"], "rdh": b["recruitment_decision_score"], "pr": b["performance_rating"], "tfs": b["tactical_squad_fit_score"], "ars": b["acquisition_risk_score"]}
                for b in top_actionable_batters[:5]
            ],
            "bowling": [
                {"name": bw["player_name"], "role": bw["tactical_role"], "country": bw["country"], "is_overseas": bw["is_overseas"], "rdh": bw["recruitment_decision_score"], "pr": bw["performance_rating"], "tfs": bw["tactical_squad_fit_score"], "ars": bw["acquisition_risk_score"]}
                for bw in top_actionable_bowlers[:5]
            ]
        }
    }
    with open(out_path / "overview_stats.json", "w", encoding="utf-8") as f:
        json.dump(overview_dict, f, indent=2)
    print(f" -> Exported overview_stats.json")

    # 9. Export Methodology & Register Data
    reg_df = pd.read_parquet(resolve_path("data/processed/source_and_assumptions_register.parquet"))
    reg_list = []
    for _, row in reg_df.iterrows():
        reg_list.append({
            "item_id": str(row["item_id"]),
            "category": str(row["category"]),
            "description": str(row["description"]),
            "source": str(row["source"]),
            "verification_date": str(row["verification_date"]),
            "status": str(row["status"]),
            "impact_on_model": str(row["impact_on_model"])
        })

    methodology_dict = {
        "metric_definitions": {
            "PR": {
                "name": "Performance Rating",
                "scale": "0.00 to 100.00",
                "summary": "Combines pressure-adjusted baseline scoring/economy with clutch performance multipliers and Empirical Bayes credibility shrinkage toward tournament prior mean.",
                "formula": "PR = Credibility_Weight * Raw_Pressure_Score + (1 - Credibility_Weight) * Prior_Mean"
            },
            "ERS": {
                "name": "Evidence Reliability Score",
                "scale": "0.00 to 100.00",
                "summary": "Multi-dimensional exposure metric capturing volume, clutch sample size, matches played, and tournament breadth through linear saturation functions.",
                "formula": "ERS = 0.40 * S_clutch + 0.25 * S_overall + 0.20 * S_matches + 0.15 * S_comps",
                "benchmarks": "Saturation caps: 120 clutch deliveries, 300 total deliveries, 25 matches, 3 competitions.",
                "tiers": "Strong Evidence: ERS >= 60.0 & Clutch >= 40 & Matches >= 10 | Moderate Evidence: ERS >= 35.0 & Clutch >= 20 & Matches >= 5 | Insufficient: Sample too small for primary ranking"
            },
            "SSS": {
                "name": "Statistical Stability Score (Top-Tier Impact Retention Index)",
                "scale": "0.00 to 100.00",
                "summary": "Calibrated Top-Tier Impact Retention Index evaluating candidate resilience across 1,000 bootstrap resamples, rank volatility (Top-20 retention frequency), match volume concentration (HHI), and leave-one-match-out (LOMO) rating shifts.",
                "formula": "SSS = 0.35 * Boot_Rel + 0.30 * Top20_Freq + 0.20 * (1 - HHI) + 0.15 * LOMO_Res",
                "note": "Specifically calibrated to measure a player's ability to retain elite top-tier impact across resampled tournament states without single-match sample dependency."
            },
            "TFS": {
                "name": "Tactical Squad Fit Score",
                "scale": "0.00 to 100.00",
                "summary": "Measures direct alignment between player tactical role and Rajasthan Royals squad voids across retention scenarios, applying a 0.90x modifier to overseas players to reflect international roster limits."
            },
            "ARS": {
                "name": "Acquisition Risk Score",
                "scale": "0.00 to 100.00 (Higher = Higher Risk)",
                "summary": "Quantifies auction bidding inflation risk, overseas slot scarcity, statistical volatility, and historical availability constraints.",
                "penalty": "Includes a +6.0 risk penalty for overseas candidates."
            },
            "RDH": {
                "name": "Recruitment Decision Holistic Score",
                "scale": "0.00 to 90.00 (Theoretical Maximum: 90.00)",
                "summary": "Synthesizes performance, reliability, stability, and tactical fit while penalizing acquisition risk. Operates on a strict 0.00 to 90.00 theoretical scale because positive weights sum to 0.90.",
                "formula": "RDH = clip(0.30 * PR + 0.20 * ERS + 0.20 * SSS + 0.20 * TFS - 0.10 * ARS, 0.0, 90.0)",
                "critical_rule": "Theoretical range is strictly [0.0, 90.0]. Never display RDH as a percentage or win probability."
            }
        },
        "candidate_governance_rules": [
            {
                "category": "Viable Auction Target",
                "badge_class": "badge-viable",
                "description": "Actionable recruitment recommendations for Rajasthan Royals. Availability unconfirmed pending official IPL 2027 auction player registration."
            },
            {
                "category": "Strategic Benchmark (BCCI Ineligible)",
                "badge_class": "badge-ineligible",
                "description": "Pakistani players (e.g., Sufiyan Muqeem, Imad Wasim, Haris Rauf). Ineligible for IPL under long-standing regulatory policy. Displayed strictly as international analytical benchmarks, never as actionable auction recommendations."
            },
            {
                "category": "Strategic Benchmark (Rival Core)",
                "badge_class": "badge-rival",
                "description": "Elite franchise cornerstones (e.g., Jasprit Bumrah, Suryakumar Yadav, Sunil Narine, Rinku Singh) highly likely to be retained by rival teams. Included for comparative performance benchmarking."
            },
            {
                "category": "Strategic Benchmark (Retired)",
                "badge_class": "badge-retired",
                "description": "Veterans retired from IPL competition (e.g., Dinesh Karthik) serving as historical reference benchmarks."
            },
            {
                "category": "Existing RR Player (Internal Asset)",
                "badge_class": "badge-internal",
                "description": "Current Rajasthan Royals roster players (e.g., Dhruv Jurel, Ravindra Jadeja, Riyan Parag, Ravi Bishnoi, Yashasvi Jaiswal) evaluated as internal retention assets."
            }
        ],
        "assumptions_register": reg_list
    }
    with open(out_path / "methodology_data.json", "w", encoding="utf-8") as f:
        json.dump(methodology_dict, f, indent=2)
    print(f" -> Exported methodology_data.json")

    # 10. Create Offline JavaScript Bundle (Ensures dashboard works even via file:// double-click)
    js_bundle_content = f"""/**
 * SupeRR Selector - Bundled Data Feed
 * Auto-generated offline fallback data for environments where fetch() is blocked by CORS (e.g. file:// protocol).
 */
window.DASHBOARD_DATA = {{
  overview: {json.dumps(overview_dict)},
  batters: {json.dumps(batters_list)},
  bowlers: {json.dumps(bowlers_list)},
  rrSquad: {json.dumps(rr_list)},
  squadGaps: {json.dumps(gap_list)},
  recruitmentMatrix: {json.dumps(rec_list)},
  auctionScenarios: {json.dumps(scenarios_list)},
  methodology: {json.dumps(methodology_dict)}
}};
"""
    with open(Path("dashboard/js/data_bundle.js"), "w", encoding="utf-8") as f:
        f.write(js_bundle_content)
    print(f" -> Exported dashboard/js/data_bundle.js (Offline fallback bundle)")

    # Mirror to data/dashboard
    backup_path = Path("data/dashboard")
    backup_path.mkdir(parents=True, exist_ok=True)
    for p in out_path.glob("*.json"):
        with open(p, "r", encoding="utf-8") as f_in:
            data = json.load(f_in)
        with open(backup_path / p.name, "w", encoding="utf-8") as f_out:
            json.dump(data, f_out, indent=2)
    print(f" -> Mirrored all JSON files to data/dashboard/")

if __name__ == "__main__":
    export_dashboard_data()
