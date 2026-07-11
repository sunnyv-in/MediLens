import re


# ============================================================
# GENERIC KEYWORDS AND PATTERNS
# ============================================================

# These are packaging/instruction words, not medicine names.
# A brand candidate containing these words is usually unreliable.
BRAND_BLOCKLIST = {
    "TABLETS", "TABLET", "CAPSULES", "CAPSULE",
    "INJECTION", "INJECTIONS", "SYRUP", "SUSPENSION",
    "RESPULE", "RESPULES", "CREAM", "OINTMENT", "GEL",
    "DROPS", "SACHET", "SACHETS",

    "IP", "BP", "USP",

    "SCHEDULE", "PRESCRIPTION", "DRUG", "CAUTION",
    "WARNING", "WARNINGS",

    "STORE", "STORAGE", "KEEP", "CHILDREN", "REACH",
    "TEMPERATURE", "MOISTURE", "LIGHT",

    "MRP", "PRICE", "RS", "INCLUSIVE", "TAXES",

    "BATCH", "LOT", "MFG", "MFD", "EXP", "EXPIRY",
    "MANUFACTURED", "MANUFACTURER", "MARKETED",

    "LTD", "LIMITED", "PVT", "PRIVATE",
    "PHARMA", "PHARMACEUTICALS", "PHARMACEUTICAL",
    "LABORATORIES", "LABS", "HEALTHCARE",
    "LIFESCIENCES", "BIOSCIENCES", "COMPANY", "DRUGS",

    "REGD", "OFF", "OFFICE", "ADDRESS", "LIC", "LICENSE",
    "NO", "PLOT", "ROAD", "STREET", "VILLAGE", "DISTRICT",
    "STATE", "PIN", "INDIA",

    "SWALLOWED", "CHEWED", "CRUSHED",
    "PHYSICIAN", "DIRECTED", "DOSAGE",
    "EXCIPIENTS", "COLOUR", "COLOR",

    "EACH", "CONTAINS", "COMPOSITION", "COMPOSITIONS",
    "EQUIVALENT", "EQ", "TO",

    "AND", "OR", "BY", "FOR", "THE", "OF", "IN", "WITH",
    "FROM", "THIS", "THAT", "MONTH", "MONTHS"
}


# Words suggesting normal sentence/instruction text rather than a brand.
SENTENCE_WORDS = {
    "TAKE", "USE", "USED", "KEEP", "STORE", "CONSULT",
    "DIRECTED", "PRESCRIBED", "PHYSICIAN", "DOCTOR",
    "SHOULD", "MUST", "BEFORE", "AFTER", "DAILY",
    "ONCE", "TWICE", "THRICE", "SWALLOW", "SWALLOWED",
    "CHEW", "CHEWED", "CRUSH", "CRUSHED",
    "MONTH", "MONTHS", "DAY", "DAYS",
    "CHILD", "CHILDREN", "REACH"
}


MANUFACTURER_SUFFIXES = [
    "PRIVATE LIMITED",
    "PVT. LTD.",
    "PVT LTD",
    "PVT. LTD",
    "LIMITED",
    "LTD.",
    "LTD",
    "PHARMACEUTICALS",
    "PHARMACEUTICAL",
    "PHARMA",
    "LABORATORIES",
    "LABS",
    "HEALTHCARE",
    "LIFESCIENCES",
    "BIOSCIENCES",
    "DRUGS"
]


MANUFACTURER_LABEL_PATTERN = re.compile(
    r"\b("
    r"MANUFACTURED|MANUFACTURER|MFD|MFG|"
    r"MARKETED|DISTRIBUTED|PACKED"
    r")\b"
    r"\s*(?:BY)?\s*[:.\-]?",
    re.IGNORECASE
)


DOSAGE_FORM_PATTERN = re.compile(
    r"\b("
    r"TABLET|TABLETS|CAPSULE|CAPSULES|"
    r"INJECTION|INJECTIONS|SYRUP|SUSPENSION|"
    r"RESPULE|RESPULES|CREAM|OINTMENT|GEL|"
    r"DROPS|SACHET|SACHETS"
    r")\b",
    re.IGNORECASE
)


COMPOSITION_CONTEXT_PATTERN = re.compile(
    r"\b("
    r"EACH|CONTAINS?|COMPOSITION|COMPOSITIONS|"
    r"EQUIVALENT|EQ\.?|ACTIVE|INGREDIENT"
    r")\b",
    re.IGNORECASE
)


