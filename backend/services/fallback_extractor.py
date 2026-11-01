import re

# ============================================================
# GENERIC KEYWORDS AND PATTERNS
# ============================================================

BRAND_BLOCKLIST = {
    "TABLETS", "TABLET", "CAPSULES", "CAPSULE",
    "INJECTION", "INJECTIONS", "SYRUP", "SUSPENSION",
    "RESPULE", "RESPULES", "CREAM", "OINTMENT", "GEL",
    "DROPS", "SACHET", "SACHETS",

    "FILM", "COATED", "UNCOATED", "ENTERIC", "SUGAR",
    "SUSTAINED", "PROLONGED", "EXTENDED", "CONTROLLED",
    "DELAYED", "MODIFIED", "RELEASE", "DISPERSIBLE",
    "EFFERVESCENT", "CHEWABLE", "SUBLINGUAL", "GASTRO",
    "RESISTANT", "HARD", "SOFT", "GELATIN", "AQUEOUS",
    "STERILE", "ORAL", "TOPICAL", "EXTERNAL", "USE",
    "ONLY", "SINGLE", "DOSE", "MULTIDOSE", "VIAL", "AMPOULE",

    "IP", "BP", "USP",

    "SCHEDULE", "PRESCRIPTION", "DRUG", "CAUTION",
    "WARNING", "WARNINGS", "IMPORTANT",

    "STORE", "STORAGE", "KEEP", "CHILDREN", "REACH",
    "TEMPERATURE", "MOISTURE", "LIGHT", "PROTECT", "DIRECT",

    "MRP", "PRICE", "RS", "INCLUSIVE", "TAXES", "PER", "STRIP",

    "BATCH", "LOT", "MFG", "MFD", "EXP", "EXPIRY",
    "MANUFACTURED", "MANUFACTURER", "MARKETED",

    "LTD", "LIMITED", "PVT", "PRIVATE",
    "PHARMA", "PHARMACEUTICALS", "PHARMACEUTICAL",
    "LABORATORIES", "LABS", "HEALTHCARE",
    "LIFESCIENCES", "BIOSCIENCES", "COMPANY", "DRUGS",

    "REGD", "OFF", "OFFICE", "ADDRESS", "LIC", "LICENSE",
    "NO", "PLOT", "ROAD", "STREET", "VILLAGE", "DISTRICT",
    "STATE", "PIN", "INDIA", "TRADEMARK", "REGISTERED",

    "SWALLOWED", "CHEWED", "CRUSHED",
    "PHYSICIAN", "DIRECTED", "DOSAGE",
    "EXCIPIENTS", "COLOUR", "COLOR", "TITANIUM", "DIOXIDE",
    "Q.S", "QS", "APPROVED",

    "EACH", "CONTAINS", "COMPOSITION", "COMPOSITIONS",
    "EQUIVALENT", "EQ", "TO",

    "AND", "OR", "BY", "FOR", "THE", "OF", "IN", "WITH",
    "FROM", "THIS", "THAT", "MONTH", "MONTHS", "PREGNANCY",
    "MOTHER", "CHILD", "BLEEDING", "UNLESS", "DIRECTED", "WATER"
}

SENTENCE_WORDS = {
    "TAKE", "USE", "USED", "KEEP", "STORE", "CONSULT",
    "DIRECTED", "PRESCRIBED", "PHYSICIAN", "DOCTOR",
    "SHOULD", "MUST", "BEFORE", "AFTER", "DAILY",
    "ONCE", "TWICE", "THRICE", "SWALLOW", "SWALLOWED",
    "CHEW", "CHEWED", "CRUSH", "CRUSHED",
    "MONTH", "MONTHS", "DAY", "DAYS",
    "CHILD", "CHILDREN", "REACH", "MOTHER", "PREGNANCY",
    "BLEEDING", "UNLESS", "IMPORTANT", "CAUTION", "WARNING", "WATER"
}

MANUFACTURER_SUFFIXES = [
    "PRIVATE LIMITED", "PVT. LTD.", "PVT LTD", "PVT. LTD",
    "LIMITED", "LTD.", "LTD", "PHARMACEUTICALS", "PHARMACEUTICAL",
    "PHARMA", "LABORATORIES", "LABS", "HEALTHCARE",
    "LIFESCIENCES", "BIOSCIENCES", "DRUGS"
]

