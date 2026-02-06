
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
        # Formats can vary: '2021-01-01' or '2021/01/01'
        return datetime.datetime.strptime(date_str.replace('/', '-'), "%Y-%m-%d")
    except ValueError:
        return datetime.datetime.min

def get_match_outcomes(extract_dir):
    outcomes = {}
    print("Reading match info files...")
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
                        # Check for outcome/result keys
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
                            
                        # Sometimes winner is missing in abandoned matches, 
                        # but we rely on explicit 'no result' key.
        except Exception:
            pass
            
        outcomes[match_id] = result
        
    return outcomes

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

    # Load data into memory
    data_rows = []
    
    # Headers expected in Cricsheet csv2:
    # match_id,season,start_date,venue,innings,ball,batting_team,bowling_team,striker,non_striker,bowler,runs_off_bat,extras,wides,noballs,byes,legbyes,penalty,wicket_type,player_dismissed,other_wicket_type,other_player_dismissed
    
    for i, csv_file in enumerate(all_files):
        if i % 100 == 0:
            print(f"Processed {i}/{len(all_files)} files...", end='\r')
            
        file_path = os.path.join(EXTRACT_DIR, csv_file)
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # The header is in every file. DictReader handles it.
            for row in reader:
                data_rows.append(row)
    
    print(f"\nLoaded {len(data_rows)} rows. Sorting...")
    
    # Sort by date, match_id, innings, ball
    # Helper for sorting
    def sort_key(row):
        d = parse_date(row.get('start_date', ''))
        m = row.get('match_id', '')
        i = int(row.get('innings', 0)) if row.get('innings', '').isdigit() else 0
        b = float(row.get('ball', 0)) if row.get('ball', '').replace('.', '', 1).isdigit() else 0.0
        return (d, m, i, b)

    data_rows.sort(key=sort_key)
    
    print("Calculating stats...")
    
    players = {} 
    # Structure: 
    # { 
    #   name: { 
    #       team: "India", 
    #       runs: 0, 
    #       balls: 0, 
    #       innings: 0,
    #       last_match: None,
    #       cum_runs: 0, 
    #       milestones_balls: {1000: balls_faced_at_crossing, ...},
    #       milestones_innings: {1000: innings_at_crossing, ...}
    #   } 
    # }

    milestones = [1000, 2000, 3000, 4000, 5000]
    innings_milestones = [50, 100, 150, 200]

    # Phase Definitions
    def get_phase(ball_val):
        over = int(ball_val)
        if over < 6:
            return "Powerplay"
        elif over < 16: # 6 to 15.99 (Overs 7-16)
            return "Middle"
        else: # 16+ (Overs 17-20)
            return "Death"

    phase_stats = {
        "Powerplay": {"batsmen": {}, "bowlers": {}},
        "Middle": {"batsmen": {}, "bowlers": {}},
        "Death": {"batsmen": {}, "bowlers": {}}
    }
    
    # helper to init phase player
    def init_phase_player(phase, role, name, team):
        if name not in phase_stats[phase][role]:
            phase_stats[phase][role][name] = {
                "name": name,
                "team": team,
                "value": 0, # Runs or Wickets
                "balls": 0
            }

    for row in data_rows:
        striker = row.get('striker')
        bowler = row.get('bowler')
        runs = int(row.get('runs_off_bat', 0))
        extras = int(row.get('extras', 0))
        wides = int(row.get('wides', 0)) if row.get('wides') else 0
        noballs = int(row.get('noballs', 0)) if row.get('noballs') else 0
        # For bowler runs conceded: runs_off_bat + wides + noballs. (Byes/Legbyes don't count to bowler)
        bowler_runs = runs + wides + noballs
        
        match_id = row.get('match_id')
        team = row.get('batting_team')
        # Bowling team is opposite
        bowling_team = row.get('bowling_team')
        
        ball_val = float(row.get('ball', 0)) if row.get('ball', '').replace('.', '', 1).isdigit() else 0.0
        phase = get_phase(ball_val)

        if striker not in players:
            players[striker] = {
                "name": striker,
                "team": team, 
                "runs": 0,
                "balls": 0,
                "innings": 0,
                "last_match": None,
                "milestone_balls": {},
                "milestone_innings": {}
            }
        
        # Check for new innings
        if players[striker]['last_match'] != match_id:
            players[striker]['innings'] += 1
            players[striker]['last_match'] = match_id

        # Update run count
        players[striker]['runs'] += runs
        
        # Update ball count: Ball is legal if wides == 0
        if wides == 0:
            players[striker]['balls'] += 1
            
        # --- PHASE STATS (CAREER) ---
        # 1. Batsman Runs
        init_phase_player(phase, "batsmen", striker, team)
        phase_stats[phase]["batsmen"][striker]["value"] += runs
        if wides == 0:
             phase_stats[phase]["batsmen"][striker]["balls"] += 1
             
        # 2. Bowler Wickets
        # Wicket logic: 'player_dismissed' exists and 'wicket_type' is not run out (usually).
        # But 'wicket_type' field is available in dict lookup.
        dismissal = row.get('wicket_type')
        if dismissal and dismissal not in ["run out", "retired hurt", "retired out", "obstructing the field", "timed out"]:
            # Credit to bowler
            init_phase_player(phase, "bowlers", bowler, bowling_team)
            phase_stats[phase]["bowlers"][bowler]["value"] += 1
            
        # Also limit bowler update to valid balls for ball count? Bowlers don't strictly need ball counts for "Most Wickets" but good for economy.
        # Let's just track wickets for now as requested. 

        # --- END PHASE STATS ---

        # Check Milestones
        current_runs = players[striker]['runs']
        current_balls = players[striker]['balls']
        current_innings = players[striker]['innings']
        
        # Team update (keep latest)
        players[striker]['team'] = team
        
        for m in milestones:
            if current_runs >= m:
                if m not in players[striker]['milestone_balls']:
                    players[striker]['milestone_balls'][m] = current_balls
                if m not in players[striker]['milestone_innings']:
                    players[striker]['milestone_innings'][m] = current_innings

    # 1.5 Calculate Highest Scores (Innings based) & Team Phase Highs
    # We need to re-iterate or process differently to get per-innings score. 
    # Since we sorted by match/date, we can track current innings stats.
    
    print("Calculating highest scores and team phase stats...")
    innings_stats = {} # Key: (match_id, striker) -> {runs, balls, team, date, is_out, position}
    
    # Team Phase Tracking
    # Key: (match_id, innings) -> { "Powerplay": runs, "Middle": runs, "Death": runs, "Team": team, "Date": date, "Opposition": ... }
    team_innings_stats = {} 
    
    # Bowler Innings Phase Tracking
    # Key: (match_id, bowler) -> { name, team, opposition, date, phases: {Powerplay: {w, r}, ...} }
    bowler_innings_stats = {}

    # Checkpoint variables for batting order tracking
    current_match_innings = None
    batters_seen = []
    
    # --- BOWLING STATS TRACKING ---
    # Global tracking for milestones (Fastest to 50, 100, etc.)
    # Structure: name -> {innings: X, wickets: Y, milestones: {50: {innings: I, date: D}, ...}}
    bowler_career_stats = {} 
    
    # Split by Team (Fastest for Team X)
    bowler_team_stats = {} # Team -> Bowler -> Stats
    
    # Split by Opposition (Fastest vs Team Y)
    bowler_vs_stats = {} # Opposition -> Bowler -> Stats
    
    # Best Figures Tracking
    # List of {name, team, opposition, wickets, runs, balls, date, venue}
    best_figures_candidates = []
    
    # Wicket Milestones to track
    wicket_milestones = [50, 100, 150, 200, 250, 300]
    
    def init_bowler_stats(stats_dict, name):
        if name not in stats_dict:
            stats_dict[name] = {
                "innings": 0,
                "wickets": 0,
                "milestones": {}
            }

    for row in data_rows:
        mid = row.get('match_id')
        striker = row.get('striker')
        bowler = row.get('bowler')
        non_striker = row.get('non_striker')
        runs = int(row.get('runs_off_bat', 0))
        extras = int(row.get('extras', 0)) # Team score includes extras
        wides = int(row.get('wides', 0)) if row.get('wides') else 0
        noballs = int(row.get('noballs', 0)) if row.get('noballs') else 0
        date = row.get('start_date')
        team = row.get('batting_team')
        opposition = row.get('bowling_team')
        player_dismissed = row.get('player_dismissed')
        wicket_type = row.get('wicket_type')
        ball_val = float(row.get('ball', 0)) if row.get('ball', '').replace('.', '', 1).isdigit() else 0.0
        
        innings_num = row.get('innings')
        mi_key = (mid, innings_num)
        
        if mi_key != current_match_innings:
            # End of previous innings - Process Bowler Innings for Best Figures & Increment Innings Count
            if current_match_innings:
                # We need to process the bowlers from the previous innings *before* moving on.
                # However, since we iterate row by row, 'bowler_innings_stats' populates gradually.
                # We can't know if an innings is truly done until the key changes.
                # But 'bowler_innings_stats' key is (match_id, bowler).
                # We can construct the set of bowlers for the current_match_innings and flush them.
                pass 
                
            current_match_innings = mi_key
            batters_seen = []
            
            # Note: We need a reliable way to update Bowler Career Innings count.
            # Best way: Track (Bowler, MatchID) pairs relative to career.
            # When we see a verified legal delivery or wicket for a bowler in a new match, we increment innings?
            # Or just increment stats at the end of the file processing? 
            # Current structure iterates rows. Let's update Career Stats incrementally but handle "Innings Count" carefuly.
            # Actually, easiest is: Keep a `bowler_last_match` map like for batters.
            
        # Helper to update career stats
        def update_bowler_career(b_name, b_team, b_opp, wkt, is_new_match):
            # Overall
            init_bowler_stats(bowler_career_stats, b_name)
            if is_new_match: bowler_career_stats[b_name]["innings"] += 1
            start_w = bowler_career_stats[b_name]["wickets"]
            bowler_career_stats[b_name]["wickets"] += wkt
            end_w = bowler_career_stats[b_name]["wickets"]
            
            # Check Milestones (Overall)
            for wm in wicket_milestones:
                if start_w < wm and end_w >= wm:
                    if wm not in bowler_career_stats[b_name]["milestones"]:
                        bowler_career_stats[b_name]["milestones"][wm] = {
                            "innings": bowler_career_stats[b_name]["innings"],
                            "date": date,
                            "team": b_team, # Current team
                            "match_id": mid
                        }

            # For Team
            if b_team not in bowler_team_stats: bowler_team_stats[b_team] = {}
            init_bowler_stats(bowler_team_stats[b_team], b_name)
            if is_new_match: bowler_team_stats[b_team][b_name]["innings"] += 1
            start_w_t = bowler_team_stats[b_team][b_name]["wickets"]
            bowler_team_stats[b_team][b_name]["wickets"] += wkt
            end_w_t = bowler_team_stats[b_team][b_name]["wickets"]
            
            # Check Milestones (For Team)
            for wm in wicket_milestones:
                if start_w_t < wm and end_w_t >= wm:
                    if wm not in bowler_team_stats[b_team][b_name]["milestones"]:
                        bowler_team_stats[b_team][b_name]["milestones"][wm] = {
                            "innings": bowler_team_stats[b_team][b_name]["innings"],
                            "date": date,
                            "match_id": mid
                        }

            # Vs Opposition
            if b_opp not in bowler_vs_stats: bowler_vs_stats[b_opp] = {}
            init_bowler_stats(bowler_vs_stats[b_opp], b_name)
            if is_new_match: bowler_vs_stats[b_opp][b_name]["innings"] += 1
            start_w_v = bowler_vs_stats[b_opp][b_name]["wickets"]
            bowler_vs_stats[b_opp][b_name]["wickets"] += wkt
            end_w_v = bowler_vs_stats[b_opp][b_name]["wickets"]
            
            # Check Milestones (Vs Opposition)
            for wm in wicket_milestones:
                if start_w_v < wm and end_w_v >= wm:
                    if wm not in bowler_vs_stats[b_opp][b_name]["milestones"]:
                        bowler_vs_stats[b_opp][b_name]["milestones"][wm] = {
                            "innings": bowler_vs_stats[b_opp][b_name]["innings"],
                            "date": date,
                            "match_id": mid
                        }
            
        # Init Team Innings Stat
        if mi_key not in team_innings_stats:
            team_innings_stats[mi_key] = {
                "team": team,
                "opposition": opposition,
                "date": date,
                "venue": row.get('venue'),
                "Powerplay": {"runs": 0, "wickets": 0, "balls": 0},
                "Middle": {"runs": 0, "wickets": 0, "balls": 0},
                "Death": {"runs": 0, "wickets": 0, "balls": 0}
            }
            
        # Update Team Phase Score
        phase = get_phase(ball_val)
        team_innings_stats[mi_key][phase]["runs"] += (runs + extras)
        if player_dismissed:
             team_innings_stats[mi_key][phase]["wickets"] += 1
        if wides == 0 and noballs == 0:
             team_innings_stats[mi_key][phase]["balls"] += 1
        
        # Add batters if seen for the first time in this innings
        if striker not in batters_seen:
            batters_seen.append(striker)
        if non_striker not in batters_seen:
            batters_seen.append(non_striker)
            
        # Helper to get position string
        def get_position_str(player, b_list):
            try:
                idx = b_list.index(player)
                if idx < 2:
                    return "Opener"
                else:
                    return str(idx + 1)
            except ValueError:
                return "N/A" # Should not happen

        key = (mid, striker)
        if key not in innings_stats:
            pos = get_position_str(striker, batters_seen)
            innings_stats[key] = {
                "name": striker,
                "team": team,
                "venue": row.get('venue'),
                "opposition": row.get('bowling_team'),
                "runs": 0,
                "balls": 0,
                "date": date,
                "is_out": False,
                "milestones": {},
                "position": pos,
                "phases": {"Powerplay": {"runs": 0, "balls": 0}, "Middle": {"runs": 0, "balls": 0}, "Death": {"runs": 0, "balls": 0}}
            }
            
        # Update Batsman Phase Stats
        innings_stats[key]['phases'][phase]["runs"] += runs
        if wides == 0:
             innings_stats[key]['phases'][phase]["balls"] += 1

        current_runs = innings_stats[key]['runs']
        innings_stats[key]['runs'] += runs
        if wides == 0:
            innings_stats[key]['balls'] += 1
            
        new_runs = innings_stats[key]['runs']
        current_balls = innings_stats[key]['balls']
        
        # Bowler Phase Stats
        b_key = (mid, bowler)
        is_new_bowler_innings = False
        
        if b_key not in bowler_innings_stats:
            is_new_bowler_innings = True
            bowler_innings_stats[b_key] = {
                "name": bowler,
                "team": opposition, # Bowler belongs to bowling team
                "opposition": team,    # Bowling AGAINST batting team
                "date": date,
                "venue": row.get('venue'),
                "phases": {
                    "Powerplay": {"w": 0, "r": 0},
                    "Middle": {"w": 0, "r": 0},
                    "Death": {"w": 0, "r": 0}
                },
                "total_wickets": 0,
                "total_runs": 0,
                "total_balls": 0
            }
            
        # Update Bowler Phase Stats
        run_conceded = (runs + wides + noballs)
        bowler_innings_stats[b_key]["phases"][phase]["r"] += run_conceded
        
        # Total Stats for Best Figures
        bowler_innings_stats[b_key]["total_runs"] += run_conceded
        if wides == 0 and noballs == 0:
             bowler_innings_stats[b_key]["total_balls"] += 1
        
        # Wicket Check
        is_wicket = 0
        dismissal = row.get('wicket_type')
        if player_dismissed and dismissal not in ["run out", "retired hurt", "retired out", "obstructing the field", "timed out"]:
            bowler_innings_stats[b_key]["phases"][phase]["w"] += 1
            bowler_innings_stats[b_key]["total_wickets"] += 1
            is_wicket = 1
            
        # Update Career Stats
        update_bowler_career(bowler, opposition, team, is_wicket, is_new_bowler_innings)



        
        for m in innings_milestones:
            if current_runs < m and new_runs >= m:
                # Record the ball count when they reached the milestone
                if m not in innings_stats[key]['milestones']:
                     innings_stats[key]['milestones'][m] = current_balls
        if player_dismissed and player_dismissed == striker:
            innings_stats[key]['is_out'] = True

    
    # --- POST PROCESSING ADVANCED BOWLING STATS ---
    print("Processing advanced bowling stats...")
    
    # 1. Best Bowling Figures
    best_figures_4 = []
    best_figures_5 = []
    
    for b_key, stats in bowler_innings_stats.items():
        wkts = stats["total_wickets"]
        if wkts >= 4:
            entry = {
                "name": stats["name"],
                "team": stats["team"],
                "opposition": stats["opposition"],
                "venue": stats["venue"],
                "date": stats["date"],
                "wickets": wkts,
                "runs": stats["total_runs"],
                "balls": stats["total_balls"]
            }
            if wkts >= 5:
                best_figures_5.append(entry)
            # Add to 4-fer list as well? Usually distinct lists. 
            # Request says "Fastest 5-wicket and 4-wickets". 
            # Let's keep them as separate lists containing exactly that count or more.
            # Actually, a 5-for is also a 4-for technically, but usually lists are exclusive or threshold based.
            # Let's add to both if 5+, effectively "4+ Wickets" list and "5+ Wickets" list.
            best_figures_4.append(entry)
            
    # Sort Best Figures: Wickets DESC, Balls ASC, Runs ASC, Date DESC
    def figures_sort_key(x):
        return (-x["wickets"], x["balls"], x["runs"], parse_date(x["date"])) # Date desc? No, usually earlier record holds precedence if tied? Or recent?
        # User said: "Fewest Balls -> Fewest Runs -> Date (Most Recent)"
        # Implicitly Wickets is primary.
        # So: (-wickets, balls, runs, -timestamp)
    
    best_figures_4.sort(key=lambda x: (-x["wickets"], x["balls"], x["runs"], -parse_date(x["date"]).timestamp()))
    best_figures_5.sort(key=lambda x: (-x["wickets"], x["balls"], x["runs"], -parse_date(x["date"]).timestamp()))

    # 2. Fastest to Wickets (Formatting)
    # Helper to format milestone list
    def format_milestone_list(stats_dict):
        # Result: { 50: [ {name, innings, date, ...}, ... ], 100: ... }
        # Or for Team/Vs: { "India": { 50: [...] } }
        
        # We need a generic way to extract.
        # stats_dict map: Key (Name) -> {milestones: {50: ...}}
        
        # Output format for "Overall": {50: [...sorted...], 100: ...}
        output = {}
        for m in wicket_milestones:
            output[m] = []
            
        for name, data in stats_dict.items():
            for m, m_data in data["milestones"].items():
                if m in output:
                    output[m].append({
                        "name": name,
                        "innings": m_data["innings"],
                        "date": m_data["date"],
                        "match_id": m_data.get("match_id"),
                        "team": m_data.get("team", data.get("team", "")) # Fallback if team not in milestone
                    })
                    
        # Sort each milestone list by Innings (ASC), then Date (ASC)
        for m in output:
            output[m].sort(key=lambda x: (x["innings"], parse_date(x["date"]).timestamp()))
            
        return output

    fastest_wickets_overall = format_milestone_list(bowler_career_stats)
    
    # For Team (Dict of Dicts)
    fastest_wickets_team = {}
    for team, b_stats in bowler_team_stats.items():
        fastest_wickets_team[team] = format_milestone_list(b_stats)

    # Vs Opposition (Dict of Dicts)
    fastest_wickets_vs = {}
    for opp, b_stats in bowler_vs_stats.items():
        fastest_wickets_vs[opp] = format_milestone_list(b_stats)


    # 3. Most Wickets & Haul Counts (New Requirement)
    # Re-process bowler_innings_stats to aggregate these since career stats didn't track hauls fully matched to innings counts logic (though it could have).
    # We want Lists for:
    # - Most Wickets (Overall, For Team, Vs Opp)
    # - Most 4w Hauls, Most 5w Hauls
    
    # helper for aggregation
    def aggregate_bowling_records(group_key_func):
        # group_key_func(stats) -> returns key to group by (e.g. "BowlerName" or "Bowler+Team")
        # We need to accumulate: Wickets, Runs, Balls, Innings, 4w, 5w
        
        agg = {}
        for b_key, stats in bowler_innings_stats.items():
            # b_key = (match_id, bowler_name)
            # stats has: name, team, opposition, total_wickets, total_runs, total_balls
            
            group_keys = group_key_func(stats) 
            if not isinstance(group_keys, list):
                group_keys = [group_keys]
                
            for k in group_keys:
                if not k: continue
                if k not in agg:
                    agg[k] = {
                        "name": stats["name"],
                        "team": stats["team"], # Might be ambiguous if aggregated across teams
                        "wickets": 0,
                        "runs": 0,
                        "balls": 0,
                        "innings": 0,
                        "4w": 0,
                        "5w": 0,
                        "span_start": stats["date"],
                        "span_end": stats["date"]
                    }
                
                rec = agg[k]
                rec["wickets"] += stats["total_wickets"]
                rec["runs"] += stats["total_runs"]
                rec["balls"] += stats["total_balls"]
                rec["innings"] += 1
                if stats["total_wickets"] >= 4:
                    rec["4w"] += 1
                if stats["total_wickets"] >= 5:
                    rec["5w"] += 1
                    
                # Update Span (basic lex compare works for ISO dates yyyy-mm-dd)
                if stats["date"] < rec["span_start"]: rec["span_start"] = stats["date"]
                if stats["date"] > rec["span_end"]: rec["span_end"] = stats["date"]
                
        return agg

    # Overall
    most_wickets_overall_dict = aggregate_bowling_records(lambda x: x["name"])
    most_wickets_overall = list(most_wickets_overall_dict.values())
    most_wickets_overall.sort(key=lambda x: x["wickets"], reverse=True)
    
    # For Team
    most_wickets_team_dict = {} # Key: TeamName -> List of Players
    # We aggregate by (Team, Name) to separate stats if players played for multiple teams
    agg_team = aggregate_bowling_records(lambda x: (x["team"], x["name"]))
    
    # Convert to nested structure: { "India": [Player1, Player2...] }
    temp_team_lists = {}
    for k, rec in agg_team.items():
        team_name, p_name = k
        if team_name not in temp_team_lists: temp_team_lists[team_name] = []
        temp_team_lists[team_name].append(rec)
        
    for t in temp_team_lists:
        temp_team_lists[t].sort(key=lambda x: x["wickets"], reverse=True)
    most_wickets_team = temp_team_lists

    # Vs Opposition
    most_wickets_vs_dict = {}
    agg_vs = aggregate_bowling_records(lambda x: (x["opposition"], x["name"]))
    
    temp_vs_lists = {}
    for k, rec in agg_vs.items():
        opp_name, p_name = k
        if opp_name not in temp_vs_lists: temp_vs_lists[opp_name] = []
        # For Vs lists, "team" field is player's team. If mixed, use last or list? 
        # Usually displayed as "Player (Country)".
        temp_vs_lists[opp_name].append(rec)

    for t in temp_vs_lists:
        temp_vs_lists[t].sort(key=lambda x: x["wickets"], reverse=True)
    most_wickets_vs = temp_vs_lists
    
    # Most 4w/5w Hauls (Overall List)
    # Simply sort the overall list by hauls
    most_4w_hauls = sorted([p for p in most_wickets_overall if p["4w"] > 0], key=lambda x: x["4w"], reverse=True)
    most_5w_hauls = sorted([p for p in most_wickets_overall if p["5w"] > 0], key=lambda x: x["5w"], reverse=True)


    
    print("Formatting output...")
    # Prepare Data JSON
    output_data = {
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d"),
        "players": players,
        "innings_stats": [v for k, v in innings_stats.items()], # Convert dict to list
        "team_innings_stats": [v for k, v in team_innings_stats.items()],
        "phase_stats": phase_stats,
        
        # New Stats
        "fastest_wickets": {
            "overall": fastest_wickets_overall,
            "for_team": fastest_wickets_team,
            "vs_team": fastest_wickets_vs
        },
        "best_figures": {
            "4_wickets": best_figures_4,
            "5_wickets": best_figures_5
        }
    }    
    # NEW: Calculate Most Runs by Position
    # Key: Position -> { PlayerName -> {runs, balls, innings} }
    position_stats = {} 
    
    for key, stats in innings_stats.items():
        pos = stats['position']
        name = stats['name']
        team = stats['team']
        runs = stats['runs']
        balls = stats['balls']
        
        if pos not in position_stats:
            position_stats[pos] = {}
        
        if name not in position_stats[pos]:
            position_stats[pos][name] = {
                "name": name,
                "team": team,
                "runs": 0,
                "balls": 0,
                "innings": 0
            }
            
        position_stats[pos][name]['runs'] += runs
        position_stats[pos][name]['balls'] += balls
        position_stats[pos][name]['innings'] += 1

    # Convert to list and sort
    most_runs_by_position = {}
    for pos, players_dict in position_stats.items():
        p_list = list(players_dict.values())
        p_list.sort(key=lambda x: x['runs'], reverse=True)
        most_runs_by_position[pos] = p_list[:50] # Top 50 per position


    # 1. Most Runs
    # Convert dict to list
    all_players = list(players.values())
    all_players.sort(key=lambda x: x['runs'], reverse=True)
    
    most_runs_list = []
    for p in all_players[:50]: # Top 50
        most_runs_list.append({
            "name": p['name'],
            "team": p['team'],
            "runs": p['runs'],
            "balls": p['balls'],
            "innings": p['innings']
        })
        
    # 2. Fastest to Milestones (Balls)
    fastest_milestones = {}
    
    for m in milestones:
        # Filter players who reached this milestone
        reached = [p for p in all_players if m in p['milestone_balls']]
        # Sort by balls taken to reach it
        reached.sort(key=lambda x: x['milestone_balls'][m])
        
        milestone_data = []
        for p in reached:
            milestone_data.append({
                "name": p['name'],
                "team": p['team'],
                "balls": p['milestone_balls'][m]
            })
        fastest_milestones[str(m)] = milestone_data

    # 2.5 Fastest to Milestones (Innings)
    fastest_milestones_innings = {}

    for m in milestones:
        # Filter players who reached this milestone
        reached = [p for p in all_players if m in p['milestone_innings']]
        # Sort by innings taken to reach it
        reached.sort(key=lambda x: x['milestone_innings'][m])
        
        milestone_data = []
        for p in reached:
            milestone_data.append({
                "name": p['name'],
                "team": p['team'],
                "innings": p['milestone_innings'][m]
            })
        fastest_milestones_innings[str(m)] = milestone_data

    # 3. Highest Scores
    all_innings = list(innings_stats.values())
    all_innings.sort(key=lambda x: x['runs'], reverse=True)
    highest_scores_list = all_innings[:10] # Top 10

    # 4. Fastest Innings Milestones
    fastest_innings_milestones = {}
    
    for m in innings_milestones:
        # Filter innings that reached this milestone
        reached = [inn for inn in all_innings if m in inn['milestones']]
        # Sort by balls taken to reach it
        reached.sort(key=lambda x: x['milestones'][m])
        
        milestone_data = []
        for inn in reached:
            milestone_data.append({
                "name": inn['name'],
                "team": inn['team'],
                "minq": inn['opposition'],
                "venue": inn['venue'],
                "balls": inn['milestones'][m],
                "date": inn['date'],
                "runs": inn['runs'], # Final score
                "position": inn['position']
            })
        fastest_innings_milestones[str(m)] = milestone_data

    # --- PROCESS PHASE STATS ---
    print("Processing phase stats...")
    
    final_phase_stats = {
        "batsman_runs": {},
        "bowler_wickets": {},
        "team_innings_highs": {},
        "batsman_innings_highs": {},
        "bowler_innings_wickets": {}
    }
    
    phases = ["Powerplay", "Middle", "Death"]
    
    # 1. Career Stats (Batsman Runs & Bowler Wickets)
    for phase in phases:
        # Batsmen
        p_batsmen = list(phase_stats[phase]["batsmen"].values())
        p_batsmen.sort(key=lambda x: x['value'], reverse=True)
        final_phase_stats["batsman_runs"][phase] = p_batsmen[:50]
        
        # Bowlers
        p_bowlers = list(phase_stats[phase]["bowlers"].values())
        p_bowlers.sort(key=lambda x: x['value'], reverse=True)
        final_phase_stats["bowler_wickets"][phase] = p_bowlers[:50]
        
    # 2. Team Innings Highs
    team_highs = { p: [] for p in phases }
    
    for key, stats in team_innings_stats.items():
        for phase in phases:
            if stats[phase]['runs'] > 0:
                team_highs[phase].append({
                    "team": stats['team'],
                    "opposition": stats['opposition'],
                    "runs": stats[phase]['runs'],
                    "wickets": stats[phase]['wickets'],
                    "date": stats['date'],
                    "venue": stats.get('venue', 'N/A'),
                    "balls": stats[phase]['balls'],
                    "result": match_outcomes.get(str(key[0]), "Normal")
                })
                
    for phase in phases:
        team_highs[phase].sort(key=lambda x: x['runs'], reverse=True)
        # Export ALL records for Team Highs to allow "Lowest Score" analysis
        final_phase_stats["team_innings_highs"][phase] = team_highs[phase]

    # 3. Batsman Innings Phase Highs
    batsman_phase_highs = { p: [] for p in phases }
    
    for key, stats in innings_stats.items():
        # key is (match_id, striker)
        if 'phases' in stats:
            for phase in phases:
                p_run = stats['phases'][phase]['runs']
                p_ball = stats['phases'][phase]['balls']
                if p_run > 0:
                     batsman_phase_highs[phase].append({
                         "name": stats['name'],
                         "team": stats['team'],
                         "opposition": stats['opposition'],
                         "runs": p_run,
                         "balls": p_ball,
                         "date": stats['date'],
                         "venue": stats.get('venue', 'N/A')
                     })

    for phase in phases:
        batsman_phase_highs[phase].sort(key=lambda x: x['runs'], reverse=True)
        final_phase_stats["batsman_innings_highs"][phase] = batsman_phase_highs[phase][:2000]

    # 4. Bowler Innings Phase Best
    bowler_phase_best = { p: [] for p in phases }
    
    for key, stats in bowler_innings_stats.items():
        for phase in phases:
             p_w = stats['phases'][phase]['w']
             p_r = stats['phases'][phase]['r']
             # Include if taken wickets OR just high usage? User asked for "Highest Score" list against them, 
             # but typically "Best Bowling" is Wickets. "Highest Score against bowler" would be Runs Conceded.
             # Let's provide BOTH if possible or just Wickets for "Best".
             # User Request: "highest phase score list by a batsmen ,bowler" -> Ambiguous.
             # "Highest score list by a bowler" -> Likely Best Bowling (Wickets).
             # If "Score against a bowler", that's "Worst Bowling".
             # I will stick to "Best Bowling (Wickets)" for now as it's a positive stat. 
             # I'll sort by Wickets DESC, then Runs Conceded ASC.
             if p_w > 0:
                 bowler_phase_best[phase].append({
                     "name": stats['name'],
                     "team": stats['team'],
                     "opposition": stats['opposition'],
                     "value": p_w, # Wickets
                     "runs": p_r,
                     "date": stats['date'],
                     "venue": stats.get('venue', 'N/A')
                 })
                 
    for phase in phases:
        # Sort by Wickets Desc, then Runs Asc
        bowler_phase_best[phase].sort(key=lambda x: (x['value'], -x['runs']), reverse=True) 
        # Wait, if x['runs'] is secondary sort (asc), negation works for simple scalar if main is reverse?
        # Sort key tuple: (Wickets DESC, Runs ASC)
        # Python sort reverse=True: (High Wickets, High Runs). We want (High Wickets, Low Runs).
        # So we want key (Wickets, -Runs).
        # Example: 3w 10r -> (3, -10). 3w 20r -> (3, -20). 
        # -10 > -20. So 3w 10r comes first. Correct.
        bowler_phase_best[phase].sort(key=lambda x: (x['value'], -x['runs']), reverse=True)
        final_phase_stats["bowler_innings_wickets"][phase] = bowler_phase_best[phase][:2000]


    final_data = {
        "most_runs": most_runs_list,
        "most_runs_by_position": most_runs_by_position,
        "fastest_milestones": fastest_milestones,
        "fastest_milestones_innings": fastest_milestones_innings,
        "highest_scores": highest_scores_list,
        "fastest_innings_milestones": fastest_innings_milestones,
        "phase_stats": final_phase_stats,
        
        # New Bowling Stats
        "fastest_wickets": {
            "overall": fastest_wickets_overall,
            "for_team": fastest_wickets_team,
            "vs_team": fastest_wickets_vs
        },
        "best_figures": {
            "4_wickets": best_figures_4,
            "5_wickets": best_figures_5
        },
        "most_wickets": {
             "overall": most_wickets_overall,
             "for_team": most_wickets_team,
             "vs_team": most_wickets_vs
        },
        "most_hauls": {
             "4w": most_4w_hauls,
             "5w": most_5w_hauls
        }
    }
    
    OUTPUT_FILE = "data.js"
    print(f"Writing to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        f.write("const t20Data = ")
        json.dump(final_data, f, indent=2)
        f.write(";")
    print("Success.")

if __name__ == "__main__":
    if download_and_extract():
        process_data()