STRENGTH_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*"
    r"(MG|MCG|UG|G|ML|IU|I\.U\.|%|MG/ML|MCG/ML)\b",
    re.IGNORECASE
)


DATE_PATTERN = (
    r"(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)"
    r"[.\-/\s]*\d{2,4}"
    r"|"
    r"\d{1,2}[./\-]\d{2,4}"
)


MFG_PATTERN = re.compile(
    rf"\bMF[GD]\.?"
    rf"(?:\s*DATE)?"
    rf"\s*[:.\-]?\s*({DATE_PATTERN})",
    re.IGNORECASE
)


EXP_PATTERN = re.compile(
    rf"\bEXP(?:IRY)?\.?"
    rf"(?:\s*DATE)?"
    rf"\s*[:.\-]?\s*({DATE_PATTERN})",
    re.IGNORECASE
)


MFG_LABEL_ONLY = re.compile(
    r"^MF[GD]\.?"
    r"\s*(?:DATE)?"
    r"\s*[:.\-]?\s*$",
    re.IGNORECASE
)


EXP_LABEL_ONLY = re.compile(
    r"^EXP(?:IRY)?\.?"
    r"\s*(?:DATE)?"
    r"\s*[:.\-]?\s*$",
    re.IGNORECASE
)


DATE_ONLY = re.compile(
    rf"^({DATE_PATTERN})[.,;:'\"]*$",
    re.IGNORECASE
)


BATCH_LABEL_WITH_VALUE = re.compile(
    r"(?:"
    r"B\.?\s*[:.]?\s*NO\.?"
    r"|BATCH(?:\s*NO\.?)?"
    r"|LOT(?:\s*NO\.?)?"
    r")"
    r"\s*[:.\-]?\s*"
    r"([A-Z0-9./\-]{3,})",
    re.IGNORECASE
)


BATCH_LABEL_ONLY = re.compile(
    r"^(?:"
    r"B\.?\s*[:.]?\s*NO\.?"
    r"|BATCH(?:\s*NO\.?)?"
    r"|LOT(?:\s*NO\.?)?"
    r")"
    r"\s*[:.\-]?\s*$",
    re.IGNORECASE
)


BARE_VALUE = re.compile(
    r"^[A-Z0-9][A-Z0-9./\-]{2,}$",
    re.IGNORECASE
)


# ============================================================
# BASIC HELPERS
# ============================================================

def clean_ocr_value(text):
    """
    Removes common OCR punctuation around a value.

    Examples:
        03/2026.   -> 03/2026
        :02/2028   -> 02/2028
        GP2409A:   -> GP2409A
    """

    if not text:
        return ""

    return text.strip().strip(" .,:;'\"")


def normalize_spaces(text):
    return re.sub(r"\s+", " ", text).strip()


def get_words(text):
    return re.findall(r"[A-Za-z]+", text.upper())


def contains_manufacturer_suffix(text):
    upper = text.upper()

    return any(
        suffix in upper
        for suffix in MANUFACTURER_SUFFIXES
    )


def is_date_value(text):
    cleaned = clean_ocr_value(text).upper()
    return bool(DATE_ONLY.fullmatch(cleaned))


def is_sentence_like(text):
    """
    Rejects obvious instruction/sentence fragments.

    This does not use known medicine names.
    """

    words = get_words(text)

    if not words:
        return True

    sentence_hits = sum(
        1 for word in words
        if word in SENTENCE_WORDS
    )

    # Multiple sentence/instruction words are suspicious.
    if sentence_hits >= 2:
        return True

    # Long multi-word strings are less likely to be brand names.
    if len(words) >= 5:
        return True

    return False


# ============================================================
# MEDICINE NAME EXTRACTION
# ============================================================