MANUFACTURER_LABEL_PATTERN = re.compile(
    r"\b(MANUFACTURED|MANUFACTURER|MFD|MFG|MARKETED|DISTRIBUTED|PACKED)\b\s*(?:BY)?\s*[:.\-]?",
    re.IGNORECASE
)

DOSAGE_FORM_PATTERN = re.compile(
    r"\b(TABLET|TABLETS|CAPSULE|CAPSULES|INJECTION|INJECTIONS|SYRUP|SUSPENSION|RESPULE|RESPULES|CREAM|OINTMENT|GEL|DROPS|SACHET|SACHETS)\b",
    re.IGNORECASE
)

COMPOSITION_CONTEXT_PATTERN = re.compile(
    r"\b(EACH|CONTAINS?|COMPOSITION|COMPOSITIONS|EQUIVALENT|EQ\.?|ACTIVE|INGREDIENT)\b",
    re.IGNORECASE
)

STRENGTH_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(MG/ML|MCG/ML|MG|MCG|UG|G|ML|IU|I\.U\.|%)\b",
    re.IGNORECASE
)

DATE_PATTERN = (
    r"(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[.\-/\s]*\d{2,4}"
    r"|\d{1,2}[./\-]\d{2,4}"
)

MFG_PATTERN = re.compile(rf"\bMF[GD]\.?(?:\s*DATE)?\s*[:.\-]?\s*({DATE_PATTERN})", re.IGNORECASE)
EXP_PATTERN = re.compile(rf"\bEXP(?:IRY)?\.?(?:\s*DATE)?\s*[:.\-]?\s*({DATE_PATTERN})", re.IGNORECASE)
MFG_LABEL_ONLY = re.compile(r"^MF[GD]\.?\s*(?:DATE)?\s*[:.\-]?\s*$", re.IGNORECASE)
EXP_LABEL_ONLY = re.compile(r"^EXP(?:IRY)?\.?\s*(?:DATE)?\s*[:.\-]?\s*$", re.IGNORECASE)
DATE_ONLY = re.compile(rf"^({DATE_PATTERN})[.,;:'\"]*$", re.IGNORECASE)

BATCH_LABEL_WITH_VALUE = re.compile(
    r"(?:B\s*[:.]?\s*N[O0]\.?|BATCH(?:\s*N[O0]\.?)?|LOT(?:\s*N[O0]\.?)?)\s*[:.\-]?\s*([A-Z0-9./\-]{3,})",
    re.IGNORECASE
)
BATCH_LABEL_ONLY = re.compile(
    r"^(?:B\s*[:.]?\s*N[O0]\.?|BATCH(?:\s*N[O0]\.?)?|LOT(?:\s*N[O0]\.?)?)\s*[:.\-]?\s*$",
    re.IGNORECASE
)
BARE_VALUE = re.compile(r"^[A-Z0-9][A-Z0-9./\-]{2,}$", re.IGNORECASE)
CODE_LIKE_PATTERN = re.compile(r"^[A-Z]{1,4}\d{2,}[A-Z0-9]*$", re.IGNORECASE)

# ============================================================
# BASIC HELPERS
# ============================================================

def clean_ocr_value(text):
    if not text: return ""
    return text.strip().strip(" .,:;'\"")

def normalize_spaces(text):
    return re.sub(r"\s+", " ", text).strip()

def get_words(text):
    return re.findall(r"[A-Za-z]+", text.upper())

def contains_manufacturer_suffix(text):
    normalized = re.sub(r"\.", "", text.upper())
    for suffix in MANUFACTURER_SUFFIXES:
        suffix_normalized = re.sub(r"\.", "", suffix.upper())
        if re.search(rf"\b{re.escape(suffix_normalized)}\b", normalized):
            return True
    return False

def is_date_value(text):
    return bool(DATE_ONLY.fullmatch(clean_ocr_value(text).upper()))

def is_sentence_like(text):
    words = get_words(text)
    if not words: return True
    sentence_hits = sum(1 for word in words if word in SENTENCE_WORDS)
    if sentence_hits >= 2: return True
    if len(words) >= 5: return True
    return False

# ============================================================
# MEDICINE NAME EXTRACTION
# ============================================================

