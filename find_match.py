import os

EXTRACT_DIR = "t20i_data"
info_files = [f for f in os.listdir(EXTRACT_DIR) if f.endswith('_info.csv')]

for f_name in info_files:
    path = os.path.join(EXTRACT_DIR, f_name)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "Hong Kong" in content and "Bahrain" in content and "Bayuemas Oval" in content:
                print(f"Found match: {f_name}")
                print("-" * 20)
                f.seek(0)
                for _ in range(25):
                    print(f.readline().strip())
                print("-" * 20)
                break
    except Exception:
        pass
