
import json

try:
    with open("data.js", "r", encoding="utf-8") as f:
        content = f.read()
        json_str = content.replace("const statsData = ", "").replace(";", "")
        data = json.loads(json_str)
        
        if "tournaments" in data and "wc" in data["tournaments"]:
            wc_data = data["tournaments"]["wc"]
            print("Keys in 'wc':", list(wc_data.keys()))
            
            # Check specific arrays
            if "fastest_innings_milestones" in wc_data:
                fim = wc_data["fastest_innings_milestones"]
                print("fastest_innings_milestones keys:", list(fim.keys()))
                for k, v in fim.items():
                    print(f"  {k}: {len(v)} items")
            
            if "most_wickets" in wc_data:
                mw = wc_data["most_wickets"]
                print("most_wickets keys:", list(mw.keys()))
                if "overall" in mw:
                    print(f"  overall: {len(mw['overall'])} items")

            if "most_runs" in wc_data:
                print(f"most_runs: {len(wc_data['most_runs'])} items")

        else:
            print("wc key not found in tournaments.")
except Exception as e:
    print(f"Error: {e}")
