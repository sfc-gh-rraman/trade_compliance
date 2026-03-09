#!/usr/bin/env python3
"""
Generate semantic-rich CORRECTIONS_HISTORY data for LLM rule discovery testing.
Includes discoverable patterns with varied phrasings for semantic clustering.
"""

import uuid
import random
import csv
from datetime import datetime, timedelta
from pathlib import Path

OUTPUT_DIR = Path("/Users/rraman/Documents/Cummins_Entry_Visibility/data/synthetic/corrections")
OUTPUT_FILE = OUTPUT_DIR / "corrections_history.csv"

ANALYSTS = [
    "Sarah Chen", "Michael Rodriguez", "Jennifer Walsh", "David Kim",
    "Amanda Foster", "Robert Thompson", "Lisa Martinez", "James Wilson",
    "Emily Davis", "Christopher Lee", "Michelle Brown", "Daniel Garcia",
    "Rachel Anderson", "Kevin Taylor", "Stephanie Moore", "Brian Jackson"
]

BROKERS = ["CEVA", "EXPEDITOR", "KUEHNE_NAGEL", "FEDEX_TRADE", "UPS_SCS", "DHL_GLOBAL"]

COUNTRIES = ["CN", "TW", "MX", "IN", "DE", "JP", "KR", "VN", "TH", "MY", "IT", "GB", "CA"]

CORRECTION_CATEGORIES = [
    "HTS_CLASSIFICATION", "DUTY_ADJUSTMENT", "COUNTRY_OF_ORIGIN", 
    "VALUATION", "FTA_ELIGIBILITY", "ADD_CVD", "DOCUMENTATION", "SPLIT_LINE"
]

FIELD_TYPES = ["HTS_CODE", "ADD_FLAG", "CVD_FLAG", "COO", "PREFERENTIAL", 
               "ENTERED_VALUE", "QUANTITY", "UNIT_PRICE", "DUTY_RATE", "FEE_CODE"]

CONFIDENCE_LEVELS = ["HIGH", "MEDIUM", "LOW"]

def generate_uuid():
    return str(uuid.uuid4()).upper()

def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

def random_entry_number():
    styles = [
        lambda: f"{random.randint(100, 999)}-{random.randint(1000000, 9999999)}-{random.randint(0, 9)}",
        lambda: f"00{random.randint(100000000, 999999999)}",
        lambda: f"E{random.randint(10000000, 99999999)}"
    ]
    return random.choice(styles)()

def random_part_number(prefix=None):
    if prefix:
        return f"{prefix}-{random.randint(10000, 99999)}-{random.choice(['A', 'B', 'C', 'D'])}"
    prefixes = ["E", "P", "M", "C", "S", "F", "H", "T", "X", "R"]
    return f"{random.choice(prefixes)}-{random.randint(10000, 99999)}-{random.choice(['A', 'B', 'C', 'D'])}"

def random_hts():
    chapters = ["8453", "8479", "8481", "8482", "8483", "8501", "8504", "8544", "7318", "7326", "8413", "8414"]
    return f"{random.choice(chapters)}{random.randint(100000, 999999)}"

def random_value():
    return round(random.uniform(500, 150000), 2)


CP001_REASONS = [
    "ADD applies per CBP ruling HQ H301245",
    "Antidumping duty required - PRC origin",
    "China ADD order covers this part category",
    "ADD assessment needed for Chinese-sourced component",
    "Per A-570-967, antidumping duty applies",
    "需要反倾销税 - E-prefix part from China",
    "E-prefix indicates Chinese mfg - ADD required per scope ruling",
    "Missing ADD - part is covered under steel wheels order",
    "CBP requires ADD for this PRC classification",
    "ADD omitted - falls under antidumping case A-570-909",
    "Chinese origin E-series - subject to antidumping measures",
    "Antidumping duty missing; China steel component",
    "Per CBP guidance, E-prefix from CN requires ADD assessment",
    "ADD applies - Chinese steel fabrication (E-type)",
    "PRC sourced E-part subject to antidumping order",
    "Required ADD per Commerce Dept scope determination",
    "E-prefix + China = antidumping territory",
    "ADD duty rate should be 25.76% per case ruling",
    "Chinese manufacturer - covered ADD product",
    "ADD applies; E-numbered part, PRC origin confirmed"
]

