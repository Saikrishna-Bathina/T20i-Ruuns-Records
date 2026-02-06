import os

EXTRACT_DIR = "t20i_data"

def scan_abandoned():
    info_files = [f for f in os.listdir(EXTRACT_DIR) if f.endswith('_info.csv')]
    for f_name in info_files:
        path = os.path.join(EXTRACT_DIR, f_name)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "abandoned" in content.lower():
                print(f"Found 'abandoned' in {f_name}")
                # Print the line
                for line in content.splitlines():
                     if "abandoned" in line.lower():
                         print(line)

scan_abandoned()
