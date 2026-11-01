from flask import Blueprint, render_template, request, redirect, url_for

from flask import flash
from flask_login import current_user
from backend.services.email_service import send_history_email

from backend.services.history_service import (
    get_all_history,
    get_history_by_id,
    update_history,
    delete_history,
)

medicine_history_bp = Blueprint("medicine_history", __name__)


@medicine_history_bp.route("/medicine-history")
def medicine_history():
    history_records = get_all_history()

    return render_template(
        "history/medicine_history.html",
        history_records=history_records,
    )


@medicine_history_bp.route("/medicine-history/<int:history_id>")
def history_details(history_id):
    history = get_history_by_id(history_id)

    return render_template(
        "history/history_details.html",
        history=history,
    )


@medicine_history_bp.route(
    "/medicine-history/edit/<int:history_id>",
    methods=["GET", "POST"],
)
def edit_history(history_id):
    history = get_history_by_id(history_id)

    if request.method == "POST":
        update_history(history_id, request.form)
        return redirect(
            url_for(
                "medicine_history.history_details",
                history_id=history_id,
            )
        )

    return render_template(
        "history/edit_history.html",
        history=history,
    )


@medicine_history_bp.route(
    "/medicine-history/delete/<int:history_id>",
    methods=["POST"],
)
def remove_history(history_id):
    delete_history(history_id)

    return redirect(url_for("medicine_history.medicine_history"))


@medicine_history_bp.route(
    "/medicine-history/<int:history_id>/email",
    methods=["POST"],
)
def email_history(history_id):
    history = get_history_by_id(history_id)

    recipient = request.form.get("recipient_email", "").strip()

    if not recipient and current_user.is_authenticated:
        recipient = current_user.email

    try:
        send_history_email(history, recipient)
        flash("Medicine scan details emailed successfully.", "success")
    except ValueError as error:
        flash(str(error), "error")
    except Exception:
        flash("Could not send the email. Check your mail configuration.", "error")

    return redirect(
        url_for(
            "medicine_history.history_details",
            history_id=history_id,
        )
    )
