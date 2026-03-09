import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

np.random.seed(43)

OUTPUT_PATH = "/Users/rraman/Documents/Cummins_Entry_Visibility/data/synthetic/broker_raw/expeditor/expeditor_entries.csv"

COUNTRIES = ["China", "Mexico", "United States", "India"]
COUNTRY_WEIGHTS = [0.40, 0.30, 0.15, 0.15]

HTS_CODES = [
    "8408.20.10.00", "8408.20.90.20", "8408.20.90.90", "8409.91.10.00", "8409.91.99.90",
    "8411.81.00.00", "8411.99.00.00", "8413.30.20.00", "8413.30.90.10", "8414.30.10.00",
    "8414.59.20.00", "8414.80.22.00", "8415.81.00.10", "8421.23.00.00", "8421.31.00.00",
    "8481.20.10.00", "8481.80.25.00", "8482.10.10.50", "8482.50.00.00", "8483.10.10.10",
    "8483.30.10.00", "8483.40.20.00", "8483.90.90.10", "8484.10.00.90", "8484.20.00.00",
    "8501.10.10.00", "8501.20.10.00", "8501.32.00.00", "8503.00.10.00", "8503.00.95.80",
    "8511.10.00.00", "8511.20.10.00", "8511.30.90.00", "8511.40.00.00", "8511.50.90.00",
    "8536.50.10.00", "8536.50.90.00", "8537.10.18.00", "8538.90.10.00", "8544.30.00.00",
    "8708.30.21.00", "8708.30.90.10", "8708.40.90.00", "8708.50.79.00", "8708.70.90.00",
    "8708.80.90.00", "8708.91.90.00", "8708.95.90.00", "8708.99.15.00", "8708.99.91.90",
    "8302.49.80.90", "8302.41.60.30", "8302.42.30.65", "8301.40.90.00", "8301.60.00.00"
]

def generate_part_number(is_valid=True):
    if is_valid:
        pattern = np.random.choice([0, 1, 2, 3], p=[0.30, 0.35, 0.25, 0.10])
        if pattern == 0:
            return f"SO{np.random.randint(10000, 99999)}"
        elif pattern == 1:
            return f"{np.random.randint(10, 99)}-{np.random.randint(100000, 999999)}"
        elif pattern == 2:
            return f"E{np.random.randint(100000, 999999)}"
        else:
            descriptors = [
                "FUEL FILTER ASSY", "INJECTOR NOZZLE", "GASKET KIT", "BEARING SET",
                "TURBO CHARGER", "WATER PUMP", "OIL COOLER", "CAMSHAFT ASSY",
                "PISTON RING SET", "VALVE SPRING", "CYLINDER HEAD", "CRANKSHAFT",
                "CONNECTING ROD", "FLYWHEEL ASSY", "STARTER MOTOR", "ALTERNATOR"
            ]
            return np.random.choice(descriptors)
    else:
        invalid_pattern = np.random.choice([0, 1, 2, 3])
        if invalid_pattern == 0:
            return f"INVALID-{np.random.randint(1000, 9999)}"
        elif invalid_pattern == 1:
            return f"XX{np.random.randint(100000, 999999)}"
        elif invalid_pattern == 2:
            return f"UNKNOWN-PART-{np.random.randint(100, 999)}"
        else:
            return f"TEST{np.random.randint(10000, 99999)}"

def generate_hts_code(is_valid=True):
    if is_valid:
        return np.random.choice(HTS_CODES)
    else:
        base = np.random.choice(HTS_CODES)
        if np.random.random() < 0.4:
            parts = base.split(".")
            parts[-1] = str(np.random.randint(10, 99))
            return ".".join(parts)
        elif np.random.random() < 0.7:
            return f"9999.99.99.99"
        else:
            return f"{np.random.randint(1000,9999)}.{np.random.randint(10,99)}.{np.random.randint(10,99)}.{np.random.randint(10,99)}"

def generate_entry_number():
    prefix = np.random.randint(100, 999)
    middle = np.random.randint(1000000, 9999999)
    suffix = np.random.randint(0, 9)
    return f"{prefix}-{middle}-{suffix}"

