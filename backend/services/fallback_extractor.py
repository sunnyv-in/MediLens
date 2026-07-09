import re

# Packaging mein common generic words — inhe kabhi brand name mat maano
BRAND_BLOCKLIST = {
    "TABLETS", "TABLET", "CAPSULES", "CAPSULE", "IP", "BP", "USP",
    "SCHEDULE", "PRESCRIPTION", "DRUG", "CAUTION", "STORE", "KEEP",
    "CHILDREN", "REACH", "MRP", "BATCH", "MFG", "MFD", "EXP", "EXPIRY",
    "MANUFACTURED", "MARKETED", "LTD", "LIMITED", "PVT", "PRIVATE",
    "PHARMA", "PHARMACEUTICALS", "PHARMACEUTICAL", "LABORATORIES",
    "LABS", "HEALTHCARE", "LIFESCIENCES", "BIOSCIENCES", "COMPANY",
    "REGD", "OFF", "ADDRESS", "LIC", "NO", "GASTRO", "RESISTANT",
    "SWALLOWED", "CHEWED", "CRUSHED", "MOISTURE", "TEMPERATURE",
    "PHYSICIAN", "DIRECTED", "DOSAGE", "EXCIPIENTS", "COLOUR", "AND"
}

MANUFACTURER_SUFFIXES = [
    "LTD", "LIMITED", "PVT LTD", "PVT. LTD", "PRIVATE LIMITED",
    "PHARMA", "PHARMACEUTICALS", "PHARMACEUTICAL", "LABORATORIES",
    "LABS", "HEALTHCARE", "LIFESCIENCES", "BIOSCIENCES", "DRUGS"
]

STRENGTH_PATTERN = re.compile(
    r'(\d+(?:\.\d+)?)\s*(MG|MCG|G|ML|IU|%)\b', re.IGNORECASE
)

BATCH_PATTERN = re.compile(
    r"(?:B\.?\s*NO\.?|BATCH(?:\s*NO\.?)?|LOT(?:\s*NO\.?)?)"
    r"\s*[:.\-]?\s*([A-Z0-9/-]{3,})", re.IGNORECASE
)

DATE_PATTERN = (
    r"(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)"
    r"[.\-/\s]*\d{2,4}"
    r"|\d{1,2}[./\-]\d{2,4}"
)

MFG_PATTERN = re.compile(rf"\bMF[GD]\.?(?:\s*DATE)?\s*[:.\-]?\s*({DATE_PATTERN})", re.IGNORECASE)
EXP_PATTERN = re.compile(rf"\bEXP(?:IRY)?\.?(?:\s*DATE)?\s*[:.\-]?\s*({DATE_PATTERN})", re.IGNORECASE)


def extract_strength(full_text):
    matches = STRENGTH_PATTERN.findall(full_text)
    seen = []
    for value, unit in matches:
        combo = f"{value} {unit.lower()}"
        if combo not in seen:
            seen.append(combo)
    return " + ".join(seen)


def extract_batch_number(lines):
    for line in lines:
        match = BATCH_PATTERN.search(line.upper())
        if match:
            return match.group(1).strip()
    return ""


def extract_dates(lines):
    mfg_date, exp_date = "", ""
    for line in lines:
        upper = line.upper()

        if re.search(r"\bMFD\.?\s*[:.\-]?\s*BY\b", upper):
            continue  # "Mfd: by CIPLA LTD" — yeh manufacturer hai, date nahi

        if not mfg_date:
            m = MFG_PATTERN.search(upper)
            if m:
                mfg_date = m.group(1).strip()

        if not exp_date:
            m = EXP_PATTERN.search(upper)
            if m:
                exp_date = m.group(1).strip()

    return mfg_date, exp_date


def extract_manufacturer(lines):
    for line in lines:
        upper = line.upper()
        for suffix in MANUFACTURER_SUFFIXES:
            if suffix in upper:
                # "Mfd. by" / "Marketed by" jaise prefix hata do
                cleaned = re.sub(
                    r"^(MFD|MFG|MANUFACTURED|MARKETED)\.?\s*(BY)?\s*[:.\-]?\s*",
                    "", line, flags=re.IGNORECASE
                ).strip()
                return cleaned if cleaned else line.strip()
    return ""


def extract_brand_name(ranked_data):
    """
    High-confidence, short, all-caps-ish tokens jo blocklist mein nahi hain
    aur dosage/date/batch pattern nahi hain — best candidate brand name.
    """
    best_candidate = ""
    best_score = 0

    for item in ranked_data:
        text = item["text"].strip()
        upper = text.upper()

        # skip agar yeh clearly kuch aur hai
        if STRENGTH_PATTERN.search(text):
            continue
        if BATCH_PATTERN.search(upper) or MFG_PATTERN.search(upper) or EXP_PATTERN.search(upper):
            continue
        if len(text) < 3 or len(text) > 25:
            continue

        words = re.findall(r"[A-Za-z]+", upper)
        if not words:
            continue
        if any(w in BRAND_BLOCKLIST for w in words):
            continue
        if not re.match(r'^[A-Z0-9\-\s]+$', upper):
            continue

        score = item["confidence"] + (item["votes"] * 0.1)
        if upper.isupper():
            score += 0.2

        if score > best_score:
            best_score = score
            best_candidate = text

    # bahut kam confidence pe empty rakho — galat guess se better
    return best_candidate if best_score >= 0.5 else ""


def extract_generic_composition(lines):
    """Generic drug name line, jisme usually IP/BP/USP tag hota hai."""
    for line in lines:
        if re.search(r'\b(IP|BP|USP)\b', line, re.IGNORECASE) and \
           re.search(r'(TABLET|CAPSULE|RESPULE|SYRUP|INJECTION)', line, re.IGNORECASE):
            return line.strip()
    return ""


def extract_medicine_info_fallback(ranked_data):
    lines = [item["text"] for item in ranked_data]
    full_text = " ".join(lines)

    brand = extract_brand_name(ranked_data)
    generic = extract_generic_composition(lines)
    mfg_date, exp_date = extract_dates(lines)

    medicine_name = brand or generic

    return {
        "medicine": medicine_name,
        "manufacturer": extract_manufacturer(lines),
        "strength": extract_strength(full_text),
        "batch_number": extract_batch_number(lines),
        "manufacturing_date": mfg_date,
        "expiry_date": exp_date
    }