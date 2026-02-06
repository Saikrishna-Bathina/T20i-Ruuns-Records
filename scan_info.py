import os
import csv

EXTRACT_DIR = "t20i_data"
info_files = [f for f in os.listdir(EXTRACT_DIR) if f.endswith('_info.csv')]

results = set()
outcomes = set()

for f_name in info_files:
    path = os.path.join(EXTRACT_DIR, f_name)
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) >= 3 and parts[0] == 'info':
                if parts[1] == 'outcome':
                    outcomes.add(parts[2])
                if parts[1] == 'result':
                    results.add(parts[2])
                if parts[1] == 'winner':
                    pass # We know this exists

print("Outcomes found:", outcomes)
print("Results found:", results)

# Check for "abandoned" or "no result" explicitly in any value
print("Checking for 'no result' or 'abandoned' in any info field...")
for f_name in info_files:
    path = os.path.join(EXTRACT_DIR, f_name)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        if "no result" in content.lower() or "abandoned" in content.lower():
            print(f"Found in {f_name}:")
            # Print the relevant lines
            f.seek(0)
            for line in f:
                if "no result" in line.lower() or "abandoned" in line.lower():
                    print(f"  {line.strip()}")
            break
