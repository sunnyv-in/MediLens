from flask import Blueprint, render_template

from backend.models.medicine import Medicine
from backend.services.expiry_service import get_expiry_date, get_expiry_status

expiry_bp = Blueprint("expiry", __name__)


@expiry_bp.route("/expiry-alerts")
def expiry_alerts():
    medicines = Medicine.query.all()
    alerts = []
    for m in medicines:
        exp_date = get_expiry_date(m.expiry_date)
        status = get_expiry_status(exp_date)
        alerts.append({
            "id": m.id,
            "medicine_name": m.medicine_name,
            "expiry_date": exp_date,
            "status": status
        })
    return render_template("expiry/expiry_alerts.html", alerts=alerts)