from flask import Blueprint, render_template
from flask_login import current_user

from backend.services.emergency_service import get_emergency_snapshot

emergency_bp = Blueprint("emergency", __name__)


@emergency_bp.route("/emergency")
def emergency_mode():
    snapshot = get_emergency_snapshot()

    phone_number = current_user.phone_number if current_user.is_authenticated else ""

    return render_template(
        "emergency/emergency_mode.html",
        medicines=snapshot["medicines"],
        phone_number=phone_number,
    )
