import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

np.random.seed(2026)

OUTPUT_PATH = "/Users/rraman/Documents/Cummins_Entry_Visibility/data/synthetic/broker_raw/kuehne/kuehne_entries.csv"

COUNTRIES = ["CHN", "MEX", "USA", "IND", "TWN", "KOR", "DEU", "POL", "CZE"]
COUNTRY_WEIGHTS = [0.30, 0.20, 0.12, 0.10, 0.08, 0.07, 0.05, 0.05, 0.03]

HTS_CODES_EU = [
    "8408 2010 00", "8408 2090 20", "8408 2090 90", "8409 9110 00", "8409 9199 90",
    "8411 8100 00", "8411 9900 00", "8413 3020 00", "8413 3090 10", "8414 3010 00",
    "8414 5920 00", "8414 8022 00", "8415 8100 10", "8421 2300 00", "8421 3100 00",
    "8481 2010 00", "8481 8025 00", "8482 1010 50", "8482 5000 00", "8483 1010 10",
    "8483 3010 00", "8483 4020 00", "8483 9090 10", "8484 1000 90", "8484 2000 00",
    "8501 1010 00", "8501 2010 00", "8501 3200 00", "8503 0010 00", "8503 0095 80",
    "8511 1000 00", "8511 2010 00", "8511 3090 00", "8511 4000 00", "8511 5090 00",
    "8536 5010 00", "8536 5090 00", "8537 1018 00", "8538 9010 00", "8544 3000 00",
    "8708 3021 00", "8708 3090 10", "8708 4090 00", "8708 5079 00", "8708 7090 00",
    "8708 8090 00", "8708 9190 00", "8708 9590 00", "8708 9915 00", "8708 9991 90",
    "8302 4980 90", "8302 4100 00", "8302 4200 00", "8307 1010 00", "8307 9000 00"
]

VALID_PART_PREFIXES = [
    ("SO", 5),
    ("##-######", 0),
    ("E", 6),
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
                "KRAFTSTOFFFILTER", "EINSPRITZDÜSE", "DICHTUNGSSATZ", "LAGERSATZ",
                "TURBOLADER", "WASSERPUMPE", "ÖLKÜHLER", "NOCKENWELLE",
                "KOLBENRINGSATZ", "VENTILFEDER", "ZYLINDERKOPF", "KURBELWELLE",
                "PLEUELSTANGE", "SCHWUNGRAD", "ANLASSER", "LICHTMASCHINE"
            ]
            return np.random.choice(descriptors)
    else:
        invalid_pattern = np.random.choice([0, 1, 2, 3])
        if invalid_pattern == 0:
            return f"UNGÜLTIG-{np.random.randint(1000, 9999)}"
        elif invalid_pattern == 1:
            return f"XX{np.random.randint(100000, 999999)}"
        elif invalid_pattern == 2:
            return f"UNBEKANNT-TEIL-{np.random.randint(100, 999)}"
        else:
            return f"TEST{np.random.randint(10000, 99999)}"

def generate_hts_code_eu(is_valid=True):
    if is_valid:
        return np.random.choice(HTS_CODES_EU)
    else:
        base = np.random.choice(HTS_CODES_EU)
        if np.random.random() < 0.5:
            parts = base.split()
            parts[0] = str(int(parts[0]) + np.random.randint(1, 100)).zfill(4)
            return " ".join(parts)
        else:
            invalid_prefixes = ["9999", "0000", "1234", "5678"]
            return f"{np.random.choice(invalid_prefixes)} {np.random.randint(1000, 9999)} {np.random.randint(10, 99)}"

def generate_entry_number_de():
    return f"DE-2025-{np.random.randint(100000, 999999)}"

