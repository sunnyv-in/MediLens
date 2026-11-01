
from datetime import datetime
import re


def parse_medicine_date(date_string):
    if not date_string:
        return None

    cleaned_date = date_string.strip().upper()

    date_formats = [
        "%b.%y",
        "%b %y",
        "%b.%Y",
        "%b %Y",
        "%m/%y",
        "%m/%Y",
        "%m-%y",
        "%m-%Y",
    ]

    for fmt in date_formats:
        try:
            return datetime.strptime(cleaned_date, fmt)
        except ValueError:
            continue

    return None


GENERIC_MANUFACTURERS = {
    "LTD", "LIMITED", "PRIVATE LIMITED",
    "PVT", "PVT LTD", "PVT. LTD",
    "PHARMA", "PHARMACEUTICAL",
    "PHARMACEUTICALS", "HEALTHCARE"
}


def valid_strength(value):
    return bool(re.search(r"\d+(?:\.\d+)?\s*(MG|MCG|ML|G|IU|%)", value, re.I))


def valid_batch(batch):
    batch = batch.strip()
    if len(batch) < 4:
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9./\-]+", batch))


def analyze_counterfeit_risk(medicine_info):
    """
    Generic packaging consistency analyzer.

    NOTE:
    This DOES NOT authenticate a medicine.
    It only evaluates packaging completeness and consistency.
    """

    risk_score = 100
    checks = []

    medicine = medicine_info.get("medicine_name", "").strip()
    manufacturer = medicine_info.get("manufacturer", "").strip()
    strength = medicine_info.get("strength", "").strip()
    batch = medicine_info.get("batch_number", "").strip()
    mfg = medicine_info.get("manufacturing_date", "").strip()
    exp = medicine_info.get("expiry_date", "").strip()

    # Medicine
    if medicine:
        checks.append("✓ Medicine name detected")
    else:
        checks.append("⚠ Medicine name missing")
        risk_score -= 20

    # Manufacturer
    if manufacturer:
        if manufacturer.upper() in GENERIC_MANUFACTURERS:
            checks.append("⚠ Manufacturer appears incomplete")
            risk_score -= 8
        else:
            checks.append("✓ Manufacturer detected")
    else:
        checks.append("⚠ Manufacturer missing or unreadable")
        risk_score -= 15

    # Strength
    if strength:
        if valid_strength(strength):
            checks.append("✓ Medicine strength detected")
        else:
            checks.append("⚠ Medicine strength format looks unusual")
            risk_score -= 5
    else:
        checks.append("⚠ Medicine strength missing")
        risk_score -= 10

    # Batch
    if batch:
        if valid_batch(batch):
            checks.append("✓ Batch number format looks valid")
        else:
            checks.append("⚠ Batch number format looks unusual")
            risk_score -= 10
    else:
        checks.append("⚠ Batch number missing or unreadable")
        risk_score -= 15

    mfg_date = None
    exp_date = None

    # Manufacturing date
    if mfg:
        mfg_date = parse_medicine_date(mfg)
        if mfg_date:
            checks.append("✓ Manufacturing date detected")
        else:
            checks.append("⚠ Manufacturing date format could not be validated")
            risk_score -= 5
    else:
        checks.append("⚠ Manufacturing date missing")
        risk_score -= 10

    # Expiry date
    if exp:
        exp_date = parse_medicine_date(exp)
        if exp_date:
            checks.append("✓ Expiry date detected")
        else:
            checks.append("⚠ Expiry date format could not be validated")
            risk_score -= 5
    else:
        checks.append("⚠ Expiry date missing")
        risk_score -= 10

    # Logical validation
    if mfg_date and exp_date:
        if exp_date > mfg_date:
            checks.append("✓ Manufacturing and expiry dates are logically consistent")
        else:
            checks.append("✖ Expiry date is earlier than manufacturing date")
            risk_score -= 30

    risk_score = max(0, min(100, risk_score))

    detected_fields = sum([
        bool(medicine),
        bool(manufacturer),
        bool(strength),
        bool(batch),
        bool(mfg),
        bool(exp)
    ])

    if detected_fields >= 5:
        assessment_confidence = "HIGH"
    elif detected_fields >= 3:
        assessment_confidence = "LIMITED"
    else:
        assessment_confidence = "VERY LIMITED"

    if risk_score >= 90:
        risk_level = "VERY LOW"
    elif risk_score >= 70:
        risk_level = "LOW"
    elif risk_score >= 50:
        risk_level = "MEDIUM"
    elif risk_score >= 30:
        risk_level = "HIGH"
    else:
        risk_level = "VERY HIGH"

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "checks": checks,
        "assessment_confidence": assessment_confidence,
        "note": (
            "This assessment does not confirm whether a medicine is genuine "
            "or counterfeit. It evaluates packaging consistency, OCR quality, "
            "and logical validation only."
        )
    }
