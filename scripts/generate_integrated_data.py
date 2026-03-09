#!/usr/bin/env python3
"""
Generate integrated/standardized trade compliance data from broker raw files.
Produces:
  - fact_trade_tariff_detail.csv (integrated data)
  - fact_trade_tariff_validation.csv (validation results)
"""

import pandas as pd
import uuid
import re
from datetime import datetime
from pathlib import Path
import random
import numpy as np

random.seed(42)
np.random.seed(42)

BASE_DIR = Path("/Users/rraman/Documents/Cummins_Entry_Visibility/data/synthetic")

CEVA_FILE = BASE_DIR / "broker_raw/ceva/ceva_entries.csv"
EXPEDITOR_FILE = BASE_DIR / "broker_raw/expeditor/expeditor_entries.csv"
KUEHNE_FILE = BASE_DIR / "broker_raw/kuehne/kuehne_entries.csv"
GTM_FILE = BASE_DIR / "reference/gtm_part_master.csv"
OUTPUT_DIR = BASE_DIR / "integrated"
VALIDATION_DIR = BASE_DIR / "validation"

COUNTRY_MAPPING = {
    "US": "US", "USA": "US", "United States": "US", "UNITED STATES": "US",
    "CN": "CN", "CHN": "CN", "China": "CN", "CHINA": "CN",
    "MX": "MX", "MEX": "MX", "Mexico": "MX", "MEXICO": "MX",
    "IN": "IN", "IND": "IN", "India": "IN", "INDIA": "IN",
    "KR": "KR", "KOR": "KR", "Korea": "KR", "KOREA": "KR", "South Korea": "KR",
    "TW": "TW", "TWN": "TW", "Taiwan": "TW", "TAIWAN": "TW",
    "DE": "DE", "DEU": "DE", "Germany": "DE", "GERMANY": "DE",
    "JP": "JP", "JPN": "JP", "Japan": "JP", "JAPAN": "JP",
    "BR": "BR", "BRA": "BR", "Brazil": "BR", "BRAZIL": "BR",
    "UK": "GB", "GBR": "GB", "United Kingdom": "GB",
    "PL": "PL", "POL": "PL", "Poland": "PL",
    "CZ": "CZ", "CZE": "CZ", "Czech Republic": "CZ",
    "TH": "TH", "THA": "TH", "Thailand": "TH",
    "VN": "VN", "VNM": "VN", "Vietnam": "VN",
    "MY": "MY", "MYS": "MY", "Malaysia": "MY",
    "ID": "ID", "IDN": "ID", "Indonesia": "ID",
}


def normalize_hts(hts_value):
    """Normalize HTS code to 10 digits without punctuation."""
    if pd.isna(hts_value):
        return None
    hts_str = str(hts_value).strip()
    hts_clean = re.sub(r'[^0-9]', '', hts_str)
    if len(hts_clean) < 10:
        hts_clean = hts_clean.ljust(10, '0')
    return hts_clean[:10]


def normalize_country(country):
    """Normalize country to 2-letter ISO code."""
    if pd.isna(country):
        return None
    country_str = str(country).strip().upper()
    return COUNTRY_MAPPING.get(country_str, country_str[:2] if len(country_str) >= 2 else country_str)


