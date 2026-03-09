import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

np.random.seed(42)

OUTPUT_PATH = "/Users/rraman/Documents/Cummins_Entry_Visibility/data/synthetic/broker_raw/ceva/ceva_entries.csv"

COUNTRIES = ["CN", "MX", "US", "IN", "TW", "KR"]
COUNTRY_WEIGHTS = [0.35, 0.25, 0.15, 0.10, 0.08, 0.07]

HTS_CODES = [
    "8408201000", "8408209020", "8408209090", "8409911000", "8409919990",
    "8411810000", "8411990000", "8413302000", "8413309010", "8414301000",
    "8414592000", "8414802200", "8415810010", "8421230000", "8421310000",
    "8481201000", "8481802500", "8482101050", "8482500000", "8483101010",
    "8483301000", "8483402000", "8483909010", "8484100090", "8484200000",
    "8501101000", "8501201000", "8501320000", "8503001000", "8503009580",
    "8511100000", "8511201000", "8511309000", "8511400000", "8511509000",
    "8536501000", "8536509000", "8537101800", "8538901000", "8544300000",
    "8708302100", "8708309010", "8708409000", "8708507900", "8708709000",
    "8708809000", "8708919000", "8708959000", "8708991500", "8708999190"
]

VALID_PART_PREFIXES = [
    ("SO", 5, True),
    ("##-######", 0, False),
    ("E", 6, True),
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
        if np.random.random() < 0.5:
            return str(int(base) + np.random.randint(1, 100)).zfill(10)
        else:
            invalid_prefixes = ["9999", "0000", "1234", "5678"]
            return np.random.choice(invalid_prefixes) + str(np.random.randint(100000, 999999))

def generate_entry_number():
    return str(np.random.randint(40000000000, 49999999999)).zfill(11)

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

    num_entries = 3000
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

    total_target = 50000
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
        is_valid_part = np.random.random() > 0.10
        is_valid_hts = np.random.random() > 0.15
        add_cvd_issue = np.random.random() < 0.05
        
        country = np.random.choice(COUNTRIES, p=COUNTRY_WEIGHTS)
        entered_value = generate_entered_value()
        
        if country == "US":
            duty_amt = 0.0
        else:
            duty_rate = np.random.choice([0.0, 0.025, 0.05, 0.075, 0.10, 0.15, 0.25], 
                                         p=[0.20, 0.15, 0.20, 0.15, 0.15, 0.10, 0.05])
            duty_amt = round(entered_value * duty_rate, 2)
        
        if add_cvd_issue:
            add_flag = "" if np.random.random() < 0.5 else ("Y" if np.random.random() < 0.3 else "N")
            cvd_flag = "" if np.random.random() < 0.5 else ("Y" if np.random.random() < 0.3 else "N")
        else:
            if country in ["CN", "KR", "TW"] and np.random.random() < 0.25:
                add_flag = "Y"
            else:
                add_flag = "N"
            
            if country in ["CN", "IN"] and np.random.random() < 0.15:
                cvd_flag = "Y"
            else:
                cvd_flag = "N"
        
        record = {
            "FILE_ID": f"CEVA_{file_id_counter:08d}",
            "LOAD_TIMESTAMP": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ENTRY_NUM": entry["entry_num"],
            "ENTRY_DT": entry["entry_date"].strftime("%Y-%m-%d"),
            "LINE_NUM": entry["line_num"],
            "ITEM_NUM": generate_part_number(is_valid=is_valid_part),
            "TARIFF_NUM": generate_hts_code(is_valid=is_valid_hts),
            "ORIGIN_CTRY": country,
            "ENTERED_VALUE": entered_value,
            "DUTY_AMT": duty_amt,
            "ADD_FLAG": add_flag,
            "CVD_FLAG": cvd_flag
        }
        records.append(record)
        file_id_counter += 1

    df = pd.DataFrame(records)
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    
    print(f"Generated {len(df):,} rows")
    print(f"Output: {OUTPUT_PATH}")
    print(f"\nUnique entries: {df['ENTRY_NUM'].nunique():,}")
    print(f"Date range: {df['ENTRY_DT'].min()} to {df['ENTRY_DT'].max()}")
    print(f"\nCountry distribution:")
    print(df['ORIGIN_CTRY'].value_counts())
    print(f"\nADD_FLAG distribution:")
    print(df['ADD_FLAG'].value_counts(dropna=False))
    print(f"\nCVD_FLAG distribution:")
    print(df['CVD_FLAG'].value_counts(dropna=False))

if __name__ == "__main__":
    main()
