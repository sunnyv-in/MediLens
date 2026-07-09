from datetime import datetime


def parse_medicine_date(date_string):
    """
    Attempts to parse common medicine packaging date formats.

    Examples:
    JAN.26
    DEC.27
    JAN 2026
    DEC 2027
    01/2026
    12/2027
    """

    if not date_string:
        return None

    cleaned_date = date_string.strip().upper()

    date_formats = [
        "%b.%y",   # JAN.26
        "%b %y",   # JAN 26
        "%b.%Y",   # JAN.2026
        "%b %Y",   # JAN 2026
        "%m/%y",   # 01/26
        "%m/%Y",   # 01/2026
        "%m-%y",   # 01-26
        "%m-%Y",   # 01-2026
    ]

    for date_format in date_formats:
        try:
            return datetime.strptime(cleaned_date, date_format)
        except ValueError:
            continue

    return None


def analyze_counterfeit_risk(medicine_info):
    """
    Basic rule-based packaging consistency analyzer.

    Important:
    This does NOT confirm whether a medicine is genuine or counterfeit.

    Missing OCR information reduces assessment confidence.
    It does not automatically mean the medicine is suspicious.
    """

    risk_score = 0
    checks = []

    medicine = medicine_info.get("medicine", "").strip()
    manufacturer = medicine_info.get("manufacturer", "").strip()
    strength = medicine_info.get("strength", "").strip()
    batch_number = medicine_info.get("batch_number", "").strip()
    manufacturing_date = medicine_info.get("manufacturing_date", "").strip()
    expiry_date = medicine_info.get("expiry_date", "").strip()

    # -----------------------------
    # Field detection checks
    # -----------------------------

    if medicine:
        checks.append("Medicine name detected")
    else:
        checks.append("Medicine name could not be detected")

    if manufacturer:
        checks.append("Manufacturer detected")
    else:
        checks.append("Manufacturer could not be detected")

    if strength:
        checks.append("Medicine strength detected")
    else:
        checks.append("Medicine strength missing or unreadable")

    if batch_number:
        checks.append("Batch number detected")
    else:
        checks.append("Batch number missing or unreadable")

    if manufacturing_date:
        checks.append("Manufacturing date detected")
    else:
        checks.append("Manufacturing date missing or unreadable")

    if expiry_date:
        checks.append("Expiry date detected")
    else:
        checks.append("Expiry date missing or unreadable")

    # -----------------------------
    # Date consistency check
    # -----------------------------

    if manufacturing_date and expiry_date:

        mfg_date = parse_medicine_date(manufacturing_date)
        exp_date = parse_medicine_date(expiry_date)

        if mfg_date and exp_date:

            if exp_date <= mfg_date:
                checks.append(
                    "Suspicious date inconsistency: expiry date is not after manufacturing date"
                )
                risk_score += 40

            else:
                checks.append(
                    "Manufacturing and expiry dates are logically consistent"
                )

        else:
            checks.append(
                "Date format could not be validated"
            )

    # -----------------------------
    # Count detected fields
    # -----------------------------

    detected_fields = sum([
        bool(medicine),
        bool(manufacturer),
        bool(strength),
        bool(batch_number),
        bool(manufacturing_date),
        bool(expiry_date)
    ])

    # -----------------------------
    # Assessment confidence
    # -----------------------------

    if detected_fields >= 5:
        assessment_confidence = "HIGH"

    elif detected_fields >= 3:
        assessment_confidence = "LIMITED"

    else:
        assessment_confidence = "VERY LIMITED"

    # -----------------------------
    # Assessment result
    # -----------------------------

    if risk_score >= 40:
        risk_level = "HIGH"

    elif risk_score >= 15:
        risk_level = "MEDIUM"

    elif risk_score > 0:
        risk_level = "LOW"

    else:
        risk_level = "INCONCLUSIVE"

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "checks": checks,
        "assessment_confidence": assessment_confidence,
        "note": (
            "This assessment does not confirm whether a medicine is "
            "genuine or counterfeit. It only evaluates detected packaging "
            "information and basic consistency checks. Missing information "
            "may be caused by image quality, packaging layout, or OCR limitations."
        )
    }