def parse_date(date_str):
    """Parse various date formats to YYYY-MM-DD."""
    if pd.isna(date_str):
        return None
    date_str = str(date_str).strip()
    
    formats = [
        "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%d.%m.%Y",
        "%Y-%m-%d %H:%M:%S", "%m/%d/%Y %H:%M:%S"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return date_str


def parse_german_number(val):
    """Parse German number format (1.234,56) to float."""
    if pd.isna(val):
        return 0.0
    val_str = str(val).strip()
    val_str = val_str.replace('.', '').replace(',', '.')
    try:
        return float(val_str)
    except ValueError:
        return 0.0


def normalize_add_cvd_flag(val):
    """Normalize ADD/CVD flags to boolean."""
    if pd.isna(val) or val == '':
        return False
    val_str = str(val).strip().upper()
    return val_str in ['Y', 'YES', 'TRUE', '1', 'JA']


def load_ceva(filepath):
    """Load and transform CEVA broker data."""
    df = pd.read_csv(filepath)
    entry_id_map = {}
    
    records = []
    for _, row in df.iterrows():
        entry_num = str(row['ENTRY_NUM'])
        if entry_num not in entry_id_map:
            entry_id_map[entry_num] = str(uuid.uuid4())
        
        records.append({
            'LINE_ID': str(uuid.uuid4()),
            'ENTRY_ID': entry_id_map[entry_num],
            'ENTRY_NUMBER': entry_num,
            'ENTRY_DATE': parse_date(row['ENTRY_DT']),
            'BROKER_ID': 'CEVA',
            'BROKER_NAME': 'CEVA',
            'LINE_NUMBER': int(row['LINE_NUM']),
            'PART_NUMBER': str(row['ITEM_NUM']).strip(),
            'PART_DESCRIPTION': None,
            'BROKER_HTS_CODE': normalize_hts(row['TARIFF_NUM']),
            'COUNTRY_OF_ORIGIN': normalize_country(row['ORIGIN_CTRY']),
            'ENTERED_VALUE': float(row['ENTERED_VALUE']),
            'DUTY_AMOUNT': float(row['DUTY_AMT']),
            'ADD_AMOUNT': 0.0,
            'CVD_AMOUNT': 0.0,
            'BROKER_ADD_FLAG': normalize_add_cvd_flag(row['ADD_FLAG']),
            'BROKER_CVD_FLAG': normalize_add_cvd_flag(row['CVD_FLAG']),
            'LOAD_TIMESTAMP': datetime.now().isoformat(),
            'SOURCE_FILE': 'ceva_entries.csv'
        })
    
    return pd.DataFrame(records)


def load_expeditor(filepath):
    """Load and transform EXPEDITOR broker data."""
    df = pd.read_csv(filepath)
    entry_id_map = {}
    
    records = []
    for _, row in df.iterrows():
        entry_num = str(row['ENTRY_NUMBER'])
        if entry_num not in entry_id_map:
            entry_id_map[entry_num] = str(uuid.uuid4())
        
        records.append({
            'LINE_ID': str(uuid.uuid4()),
            'ENTRY_ID': entry_id_map[entry_num],
            'ENTRY_NUMBER': entry_num,
            'ENTRY_DATE': parse_date(row['ENTRY_DATE']),
            'BROKER_ID': 'EXPEDITOR',
            'BROKER_NAME': 'EXPEDITOR',
            'LINE_NUMBER': int(row['LINE_NO']),
            'PART_NUMBER': str(row['PART_NO']).strip(),
            'PART_DESCRIPTION': None,
            'BROKER_HTS_CODE': normalize_hts(row['HTS']),
            'COUNTRY_OF_ORIGIN': normalize_country(row['COUNTRY_OF_ORIGIN']),
            'ENTERED_VALUE': float(row['VALUE']),
            'DUTY_AMOUNT': float(row['DUTY']),
            'ADD_AMOUNT': 0.0,
            'CVD_AMOUNT': 0.0,
            'BROKER_ADD_FLAG': normalize_add_cvd_flag(row['ANTIDUMPING']),
            'BROKER_CVD_FLAG': normalize_add_cvd_flag(row['COUNTERVAILING']),
            'LOAD_TIMESTAMP': datetime.now().isoformat(),
            'SOURCE_FILE': 'expeditor_entries.csv'
        })
    
    return pd.DataFrame(records)


def load_kuehne(filepath):
    """Load and transform Kuehne+Nagel broker data (German format)."""
    df = pd.read_csv(filepath)
    entry_id_map = {}
    
    records = []
    for _, row in df.iterrows():
        entry_num = str(row['EINTRITTSNUMMER'])
        if entry_num not in entry_id_map:
            entry_id_map[entry_num] = str(uuid.uuid4())
        
        date_str = row['EINTRITTSDATUM']
        if isinstance(date_str, str) and '.' in date_str:
            parts = date_str.split('.')
            if len(parts) == 3:
                date_str = f"{parts[2]}-{parts[1]}-{parts[0]}"
        
        records.append({
            'LINE_ID': str(uuid.uuid4()),
            'ENTRY_ID': entry_id_map[entry_num],
            'ENTRY_NUMBER': entry_num,
            'ENTRY_DATE': parse_date(date_str),
            'BROKER_ID': 'KUEHNE',
            'BROKER_NAME': 'KUEHNE',
            'LINE_NUMBER': int(row['ZEILE']),
            'PART_NUMBER': str(row['TEILENUMMER']).strip(),
            'PART_DESCRIPTION': None,
            'BROKER_HTS_CODE': normalize_hts(row['ZOLLTARIFNUMMER']),
            'COUNTRY_OF_ORIGIN': normalize_country(row['URSPRUNGSLAND']),
            'ENTERED_VALUE': parse_german_number(row['WARENWERT']),
            'DUTY_AMOUNT': parse_german_number(row['ZOLLBETRAG']),
            'ADD_AMOUNT': 0.0,
            'CVD_AMOUNT': 0.0,
            'BROKER_ADD_FLAG': normalize_add_cvd_flag(row['ANTIDUMPING_ZOLL']),
            'BROKER_CVD_FLAG': normalize_add_cvd_flag(row['AUSGLEICHSZOLL']),
            'LOAD_TIMESTAMP': datetime.now().isoformat(),
            'SOURCE_FILE': 'kuehne_entries.csv'
        })
    
    return pd.DataFrame(records)


def generate_validation(integrated_df, gtm_df):
    """Generate validation results with target distributions."""
    gtm_parts = set(gtm_df['PART_NUMBER'].str.upper().str.strip())
    gtm_lookup = gtm_df.set_index(gtm_df['PART_NUMBER'].str.upper().str.strip())
    
    validation_records = []
    timestamp = datetime.now().isoformat()
    
    total_rows = len(integrated_df)
    part_pass_target = 0.70
    hs_pass_target = 0.65
    add_cvd_pass_target = 0.90
    anomaly_target = 0.02
    
    for idx, row in integrated_df.iterrows():
        line_id = row['LINE_ID']
        part_num = str(row['PART_NUMBER']).upper().strip()
        broker_hts = row['BROKER_HTS_CODE']
        broker_add = row['BROKER_ADD_FLAG']
        broker_cvd = row['BROKER_CVD_FLAG']
        coo = row['COUNTRY_OF_ORIGIN']
        
        part_exists_in_gtm = part_num in gtm_parts
        
        if part_exists_in_gtm:
            part_status = "PASS"
            part_message = "Part found in GTM"
        else:
            if random.random() < part_pass_target:
                part_status = "PASS"
                part_message = "Part verified via alternate lookup"
            else:
                part_status = "FAIL"
                part_message = f"Part {part_num} not found in GTM"
        
        gtm_hts = None
        if part_exists_in_gtm and part_num in gtm_lookup.index:
            try:
                gtm_record = gtm_lookup.loc[part_num]
                if isinstance(gtm_record, pd.DataFrame):
                    gtm_record = gtm_record.iloc[0]
                gtm_hts = normalize_hts(gtm_record.get('HTS_CODE'))
            except:
                pass
        
        if coo == 'US':
            hs_status = "PASS"
            hs_message = "COO is US - auto pass"
        elif gtm_hts and broker_hts == gtm_hts:
            hs_status = "PASS"
            hs_message = "HTS matches GTM"
        else:
            if random.random() < hs_pass_target:
                hs_status = "PASS"
                hs_message = "HTS validated via alternate classification"
            else:
                hs_status = "FAIL"
                hs_message = f"HTS mismatch: broker={broker_hts}, expected={gtm_hts or 'unknown'}"
        
        gtm_add = False
        gtm_cvd = False
        if part_exists_in_gtm and part_num in gtm_lookup.index:
            try:
                gtm_record = gtm_lookup.loc[part_num]
                if isinstance(gtm_record, pd.DataFrame):
                    gtm_record = gtm_record.iloc[0]
                gtm_add = gtm_record.get('ADD_APPLICABLE', False) == True
                gtm_cvd = gtm_record.get('CVD_APPLICABLE', False) == True
            except:
                pass
        
        add_cvd_status = "PASS"
        add_cvd_message = "ADD/CVD flags validated"
        
        if gtm_add and not broker_add:
            if random.random() >= add_cvd_pass_target:
                add_cvd_status = "FAIL"
                add_cvd_message = "Missing ADD flag - GTM indicates ADD applicable"
        elif gtm_cvd and not broker_cvd:
            if random.random() >= add_cvd_pass_target:
                add_cvd_status = "FAIL"
                add_cvd_message = "Missing CVD flag - GTM indicates CVD applicable"
        elif broker_add and not gtm_add:
            if random.random() >= add_cvd_pass_target:
                add_cvd_status = "FAIL"
                add_cvd_message = "Unexpected ADD flag - GTM does not indicate ADD"
        elif broker_cvd and not gtm_cvd:
            if random.random() >= add_cvd_pass_target:
                add_cvd_status = "FAIL"
                add_cvd_message = "Unexpected CVD flag - GTM does not indicate CVD"
        
        is_anomaly = random.random() < anomaly_target
        anomaly_type = None
        anomaly_score = 0.0
        
        if is_anomaly:
            anomaly_types = [
                "VALUE_SPIKE", "DUTY_RATIO_OUTLIER", "UNUSUAL_COO_HTS_COMBO",
                "DUPLICATE_LINE_PATTERN", "SUSPICIOUS_TIMING"
            ]
            anomaly_type = random.choice(anomaly_types)
            anomaly_score = round(random.uniform(0.75, 0.99), 3)
        
        overall_status = "PASS"
        if part_status == "FAIL" or hs_status == "FAIL" or add_cvd_status == "FAIL":
            overall_status = "FAIL"
        
        validation_records.append({
            'VALIDATION_ID': str(uuid.uuid4()),
            'LINE_ID': line_id,
            'ENTRY_NUMBER': row['ENTRY_NUMBER'],
            'ENTRY_DATE': row['ENTRY_DATE'],
            'BROKER_NAME': row['BROKER_NAME'],
            'LINE_NUMBER': row['LINE_NUMBER'],
            'PART_NUMBER': row['PART_NUMBER'],
            'PART_NUMBER_STATUS': part_status,
            'PART_NUMBER_MESSAGE': part_message,
            'HS_CODE_STATUS': hs_status,
            'HS_CODE_MESSAGE': hs_message,
            'GTM_HS_CODE': gtm_hts,
            'PREFERENTIAL_PROGRAM_STATUS': "PASS",
            'ADD_CVD_STATUS': add_cvd_status,
            'ADD_CVD_MESSAGE': add_cvd_message,
            'ANOMALY_FLAG': is_anomaly,
            'ANOMALY_TYPE': anomaly_type,
            'ANOMALY_SCORE': anomaly_score,
            'OVERALL_STATUS': overall_status,
            'VALIDATION_TIMESTAMP': timestamp
        })
    
    return pd.DataFrame(validation_records)


def main():
    print("=" * 60)
    print("Cummins Trade Compliance - Integrated Data Generator")
    print("=" * 60)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    
    print("\n[1/5] Loading GTM reference data...")
    gtm_df = pd.read_csv(GTM_FILE)
    print(f"      Loaded {len(gtm_df):,} GTM parts")
    
    print("\n[2/5] Loading and transforming broker data...")
    
    print("      Loading CEVA...")
    ceva_df = load_ceva(CEVA_FILE)
    print(f"      - CEVA: {len(ceva_df):,} rows")
    
    print("      Loading EXPEDITOR...")
    expeditor_df = load_expeditor(EXPEDITOR_FILE)
    print(f"      - EXPEDITOR: {len(expeditor_df):,} rows")
    
    print("      Loading KUEHNE...")
    kuehne_df = load_kuehne(KUEHNE_FILE)
    print(f"      - KUEHNE: {len(kuehne_df):,} rows")
    
    print("\n[3/5] Combining into integrated dataset...")
    integrated_df = pd.concat([ceva_df, expeditor_df, kuehne_df], ignore_index=True)
    print(f"      Total integrated rows: {len(integrated_df):,}")
    
    print("\n[4/5] Generating validation results...")
    validation_df = generate_validation(integrated_df, gtm_df)
    
    part_pass_pct = (validation_df['PART_NUMBER_STATUS'] == 'PASS').mean() * 100
    hs_pass_pct = (validation_df['HS_CODE_STATUS'] == 'PASS').mean() * 100
    add_cvd_pass_pct = (validation_df['ADD_CVD_STATUS'] == 'PASS').mean() * 100
    anomaly_pct = validation_df['ANOMALY_FLAG'].mean() * 100
    overall_pass_pct = (validation_df['OVERALL_STATUS'] == 'PASS').mean() * 100
    
    print(f"      Validation Distribution:")
    print(f"        - Part Number PASS: {part_pass_pct:.1f}%")
    print(f"        - HS Code PASS: {hs_pass_pct:.1f}%")
    print(f"        - ADD/CVD PASS: {add_cvd_pass_pct:.1f}%")
    print(f"        - Anomalies: {anomaly_pct:.1f}%")
    print(f"        - Overall PASS: {overall_pass_pct:.1f}%")
    
    print("\n[5/5] Writing output files...")
    
    integrated_path = OUTPUT_DIR / "fact_trade_tariff_detail.csv"
    integrated_df.to_csv(integrated_path, index=False)
    print(f"      Written: {integrated_path}")
    
    validation_path = VALIDATION_DIR / "fact_trade_tariff_validation.csv"
    validation_df.to_csv(validation_path, index=False)
    print(f"      Written: {validation_path}")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"\nIntegrated Data:")
    print(f"  Path: {integrated_path}")
    print(f"  Rows: {len(integrated_df):,}")
    print(f"  Brokers: CEVA ({len(ceva_df):,}), EXPEDITOR ({len(expeditor_df):,}), KUEHNE ({len(kuehne_df):,})")
    
    print(f"\nValidation Results:")
    print(f"  Path: {validation_path}")
    print(f"  Rows: {len(validation_df):,}")
    print(f"  Pass Rate: {overall_pass_pct:.1f}%")
    
    return integrated_path, validation_path, len(integrated_df), len(validation_df)


if __name__ == "__main__":
    main()
