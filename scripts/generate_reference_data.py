import pandas as pd
import numpy as np
import uuid
from datetime import datetime, timedelta
import os

np.random.seed(42)

OUTPUT_DIR = "/Users/rraman/Documents/Cummins_Entry_Visibility/data/synthetic/reference"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HTS_CODES = {
    "84": {
        "8408": ["8408101000", "8408102000", "8408109000", "8408201000", "8408202000", "8408209000"],
        "8409": ["8409911000", "8409914000", "8409919100", "8409919900", "8409991000", "8409999100"],
        "8413": ["8413301000", "8413302000", "8413309100", "8413601000", "8413709100", "8413819000"],
        "8481": ["8481101000", "8481201000", "8481301000", "8481401000", "8481802500", "8481809000"],
        "8483": ["8483101000", "8483102000", "8483109000", "8483301000", "8483401000", "8483509000"],
        "8412": ["8412211000", "8412215000", "8412291000", "8412311000", "8412391000", "8412909000"],
        "8414": ["8414301000", "8414308000", "8414599500", "8414809100", "8414901000", "8414909000"],
    },
    "85": {
        "8501": ["8501101000", "8501102000", "8501201000", "8501311000", "8501401000", "8501521000"],
        "8503": ["8503001000", "8503004500", "8503009500", "8503009900"],
        "8504": ["8504101000", "8504211000", "8504311000", "8504401000", "8504501000", "8504909500"],
        "8544": ["8544111000", "8544191000", "8544301000", "8544421000", "8544491000", "8544609000"],
        "8536": ["8536101000", "8536201000", "8536411000", "8536501000", "8536699000", "8536909500"],
        "8507": ["8507101000", "8507201000", "8507309000", "8507500000", "8507600000", "8507800000"],
    },
    "87": {
        "8708": ["8708101000", "8708211000", "8708291000", "8708301000", "8708401000", "8708501000",
                 "8708709000", "8708801000", "8708911000", "8708921000", "8708941000", "8708999100",
                 "8708999500", "8708999700", "8708999800"],
    },
    "73": {
        "7318": ["7318110000", "7318120000", "7318130000", "7318140000", "7318150000", "7318160000",
                 "7318210000", "7318220000", "7318230000", "7318240000", "7318290000"],
        "7326": ["7326110000", "7326190000", "7326200000", "7326901000", "7326908600"],
    },
}

HTS_DESCRIPTIONS = {
    "8408": "Compression-ignition internal combustion piston engines (diesel or semi-diesel)",
    "8409": "Parts suitable for use with spark-ignition or compression-ignition engines",
    "8413": "Pumps for liquids; liquid elevators",
    "8481": "Taps, cocks, valves for pipes, boiler shells, tanks, vats",
    "8483": "Transmission shafts, cranks, bearing housings, gears, gearing",
    "8412": "Engines and motors, other (hydraulic, pneumatic)",
    "8414": "Air or vacuum pumps, air or gas compressors, fans, blowers",
    "8501": "Electric motors and generators",
    "8503": "Parts suitable for use with electric motors and generators",
    "8504": "Electrical transformers, static converters, inductors",
    "8544": "Insulated wire, cable; optical fiber cables",
    "8536": "Electrical apparatus for switching, protecting circuits",
    "8507": "Electric accumulators including separators",
    "8708": "Parts and accessories of motor vehicles",
    "7318": "Screws, bolts, nuts, coach screws, similar articles of iron or steel",
    "7326": "Other articles of iron or steel",
}

