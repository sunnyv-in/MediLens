from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

from backend.services.expiry_service import get_expiry_date, get_expiry_status
from backend.services.emergency_service import get_active_interaction_warnings
from backend.models.medicine import Medicine
from backend.models.reminder import MedicationReminder
from backend.services.reminder_service import reminder_status, get_all_reminders
from backend.services.medicine_service import get_all_medicines
from backend.services.history_service import get_all_history

home_bp = Blueprint("home", __name__)


def _compute_dashboard_data():
    medicines = get_all_medicines()

    expiring_soon_count = 0
    expired_count = 0
    safe_count = 0
    enriched_medicines = []

    for m in medicines:
        exp_date = get_expiry_date(m.expiry_date)
        status = get_expiry_status(exp_date)
        if status == "Expiring soon":
            expiring_soon_count += 1
        elif status == "Expired":
            expired_count += 1
        else:
            safe_count += 1

        enriched_medicines.append({
            "id": m.id,
            "medicine_name": m.medicine_name,
            "generic_name": m.generic_name or "",
            "strength": m.strength or "Standard",
            "manufacturer": m.manufacturer or "Unknown",
            "expiry_date": m.expiry_date or "N/A",
            "parsed_expiry": exp_date.strftime("%b %d, %Y") if exp_date else (m.expiry_date or "N/A"),
            "expiry_status": status,
            "dosage": m.dosage or "As directed",
            "quantity": getattr(m, "quantity", 1) or 1,
            "counterfeit_score": getattr(m, "counterfeit_score", 0) or 0,
        })

    reminders = get_all_reminders()
    active_reminders = [r for r in reminders if r.is_active]

    due_count = 0
    morning_doses = []
    afternoon_doses = []
    evening_doses = []

    for r in active_reminders:
        status = reminder_status(r)
        if status == "Due":
            due_count += 1

        r_time = r.reminder_time
        hour = r_time.hour if r_time else 9
        time_str = r_time.strftime("%I:%M %p") if r_time else "Scheduled"

        item = {
            "id": r.id,
            "medicine_id": r.medicine_id,
            "medicine_name": r.medicine.medicine_name if r.medicine else "Medication",
            "time_str": time_str,
            "frequency": r.frequency,
            "instructions": r.instructions or "Take with water",
            "status": status,
            "is_due": (status == "Due"),
        }

        if hour < 12:
            morning_doses.append(item)
        elif hour < 17:
            afternoon_doses.append(item)
        else:
            evening_doses.append(item)

    warnings = get_active_interaction_warnings()

    try:
        recent_scans = get_all_history()[:5]
    except Exception:
        recent_scans = []

    dashboard = {
        "total_medicines": len(medicines),
        "expiring_soon": expiring_soon_count,
        "expired": expired_count,
        "safe_medicines": safe_count,
        "active_reminders": len(active_reminders),
        "due_now": due_count,
        "interaction_warnings": len(warnings),
    }

    return {
        "dashboard": dashboard,
        "medicines": enriched_medicines,
        "reminders": active_reminders,
        "warnings": warnings,
        "schedule": {
            "morning": morning_doses,
            "afternoon": afternoon_doses,
            "evening": evening_doses,
        },
        "recent_scans": recent_scans,
        "today_str": datetime.now().strftime("%A, %B %d, %Y"),
    }


@home_bp.route("/")
def home():
    data = _compute_dashboard_data()
    return render_template("home/index.html", dashboard=data["dashboard"], full_data=data)


@home_bp.route("/dashboard")
def dashboard():
    data = _compute_dashboard_data()
    return render_template(
        "dashboard/dashboard.html",
        dashboard=data["dashboard"],
        medicines=data["medicines"],
        reminders=data["reminders"],
        warnings=data["warnings"],
        schedule=data["schedule"],
        recent_scans=data["recent_scans"],
        today_str=data["today_str"],
        user=current_user,
    )
