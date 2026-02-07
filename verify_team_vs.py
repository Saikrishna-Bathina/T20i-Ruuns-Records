
import json
import sys

try:
    with open('data.js', 'r', encoding='utf-8') as f:
        content = f.read()
        json_str = content.replace('const t20Data = ', '').replace(';', '')
        data = json.loads(json_str)
        
        # Check Fastest Wickets Team Vs
        if 'fastest_wickets' in data and 'team_vs' in data['fastest_wickets']:
            fw_tv = data['fastest_wickets']['team_vs']
            print(f"Fastest Wickets Team Vs Keys: {len(fw_tv)}")
            if 'India' in fw_tv:
                print(f"India vs Opponents: {list(fw_tv['India'].keys())[:5]}")
        else:
            print("fastest_wickets.team_vs NOT found.")
            
        # Check Most Wickets Team Vs
        if 'most_wickets' in data and 'team_vs' in data['most_wickets']:
            mw_tv = data['most_wickets']['team_vs']
            print(f"Most Wickets Team Vs Keys: {len(mw_tv)}")
            if 'Australia' in mw_tv:
                 print(f"Australia vs Opponents: {list(mw_tv['Australia'].keys())[:5]}")
                 if 'England' in mw_tv['Australia']:
                     print(f"Australia vs England Sample: {mw_tv['Australia']['England'][0]}")
        else:
             print("most_wickets.team_vs NOT found.")

except Exception as e:
    print(f"Error: {e}")
