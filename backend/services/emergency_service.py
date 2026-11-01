from itertools import combinations

from backend.models.medicine import Medicine
from backend.services.expiry_service import get_expiry_date, get_expiry_status
from backend.services.interaction_service import find_interaction


def get_current_medicines_summary():
    """
    Returns every medicine on the shelf with its expiry status attached.
    Used as the core data for Emergency Mode.
    """
    medicines = Medicine.query.all()
    summary = []

    for m in medicines:
        exp_date = get_expiry_date(m.expiry_date)
        status = get_expiry_status(exp_date)

        summary.append({
            "id": m.id,
            "medicine_name": m.medicine_name,
            "dosage": m.dosage,
            "expiry_date": exp_date,
            "expiry_status": status
        })

    return summary


def get_active_interaction_warnings():
    """
    Checks every pair of medicines currently on the shelf
    for known drug interactions. Returns a list of warnings.
    """
    medicines = Medicine.query.all()
    warnings = []

    for med_a, med_b in combinations(medicines, 2):
        interaction = find_interaction(med_a.medicine_name, med_b.medicine_name)
        if interaction:
            warnings.append({
                "drug_one": med_a.medicine_name,
                "drug_two": med_b.medicine_name,
                "severity": interaction.severity,
                "description": interaction.description,
                "recommendation": interaction.recommendation
            })

    return warnings


def get_emergency_snapshot():
    """
    Full snapshot used by Emergency Mode:
    current medicines + expiry status + any interaction warnings.
    """
    return {
        "medicines": get_current_medicines_summary(),
        "warnings": get_active_interaction_warnings()
    }