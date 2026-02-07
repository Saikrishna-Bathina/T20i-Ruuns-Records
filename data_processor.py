
import os
import urllib.request
import zipfile
import csv
import json
import datetime
from operator import itemgetter

DATA_URL = "https://cricsheet.org/downloads/t20s_male_csv2.zip"
ZIP_FILE = "t20s_male_csv2.zip"
EXTRACT_DIR = "t20i_data"
OUTPUT_FILE = "data.json"

def download_and_extract():
    if not os.path.exists(ZIP_FILE):
        print(f"Downloading {ZIP_FILE}...")
        try:
            import ssl
            ssl._create_default_https_context = ssl._create_unverified_context
            urllib.request.urlretrieve(DATA_URL, ZIP_FILE)
            print("Download complete.")
        except Exception as e:
            print(f"Error downloading: {e}")
            return False
    else:
        print(f"{ZIP_FILE} already exists.")

    if not os.path.exists(EXTRACT_DIR):
        print(f"Extracting to {EXTRACT_DIR}...")
        try:
            with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
                zip_ref.extractall(EXTRACT_DIR)
            print("Extraction complete.")
        except Exception as e:
            print(f"Error extracting: {e}")
            return False
    else:
        print(f"Data already extracted to {EXTRACT_DIR}.")
    return True

def parse_date(date_str):
    if not date_str:
        return datetime.datetime.min
    try:
        return datetime.datetime.strptime(date_str.replace('/', '-'), "%Y-%m-%d")
    except ValueError:
        return datetime.datetime.min

def get_match_outcomes(extract_dir):
    outcomes = {}
    # print("Reading match info files...")
    info_files = [f for f in os.listdir(extract_dir) if f.endswith('_info.csv')]
    
    for f_name in info_files:
        match_id = f_name.replace('_info.csv', '')
        path = os.path.join(extract_dir, f_name)
        result = "Normal"
        is_abandoned = False
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) >= 3 and parts[0] == 'info':
                        key = parts[1].lower()
                        val = parts[2].lower()
                        
                        if key == 'outcome' and val == 'no result':
                            result = "No Result"
                            is_abandoned = True
                        elif key == 'result' and val == 'no result':
                            result = "No Result"
                            is_abandoned = True
                        elif key == 'outcome' and val == 'tie':
                            result = "Tie"
        except Exception:
            pass
            
        outcomes[match_id] = result
        
    return outcomes

# --- NEW HELPERS ---

def get_phase(ball_val):
    over = int(ball_val)
    if over < 6:
        return "Powerplay"
    elif over < 15: # 6 to 14.99 (Overs 7-15)
        return "Middle"
    else: # 15+ (Overs 16-20)
        return "Death"
        
def load_match_info(extract_dir):
    info_map = {}
    for f_name in os.listdir(extract_dir):
        if f_name.endswith('_info.csv'):
            mid = f_name.replace('_info.csv', '')
            info_map[mid] = {}
            try:
                with open(os.path.join(extract_dir, f_name), 'r', encoding='utf-8') as f:
                    for line in f:
                        parts = line.strip().split(',')
                        if len(parts) >= 3 and parts[0] == 'info':
                            key = parts[1].lower()
                            val = ",".join(parts[2:]).replace('"', '')
                            info_map[mid][key] = val
            except: pass
    return info_map