PART_DESCRIPTIONS = {
    "8408": ["DIESEL ENGINE ASSEMBLY", "ENGINE BLOCK DIESEL", "FUEL INJECTION PUMP ASSY", "DIESEL MOTOR UNIT"],
    "8409": ["PISTON RING SET", "CONNECTING ROD", "CYLINDER LINER", "VALVE COVER GASKET", "CRANKSHAFT BEARING",
             "CAMSHAFT ASSEMBLY", "ROCKER ARM", "PUSH ROD", "TIMING GEAR", "FLYWHEEL HOUSING"],
    "8413": ["FUEL TRANSFER PUMP", "WATER PUMP ASSEMBLY", "OIL PUMP", "COOLANT PUMP", "HYDRAULIC PUMP"],
    "8481": ["PRESSURE RELIEF VALVE", "CHECK VALVE", "SOLENOID VALVE", "FUEL SHUTOFF VALVE", "EGR VALVE"],
    "8483": ["DRIVE SHAFT", "GEAR SET", "BEARING HOUSING", "TIMING CHAIN", "CRANKSHAFT PULLEY"],
    "8412": ["HYDRAULIC MOTOR", "PNEUMATIC ACTUATOR", "AIR STARTER", "HYDRAULIC CYLINDER"],
    "8414": ["TURBOCHARGER ASSEMBLY", "AIR COMPRESSOR", "COOLING FAN", "BLOWER MOTOR", "VACUUM PUMP"],
    "8501": ["ALTERNATOR", "STARTER MOTOR", "ELECTRIC MOTOR", "GENERATOR ASSEMBLY"],
    "8503": ["STATOR ASSEMBLY", "ROTOR ASSEMBLY", "BRUSH SET", "COMMUTATOR", "ARMATURE"],
    "8504": ["VOLTAGE REGULATOR", "RECTIFIER", "TRANSFORMER", "INVERTER MODULE"],
    "8544": ["WIRING HARNESS", "BATTERY CABLE", "SENSOR WIRE", "IGNITION CABLE", "GROUND STRAP"],
    "8536": ["RELAY", "CIRCUIT BREAKER", "FUSE HOLDER", "TERMINAL BLOCK", "CONNECTOR"],
    "8507": ["BATTERY", "BATTERY MODULE", "ACCUMULATOR CELL"],
    "8708": ["BUMPER BRACKET", "FENDER ASSEMBLY", "HOOD LATCH", "DOOR HINGE", "MIRROR MOUNT",
             "EXHAUST BRACKET", "ENGINE MOUNT", "TRANSMISSION MOUNT", "AXLE SHAFT"],
    "7318": ["HEX BOLT", "LOCK NUT", "FLAT WASHER", "SPRING WASHER", "STUD BOLT", "CAP SCREW"],
    "7326": ["MOUNTING BRACKET", "SUPPORT PLATE", "CLAMP", "HOSE CLAMP", "METAL BRACKET"],
}

COMMODITY_CODES = {
    "8408": "ENGINE", "8409": "ENGINE_PARTS", "8413": "PUMP", "8481": "VALVE", "8483": "TRANSMISSION",
    "8412": "HYDRAULIC", "8414": "AIR_SYSTEM", "8501": "ELECTRICAL", "8503": "ELECTRICAL_PARTS",
    "8504": "ELECTRONICS", "8544": "WIRING", "8536": "SWITCHES", "8507": "BATTERY",
    "8708": "VEHICLE_PARTS", "7318": "FASTENERS", "7326": "STEEL_ARTICLES",
}

DESCRIPTORS = ["WOODEN SKID", "METAL BRACKET", "SHIPPING CRATE", "PACKING MATERIAL", "TOOL KIT",
               "SERVICE MANUAL", "GASKET SET", "SEAL KIT", "HARDWARE KIT", "MOUNTING KIT"]

COO_DIST = {"CN": 0.40, "MX": 0.20, "US": 0.15, "IN": 0.10, "TW": 0.05, "KR": 0.05,
            "JP": 0.02, "DE": 0.01, "BR": 0.01, "TH": 0.01}


def generate_part_number(pattern_type):
    if pattern_type == "SO":
        return f"SO{np.random.randint(10000, 99999)}"
    elif pattern_type == "DASH":
        return f"{np.random.randint(0, 99):02d}-{np.random.randint(0, 999999):06d}"
    elif pattern_type == "E":
        return f"E{np.random.randint(100000, 999999)}"
    else:
        return np.random.choice(DESCRIPTORS)


def get_all_hts_codes():
    all_codes = []
    for chapter, headings in HTS_CODES.items():
        for heading, codes in headings.items():
            all_codes.extend(codes)
    return all_codes