CP001_NOTES = [
    "Another E-prefix from China slipping through. Third one this week.",
    "Classic miss - E parts from China ALWAYS need ADD check",
    "Why doesn't the system flag E-prefix + CN automatically?!",
    "Broker missed ADD again. They need training on this.",
    "E-prefix parts are 90% from China. Should be auto-flagged.",
    "Frustrating - this is such an obvious pattern",
    "Need to add E-prefix/CN to validation rules ASAP",
    "Caught this during random audit. Lucky catch.",
    "Same broker, same mistake. Pattern emerging.",
    "ADD calculation was zero but should be ~26%",
]

CP001_REFS = [
    "19 CFR 351.212; A-570-967",
    "CBP HQ H301245; 19 USC 1673",
    "A-570-909; Commerce scope memo dated 2023-04-15",
    "19 CFR 351.225; ITC publication 5215",
    "AD order A-570-967; CBP CSMS #45123456",
]


CP002_REASONS = [
    "Correct subheading for metal-cutting machinery parts",
    "Wrong classification - should be 8453906000",
    "HTS 8453905090 misclassified - functional use determines code",
    "Reclassify to 8453906000 per CBP ruling NY N312456",
    "Metal-cutting accessory, not general machinery part",
    "8453905090 is incorrect - actual use is precision cutting",
    "Tariff shift analysis shows 8453906000 is correct",
    "Misclassification - subheading should reflect cutting function",
    "Per GRI 1 and Note 1(k) to Chapter 84, reclassify",
    "CBP informed compliance letter requires 8453906000",
    "Classification error - functional test indicates 8453906000",
    "Should be classified under 8453.90.6000 per end-use"
]

CP002_NOTES = [
    "8453905090 keeps appearing but it's almost never right for these parts",
    "Brokers default to 905090 but the metal-cutting function matters",
    "Had to pull CBP ruling to prove this one. Took 2 hours.",
    "Same misclassification we saw last month",
    "Classification seems arbitrary from broker side",
]

CP002_REFS = [
    "CBP Ruling NY N312456; GRI 1, 6",
    "19 CFR 152.103; EN 84.53",
    "CBP Informed Compliance Publication (Classification)",
    "HTS General Note 3(c)(ii)",
]


CP003_REASONS = [
    "Value exceeds FTA threshold - no preferential treatment",
    "Over $50K doesn't qualify for FTA preference",
    "High value entry - ineligible for preferential rate",
    "FTA preference removed - value threshold exceeded",
    "Transaction value too high for FTA eligibility",
    "Entry value $75K+ precludes preferential claim",
    "Removed USMCA preference - exceeds de minimis",
    "FTA not applicable at this value tier",
    "Preferential claim invalid - value disqualifies",
    "High-value entry cannot use FTA rate per rules of origin",
    "Value-based exclusion from preferential program",
    "Above threshold - standard duty rate applies"
]

CP003_NOTES = [
    "High value = no FTA. Simple rule but often missed.",
    "Broker applied FTA to a $72K shipment. Nope.",
    "Need automated value threshold checking",
    "FTA rules have value limits - who knew? (Brokers apparently don't)",
    "Classic case of applying preference without checking value",
]

CP003_REFS = [
    "USMCA Article 4.1; 19 CFR 10.411",
    "19 USC 1520(d); USMCA Implementation Instructions",
    "CBP Trade Facilitation Notice (value thresholds)",
    "CAFTA-DR Art. 4.2; 19 CFR 10.583",
]