def is_valid_brand_candidate(text):
    text = normalize_spaces(text)
    upper = text.upper()

    if len(text) < 3 or len(text) > 35: return False
    if not re.search(r"[A-Za-z]", text): return False
    if is_date_value(text): return False
    if STRENGTH_PATTERN.search(text): return False
    if BATCH_LABEL_WITH_VALUE.search(upper) or BATCH_LABEL_ONLY.match(upper): return False
    if MFG_PATTERN.search(upper) or EXP_PATTERN.search(upper): return False
    if MFG_LABEL_ONLY.match(upper) or EXP_LABEL_ONLY.match(upper): return False
    if contains_manufacturer_suffix(upper): return False
    if " " not in upper and "-" not in upper and CODE_LIKE_PATTERN.match(upper): return False
    if MANUFACTURER_LABEL_PATTERN.search(upper): return False
    if DOSAGE_FORM_PATTERN.fullmatch(upper): return False

    words = get_words(text)
    if not words: return False
    if sum(1 for word in words if word in BRAND_BLOCKLIST) == len(words): return False

    packaging_reject_words = {"CAUTION", "WARNING", "PRESCRIPTION", "SCHEDULE", "STORAGE", "ADDRESS", "DOSAGE", "PHYSICIAN", "CHILDREN", "COMPOSITION", "EXCIPIENTS", "PREGNANCY"}
    if any(word in packaging_reject_words for word in words): return False
    if is_sentence_like(text): return False
    if re.search(r"\b(PLOT|ROAD|STREET|VILLAGE|DISTRICT|PIN)\b", upper): return False
    return True

def calculate_brand_score(item):
    text = normalize_spaces(item.get("text", ""))
    confidence = float(item.get("confidence", 0)) if isinstance(item.get("confidence"), (int, float, str)) else 0
    votes = int(item.get("votes", 1)) if isinstance(item.get("votes"), (int, str)) else 1

    score = confidence + min(votes, 10) * 0.12
    words = get_words(text)
    if len(words) == 1: score += 0.30
    elif len(words) == 2: score += 0.15
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9\-]*(?:\s[A-Za-z0-9\-]+)?", text): score += 0.20
    if text.isupper(): score += 0.08
    if len(text) > 25: score -= 0.20
    return score

def extract_brand_name(ranked_data):
    grouped = {}
    for item in ranked_data:
        text = normalize_spaces(item.get("text", ""))
        candidate = STRENGTH_PATTERN.sub("", text).strip()
        if candidate: text = candidate
        if not is_valid_brand_candidate(text): continue

        key = text.upper()
        scored_item = dict(item)
        scored_item["text"] = text
        score = calculate_brand_score(scored_item)

        if key not in grouped: grouped[key] = {"text": text, "score": score, "count": 1}
        else:
            grouped[key]["score"] = max(grouped[key]["score"], score)
            grouped[key]["count"] += 1

    if not grouped: return ""
    candidates = list(grouped.values())
    for candidate in candidates:
        candidate["final_score"] = candidate["score"] + min(candidate["count"] - 1, 3) * 0.15
    candidates.sort(key=lambda item: item["final_score"], reverse=True)
    return candidates[0]["text"] if candidates[0]["final_score"] >= 0.60 else ""

# ============================================================
# GENERIC / COMPOSITION NAME FALLBACK
# ============================================================

def extract_generic_composition(lines):
    best_candidate = ""
    fallback_candidate = ""
    for line in lines:
        text = normalize_spaces(line)
        if len(text) < 5 or len(text) > 100: continue

        # Block sentences completely from becoming generic names
        if is_sentence_like(text): continue

        upper = text.upper()
        if any(w in upper for w in ("EACH ", "CONTAINS", "EXCIPIENTS", "DOSAGE", "STORE")): continue

        has_standard = bool(re.search(r"\b(IP|BP|USP)\b", text, re.IGNORECASE))
        has_form = bool(DOSAGE_FORM_PATTERN.search(text))

        if has_standard:
            best_candidate = text
            break
        elif has_form and len(get_words(text)) >= 2 and not fallback_candidate:
            fallback_candidate = text
    return best_candidate or fallback_candidate

# ============================================================
# MANUFACTURER EXTRACTION
# ============================================================

def clean_manufacturer_text(text):
    text = normalize_spaces(text)
    text = re.sub(r"^(?:MANUFACTURED|MANUFACTURER|MFD|MFG|MARKETED|DISTRIBUTED|PACKED)\.?\s*(?:BY)?\s*[:.\-]?\s*", "", text, flags=re.IGNORECASE)
    return normalize_spaces(text)