def format_european_value(value):
    int_part = int(value)
    dec_part = int((value - int_part) * 100)
    int_str = f"{int_part:,}".replace(",", ".")
    return f"{int_str},{dec_part:02d}"

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
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 3, 31)
    date_range = (end_date - start_date).days

    num_entries = 700
    entries = []
    
    for _ in range(num_entries):
        entry_num = generate_entry_number_de()
        entry_date = start_date + timedelta(days=np.random.randint(0, date_range))
        num_lines = np.random.randint(1, 20)
        
        for line_num in range(1, num_lines + 1):
            entries.append({
                "entry_num": entry_num,
                "entry_date": entry_date,
                "line_num": line_num,
                "total_lines": num_lines
            })

    total_target = 10000
    current_count = len(entries)
    
    while current_count < total_target:
        entry_num = generate_entry_number_de()
        entry_date = start_date + timedelta(days=np.random.randint(0, date_range))
        num_lines = np.random.randint(1, 20)
        
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
        add_cvd_issue = np.random.random() < 0.06
        
        country = np.random.choice(COUNTRIES, p=COUNTRY_WEIGHTS)
        entered_value = generate_entered_value()
        
        if country in ["USA", "DEU"]:
            duty_amt = 0.0
        else:
            duty_rate = np.random.choice([0.0, 0.025, 0.05, 0.075, 0.10, 0.15, 0.25], 
                                         p=[0.20, 0.15, 0.20, 0.15, 0.15, 0.10, 0.05])
            duty_amt = round(entered_value * duty_rate, 2)
        
        if add_cvd_issue:
            add_flag = "" if np.random.random() < 0.5 else ("JA" if np.random.random() < 0.3 else "NEIN")
            cvd_flag = "" if np.random.random() < 0.5 else ("JA" if np.random.random() < 0.3 else "NEIN")
        else:
            if country in ["CHN", "KOR", "TWN"] and np.random.random() < 0.25:
                add_flag = "JA"
            else:
                add_flag = "NEIN"
            
            if country in ["CHN", "IND"] and np.random.random() < 0.15:
                cvd_flag = "JA"
            else:
                cvd_flag = "NEIN"
        
        record = {
            "DATEI_ID": f"KN_{file_id_counter:08d}",
            "LADEN_ZEIT": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "EINTRITTSNUMMER": entry["entry_num"],
            "EINTRITTSDATUM": entry["entry_date"].strftime("%d.%m.%Y"),
            "ZEILE": entry["line_num"],
            "TEILENUMMER": generate_part_number(is_valid=is_valid_part),
            "ZOLLTARIFNUMMER": generate_hts_code_eu(is_valid=is_valid_hts),
            "URSPRUNGSLAND": country,
            "WARENWERT": format_european_value(entered_value),
            "ZOLLBETRAG": format_european_value(duty_amt),
            "ANTIDUMPING_ZOLL": add_flag,
            "AUSGLEICHSZOLL": cvd_flag
        }
        records.append(record)
        file_id_counter += 1

    df = pd.DataFrame(records)
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    
    print(f"Generated {len(df):,} rows")
    print(f"Output: {OUTPUT_PATH}")
    print(f"\nUnique entries (EINTRITTSNUMMER): {df['EINTRITTSNUMMER'].nunique():,}")
    print(f"Date range: {df['EINTRITTSDATUM'].min()} to {df['EINTRITTSDATUM'].max()}")
    print(f"\nColumn names (German → English mapping for AI inference):")
    print("  DATEI_ID → FILE_ID")
    print("  LADEN_ZEIT → LOAD_TIMESTAMP")
    print("  EINTRITTSNUMMER → ENTRY_NUMBER")
    print("  EINTRITTSDATUM → ENTRY_DATE")
    print("  ZEILE → LINE_NUMBER")
    print("  TEILENUMMER → PART_NUMBER")
    print("  ZOLLTARIFNUMMER → HTS_CODE")
    print("  URSPRUNGSLAND → COUNTRY_OF_ORIGIN")
    print("  WARENWERT → ENTERED_VALUE")
    print("  ZOLLBETRAG → DUTY_AMOUNT")
    print("  ANTIDUMPING_ZOLL → ADD_FLAG")
    print("  AUSGLEICHSZOLL → CVD_FLAG")
    print(f"\nCountry distribution (URSPRUNGSLAND):")
    print(df['URSPRUNGSLAND'].value_counts())
    print(f"\nANTIDUMPING_ZOLL distribution:")
    print(df['ANTIDUMPING_ZOLL'].value_counts(dropna=False))
    print(f"\nAUSGLEICHSZOLL distribution:")
    print(df['AUSGLEICHSZOLL'].value_counts(dropna=False))

if __name__ == "__main__":
    main()
