
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

    for row in data_rows:
        striker = row.get('striker')
        runs = int(row.get('runs_off_bat', 0))
        wides = int(row.get('wides', 0)) if row.get('wides') else 0
        match_id = row.get('match_id')
        team = row.get('batting_team')

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
        # Note: A player plays an innings if they face a ball OR are at the crease.
        # But simply appearing in the ball-by-ball data means they played.
        # We check if match_id is different from last_match
        if players[striker]['last_match'] != match_id:
            players[striker]['innings'] += 1
            players[striker]['last_match'] = match_id

        # Update run count
        players[striker]['runs'] += runs
        
        # Update ball count: Ball is legal if wides == 0
        if wides == 0:
            players[striker]['balls'] += 1
            
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

    # 1.5 Calculate Highest Scores (Innings based)
    # We need to re-iterate or process differently to get per-innings score. 
    # Since we sorted by match/date, we can track current innings stats.
    
    print("Calculating highest scores...")
    innings_stats = {} # Key: (match_id, striker) -> {runs, balls, team, date, is_out}
    
    for row in data_rows:
        mid = row.get('match_id')
        striker = row.get('striker')
        runs = int(row.get('runs_off_bat', 0))
        wides = int(row.get('wides', 0)) if row.get('wides') else 0
        date = row.get('start_date')
        team = row.get('batting_team')
        player_dismissed = row.get('player_dismissed')
        
        key = (mid, striker)
        if key not in innings_stats:
            innings_stats[key] = {
                "name": striker,
                "team": team,
                "runs": 0,
                "balls": 0,
                "date": date,
                "is_out": False,
                "milestones": {}
            }
            
        current_runs = innings_stats[key]['runs']
        innings_stats[key]['runs'] += runs
        if wides == 0:
            innings_stats[key]['balls'] += 1
            
        new_runs = innings_stats[key]['runs']
        current_balls = innings_stats[key]['balls']
        
        for m in innings_milestones:
            if current_runs < m and new_runs >= m:
                # Record the ball count when they reached the milestone
                if m not in innings_stats[key]['milestones']:
                     innings_stats[key]['milestones'][m] = current_balls

        if player_dismissed and player_dismissed == striker:
            innings_stats[key]['is_out'] = True

    
    print("Formatting output...")
    
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
                "balls": inn['milestones'][m],
                "date": inn['date'],
                "runs": inn['runs'] # Final score
            })
        fastest_innings_milestones[str(m)] = milestone_data

    final_data = {
        "most_runs": most_runs_list,
        "fastest_milestones": fastest_milestones,
        "fastest_milestones_innings": fastest_milestones_innings,
        "highest_scores": highest_scores_list,
        "fastest_innings_milestones": fastest_innings_milestones
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