def generate_gtm_part_master(n_rows=5000):
    print(f"Generating gtm_part_master.csv with {n_rows} rows...")
    
    all_hts = get_all_hts_codes()
    coo_choices = list(COO_DIST.keys())
    coo_probs = list(COO_DIST.values())
    
    pattern_types = np.random.choice(["SO", "DASH", "E", "DESC"], size=n_rows, p=[0.4, 0.3, 0.2, 0.1])
    
    data = []
    for i in range(n_rows):
        hts_code = np.random.choice(all_hts)
        heading = hts_code[:4]
        chapter = hts_code[:2]
        coo = np.random.choice(coo_choices, p=coo_probs)
        
        descriptions = PART_DESCRIPTIONS.get(heading, ["MISCELLANEOUS PART"])
        description = np.random.choice(descriptions)
        if pattern_types[i] == "DESC":
            description = generate_part_number("DESC")
        
        add_applicable = False
        if coo == "CN":
            add_applicable = np.random.random() < 0.60
        elif coo == "IN":
            add_applicable = np.random.random() < 0.30
        
        cvd_applicable = False
        if coo == "CN":
            cvd_applicable = np.random.random() < 0.40
        elif coo == "IN":
            cvd_applicable = np.random.random() < 0.50
        
        fta_eligible = coo in ["MX", "KR"] or (coo == "US")
        if coo in ["MX", "KR"]:
            fta_eligible = np.random.random() < 0.70
        
        created_date = datetime(2020, 1, 1) + timedelta(days=np.random.randint(0, 1800))
        updated_date = created_date + timedelta(days=np.random.randint(0, 365))
        
        data.append({
            "PART_ID": str(uuid.uuid4()),
            "PART_NUMBER": generate_part_number(pattern_types[i]),
            "DESCRIPTION": description,
            "COMMODITY_CODE": COMMODITY_CODES.get(heading, "GENERAL"),
            "HTS_CODE": hts_code,
            "COO_DEFAULT": coo,
            "ADD_APPLICABLE": add_applicable,
            "CVD_APPLICABLE": cvd_applicable,
            "FTA_ELIGIBLE": fta_eligible,
            "CREATED_DATE": created_date.strftime("%Y-%m-%d"),
            "UPDATED_DATE": updated_date.strftime("%Y-%m-%d"),
        })
    
    df = pd.DataFrame(data)
    output_path = os.path.join(OUTPUT_DIR, "gtm_part_master.csv")
    df.to_csv(output_path, index=False)
    print(f"  Saved to {output_path}")
    return df


def generate_gtm_hts_reference(n_rows=500):
    print(f"Generating gtm_hts_reference.csv with {n_rows} rows...")
    
    data = []
    all_entries = []
    
    for chapter, headings in HTS_CODES.items():
        for heading, codes in headings.items():
            for code in codes:
                all_entries.append((chapter, heading, code))
    
    selected_entries = []
    while len(selected_entries) < n_rows:
        selected_entries.extend(all_entries)
    selected_entries = selected_entries[:n_rows]
    np.random.shuffle(selected_entries)
    
    sections = {"73": "XV", "84": "XVI", "85": "XVI", "87": "XVII"}
    
    for chapter, heading, hts_code in selected_entries:
        base_description = HTS_DESCRIPTIONS.get(heading, "Other articles")
        suffix = hts_code[-4:]
        description = f"{base_description}, {suffix}"
        
        duty_rate = np.random.choice([0, 2.5, 3.5, 5.0, 6.0, 7.5, 10.0, 12.5, 15.0, 20.0, 25.0],
                                     p=[0.15, 0.15, 0.10, 0.15, 0.10, 0.10, 0.10, 0.05, 0.05, 0.03, 0.02])
        
        add_rate = 0.0
        cvd_rate = 0.0
        if chapter in ["84", "85"]:
            if np.random.random() < 0.3:
                add_rate = np.random.choice([25.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0])
            if np.random.random() < 0.2:
                cvd_rate = np.random.choice([10.0, 25.0, 50.0, 75.0, 100.0, 150.0, 200.0])
        elif chapter == "73":
            if np.random.random() < 0.4:
                add_rate = np.random.choice([50.0, 100.0, 150.0, 200.0])
            if np.random.random() < 0.35:
                cvd_rate = np.random.choice([25.0, 50.0, 100.0])
        
        effective_date = datetime(2019, 1, 1) + timedelta(days=np.random.randint(0, 365))
        expiration_date = datetime(2030, 12, 31)
        
        data.append({
            "HTS_CODE": hts_code,
            "HTS_DESCRIPTION": description,
            "CHAPTER": chapter,
            "SECTION": sections.get(chapter, "XVI"),
            "DUTY_RATE": duty_rate,
            "ADD_RATE": add_rate,
            "CVD_RATE": cvd_rate,
            "EFFECTIVE_DATE": effective_date.strftime("%Y-%m-%d"),
            "EXPIRATION_DATE": expiration_date.strftime("%Y-%m-%d"),
        })
    
    df = pd.DataFrame(data)
    output_path = os.path.join(OUTPUT_DIR, "gtm_hts_reference.csv")
    df.to_csv(output_path, index=False)
    print(f"  Saved to {output_path}")
    return df