class StatsContext:
    def __init__(self, name):
        self.name = name
        
        # --- BATTING STATS ---
        self.batsman_career_stats = {} 
        self.most_runs_list = []
        self.fastest_milestones = {1000: [], 2000: [], 3000: [], 4000: [], 5000: []}
        self.fastest_milestones_innings = {1000: [], 2000: [], 3000: [], 4000: [], 5000: []}
        self.highest_scores_list = []
        self.fastest_innings_milestones = {}
        self.innings_milestones = { "overall": {}, "team": {}, "vs": {} }
        self.most_runs_by_position = {} 
        
        # --- BOWLING STATS ---
        self.bowler_career_stats = {} 
        self.bowler_team_stats = {} 
        self.bowler_vs_stats = {} 
        self.bowler_team_vs_stats = {}
        self.best_figures_candidates = []
        self.fastest_wickets_overall = {}
        self.fastest_wickets_team = {}
        self.fastest_wickets_vs = {}
        self.fastest_wickets_team_vs = {}
        
        # --- PHASE STATS ---
        self.phase_stats = {
            "Powerplay": {"batsmen": {}, "bowlers": {}},
            "Middle": {"batsmen": {}, "bowlers": {}},
            "Death": {"batsmen": {}, "bowlers": {}}
        }
        self.final_phase_stats = {
                "team_innings_highs": {},
                "batsman_innings_highs": {},
                "bowler_innings_wickets": {},
                "batsman_runs": {},
                "bowler_wickets": {}
        }
        self.team_highs_candidates = { p: [] for p in ["Powerplay", "Middle", "Death"] }
        self.batsman_phase_highs_candidates = { p: [] for p in ["Powerplay", "Middle", "Death"] }
        self.bowler_phase_best_candidates = { p: [] for p in ["Powerplay", "Middle", "Death"] }
        
    def process_match(self, innings_stats, bowler_innings_stats, team_innings_stats, mid, match_date, info):
        # --- AGGREGATE BATTING ---
        for key, stats in innings_stats.items():
            name = stats["name"]
            team = stats["team"]
            runs = stats["runs"]
            balls = stats["balls"]
            is_out = stats["is_out"]
            pos = stats.get("position", 11)
            
            if name not in self.batsman_career_stats:
                self.batsman_career_stats[name] = {"runs": 0, "balls": 0, "innings": 0, "hs": 0, "hs_not_out": False, "100": 0, "50": 0, "4s": 0, "6s": 0, "team": team, "span_start": match_date, "span_end": match_date}
            
            p = self.batsman_career_stats[name]
            p["runs"] += runs
            p["balls"] += balls
            p["innings"] += 1
            if runs >= 100: p["100"] += 1
            elif runs >= 50: p["50"] += 1
            
            if runs > p["hs"]:
                p["hs"] = runs
                p["hs_not_out"] = (not is_out)
            elif runs == p["hs"] and not is_out:
                p["hs_not_out"] = True
                
            if match_date < p["span_start"]: p["span_start"] = match_date
            if match_date > p["span_end"]: p["span_end"] = match_date
            
            current_runs = p["runs"]
            current_innings = p["innings"]
            for m in [1000, 2000, 3000, 4000, 5000]:
                prev_runs = p["runs"] - runs
                if prev_runs < m and current_runs >= m:
                            if m not in self.fastest_milestones: self.fastest_milestones[m] = []
                            self.fastest_milestones[m].append({ "name": name, "team": team, "balls": p["balls"], "date": match_date, "innings": current_innings })
                            
                            if m not in self.fastest_milestones_innings: self.fastest_milestones_innings[m] = []
                            self.fastest_milestones_innings[m].append({ "name": name, "team": team, "innings": current_innings, "date": match_date })

            if runs >= 30: 
                    entry = {
                    "name": name, "team": team, "runs": runs, "balls": balls,
                    "4s": stats.get("4s", 0), "6s": stats.get("6s", 0),
                    "sr": round(runs * 100 / balls, 2) if balls > 0 else 0,
                    "date": match_date, "not_out": not is_out,
                    "opposition": stats["opposition"], "venue": stats.get("venue", ""), "position": pos
                    }
                    self.highest_scores_list.append(entry)
                    
                    if pos not in self.most_runs_by_position: self.most_runs_by_position[pos] = []
                    self.most_runs_by_position[pos].append(entry)

            for m_str, m_val in [("50", 50), ("100", 100), ("150", 150), ("200", 200)]:
                if runs >= m_val: self._check_innings_milestones(stats, match_date, m_str)

            if 'phases' in stats:
                    for phase, p_data in stats['phases'].items():
                        if p_data['runs'] > 0:
                            self.batsman_phase_highs_candidates[phase].append({
                                "name": name, "team": team, "opposition": stats["opposition"],
                                "runs": p_data['runs'], "balls": p_data['balls'], "date": match_date, "venue": stats.get("venue", "")
                            })

        # --- AGGREGATE BOWLING ---
        for key, stats in bowler_innings_stats.items():
            name = stats["name"]
            team = stats["team"]
            opp = stats["opposition"]
            wkt = stats["total_wickets"]
            runs = stats["total_runs"]
            balls = stats["total_balls"]
            
            if name not in self.bowler_career_stats:
                    self.bowler_career_stats[name] = {"wickets": 0, "runs": 0, "balls": 0, "innings": 0, "4w": 0, "5w": 0, "team": team, "span_start": match_date, "span_end": match_date}
            
            b = self.bowler_career_stats[name]
            b["wickets"] += wkt
            b["runs"] += runs
            b["balls"] += balls
            b["innings"] += 1
            if wkt == 4: b["4w"] += 1
            if wkt >= 5: b["5w"] += 1
            if match_date < b["span_start"]: b["span_start"] = match_date
            if match_date > b["span_end"]: b["span_end"] = match_date

            if wkt >= 3: 
                self.best_figures_candidates.append({
                    "name": name, "team": team, "opposition": opp,
                    "wickets": wkt, "runs": runs, "balls": balls,
                    "venue": stats.get("venue", ""), "date": match_date
                })

            start_w = b["wickets"] - wkt
            end_w = b["wickets"]
            for wm in [50, 100, 150, 200, 250, 300]:
                if start_w < wm and end_w >= wm:
                    if wm not in self.fastest_wickets_overall: self.fastest_wickets_overall[wm] = []
                    self.fastest_wickets_overall[wm].append({
                        "name": name, "team": team, "innings": b["innings"], "date": match_date
                    })
            
            self._update_bowler_sub_stats(self.bowler_team_stats, team, name, wkt, match_date, mid)
            self._update_bowler_sub_stats(self.bowler_vs_stats, opp, name, wkt, match_date, mid)
            
            if team not in self.bowler_team_vs_stats: self.bowler_team_vs_stats[team] = {}
            self._update_bowler_sub_stats(self.bowler_team_vs_stats[team], opp, name, wkt, match_date, mid)
            
            if 'phases' in stats:
                    for phase, p_data in stats['phases'].items():
                        if p_data['w'] > 0:
                            self.bowler_phase_best_candidates[phase].append({
                                "name": name, "team": team, "opposition": opp,
                                "value": p_data['w'], "runs": p_data['r'], "date": match_date, "venue": stats.get("venue", "")
                            })

        # --- TEAM HIGH SCORES ---
        for phase, p_data in team_innings_stats.items():
            if phase in ["Powerplay", "Middle", "Death"]:
                    if p_data['runs'] > 0:
                        self.team_highs_candidates[phase].append({
                            "team": p_data['team'], "opposition": p_data['opposition'],
                            "runs": p_data['runs'], "wickets": p_data['wickets'], "balls": p_data['balls'],
                            "date": match_date, "venue": team_innings_stats.get('venue', ''), "result": info.get('winner', '')
                        })

    def get_final_data(self):
        most_runs = []
        for name, s in self.batsman_career_stats.items():
            if s["runs"] > 50: 
                avg = s["runs"] / (s["innings"] - (1 if s["hs_not_out"] else 0)) if (s["innings"] - (1 if s["hs_not_out"] else 0)) > 0 else s["runs"]
                sr = s["runs"] * 100 / s["balls"] if s["balls"] > 0 else 0
                most_runs.append({
                    "name": name, "team": s["team"], "runs": s["runs"], "innings": s["innings"],
                    "hs": f"{s['hs']}*" if s["hs_not_out"] else f"{s['hs']}",
                    "avg": round(avg, 2), "sr": round(sr, 2), "100": s["100"], "50": s["50"],
                    "4s": s["4s"], "6s": s["6s"], "span": f"{s['span_start'][:4]}-{s['span_end'][:4]}"
                })
        most_runs.sort(key=lambda x: x["runs"], reverse=True)
        most_runs = most_runs[:200]

        self.highest_scores_list.sort(key=lambda x: x["runs"], reverse=True)
        highest_scores = self.highest_scores_list[:100]
        
        for m in self.fastest_milestones:
            self.fastest_milestones[m].sort(key=lambda x: x["balls"])
            self.fastest_milestones[m] = self.fastest_milestones[m][:50]
            self.fastest_milestones_innings[m].sort(key=lambda x: x["innings"])
            self.fastest_milestones_innings[m] = self.fastest_milestones_innings[m][:50]
            
        for m_key in self.innings_milestones["overall"]:
            self.innings_milestones["overall"][m_key]["fastest"].sort(key=lambda x: x["balls"])
            self.innings_milestones["overall"][m_key]["fastest"] = self.innings_milestones["overall"][m_key]["fastest"][:50]
            s_list = sorted(self.innings_milestones["overall"][m_key]["fastest"], key=lambda x: x["balls"], reverse=True)
            self.innings_milestones["overall"][m_key]["slowest"] = s_list[:50]

        most_wickets_overall = []
        for name, s in self.bowler_career_stats.items():
            if s["wickets"] > 5:
                most_wickets_overall.append({
                    "name": name, "team": s["team"], "wickets": s["wickets"], "innings": s["innings"],
                    "runs": s["runs"], "balls": s["balls"]
                })
        most_wickets_overall.sort(key=lambda x: x["wickets"], reverse=True)
        most_wickets_overall = most_wickets_overall[:200]

        self.best_figures_candidates.sort(key=lambda x: (x["wickets"], -x["runs"]), reverse=True)
        best_figs_4 = [x for x in self.best_figures_candidates if x["wickets"] == 4][:50]
        best_figs_5 = [x for x in self.best_figures_candidates if x["wickets"] >= 5][:50]

        for phase in ["Powerplay", "Middle", "Death"]:
            self.team_highs_candidates[phase].sort(key=lambda x: x["runs"], reverse=True)
            self.final_phase_stats["team_innings_highs"][phase] = self.team_highs_candidates[phase][:50]
            
            self.batsman_phase_highs_candidates[phase].sort(key=lambda x: x["runs"], reverse=True)
            self.final_phase_stats["batsman_innings_highs"][phase] = self.batsman_phase_highs_candidates[phase][:50]
            
            self.bowler_phase_best_candidates[phase].sort(key=lambda x: (x["value"], -x["runs"]), reverse=True)
            self.final_phase_stats["bowler_innings_wickets"][phase] = self.bowler_phase_best_candidates[phase][:50]

        # Prepare specific most_wickets dicts
        most_wickets_for_team = {}
        for team, players in self.bowler_team_stats.items():
            most_wickets_for_team[team] = sorted([
                {"name": n, "team": team, "wickets": s["wickets"], "innings": s["innings"], "runs": 0, "balls": 0} 
                for n, s in players.items() if s["wickets"] > 0
            ], key=lambda x: x["wickets"], reverse=True)[:50]

        most_wickets_vs_team = {}
        for team, players in self.bowler_vs_stats.items():
            most_wickets_vs_team[team] = sorted([
                 {"name": n, "team": team, "wickets": s["wickets"], "innings": s["innings"], "runs": 0, "balls": 0}
                 for n, s in players.items() if s["wickets"] > 0
            ], key=lambda x: x["wickets"], reverse=True)[:50]
            
        most_wickets_team_vs = {}
        for team, opps in self.bowler_team_vs_stats.items():
            most_wickets_team_vs[team] = {}
            for opp, players in opps.items():
                most_wickets_team_vs[team][opp] = sorted([
                    {"name": n, "team": team, "wickets": s["wickets"], "innings": s["innings"], "runs": 0, "balls": 0}
                    for n, s in players.items() if s["wickets"] > 0
                ], key=lambda x: x["wickets"], reverse=True)[:50]

        # Flatten innings_milestones for fastest_innings_milestones compatibility
        fastest_innings_milestones_flat = {}
        if "overall" in self.innings_milestones:
            for m_key, m_data in self.innings_milestones["overall"].items():
                if "fastest" in m_data:
                    fastest_innings_milestones_flat[m_key] = m_data["fastest"]

        return {
            "most_runs": most_runs,
            "most_runs_by_position": {k: v[:50] for k,v in self.most_runs_by_position.items()},
            "fastest_milestones": self.fastest_milestones,
            "fastest_milestones_innings": self.fastest_milestones_innings,
            "highest_scores": highest_scores,
            "innings_milestones": self.innings_milestones,
            "fastest_innings_milestones": fastest_innings_milestones_flat, # Added key
            "phase_stats": self.final_phase_stats,
            "fastest_wickets": {
                "overall": self.fastest_wickets_overall,
                "for_team": {k: {mk: mv[:20] for mk, mv in v.items()} for k,v in self.fastest_wickets_team.items()}, 
                "vs_team": {k: {mk: mv[:20] for mk, mv in v.items()} for k,v in self.fastest_wickets_vs.items()},
                "team_vs": {t: {o: {mk: mv[:20] for mk, mv in v.items()} for o,v in t_d.items()} for t,t_d in self.fastest_wickets_team_vs.items()}
            },
            "best_figures": { "4_wickets": best_figs_4, "5_wickets": best_figs_5 },
            "most_wickets": { 
                "overall": most_wickets_overall,
                "for_team": most_wickets_for_team,
                "vs_team": most_wickets_vs_team,
                "team_vs": most_wickets_team_vs
            }, 
            "most_hauls": {
                "4w": sorted([{"name": n, "team": s["team"], "4w": s["4w"], "innings": s["innings"]} for n,s in self.bowler_career_stats.items() if s["4w"] > 0], key=lambda x: x["4w"], reverse=True)[:50],
                "5w": sorted([{"name": n, "team": s["team"], "5w": s["5w"], "innings": s["innings"]} for n,s in self.bowler_career_stats.items() if s["5w"] > 0], key=lambda x: x["5w"], reverse=True)[:50]
            }
        }

    def _check_innings_milestones(self, stats, date, milestone_key):
            m_val = int(milestone_key)
            if m_val in stats.get('milestone_balls', {}):
                balls_faced = stats['milestone_balls'][m_val]
                if milestone_key not in self.innings_milestones["overall"]: self.innings_milestones["overall"][milestone_key] = {"fastest": [], "slowest": []}
                entry = { "name": stats["name"], "team": stats["team"], "opposition": stats["opposition"], "balls": balls_faced, "runs": stats["runs"], "date": date, "is_out": stats["is_out"] }
                self.innings_milestones["overall"][milestone_key]["fastest"].append(entry)
                
                t = stats["team"]
                if t not in self.innings_milestones["team"]: self.innings_milestones["team"][t] = {}
                if milestone_key not in self.innings_milestones["team"][t]: self.innings_milestones["team"][t][milestone_key] = {"fastest": [], "slowest": []}
                self.innings_milestones["team"][t][milestone_key]["fastest"].append(entry)
                
                o = stats["opposition"]
                if o not in self.innings_milestones["vs"]: self.innings_milestones["vs"][o] = {}
                if milestone_key not in self.innings_milestones["vs"][o]: self.innings_milestones["vs"][o][milestone_key] = {"fastest": [], "slowest": []}
                self.innings_milestones["vs"][o][milestone_key]["fastest"].append(entry)

    def _update_bowler_sub_stats(self, root_dict, key, name, wkt, date, mid):
        if key not in root_dict: root_dict[key] = {}
        p_dict = root_dict[key]
        if name not in p_dict: p_dict[name] = { "wickets": 0, "innings": 0, "milestones": {} }
        p = p_dict[name]
        p["innings"] += 1
        start_w = p["wickets"]
        p["wickets"] += wkt
        end_w = p["wickets"]
        for wm in [50, 100, 150, 200]:
            if start_w < wm and end_w >= wm:
                if wm not in p["milestones"]:
                    p["milestones"][wm] = { "innings": p["innings"], "date": date }

