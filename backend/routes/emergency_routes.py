from flask import Blueprint, render_template

from backend.services.emergency_service import get_emergency_snapshot

emergency_bp = Blueprint("emergency", __name__)


@emergency_bp.route("/emergency")
def emergency_mode():
    snapshot = get_emergency_snapshot()
    return render_template(
        "emergency/emergency_mode.html",
        medicines=snapshot["medicines"],
        warnings=snapshot["warnings"]
    )