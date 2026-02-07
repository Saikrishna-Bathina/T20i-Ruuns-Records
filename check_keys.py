
import json

try:
    with open("data.js", "r", encoding="utf-8") as f:
        content = f.read()
        # Strip JS definition
        json_str = content.replace("const statsData = ", "").replace(";", "")
        data = json.loads(json_str)
        
        if "tournaments" in data:
            keys = list(data["tournaments"].keys())
            print(f"Found {len(keys)} tournament keys:")
            print(sorted(keys))
        else:
            print("No 'tournaments' key found.")
except Exception as e:
    print(f"Error: {e}")
