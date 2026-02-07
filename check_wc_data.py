
import os

EXTRACT_DIR = "t20i_data"

def check_years():
    if not os.path.exists(EXTRACT_DIR):
        print("Data dir not found.")
        return

    years_to_check = ['2007', '2009', '2010']
    events_found = {}

    print(f"Scanning {EXTRACT_DIR} for matches in {years_to_check}...")
    
    count = 0
    for f_name in os.listdir(EXTRACT_DIR):
        if f_name.endswith('_info.csv'):
            path = os.path.join(EXTRACT_DIR, f_name)
            date_val = ""
            event_val = ""
            
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        parts = line.strip().split(',')
                        if len(parts) >= 3 and parts[0] == 'info':
                            key = parts[1].lower()
                            val = ",".join(parts[2:]).replace('"', '').strip()
                            
                            if key == 'date':  # One of the dates
                                if not date_val: date_val = val # Take first date
                            if key == 'event':
                                event_val = val
            except: 
                continue

            if date_val:
                date_val = date_val.replace('/', '-')
                year = date_val.split('-')[0]
                if year in years_to_check:
                    if year not in events_found: events_found[year] = {}
                    if not event_val: event_val = "NO_EVENT_TAG"
                    if event_val not in events_found[year]: events_found[year][event_val] = 0
                    events_found[year][event_val] += 1
                    count += 1

    print("-" * 30)
    for year in sorted(events_found.keys()):
        print(f"Year: {year}")
        for ev, cnt in events_found[year].items():
            print(f"  Event: '{ev}' (Matches: {cnt})")
    print("-" * 30)
    print(f"Total info files checked for these years: {count}")

if __name__ == "__main__":
    check_years()