def process_data():
    if not os.path.exists(EXTRACT_DIR):
        print("Data directory not found.")
        return

    print(f"Scanning {EXTRACT_DIR} for CSVs...")
    all_files = [f for f in os.listdir(EXTRACT_DIR) if f.endswith('.csv') and not f.endswith('_info.csv')]
    
    if not all_files:
        print("No match CSV files found.")
        return
        
    print(f"Found {len(all_files)} match files. Loading data...")
    # Load match outcomes
    match_outcomes = get_match_outcomes(EXTRACT_DIR)
    match_info = load_match_info(EXTRACT_DIR)

    # Load data into memory
    data_rows = []
    
    for i, csv_file in enumerate(all_files):
        if i % 100 == 0:
            print(f"Processed {i}/{len(all_files)} files...", end='\r')
            
        file_path = os.path.join(EXTRACT_DIR, csv_file)
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data_rows.append(row)
    
    print(f"\nLoaded {len(data_rows)} rows. Sorting...")
    
    def sort_key(row):
        d = parse_date(row.get('start_date', ''))
        m = row.get('match_id', '')
        i = int(row.get('innings', 0)) if row.get('innings', '').isdigit() else 0
        b = float(row.get('ball', 0)) if row.get('ball', '').replace('.', '', 1).isdigit() else 0.0
        return (d, m, i, b)

    data_rows.sort(key=sort_key)
    
    print("Calculating stats...")

    # Init Contexts
    contexts = {
        'all': StatsContext('all'),
        'wc': StatsContext('wc')
    }

    
    VALID_WC_YEARS = ['2007', '2009', '2010', '2012', '2014', '2016', '2021', '2022', '2024']

    def is_world_cup(event_name):
        if not event_name: return False
        ev = event_name.lower()
        if "qualifier" in ev: return False
        return "world cup" in ev or "world t20" in ev or "world twenty20" in ev

    current_match_id = None
    innings_stats = {} 
    bowler_innings_stats = {} 
    team_innings_stats = { "Powerplay": {"runs":0, "wickets":0, "balls":0, "team": "", "opposition": ""}, 
                           "Middle": {"runs":0, "wickets":0, "balls":0, "team": "", "opposition": ""}, 
                           "Death": {"runs":0, "wickets":0, "balls":0, "team": "", "opposition": ""} }
    current_match_date = ""
    current_match_info = {}

    for row in data_rows:
        mid = row['match_id']
        match_date = row['start_date']
        
        if mid != current_match_id:
            if current_match_id is not None:
                active_contexts = [contexts['all']]
                event = current_match_info.get('event', '')
                
                # Check year first
                year = ""
                if current_match_date and len(current_match_date) >= 4:
                     year = current_match_date[:4]
                
                if is_world_cup(event) and year in VALID_WC_YEARS:
                    active_contexts.append(contexts['wc'])
                    wc_key = f"wc_{year}"
                    if wc_key not in contexts: contexts[wc_key] = StatsContext(wc_key)
                    active_contexts.append(contexts[wc_key])

                for ctx in active_contexts:
                    ctx.process_match(innings_stats, bowler_innings_stats, team_innings_stats, current_match_id, current_match_date, current_match_info)

            current_match_id = mid
            current_match_date = match_date
            current_match_info = match_info.get(mid, {})
            innings_stats = {}
            bowler_innings_stats = {}
            team_innings_stats = { "Powerplay": {"runs":0, "wickets":0, "balls":0, "team": "", "opposition": ""}, 
                                   "Middle": {"runs":0, "wickets":0, "balls":0, "team": "", "opposition": ""}, 
                                   "Death": {"runs":0, "wickets":0, "balls":0, "team": "", "opposition": ""} }

        innings = int(row['innings'])
        if innings > 2: continue 
        
        batting_team = row['batting_team']
        bowling_team = row['bowling_team']
        striker = row['striker']
        bowler = row['bowler']
        runs_off_bat = int(row['runs_off_bat'])
        extras = int(row['extras'])
        total_runs = runs_off_bat + extras
        ball = float(row['ball'])
        phase = get_phase(ball)
        
        if team_innings_stats[phase]["team"] == "":
            team_innings_stats[phase]["team"] = batting_team
            team_innings_stats[phase]["opposition"] = bowling_team
        
        if striker not in innings_stats:
            innings_stats[striker] = {
                "name": striker, "team": batting_team, "opposition": bowling_team,
                "runs": 0, "balls": 0, "4s": 0, "6s": 0, "is_out": False, 
                "phases": {"Powerplay": {"runs":0, "balls":0}, "Middle": {"runs":0, "balls":0}, "Death": {"runs":0, "balls":0}},
                "venue": current_match_info.get('venue', ''), "milestone_balls": {}
            }
        
        p_stats = innings_stats[striker]
        p_stats["runs"] += runs_off_bat
        is_wide = False
        try:
             if int(row.get('wides', 0)) > 0: is_wide = True
        except: pass
        
        if not is_wide:
            p_stats["balls"] += 1
            p_stats["phases"][phase]["balls"] += 1
            
        p_stats["phases"][phase]["runs"] += runs_off_bat
        if runs_off_bat == 4: p_stats["4s"] += 1
        if runs_off_bat == 6: p_stats["6s"] += 1
        
        if "position" not in p_stats:
             teammates_count = len([s for s in innings_stats.values() if s['team'] == batting_team and "position" in s])
             p_stats["position"] = teammates_count + 1

        curr_run = p_stats["runs"]
        if curr_run >= 50 and 50 not in p_stats["milestone_balls"]: p_stats["milestone_balls"][50] = p_stats["balls"]
        if curr_run >= 100 and 100 not in p_stats["milestone_balls"]: p_stats["milestone_balls"][100] = p_stats["balls"]
        if curr_run >= 150 and 150 not in p_stats["milestone_balls"]: p_stats["milestone_balls"][150] = p_stats["balls"]
        if curr_run >= 200 and 200 not in p_stats["milestone_balls"]: p_stats["milestone_balls"][200] = p_stats["balls"]

        if 'wicket_type' in row and row['wicket_type'] != "":
            player_out = row['player_dismissed']
            if player_out in innings_stats:
                innings_stats[player_out]["is_out"] = True
            
            wt = row['wicket_type']
            if wt not in ["run out", "hit ball twice", "obstructing the field", "retired hurt"]:
                 if bowler not in bowler_innings_stats:
                     bowler_innings_stats[bowler] = {
                         "name": bowler, "team": bowling_team, "opposition": batting_team,
                         "total_wickets": 0, "total_runs": 0, "total_balls": 0,
                         "phases": {"Powerplay": {"w":0, "r":0}, "Middle": {"w":0, "r":0}, "Death": {"w":0, "r":0}},
                         "venue": current_match_info.get('venue', '')
                     }
                 b_stats = bowler_innings_stats[bowler]
                 b_stats["total_wickets"] += 1
                 b_stats["phases"][phase]["w"] += 1
                 team_innings_stats[phase]["wickets"] += 1

        if bowler not in bowler_innings_stats:
             bowler_innings_stats[bowler] = {
                 "name": bowler, "team": bowling_team, "opposition": batting_team,
                 "total_wickets": 0, "total_runs": 0, "total_balls": 0,
                 "phases": {"Powerplay": {"w":0, "r":0}, "Middle": {"w":0, "r":0}, "Death": {"w":0, "r":0}},
                 "venue": current_match_info.get('venue', '')
             }
        
        b_estats = bowler_innings_stats[bowler]
        r_conceded = runs_off_bat
        try:
             w = int(row.get('wides', 0))
             nb = int(row.get('noballs', 0))
             r_conceded += (w + nb)
        except: pass
        b_estats["total_runs"] += r_conceded
        b_estats["phases"][phase]["r"] += r_conceded
        
        is_valid = True
        try:
            if int(row.get('wides', 0)) > 0 or int(row.get('noballs', 0)) > 0: is_valid = False
        except: pass
        if is_valid: b_estats["total_balls"] += 1
        
        team_innings_stats[phase]["runs"] += total_runs


    if current_match_id is not None:
        active_contexts = [contexts['all']]
        event = current_match_info.get('event', '')
        
        # Check year first
        year = ""
        if current_match_date and len(current_match_date) >= 4:
                year = current_match_date[:4]
        
        if is_world_cup(event) and year in VALID_WC_YEARS:
            active_contexts.append(contexts['wc'])
            wc_key = f"wc_{year}"
            if wc_key not in contexts: contexts[wc_key] = StatsContext(wc_key)
            active_contexts.append(contexts[wc_key])

        for ctx in active_contexts:
            ctx.process_match(innings_stats, bowler_innings_stats, team_innings_stats, current_match_id, current_match_date, current_match_info)

    print("Finalizing Data...")
    output_tree = { "tournaments": {} }
    output_tree.update(contexts['all'].get_final_data()) 
    for key, ctx in contexts.items():
        if key == 'all': continue
        output_tree["tournaments"][key] = ctx.get_final_data()

    print("Writing data.js...")
    with open("data.js", "w", encoding="utf-8") as f:
        f.write(f"const statsData = {json.dumps(output_tree, indent=4)};")
    print("Done!")

if __name__ == "__main__":
    download_and_extract()
    process_data()