CP004_REASONS = [
    "CVD applies per C-533-866 for Indian steel fasteners",
    "Indian origin steel = CVD assessment required",
    "ITC case 701-TA-549 covers this product",
    "CVD duty required - India steel fasteners order",
    "Per CVD order C-533-866, duty applies to Indian fasteners",
    "Countervailing duty missing - Indian steel product",
    "India CVD order in effect - fastener category",
    "ITC determined CVD applies to Indian steel fasteners",
    "CVD rate should be 5.29% per Commerce final determination",
    "Indian steel fastener subject to countervailing measures",
    "CVD omitted - product within scope of C-533-866",
    "Per 701-TA-549, India fasteners require CVD",
    "Countervailing duty applies - Indian origin confirmed",
    "Steel fastener from India = CVD territory"
]

CP004_NOTES = [
    "India + steel + fasteners = CVD. Always.",
    "ITC order is crystal clear on this. Broker should know.",
    "Third Indian steel fastener miss this month from same broker",
    "CVD cases are public. Why don't brokers check?",
    "Need India CVD rule in automated validation",
    "Easy pattern to automate - surprised it's not",
]

CP004_REFS = [
    "C-533-866; 19 CFR 351.503",
    "ITC Pub 5123; 701-TA-549",
    "Commerce Final Determination 87 FR 12345",
    "19 USC 1671; C-533-866 scope memo",
]


CP005_REASONS = [
    "Part originated in Taiwan, not PRC",
    "Misattributed COO - should be TW not CN",
    "Taiwan origin incorrectly reported as China",
    "COO correction: manufacturer is in Taiwan",
    "PRC code used in error - actual origin Taiwan",
    "Taiwan vs China confusion - corrected to TW",
    "Country code should be TW per supplier cert",
    "Origin misidentification - Taiwan not mainland",
    "Precision parts from Taiwan plant, not PRC",
    "COO error: TW mislabeled as CN",
    "Taiwan manufacturer, China COO reported incorrectly",
    "Corrected origin code from CN to TW per documentation"
]

CP005_NOTES = [
    "Taiwan/China mix-up is SO common. Critical for duty implications.",
    "Supplier has plants in both - broker picked wrong one",
    "COO error could have triggered ADD incorrectly",
    "Documentation clearly shows Taiwan - broker didn't read",
    "TW vs CN affects ADD applicability significantly",
]

CP005_REFS = [
    "19 CFR 134.1; CBP country code list",
    "19 USC 1304; Origin marking requirements",
    "CBP Ruling HQ H298765 (origin determination)",
]


CP006_REASONS = [
    "Voltage affects HTS classification",
    ">80V requires different code (8544.49 not 8544.42)",
    "Electrical cable voltage classification error",
    "High voltage cable - reclassify per voltage specs",
    "Cable rated >80V - wrong HTS subheading used",
    "Voltage specification determines HTS - over 80V threshold",
    "8544.42 is for <=80V; this cable is 120V rated",
    "Reclassify to 8544.49 per voltage rating",
    "High voltage electrical cable misclassified",
    "Voltage-based classification: >80V = 8544.49.xx",
    "Per technical specs, voltage exceeds 80V threshold",
    "Cable HTS depends on voltage - this is >80V"
]

CP006_NOTES = [
    "Voltage matters for cable classification! 80V is the line.",
    "Had to check technical specs to verify voltage rating",
    "Brokers rarely check voltage specs for cables",
    ">80V vs <=80V is a common classification trap",
    "Need voltage field in validation checks",
]

CP006_REFS = [
    "HTS 8544 heading notes; EN 85.44",
    "CBP Ruling NY N234567 (voltage classification)",
    "19 CFR 152.106; GRI 1, 3(a)",
]


CP007_REASONS = [
    "USMCA cert on file - exempt from ADD",
    "Remove ADD - preferential treatment under USMCA",
    "USMCA exempts Mexico from antidumping duty",
    "Mexican origin with USMCA cert = no ADD",
    "Preferential USMCA treatment removes ADD obligation",
    "ADD not applicable - USMCA preference claimed",
    "Mexico exempt from ADD per USMCA provisions",
    "Valid USMCA certificate - remove antidumping duty",
    "USMCA preferential status precludes ADD",
    "Remove ADD assessment - Mexican USMCA eligible goods",
    "Per USMCA, Mexico-origin exempt from ADD order",
    "USMCA supersedes ADD for Mexican goods",
    "Mexican preferential - ADD doesn't apply",
    "Valid cert of origin = USMCA exemption from ADD"
]

