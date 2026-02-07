
import os

DATA_DIR = "t20i_data"

def scan_files():
    count = 0
    wc_matches = 0
    keys_found = set()
    
    print(f"Scanning {DATA_DIR}...")
    
    for filename in os.listdir(DATA_DIR):
        if filename.endswith("_info.csv"):
            filepath = os.path.join(DATA_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    file_keys = {}
                    for line in lines:
                        parts = line.strip().split(',')
                        if len(parts) >= 3 and parts[0] == 'info':
                            key = parts[1]
                            val = ",".join(parts[2:]).replace('"', '')
                            file_keys[key] = val
                            
                            if "World Cup" in val:
                                print(f"Found 'World Cup' in {filename}: Key='{key}', Value='{val}'")
                                keys_found.add(key)
                                wc_matches += 1
                                break # Found it for this file
            except Exception as e:
                pass
            count += 1
            if count % 1000 == 0:
                print(f"Scanned {count} files...")

    print(f"Total Files: {count}")
    print(f"Files with 'World Cup': {wc_matches}")
    print(f"Keys used: {keys_found}")

if __name__ == "__main__":
    scan_files()