def is_valid_brand_candidate(text):
    """
    Generic validation for a possible medicine/brand name.
    """

    text = normalize_spaces(text)
    upper = text.upper()

    if len(text) < 3 or len(text) > 35:
        return False

    # Must contain at least one alphabetic character.
    if not re.search(r"[A-Za-z]", text):
        return False

    # Reject dates.
    if is_date_value(text):
        return False

    # Reject strengths.
    if STRENGTH_PATTERN.search(text):
        return False

    # Reject batch/date labels.
    if BATCH_LABEL_WITH_VALUE.search(upper):
        return False

    if BATCH_LABEL_ONLY.match(upper):
        return False

    if MFG_PATTERN.search(upper):
        return False

    if EXP_PATTERN.search(upper):
        return False

    if MFG_LABEL_ONLY.match(upper):
        return False

    if EXP_LABEL_ONLY.match(upper):
        return False

    # Reject manufacturer/company lines.
    if contains_manufacturer_suffix(upper):
        return False

    if MANUFACTURER_LABEL_PATTERN.search(upper):
        return False

    # Reject dosage-form-only lines.
    if DOSAGE_FORM_PATTERN.fullmatch(upper):
        return False

    words = get_words(text)

    if not words:
        return False

    # If every meaningful word is packaging/instruction text,
    # it cannot be a useful medicine name.
    blocked_count = sum(
        1 for word in words
        if word in BRAND_BLOCKLIST
    )

    if blocked_count == len(words):
        return False

    # Reject if any highly specific packaging word is present.
    packaging_reject_words = {
        "CAUTION", "WARNING", "PRESCRIPTION",
        "SCHEDULE", "STORAGE", "ADDRESS",
        "DOSAGE", "PHYSICIAN", "CHILDREN",
        "COMPOSITION", "EXCIPIENTS"
    }

    if any(word in packaging_reject_words for word in words):
        return False

    if is_sentence_like(text):
        return False

    # Avoid address-like lines.
    if re.search(
        r"\b(PLOT|ROAD|STREET|VILLAGE|DISTRICT|PIN)\b",
        upper
    ):
        return False

    return True


def calculate_brand_score(item):
    """
    Generic score based only on OCR evidence and text shape.
    """

    text = normalize_spaces(item.get("text", ""))

    try:
        confidence = float(item.get("confidence", 0))
    except (TypeError, ValueError):
        confidence = 0

    try:
        votes = int(item.get("votes", 1))
    except (TypeError, ValueError):
        votes = 1

    score = confidence
    score += min(votes, 10) * 0.12

    words = get_words(text)

    # Medicine brands are often short.
    if len(words) == 1:
        score += 0.30

    elif len(words) == 2:
        score += 0.15

    # Mixed alphabetic/alphanumeric brand forms are common.
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9\-]*", text):
        score += 0.20

    # All-uppercase packaging text may indicate prominent brand text,
    # but only a small bonus because warnings may also be uppercase.
    if text.isupper():
        score += 0.08

    # Very long text is less likely to be a brand.
    if len(text) > 25:
        score -= 0.20

    return score


def extract_brand_name(ranked_data):
    """
    Selects the strongest plausible medicine-name candidate
    without using a known medicine database.
    """

    candidates = []

    for item in ranked_data:
        text = normalize_spaces(item.get("text", ""))

        if not is_valid_brand_candidate(text):
            continue

        score = calculate_brand_score(item)

        candidates.append({
            "text": text,
            "score": score
        })

    if not candidates:
        return ""

    candidates.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    best = candidates[0]

    # Conservative acceptance threshold.
    if best["score"] < 0.60:
        return ""

    return best["text"]


# ============================================================
# GENERIC / COMPOSITION NAME FALLBACK
# ============================================================

def extract_generic_composition(lines):
    """
    Attempts to find a generic medicine/composition description.

    Examples of useful context:
        Paracetamol Tablets IP
        Amoxicillin Capsules IP

    No known medicine names are hardcoded.
    """

    best_candidate = ""

    for line in lines:
        text = normalize_spaces(line)

        if len(text) < 5 or len(text) > 100:
            continue

        has_standard = bool(
            re.search(r"\b(IP|BP|USP)\b", text, re.IGNORECASE)
        )

        has_form = bool(
            DOSAGE_FORM_PATTERN.search(text)
        )

        if has_standard and has_form:
            best_candidate = text
            break

    return best_candidate


# ============================================================
# MANUFACTURER EXTRACTION
# ============================================================