CP007_NOTES = [
    "USMCA + Mexico = no ADD. Broker applied ADD anyway.",
    "Had to verify USMCA cert was on file. It was.",
    "ADD incorrectly applied to Mexican goods with preference",
    "USMCA exemption is powerful but often overlooked",
    "Broker systems don't cross-reference FTA certs with ADD",
    "Common error - applying ADD to USMCA-eligible Mexican goods",
]

CP007_REFS = [
    "USMCA Article 4.2; 19 CFR 10.1001",
    "19 USC 1677j; USMCA Implementation Act",
    "CBP USMCA Implementation Guidelines",
    "19 CFR 10.1003; USMCA preference rules",
]


CP008_REASONS = [
    "Split-line manual duty calculation required",
    "Multi-product line needs manual duty split",
    "Duty apportionment across split line items",
    "Manual calculation needed for split shipment",
    "Split-line entry requires recalculation",
    "Duty allocation error on split line",
    "Manual adjustment for multi-part line entry",
    "Split-line duty calc was incorrect"
]

CP008_NOTES = [
    "Split lines are always manual work. System can't handle them.",
    "Multi-product lines need human review every time",
    "Spent 45 min on this split-line calculation",
    "Why do brokers combine products on one line?!",
]

CP008_REFS = [
    "19 CFR 141.86; CBP Form 7501 instructions",
    "19 CFR 152.103; Value apportionment",
]


GENERIC_REASONS = {
    "HTS_CODE": [
        "Classification error - product function misidentified",
        "Wrong tariff code selected by broker",
        "HTS correction per technical review",
        "Reclassification based on product composition",
        "Updated classification per CBP guidance",
        "HTS subheading incorrect - corrected per GRI",
        "Classification adjusted based on product specifications",
        "Tariff code error identified during audit"
    ],
    "ADD_FLAG": [
        "ADD assessment missing for covered product",
        "Antidumping duty should not apply",
        "ADD calculation error corrected",
        "ADD rate updated per Commerce determination",
        "Antidumping scope review completed"
    ],
    "CVD_FLAG": [
        "CVD duty should apply per order",
        "Countervailing duty incorrectly assessed",
        "CVD rate correction per Commerce review",
        "CVD omitted - product in scope",
        "CVD not applicable - origin exempt"
    ],
    "COO": [
        "Country of origin incorrectly reported",
        "Origin documentation shows different COO",
        "Substantial transformation analysis - COO corrected",
        "Manufacturer location confirms correct COO",
        "COO error - supplier certificate reviewed"
    ],
    "PREFERENTIAL": [
        "FTA preference incorrectly claimed",
        "Preferential treatment should apply",
        "Certificate of origin validates preference",
        "Preference claim unsupported by documentation",
        "FTA eligibility confirmed upon review"
    ],
    "ENTERED_VALUE": [
        "Transaction value calculation error",
        "Value should include assists",
        "Deductions improperly applied",
        "First sale rule applies",
        "Value adjustment per CBP review"
    ],
    "DUTY_RATE": [
        "Duty rate incorrect for this classification",
        "Rate should reflect current HTS",
        "Preferential rate applies",
        "Standard rate incorrectly used",
        "Duty calculation error"
    ]
}

GENERIC_NOTES = [
    "Standard correction - nothing unusual",
    "Caught during routine audit",
    "Broker acknowledged error",
    "Documentation review required",
    "Cross-referenced with supplier records",
    "Verified against GTM database",
    "Quick fix once identified",
    "Needed research to confirm",
    "Second opinion confirmed correction",
    "Flagged by weekly review process",
    "Random sample audit finding",
    "Broker training issue perhaps?",
    "System should have caught this",
    "Manual review caught the error",
    "Documentation was ambiguous - clarified with shipper",
]

GENERIC_REFS = [
    "19 CFR 141.86",
    "19 CFR 152.103",
    "19 USC 1401a",
    "CBP Directive 3550-067",
    "HTS General Note 3",
    "19 CFR 10.411",
    "19 USC 1484",
    "CBP Trade Facilitation Guidelines",
]

