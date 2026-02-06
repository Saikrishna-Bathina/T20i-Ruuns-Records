import os

EXTRACT_DIR = "t20i_data"

def analyze_short_matches():
    csv_files = [f for f in os.listdir(EXTRACT_DIR) if f.endswith('.csv') and not f.endswith('_info.csv')]
    
    print(f"Scanning {len(csv_files)} matches...")
    
    for f_name in csv_files:
        match_id = f_name.replace('.csv', '')
        info_path = os.path.join(EXTRACT_DIR, f"{match_id}_info.csv")
        path = os.path.join(EXTRACT_DIR, f_name)
        
        # Count 1st inning balls roughly
        balls = 0
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('ball,1'):
                        balls += 1
                        if balls > 30: # Optimization: stop if > 30
                            break
        except:
            continue
            
        if balls <= 30:
            # Read info
            outcome_info = []
            try:
                with open(info_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('info,outcome') or line.startswith('info,result') or line.startswith('info,winner'):
                            outcome_info.append(line.strip())
            except:
                pass
            
            print(f"Match {match_id}: {balls} balls (1st inn). Info: {outcome_info}")

if __name__ == "__main__":
    analyze_short_matches()