def is_complete_manufacturer_candidate(text):
    text = normalize_spaces(text)
    if not text: return False

    # Exclude warnings from being caught as manufacturers
    if is_sentence_like(text) or len(text) > 65: return False
    if any(word in text.upper() for word in ["IMPORTANT", "PREGNANCY", "WARNING", "CAUTION"]): return False

    words = get_words(text)
    if len(words) < 2: return False
    generic_company_words = {"PRIVATE", "LIMITED", "PVT", "LTD", "PHARMA", "PHARMACEUTICAL", "PHARMACEUTICALS", "LABORATORIES", "LABS", "HEALTHCARE", "LIFESCIENCES", "BIOSCIENCES", "DRUGS", "COMPANY"}
    meaningful_words = [word for word in words if word not in generic_company_words]
    if not meaningful_words: return False
    if not contains_manufacturer_suffix(text.upper()): return False
    return True

def extract_manufacturer(lines):
    for i, line in enumerate(lines):
        text = normalize_spaces(line)
        if not MANUFACTURER_LABEL_PATTERN.search(text): continue
        same_line = clean_manufacturer_text(text)
        if is_complete_manufacturer_candidate(same_line): return same_line

        nearby_parts = []
        for distance in range(1, 4):
            index = i + distance
            if index >= len(lines): break
            candidate = normalize_spaces(lines[index])
            upper = candidate.upper()
            if BATCH_LABEL_ONLY.match(upper) or MFG_LABEL_ONLY.match(upper) or EXP_LABEL_ONLY.match(upper) or DATE_ONLY.match(clean_ocr_value(upper)) or any(w in upper for w in ["IMPORTANT", "PREGNANCY", "WARNING"]): break
            nearby_parts.append(candidate)
            combined = normalize_spaces(" ".join(nearby_parts))
            if is_complete_manufacturer_candidate(combined): return combined

    candidates = []
    for i, line in enumerate(lines):
        text = normalize_spaces(line)
        if is_complete_manufacturer_candidate(text): candidates.append(text)
        if i + 1 < len(lines):
            combined = normalize_spaces(f"{line} {lines[i + 1]}")
            if is_complete_manufacturer_candidate(combined): candidates.append(combined)

    candidates = [c for c in candidates if len(c) <= 100]
    if not candidates: return ""
    candidates.sort(key=lambda value: (len(get_words(value)), len(value)), reverse=True)
    return candidates[0]

# ============================================================
# STRENGTH EXTRACTION
# ============================================================

def normalize_strength(value, unit):
    unit = unit.lower()
    if unit == "ug": unit = "mcg"
    if unit == "i.u.": unit = "iu"
    return f"{value} {unit}"

def get_strengths_from_text(text):
    matches = STRENGTH_PATTERN.findall(text)
    strengths = []
    for value, unit in matches:
        normalized = normalize_strength(value, unit)
        if normalized not in strengths: strengths.append(normalized)
    return strengths

def extract_strength(lines):
    contextual_strengths = []
    dosage_form_strengths = []
    all_strength_occurrences = {}

    for i, line in enumerate(lines):
        text = normalize_spaces(line)
        strengths = get_strengths_from_text(text)
        for strength in strengths:
            all_strength_occurrences[strength] = all_strength_occurrences.get(strength, 0) + 1
        if not strengths: continue
        if COMPOSITION_CONTEXT_PATTERN.search(text):
            for strength in strengths:
                if strength not in contextual_strengths: contextual_strengths.append(strength)
        if DOSAGE_FORM_PATTERN.search(text):
            for strength in strengths:
                if strength not in dosage_form_strengths: dosage_form_strengths.append(strength)
        if i > 0 and COMPOSITION_CONTEXT_PATTERN.search(normalize_spaces(lines[i - 1])):
            for strength in strengths:
                if strength not in contextual_strengths: contextual_strengths.append(strength)
        if i + 1 < len(lines) and COMPOSITION_CONTEXT_PATTERN.search(normalize_spaces(lines[i + 1])):
            for strength in strengths:
                if strength not in contextual_strengths: contextual_strengths.append(strength)

    if contextual_strengths: return " + ".join(contextual_strengths)
    if dosage_form_strengths: return " + ".join(dosage_form_strengths)
    repeated = [strength for strength, count in all_strength_occurrences.items() if count >= 2]
    if repeated: return " + ".join(repeated)
    if len(all_strength_occurrences) == 1: return next(iter(all_strength_occurrences))
    return ""

