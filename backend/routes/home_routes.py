from flask import Blueprint, render_template

from backend.services.expiry_service import get_expiry_date, get_expiry_status
from backend.services.emergency_service import get_active_interaction_warnings
from backend.models.medicine import Medicine
from backend.models.reminder import MedicationReminder
from backend.services.reminder_service import reminder_status


home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def home():

    medicines = Medicine.query.all()

    expiring_soon_count = 0
    expired_count = 0

    for m in medicines:
        exp_date = get_expiry_date(m.expiry_date)
        status = get_expiry_status(exp_date)
        if status == "Expiring soon":
            expiring_soon_count += 1
        elif status == "Expired":
            expired_count += 1

    reminders = MedicationReminder.query.filter_by(is_active=True).all()
    due_count = sum(1 for r in reminders if reminder_status(r) == "Due")

    warning_count = len(get_active_interaction_warnings())

    dashboard = {
        "total_medicines": len(medicines),
        "expiring_soon": expiring_soon_count,
        "expired": expired_count,
        "active_reminders": len(reminders),
        "due_now": due_count,
        "interaction_warnings": warning_count
    }

    return render_template("home/index.html", dashboard=dashboard)