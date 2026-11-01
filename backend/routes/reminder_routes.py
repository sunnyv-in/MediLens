from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash

from backend.services.medicine_service import get_all_medicines
from backend.services.reminder_service import (
    get_all_reminders,
    get_reminder_by_id,
    add_reminder,
    update_reminder,
    delete_reminder,
    toggle_reminder,
)

reminder_bp = Blueprint("reminder", __name__)


def _read_reminder_form():
    try:
        medicine_id = int(request.form.get("medicine_id", ""))
        reminder_time = datetime.strptime(
            request.form.get("reminder_time", ""), "%H:%M"
        ).time()
        lead_minutes = int(request.form.get("lead_minutes", 30))
        repeat_minutes = int(request.form.get("repeat_minutes", 5))
    except (TypeError, ValueError):
        raise ValueError("Please enter valid reminder details.")

    if lead_minutes not in {0, 10, 15, 30, 60}:
        raise ValueError("Choose a valid reminder lead time.")

    if repeat_minutes not in {5, 10, 15, 30}:
        raise ValueError("Choose a valid repeat interval.")

    frequency = request.form.get("frequency", "Daily")
    if frequency not in {"Daily", "Twice Daily", "Weekly", "Monthly"}:
        raise ValueError("Choose a valid reminder frequency.")

    return {
        "medicine_id": medicine_id,
        "reminder_time": reminder_time,
        "frequency": frequency,
        "instructions": request.form.get("instructions", "").strip(),
        "lead_minutes": lead_minutes,
        "repeat_minutes": repeat_minutes,
    }


@reminder_bp.route("/reminders")
def reminders():
    return render_template(
        "reminder/reminder.html",
        reminders=get_all_reminders(),
        medicines=get_all_medicines(),
    )


@reminder_bp.route("/reminders/add", methods=["POST"])
def add_new_reminder():
    try:
        add_reminder(_read_reminder_form())
    except ValueError as error:
        flash(str(error), "error")
        return redirect(url_for("reminder.reminders"))

    flash("Reminder added successfully.", "success")
    return redirect(url_for("reminder.reminders"))


@reminder_bp.route("/reminders/edit/<int:reminder_id>", methods=["GET", "POST"])
def edit_reminder(reminder_id):
    reminder = get_reminder_by_id(reminder_id)

    if request.method == "POST":
        try:
            update_reminder(reminder_id, _read_reminder_form())
        except ValueError as error:
            flash(str(error), "error")
            return redirect(url_for("reminder.edit_reminder", reminder_id=reminder_id))

        flash("Reminder updated.", "success")
        return redirect(url_for("reminder.reminders"))

    return render_template(
        "reminder/edit_reminder.html",
        reminder=reminder,
        medicines=get_all_medicines(),
    )


@reminder_bp.route(
    "/reminders/<int:reminder_id>/settings",
    methods=["POST"],
    endpoint="update_reminder_settings",
)
def update_reminder_settings(reminder_id):
    reminder = get_reminder_by_id(reminder_id)

    try:
        lead_minutes = int(request.form.get("lead_minutes", "30"))
        repeat_minutes = int(request.form.get("repeat_minutes", "5"))
    except (TypeError, ValueError):
        flash("Choose valid reminder settings.", "error")
        return redirect(url_for("reminder.reminders"))

    if lead_minutes not in {0, 10, 15, 30, 60}:
        flash("Choose a valid lead time.", "error")
        return redirect(url_for("reminder.reminders"))

    if repeat_minutes not in {5, 10, 15, 30}:
        flash("Choose a valid repeat interval.", "error")
        return redirect(url_for("reminder.reminders"))

    reminder.lead_minutes = lead_minutes
    reminder.repeat_minutes = repeat_minutes

    from backend.extensions import db

    db.session.commit()

    flash("Reminder settings saved.", "success")
    return redirect(url_for("reminder.reminders"))


@reminder_bp.route("/reminders/delete/<int:reminder_id>", methods=["POST"])
def remove_reminder(reminder_id):
    delete_reminder(reminder_id)
    flash("Reminder deleted.", "success")
    return redirect(url_for("reminder.reminders"))


@reminder_bp.route("/reminders/toggle/<int:reminder_id>", methods=["POST"])
def toggle_reminder_status(reminder_id):
    toggle_reminder(reminder_id)
    flash("Reminder status updated.", "success")
    return redirect(url_for("reminder.reminders"))
