from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

from backend.services.expiry_service import get_expiry_date, get_expiry_status
from backend.services.emergency_service import get_active_interaction_warnings
from backend.models.medicine import Medicine
from backend.models.reminder import MedicationReminder
from backend.models.user import CareCircleContact, DoseLog
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

    # Check today's dose logs to see which doses are already taken
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_logs = []
    taken_med_names = set()

    try:
        if current_user.is_authenticated:
            today_logs = DoseLog.query.filter(
                DoseLog.user_id == current_user.id,
                DoseLog.taken_at >= today_start,
                DoseLog.status == "taken"
            ).order_by(DoseLog.taken_at.desc()).all()
        else:
            today_logs = DoseLog.query.filter(
                DoseLog.taken_at >= today_start,
                DoseLog.status == "taken"
            ).order_by(DoseLog.taken_at.desc()).all()
        taken_med_names = {log.medicine_name.lower() for log in today_logs}
    except Exception:
        today_logs = []

    for r in active_reminders:
        status = reminder_status(r)
        if status == "Due":
            due_count += 1

        r_time = r.reminder_time
        hour = r_time.hour if r_time else 9
        time_str = r_time.strftime("%I:%M %p") if r_time else "Scheduled"
        med_name = r.medicine.medicine_name if r.medicine else "Medication"

        # Check if already taken today
        is_already_taken = med_name.lower() in taken_med_names
        matching_log = next((l for l in today_logs if l.medicine_name.lower() == med_name.lower()), None)

        item = {
            "id": r.id,
            "medicine_id": r.medicine_id,
            "medicine_name": med_name,
            "time_str": time_str,
            "frequency": r.frequency,
            "instructions": r.instructions or "Take with water",
            "status": status,
            "is_due": (status == "Due"),
            "is_taken": is_already_taken,
            "administered_by": matching_log.administered_by if matching_log else None,
            "taken_time": matching_log.taken_at.strftime("%I:%M %p") if matching_log else None,
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

    # Fetch Care Circle contacts if authenticated
    care_circle = []
    if current_user.is_authenticated:
        try:
            care_circle = CareCircleContact.query.filter_by(user_id=current_user.id).all()
        except Exception:
            care_circle = []

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
        "care_circle": care_circle,
        "today_logs": today_logs,
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
        care_circle=data["care_circle"],
        today_logs=data["today_logs"],
        recent_scans=data["recent_scans"],
        today_str=data["today_str"],
        user=current_user,
    )