def generate_add_cvd_reference(n_rows=200):
    print(f"Generating add_cvd_reference.csv with {n_rows} rows...")
    
    all_hts = get_all_hts_codes()
    
    coo_prefixes = {
        "CN": {"add": "A-570", "cvd": "C-570"},
        "IN": {"add": "A-533", "cvd": "C-533"},
        "MX": {"add": "A-201", "cvd": "C-201"},
        "KR": {"add": "A-580", "cvd": "C-580"},
        "VN": {"add": "A-552", "cvd": "C-552"},
    }
    
    coo_weights = {"CN": 0.45, "IN": 0.25, "MX": 0.10, "KR": 0.10, "VN": 0.10}
    
    data = []
    case_counter = {coo: 900 for coo in coo_prefixes}
    
    for i in range(n_rows):
        coo = np.random.choice(list(coo_weights.keys()), p=list(coo_weights.values()))
        hts_code = np.random.choice(all_hts)
        
        prefixes = coo_prefixes[coo]
        case_num = case_counter[coo]
        case_counter[coo] += 1
        
        case_id = f"{coo}-{hts_code[:4]}-{case_num}"
        add_order = f"{prefixes['add']}-{case_num}"
        cvd_order = f"{prefixes['cvd']}-{case_num}" if np.random.random() < 0.7 else None
        
        if coo == "CN":
            add_rate = np.random.choice([25.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0])
            cvd_rate = np.random.choice([10.0, 25.0, 50.0, 75.0, 100.0]) if cvd_order else 0.0
        elif coo == "IN":
            add_rate = np.random.choice([10.0, 25.0, 50.0, 100.0, 150.0])
            cvd_rate = np.random.choice([5.0, 10.0, 25.0, 50.0, 100.0, 150.0, 200.0]) if cvd_order else 0.0
        else:
            add_rate = np.random.choice([5.0, 10.0, 25.0, 50.0, 75.0])
            cvd_rate = np.random.choice([5.0, 10.0, 25.0]) if cvd_order else 0.0
        
        effective_date = datetime(2018, 1, 1) + timedelta(days=np.random.randint(0, 2500))
        status = np.random.choice(["ACTIVE", "SUSPENDED", "REVOKED"], p=[0.85, 0.10, 0.05])
        
        data.append({
            "CASE_ID": case_id,
            "COO": coo,
            "HTS_CODE": hts_code,
            "ADD_ORDER_NUMBER": add_order,
            "CVD_ORDER_NUMBER": cvd_order,
            "ADD_RATE": add_rate,
            "CVD_RATE": cvd_rate,
            "EFFECTIVE_DATE": effective_date.strftime("%Y-%m-%d"),
            "STATUS": status,
        })
    
    df = pd.DataFrame(data)
    output_path = os.path.join(OUTPUT_DIR, "add_cvd_reference.csv")
    df.to_csv(output_path, index=False)
    print(f"  Saved to {output_path}")
    return df


def main():
    print("=" * 60)
    print("Generating Cummins Trade Compliance Reference Data")
    print("=" * 60)
    
    df_parts = generate_gtm_part_master(5000)
    df_hts = generate_gtm_hts_reference(500)
    df_add_cvd = generate_add_cvd_reference(200)
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"gtm_part_master.csv: {len(df_parts)} rows")
    print(f"gtm_hts_reference.csv: {len(df_hts)} rows")
    print(f"add_cvd_reference.csv: {len(df_add_cvd)} rows")
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