# ============================================================
# BATCH NUMBER EXTRACTION
# ============================================================

def normalize_batch_value(batch_value):
    batch_value = clean_ocr_value(batch_value)
    if re.fullmatch(r"\d+(?:\.\d+)+", batch_value):
        batch_value = batch_value.replace(".", "")
    return batch_value

def is_valid_batch_candidate(candidate):
    candidate = clean_ocr_value(candidate)
    upper = candidate.upper()
    if len(candidate) < 3 or len(candidate) > 30: return False
    if is_date_value(candidate): return False
    if MFG_LABEL_ONLY.match(upper) or EXP_LABEL_ONLY.match(upper) or BATCH_LABEL_ONLY.match(upper): return False
    if upper in {"MFG", "MFD", "EXP", "EXPIRY", "BATCH", "LOT", "MRP", "DATE"}: return False
    return bool(BARE_VALUE.fullmatch(upper))

def extract_batch_number(lines):
    for line in lines:
        upper = line.upper().strip()
        match = BATCH_LABEL_WITH_VALUE.search(upper)
        if match:
            batch_value = normalize_batch_value(match.group(1))
            if is_valid_batch_candidate(batch_value): return batch_value

    for i, line in enumerate(lines):
        upper = line.upper().strip()
        if not BATCH_LABEL_ONLY.match(upper): continue
        for distance in range(1, 4):
            index = i + distance
            if index >= len(lines): break
            candidate = normalize_batch_value(lines[index])
            if is_valid_batch_candidate(candidate): return candidate
        for distance in range(1, 4):
            index = i - distance
            if index < 0: break
            candidate = normalize_batch_value(lines[index])
            if is_valid_batch_candidate(candidate): return candidate
    return ""

# ============================================================
# DATE EXTRACTION
# ============================================================

def extract_nearby_date(lines, label_index):
    for distance in range(1, 4):
        index = label_index + distance
        if index >= len(lines): break
        candidate = clean_ocr_value(lines[index]).upper()
        match = DATE_ONLY.fullmatch(candidate)
        if match: return clean_ocr_value(match.group(1))
    for distance in range(1, 4):
        index = label_index - distance
        if index < 0: break
        candidate = clean_ocr_value(lines[index]).upper()
        match = DATE_ONLY.fullmatch(candidate)
        if match: return clean_ocr_value(match.group(1))
    return ""

def extract_dates(lines):
    mfg_date = ""
    exp_date = ""
    for line in lines:
        upper = line.upper().strip()
        if re.search(r"\bMF[GD]\.?\s*[:.\-]?\s*BY\b", upper): continue
        if not mfg_date:
            match = MFG_PATTERN.search(upper)
            if match: mfg_date = clean_ocr_value(match.group(1))
        if not exp_date:
            match = EXP_PATTERN.search(upper)
            if match: exp_date = clean_ocr_value(match.group(1))

    for i, line in enumerate(lines):
        upper = line.upper().strip()
        if not mfg_date and MFG_LABEL_ONLY.match(upper): mfg_date = extract_nearby_date(lines, i)
        if not exp_date and EXP_LABEL_ONLY.match(upper): exp_date = extract_nearby_date(lines, i)
        if mfg_date and exp_date: break
    return mfg_date, exp_date

# ============================================================
# FINAL FALLBACK EXTRACTOR
# ============================================================

def extract_medicine_info_fallback(cleaned_data, ranked_data):
    sequential_lines = [item["text"] for item in cleaned_data if item.get("text", "").strip()]
    brand = extract_brand_name(ranked_data)
    generic = extract_generic_composition(sequential_lines)
    manufacturer = extract_manufacturer(sequential_lines)
    strength = extract_strength(sequential_lines)
    batch_number = extract_batch_number(sequential_lines)
    manufacturing_date, expiry_date = extract_dates(sequential_lines)

    return {
        "medicine_name": brand or generic,
        "manufacturer": manufacturer,
        "generic_name": generic,
        "strength": strength,
        "composition": "",
        "batch_number": batch_number,
        "manufacturing_date": manufacturing_date,
        "expiry_date": expiry_date,
        "dosage": "",
        "storage": "",
        "warnings": "",
        "pack_size": ""
    }