def clean_manufacturer_text(text):
    """
    Removes labels while preserving the company name.
    """

    text = normalize_spaces(text)

    text = re.sub(
        r"^(?:"
        r"MANUFACTURED|MANUFACTURER|MFD|MFG|"
        r"MARKETED|DISTRIBUTED|PACKED"
        r")"
        r"\.?\s*(?:BY)?\s*[:.\-]?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    return normalize_spaces(text)


def is_complete_manufacturer_candidate(text):
    """
    Prevents meaningless fragments such as:
        Private Limited
        Pvt Ltd
        Pharmaceuticals Ltd
    """

    text = normalize_spaces(text)

    if not text:
        return False

    upper = text.upper()
    words = get_words(text)

    if len(words) < 2:
        return False

    generic_company_words = {
        "PRIVATE", "LIMITED", "PVT", "LTD",
        "PHARMA", "PHARMACEUTICAL",
        "PHARMACEUTICALS", "LABORATORIES",
        "LABS", "HEALTHCARE", "LIFESCIENCES",
        "BIOSCIENCES", "DRUGS", "COMPANY"
    }

    meaningful_words = [
        word for word in words
        if word not in generic_company_words
    ]

    # At least one actual identifying word should remain.
    if not meaningful_words:
        return False

    if not contains_manufacturer_suffix(upper):
        return False

    return True


def extract_manufacturer(lines):
    """
    Generic manufacturer extraction strategy:

    Priority 1:
        Explicit labels such as Manufactured by / Mfd by / Marketed by.

    Priority 2:
        Complete company-like OCR lines containing common company suffixes.

    Can combine nearby split OCR lines when necessary.
    """

    # --------------------------------------------------------
    # Priority 1: Explicit manufacturer labels
    # --------------------------------------------------------

    for i, line in enumerate(lines):
        text = normalize_spaces(line)

        if not MANUFACTURER_LABEL_PATTERN.search(text):
            continue

        same_line = clean_manufacturer_text(text)

        if is_complete_manufacturer_candidate(same_line):
            return same_line

        # OCR may split:
        #
        # Manufactured by:
        # Example Pharma
        # Private Limited
        #
        nearby_parts = []

        for distance in range(1, 4):
            index = i + distance

            if index >= len(lines):
                break

            candidate = normalize_spaces(lines[index])

            # Stop if we reach another clearly unrelated field.
            upper = candidate.upper()

            if (
                BATCH_LABEL_ONLY.match(upper)
                or MFG_LABEL_ONLY.match(upper)
                or EXP_LABEL_ONLY.match(upper)
                or DATE_ONLY.match(clean_ocr_value(upper))
            ):
                break

            nearby_parts.append(candidate)

            combined = normalize_spaces(
                " ".join(nearby_parts)
            )

            if is_complete_manufacturer_candidate(combined):
                return combined

    # --------------------------------------------------------
    # Priority 2: Standalone company-like lines
    # --------------------------------------------------------

    candidates = []

    for i, line in enumerate(lines):
        text = normalize_spaces(line)

        if is_complete_manufacturer_candidate(text):
            candidates.append(text)

        # Try combining current + next line for OCR-split company names.
        if i + 1 < len(lines):
            combined = normalize_spaces(
                f"{line} {lines[i + 1]}"
            )

            if is_complete_manufacturer_candidate(combined):
                candidates.append(combined)

    if not candidates:
        return ""

    # Prefer a useful complete company name, but avoid extremely
    # long address-like text.
    candidates = [
        candidate
        for candidate in candidates
        if len(candidate) <= 100
    ]

    if not candidates:
        return ""

    candidates.sort(
        key=lambda value: (
            len(get_words(value)),
            len(value)
        ),
        reverse=True
    )

    return candidates[0]


# ============================================================
# STRENGTH EXTRACTION
# ============================================================

def normalize_strength(value, unit):
    unit = unit.lower()

    if unit == "ug":
        unit = "mcg"

    if unit == "i.u.":
        unit = "iu"

    return f"{value} {unit}"


def get_strengths_from_text(text):
    matches = STRENGTH_PATTERN.findall(text)

    strengths = []

    for value, unit in matches:
        normalized = normalize_strength(value, unit)

        if normalized not in strengths:
            strengths.append(normalized)

    return strengths


def extract_strength(lines):
    """
    Generic context-aware strength extraction.

    Priority:
    1. Composition/context lines.
    2. Lines containing medicine dosage forms.
    3. Repeated strength values across OCR output.
    4. Conservative fallback to strongest available value.

    This avoids blindly joining every mg/ml/g value in the package.
    """

    contextual_strengths = []
    dosage_form_strengths = []

    all_strength_occurrences = {}

    for i, line in enumerate(lines):
        text = normalize_spaces(line)

        strengths = get_strengths_from_text(text)

        # Count all occurrences.
        for strength in strengths:
            all_strength_occurrences[strength] = (
                all_strength_occurrences.get(strength, 0) + 1
            )

        if not strengths:
            continue

        # Strong context:
        # composition, contains, equivalent, each, etc.
        if COMPOSITION_CONTEXT_PATTERN.search(text):
            for strength in strengths:
                if strength not in contextual_strengths:
                    contextual_strengths.append(strength)

        # Dosage-form context.
        if DOSAGE_FORM_PATTERN.search(text):
            for strength in strengths:
                if strength not in dosage_form_strengths:
                    dosage_form_strengths.append(strength)

        # Check nearby previous line for composition context.
        if i > 0:
            previous = normalize_spaces(lines[i - 1])

            if COMPOSITION_CONTEXT_PATTERN.search(previous):
                for strength in strengths:
                    if strength not in contextual_strengths:
                        contextual_strengths.append(strength)

        # Check nearby next line for composition context.
        if i + 1 < len(lines):
            next_line = normalize_spaces(lines[i + 1])

            if COMPOSITION_CONTEXT_PATTERN.search(next_line):
                for strength in strengths:
                    if strength not in contextual_strengths:
                        contextual_strengths.append(strength)

    # Priority 1
    if contextual_strengths:
        return " + ".join(contextual_strengths)

    # Priority 2
    if dosage_form_strengths:
        return " + ".join(dosage_form_strengths)

    # Priority 3:
    # OCR repetition across multiple processed images is useful evidence.
    repeated = [
        strength
        for strength, count in all_strength_occurrences.items()
        if count >= 2
    ]

    if repeated:
        return " + ".join(repeated)

    # Priority 4:
    # If exactly one strength exists in the entire OCR output,
    # it is a reasonable conservative fallback.
    if len(all_strength_occurrences) == 1:
        return next(iter(all_strength_occurrences))

    # Multiple unrelated values with no useful context:
    # don't guess.
    return ""


# ============================================================
# BATCH NUMBER EXTRACTION
# ============================================================

def normalize_batch_value(batch_value):
    batch_value = clean_ocr_value(batch_value)

    # OCR sometimes inserts dots inside a numeric batch number.
    #
    # Example:
    # 601.0002 -> 6010002
    #
    # Only remove dots if the entire value is numeric groups
    # separated by dots.
    if re.fullmatch(r"\d+(?:\.\d+)+", batch_value):
        batch_value = batch_value.replace(".", "")

    return batch_value


def is_valid_batch_candidate(candidate):
    candidate = clean_ocr_value(candidate)
    upper = candidate.upper()

    if len(candidate) < 3 or len(candidate) > 30:
        return False

    if is_date_value(candidate):
        return False

    if MFG_LABEL_ONLY.match(upper):
        return False

    if EXP_LABEL_ONLY.match(upper):
        return False

    if BATCH_LABEL_ONLY.match(upper):
        return False

    # Reject pure alphabetic packaging-label-like values.
    if upper in {
        "MFG", "MFD", "EXP", "EXPIRY",
        "BATCH", "LOT", "MRP", "DATE"
    }:
        return False

    return bool(BARE_VALUE.fullmatch(upper))


def extract_batch_number(lines):
    """
    Extracts batch number only with batch/lot label evidence.

    Handles:
        B.No: GP2409A
        B. No : GP2409A
        Batch No: ABC123
        Lot No: XY789
        B:NO.601.0002

    Also handles OCR splitting:
        B. No :
        GP2409A
    """

    # --------------------------------------------------------
    # Case 1: Label + value on same OCR line
    # --------------------------------------------------------

    for line in lines:
        upper = line.upper().strip()

        match = BATCH_LABEL_WITH_VALUE.search(upper)

        if match:
            batch_value = normalize_batch_value(
                match.group(1)
            )

            if is_valid_batch_candidate(batch_value):
                return batch_value

    # --------------------------------------------------------
    # Case 2: Label and value split across OCR detections
    # --------------------------------------------------------

    for i, line in enumerate(lines):
        upper = line.upper().strip()

        if not BATCH_LABEL_ONLY.match(upper):
            continue

        # Prefer following lines.
        for distance in range(1, 4):
            index = i + distance

            if index >= len(lines):
                break

            candidate = normalize_batch_value(
                lines[index]
            )

            if is_valid_batch_candidate(candidate):
                return candidate

        # Then nearby previous lines.
        for distance in range(1, 4):
            index = i - distance

            if index < 0:
                break

            candidate = normalize_batch_value(
                lines[index]
            )

            if is_valid_batch_candidate(candidate):
                return candidate

    return ""


# ============================================================
# DATE EXTRACTION
# ============================================================

def extract_nearby_date(lines, label_index):
    """
    Finds a date close to an OCR-split MFG/EXP label.

    Checks following lines first, then previous lines.
    """

    # Prefer after label.
    for distance in range(1, 4):
        index = label_index + distance

        if index >= len(lines):
            break

        candidate = clean_ocr_value(
            lines[index]
        ).upper()

        match = DATE_ONLY.fullmatch(candidate)

        if match:
            return clean_ocr_value(match.group(1))

    # Then before label.
    for distance in range(1, 4):
        index = label_index - distance

        if index < 0:
            break

        candidate = clean_ocr_value(
            lines[index]
        ).upper()

        match = DATE_ONLY.fullmatch(candidate)

        if match:
            return clean_ocr_value(match.group(1))

    return ""


def extract_dates(lines):
    """
    Generic manufacturing and expiry date extraction.

    Handles:
        MFG: 03/2026
        MFD. JAN.26
        EXP: 02/2028
        EXP. DEC.27

    Also supports split OCR:
        Mfg:
        03/2026

    And imperfect OCR ordering:
        03/2026
        Mfg:
    """

    mfg_date = ""
    exp_date = ""

    # --------------------------------------------------------
    # First pass: same-line values
    # --------------------------------------------------------

    for line in lines:
        upper = line.upper().strip()

        # Avoid manufacturer phrases:
        # Mfd by XYZ Pharmaceuticals Ltd
        if re.search(
            r"\bMF[GD]\.?\s*[:.\-]?\s*BY\b",
            upper
        ):
            continue

        if not mfg_date:
            match = MFG_PATTERN.search(upper)

            if match:
                mfg_date = clean_ocr_value(
                    match.group(1)
                )

        if not exp_date:
            match = EXP_PATTERN.search(upper)

            if match:
                exp_date = clean_ocr_value(
                    match.group(1)
                )

    # --------------------------------------------------------
    # Second pass: split OCR values
    # --------------------------------------------------------

    for i, line in enumerate(lines):
        upper = line.upper().strip()

        if not mfg_date and MFG_LABEL_ONLY.match(upper):
            mfg_date = extract_nearby_date(lines, i)

        if not exp_date and EXP_LABEL_ONLY.match(upper):
            exp_date = extract_nearby_date(lines, i)

        if mfg_date and exp_date:
            break

    return mfg_date, exp_date


# ============================================================
# FINAL FALLBACK EXTRACTOR
# ============================================================

def extract_medicine_info_fallback(cleaned_data, ranked_data):
    """
    Generic medicine-information fallback extractor.

    No medicine names or manufacturer names are hardcoded.

    Priority fields:
        1. Medicine name
        2. Manufacturer
        3. Strength

    Secondary fields:
        4. Batch number
        5. Manufacturing date
        6. Expiry date

    cleaned_data:
        OCR detections in their available sequence.

    ranked_data:
        OCR detections ranked using confidence/votes.
    """

    sequential_lines = [
        item["text"]
        for item in cleaned_data
        if item.get("text", "").strip()
    ]

    brand = extract_brand_name(ranked_data)

    generic = extract_generic_composition(
        sequential_lines
    )

    manufacturer = extract_manufacturer(
        sequential_lines
    )

    strength = extract_strength(
        sequential_lines
    )

    batch_number = extract_batch_number(
        sequential_lines
    )

    manufacturing_date, expiry_date = extract_dates(
        sequential_lines
    )

    return {
        "medicine": brand or generic,
        "manufacturer": manufacturer,
        "strength": strength,
        "batch_number": batch_number,
        "manufacturing_date": manufacturing_date,
        "expiry_date": expiry_date
    }