BUSINESS_CONTEXTS = [
    "Regular import for Cummins engine assembly",
    "Just-in-time delivery for production line",
    "Warranty replacement parts shipment",
    "Aftermarket parts inventory replenishment",
    "Engineering sample for R&D",
    "High-priority production critical parts",
    "Standard inventory restock",
    "Seasonal demand fulfillment",
    "New product line introduction",
    "Quality replacement for defective batch",
    "Customer special order fulfillment",
    "Service center inventory",
]

RELATED_CASES_TEMPLATES = [
    "Similar correction: CORR-{id1} ({date1})",
    "See also: CORR-{id1}, CORR-{id2}",
    "Related pattern in CORR-{id1}",
    "Linked to CORR-{id1} (same broker)",
    "Pattern matches CORR-{id1}, CORR-{id2}, CORR-{id3}",
    None,
    None,
    None,
]


def generate_correction(pattern_type, start_date, end_date):
    correction_date = random_date(start_date, end_date)
    entry_date = correction_date - timedelta(days=random.randint(1, 30))
    
    row = {
        "CORRECTION_ID": generate_uuid(),
        "LINE_ID": generate_uuid(),
        "ENTRY_NUMBER": random_entry_number(),
        "ENTRY_DATE": entry_date.strftime("%Y-%m-%d"),
        "BROKER_NAME": random.choice(BROKERS),
        "CORRECTED_BY": random.choice(ANALYSTS),
        "CORRECTION_DATE": correction_date.strftime("%Y-%m-%d"),
        "BUSINESS_CONTEXT": random.choice(BUSINESS_CONTEXTS),
    }
    
    if pattern_type == "CP001":
        row["PART_NUMBER"] = random_part_number(prefix="E")
        row["COUNTRY_OF_ORIGIN"] = "CN"
        row["HTS_CODE"] = random_hts()
        row["ENTERED_VALUE"] = random_value()
        row["FIELD_CORRECTED"] = "ADD_FLAG"
        row["ORIGINAL_VALUE"] = "N"
        row["CORRECTED_VALUE"] = "Y"
        row["CORRECTION_REASON"] = random.choice(CP001_REASONS)
        row["ANALYST_NOTES"] = random.choice(CP001_NOTES)
        row["REGULATORY_REFERENCE"] = random.choice(CP001_REFS)
        row["CORRECTION_CATEGORY"] = "ADD_CVD"
        row["CONFIDENCE_LEVEL"] = "HIGH"
        row["WAS_FLAGGED_BY_SYSTEM"] = random.choice(["TRUE", "FALSE", "FALSE"])
        row["TIME_TO_RESOLVE_MINUTES"] = random.randint(15, 60)
        row["REQUIRED_RESEARCH"] = random.choice(["TRUE", "FALSE"])
        
    elif pattern_type == "CP002":
        row["PART_NUMBER"] = random_part_number()
        row["COUNTRY_OF_ORIGIN"] = random.choice(["DE", "JP", "TW", "KR"])
        row["HTS_CODE"] = "8453905090"
        row["ENTERED_VALUE"] = random_value()
        row["FIELD_CORRECTED"] = "HTS_CODE"
        row["ORIGINAL_VALUE"] = "8453905090"
        row["CORRECTED_VALUE"] = "8453906000"
        row["CORRECTION_REASON"] = random.choice(CP002_REASONS)
        row["ANALYST_NOTES"] = random.choice(CP002_NOTES)
        row["REGULATORY_REFERENCE"] = random.choice(CP002_REFS)
        row["CORRECTION_CATEGORY"] = "HTS_CLASSIFICATION"
        row["CONFIDENCE_LEVEL"] = random.choice(["HIGH", "MEDIUM"])
        row["WAS_FLAGGED_BY_SYSTEM"] = "FALSE"
        row["TIME_TO_RESOLVE_MINUTES"] = random.randint(30, 120)
        row["REQUIRED_RESEARCH"] = "TRUE"
        
    elif pattern_type == "CP003":
        row["PART_NUMBER"] = random_part_number()
        row["COUNTRY_OF_ORIGIN"] = random.choice(["MX", "CA"])
        row["HTS_CODE"] = random_hts()
        row["ENTERED_VALUE"] = round(random.uniform(50001, 150000), 2)
        row["FIELD_CORRECTED"] = "PREFERENTIAL"
        row["ORIGINAL_VALUE"] = "USMCA"
        row["CORRECTED_VALUE"] = "NONE"
        row["CORRECTION_REASON"] = random.choice(CP003_REASONS)
        row["ANALYST_NOTES"] = random.choice(CP003_NOTES)
        row["REGULATORY_REFERENCE"] = random.choice(CP003_REFS)
        row["CORRECTION_CATEGORY"] = "FTA_ELIGIBILITY"
        row["CONFIDENCE_LEVEL"] = "HIGH"
        row["WAS_FLAGGED_BY_SYSTEM"] = "FALSE"
        row["TIME_TO_RESOLVE_MINUTES"] = random.randint(10, 45)
        row["REQUIRED_RESEARCH"] = "FALSE"
        
    elif pattern_type == "CP004":
        row["PART_NUMBER"] = random_part_number()
        row["COUNTRY_OF_ORIGIN"] = "IN"
        row["HTS_CODE"] = f"7318{random.randint(100000, 999999)}"
        row["ENTERED_VALUE"] = random_value()
        row["FIELD_CORRECTED"] = "CVD_FLAG"
        row["ORIGINAL_VALUE"] = "N"
        row["CORRECTED_VALUE"] = "Y"
        row["CORRECTION_REASON"] = random.choice(CP004_REASONS)
        row["ANALYST_NOTES"] = random.choice(CP004_NOTES)
        row["REGULATORY_REFERENCE"] = random.choice(CP004_REFS)
        row["CORRECTION_CATEGORY"] = "ADD_CVD"
        row["CONFIDENCE_LEVEL"] = "HIGH"
        row["WAS_FLAGGED_BY_SYSTEM"] = random.choice(["TRUE", "FALSE", "FALSE"])
        row["TIME_TO_RESOLVE_MINUTES"] = random.randint(15, 45)
        row["REQUIRED_RESEARCH"] = "FALSE"
        
    elif pattern_type == "CP005":
        row["PART_NUMBER"] = random_part_number(prefix=random.choice(["P", "M"]))
        row["COUNTRY_OF_ORIGIN"] = "TW"
        row["HTS_CODE"] = random_hts()
        row["ENTERED_VALUE"] = random_value()
        row["FIELD_CORRECTED"] = "COO"
        row["ORIGINAL_VALUE"] = "CN"
        row["CORRECTED_VALUE"] = "TW"
        row["CORRECTION_REASON"] = random.choice(CP005_REASONS)
        row["ANALYST_NOTES"] = random.choice(CP005_NOTES)
        row["REGULATORY_REFERENCE"] = random.choice(CP005_REFS)
        row["CORRECTION_CATEGORY"] = "COUNTRY_OF_ORIGIN"
        row["CONFIDENCE_LEVEL"] = "HIGH"
        row["WAS_FLAGGED_BY_SYSTEM"] = "FALSE"
        row["TIME_TO_RESOLVE_MINUTES"] = random.randint(20, 60)
        row["REQUIRED_RESEARCH"] = "TRUE"
        
    elif pattern_type == "CP006":
        row["PART_NUMBER"] = random_part_number()
        row["COUNTRY_OF_ORIGIN"] = random.choice(["CN", "MX", "VN"])
        row["HTS_CODE"] = "8544420000"
        row["ENTERED_VALUE"] = random_value()
        row["FIELD_CORRECTED"] = "HTS_CODE"
        row["ORIGINAL_VALUE"] = "8544420000"
        row["CORRECTED_VALUE"] = "8544490000"
        row["CORRECTION_REASON"] = random.choice(CP006_REASONS)
        row["ANALYST_NOTES"] = random.choice(CP006_NOTES)
        row["REGULATORY_REFERENCE"] = random.choice(CP006_REFS)
        row["CORRECTION_CATEGORY"] = "HTS_CLASSIFICATION"
        row["CONFIDENCE_LEVEL"] = "MEDIUM"
        row["WAS_FLAGGED_BY_SYSTEM"] = "FALSE"
        row["TIME_TO_RESOLVE_MINUTES"] = random.randint(30, 90)
        row["REQUIRED_RESEARCH"] = "TRUE"
        
    elif pattern_type == "CP007":
        row["PART_NUMBER"] = random_part_number()
        row["COUNTRY_OF_ORIGIN"] = "MX"
        row["HTS_CODE"] = random_hts()
        row["ENTERED_VALUE"] = random_value()
        row["FIELD_CORRECTED"] = "ADD_FLAG"
        row["ORIGINAL_VALUE"] = "Y"
        row["CORRECTED_VALUE"] = "N"
        row["CORRECTION_REASON"] = random.choice(CP007_REASONS)
        row["ANALYST_NOTES"] = random.choice(CP007_NOTES)
        row["REGULATORY_REFERENCE"] = random.choice(CP007_REFS)
        row["CORRECTION_CATEGORY"] = "ADD_CVD"
        row["CONFIDENCE_LEVEL"] = "HIGH"
        row["WAS_FLAGGED_BY_SYSTEM"] = "FALSE"
        row["TIME_TO_RESOLVE_MINUTES"] = random.randint(20, 50)
        row["REQUIRED_RESEARCH"] = "TRUE"
        
    elif pattern_type == "CP008":
        row["PART_NUMBER"] = random_part_number()
        row["COUNTRY_OF_ORIGIN"] = random.choice(COUNTRIES)
        row["HTS_CODE"] = random_hts()
        row["ENTERED_VALUE"] = random_value()
        row["FIELD_CORRECTED"] = "ENTERED_VALUE"
        row["ORIGINAL_VALUE"] = str(round(random.uniform(1000, 50000), 2))
        row["CORRECTED_VALUE"] = str(round(random.uniform(1000, 50000), 2))
        row["CORRECTION_REASON"] = random.choice(CP008_REASONS)
        row["ANALYST_NOTES"] = random.choice(CP008_NOTES)
        row["REGULATORY_REFERENCE"] = random.choice(CP008_REFS)
        row["CORRECTION_CATEGORY"] = "SPLIT_LINE"
        row["CONFIDENCE_LEVEL"] = "MEDIUM"
        row["WAS_FLAGGED_BY_SYSTEM"] = "FALSE"
        row["TIME_TO_RESOLVE_MINUTES"] = random.randint(45, 120)
        row["REQUIRED_RESEARCH"] = "FALSE"
        
    else:
        field = random.choice(FIELD_TYPES)
        row["PART_NUMBER"] = random_part_number()
        row["COUNTRY_OF_ORIGIN"] = random.choice(COUNTRIES)
        row["HTS_CODE"] = random_hts()
        row["ENTERED_VALUE"] = random_value()
        row["FIELD_CORRECTED"] = field
        
        if field == "HTS_CODE":
            row["ORIGINAL_VALUE"] = random_hts()
            row["CORRECTED_VALUE"] = random_hts()
            row["CORRECTION_CATEGORY"] = "HTS_CLASSIFICATION"
        elif field in ["ADD_FLAG", "CVD_FLAG"]:
            row["ORIGINAL_VALUE"] = random.choice(["Y", "N"])
            row["CORRECTED_VALUE"] = "N" if row["ORIGINAL_VALUE"] == "Y" else "Y"
            row["CORRECTION_CATEGORY"] = "ADD_CVD"
        elif field == "COO":
            orig = random.choice(COUNTRIES)
            corr = random.choice([c for c in COUNTRIES if c != orig])
            row["ORIGINAL_VALUE"] = orig
            row["CORRECTED_VALUE"] = corr
            row["CORRECTION_CATEGORY"] = "COUNTRY_OF_ORIGIN"
        elif field == "PREFERENTIAL":
            prefs = ["USMCA", "CAFTA-DR", "GSP", "NONE", "KORUS", "AUSFTA"]
            orig = random.choice(prefs)
            row["ORIGINAL_VALUE"] = orig
            row["CORRECTED_VALUE"] = random.choice([p for p in prefs if p != orig])
            row["CORRECTION_CATEGORY"] = "FTA_ELIGIBILITY"
        elif field == "ENTERED_VALUE":
            row["ORIGINAL_VALUE"] = str(round(random.uniform(500, 100000), 2))
            row["CORRECTED_VALUE"] = str(round(random.uniform(500, 100000), 2))
            row["CORRECTION_CATEGORY"] = "VALUATION"
        else:
            row["ORIGINAL_VALUE"] = str(random.randint(1, 100))
            row["CORRECTED_VALUE"] = str(random.randint(1, 100))
            row["CORRECTION_CATEGORY"] = random.choice(CORRECTION_CATEGORIES)
        
        reason_key = field if field in GENERIC_REASONS else "HTS_CODE"
        row["CORRECTION_REASON"] = random.choice(GENERIC_REASONS[reason_key])
        row["ANALYST_NOTES"] = random.choice(GENERIC_NOTES)
        row["REGULATORY_REFERENCE"] = random.choice(GENERIC_REFS)
        row["CONFIDENCE_LEVEL"] = random.choice(CONFIDENCE_LEVELS)
        row["WAS_FLAGGED_BY_SYSTEM"] = random.choice(["TRUE", "FALSE"])
        row["TIME_TO_RESOLVE_MINUTES"] = random.randint(10, 180)
        row["REQUIRED_RESEARCH"] = random.choice(["TRUE", "FALSE"])
    
    template = random.choice(RELATED_CASES_TEMPLATES)
    if template:
        row["RELATED_CASES"] = template.format(
            id1=f"{random.randint(1000, 9999)}",
            id2=f"{random.randint(1000, 9999)}",
            id3=f"{random.randint(1000, 9999)}",
            date1=(correction_date - timedelta(days=random.randint(30, 180))).strftime("%Y-%m-%d")
        )
    else:
        row["RELATED_CASES"] = ""
    
    return row


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    start_date = datetime(2025, 9, 9)
    end_date = datetime(2026, 3, 9)
    
    pattern_counts = {
        "CP001": 47,
        "CP002": 23,
        "CP003": 15,
        "CP004": 31,
        "CP005": 12,
        "CP006": 19,
        "CP007": 28,
        "CP008": 8,
    }
    
    total_pattern_rows = sum(pattern_counts.values())
    generic_count = 2500 - total_pattern_rows
    
    rows = []
    
    for pattern, count in pattern_counts.items():
        for _ in range(count):
            rows.append(generate_correction(pattern, start_date, end_date))
    
    for _ in range(generic_count):
        rows.append(generate_correction("GENERIC", start_date, end_date))
    
    random.shuffle(rows)
    
    columns = [
        "CORRECTION_ID", "LINE_ID", "ENTRY_NUMBER", "ENTRY_DATE", "BROKER_NAME",
        "PART_NUMBER", "COUNTRY_OF_ORIGIN", "HTS_CODE", "ENTERED_VALUE",
        "FIELD_CORRECTED", "ORIGINAL_VALUE", "CORRECTED_VALUE", "CORRECTION_REASON",
        "ANALYST_NOTES", "REGULATORY_REFERENCE", "RELATED_CASES", "BUSINESS_CONTEXT",
        "CORRECTION_CATEGORY", "CORRECTED_BY", "CORRECTION_DATE", "WAS_FLAGGED_BY_SYSTEM",
        "CONFIDENCE_LEVEL", "TIME_TO_RESOLVE_MINUTES", "REQUIRED_RESEARCH"
    ]
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Generated: {OUTPUT_FILE}")
    print(f"Total rows: {len(rows)}")
    print(f"\nPattern distribution:")
    for pattern, count in pattern_counts.items():
        print(f"  {pattern}: {count} rows")
    print(f"  GENERIC: {generic_count} rows")


if __name__ == "__main__":
    main()