def generate_entered_value():
    tier = np.random.choice([0, 1, 2, 3], p=[0.40, 0.35, 0.20, 0.05])
    if tier == 0:
        return round(np.random.uniform(50, 1000), 2)
    elif tier == 1:
        return round(np.random.uniform(1000, 10000), 2)
    elif tier == 2:
        return round(np.random.uniform(10000, 100000), 2)
    else:
        return round(np.random.uniform(100000, 500000), 2)

def main():
    start_date = datetime(2025, 10, 1)
    end_date = datetime(2026, 3, 31)
    date_range = (end_date - start_date).days

    num_entries = 2000
    entries = []
    
    for _ in range(num_entries):
        entry_num = generate_entry_number()
        entry_date = start_date + timedelta(days=np.random.randint(0, date_range))
        num_lines = np.random.randint(1, 16)
        
        for line_num in range(1, num_lines + 1):
            entries.append({
                "entry_num": entry_num,
                "entry_date": entry_date,
                "line_num": line_num,
                "total_lines": num_lines
            })

    total_target = 30000
    current_count = len(entries)
    
    while current_count < total_target:
        entry_num = generate_entry_number()
        entry_date = start_date + timedelta(days=np.random.randint(0, date_range))
        num_lines = np.random.randint(1, 16)
        
        for line_num in range(1, num_lines + 1):
            if current_count >= total_target:
                break
            entries.append({
                "entry_num": entry_num,
                "entry_date": entry_date,
                "line_num": line_num,
                "total_lines": num_lines
            })
            current_count += 1

    entries = entries[:total_target]
    
    records = []
    file_id_counter = 1
    
    for idx, entry in enumerate(entries):
        is_valid_part = np.random.random() > 0.12
        is_valid_hts = np.random.random() > 0.18
        add_cvd_issue = np.random.random() < 0.08
        
        country = np.random.choice(COUNTRIES, p=COUNTRY_WEIGHTS)
        entered_value = generate_entered_value()
        
        if country == "United States":
            duty_amt = 0.0
        else:
            duty_rate = np.random.choice([0.0, 0.025, 0.05, 0.075, 0.10, 0.15, 0.25], 
                                         p=[0.20, 0.15, 0.20, 0.15, 0.15, 0.10, 0.05])
            duty_amt = round(entered_value * duty_rate, 2)
        
        if add_cvd_issue:
            add_flag = "" if np.random.random() < 0.5 else ("YES" if np.random.random() < 0.3 else "NO")
            cvd_flag = "" if np.random.random() < 0.5 else ("YES" if np.random.random() < 0.3 else "NO")
        else:
            if country in ["China"] and np.random.random() < 0.30:
                add_flag = "YES"
            else:
                add_flag = "NO"
            
            if country in ["China", "India"] and np.random.random() < 0.20:
                cvd_flag = "YES"
            else:
                cvd_flag = "NO"
        
        record = {
            "FILE_ID": f"EXP_{file_id_counter:08d}",
            "LOAD_TIMESTAMP": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ENTRY_NUMBER": entry["entry_num"],
            "ENTRY_DATE": entry["entry_date"].strftime("%m/%d/%Y"),
            "LINE_NO": entry["line_num"],
            "PART_NO": generate_part_number(is_valid=is_valid_part),
            "HTS": generate_hts_code(is_valid=is_valid_hts),
            "COUNTRY_OF_ORIGIN": country,
            "VALUE": entered_value,
            "DUTY": duty_amt,
            "ANTIDUMPING": add_flag,
            "COUNTERVAILING": cvd_flag
        }
        records.append(record)
        file_id_counter += 1

    df = pd.DataFrame(records)
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    
    print(f"Generated {len(df):,} rows")
    print(f"Output: {OUTPUT_PATH}")
    print(f"\nUnique entries: {df['ENTRY_NUMBER'].nunique():,}")
    print(f"Date range: {df['ENTRY_DATE'].min()} to {df['ENTRY_DATE'].max()}")
    print(f"\nCountry distribution:")
    print(df['COUNTRY_OF_ORIGIN'].value_counts())
    print(f"\nANTIDUMPING distribution:")
    print(df['ANTIDUMPING'].value_counts(dropna=False))
    print(f"\nCOUNTERVAILING distribution:")
    print(df['COUNTERVAILING'].value_counts(dropna=False))

if __name__ == "__main__":
    main()
