from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime

from backend.extensions import db
from backend.models.medicine import Medicine
from backend.models.reminder import MedicationReminder
from backend.services.reminder_service import reminder_status

reminder_bp = Blueprint("reminder", __name__)


@reminder_bp.route("/reminders")
def reminders():
    all_medicines = Medicine.query.all()
    all_reminders = MedicationReminder.query.all()
    reminder_data = []
    for reminder in all_reminders:
        medicine = Medicine.query.get(reminder.medicine_id)
        reminder_data.append({
            "id": reminder.id,
            "medicine_name": medicine.medicine_name if medicine else "Unknown",
            "time": reminder.reminder_time.strftime("%H:%M"),
            "frequency": reminder.frequency,
            "instructions": reminder.instructions,
            "status": reminder_status(reminder),
            "active": reminder.is_active
        })
    return render_template("reminders.html", reminders=reminder_data, medicines=all_medicines)


@reminder_bp.route("/reminders/add", methods=["POST"])
def add_reminder():
    medicine_id = request.form["medicine_id"]
    reminder_time = datetime.strptime(request.form["reminder_time"], "%H:%M").time()
    frequency = request.form["frequency"]
    instructions = request.form.get("instructions", "")

    reminder = MedicationReminder(
        medicine_id=medicine_id,
        reminder_time=reminder_time,
        frequency=frequency,
        instructions=instructions,
        is_active=True
    )
    db.session.add(reminder)
    db.session.commit()
    flash("Reminder added successfully.")
    return redirect(url_for("reminder.reminders"))


@reminder_bp.route("/reminders/delete/<int:id>", methods=["POST"])
def delete_reminder(id):
    reminder = MedicationReminder.query.get_or_404(id)
    db.session.delete(reminder)
    db.session.commit()
    flash("Reminder removed.")
    return redirect(url_for("reminder.reminders"))


@reminder_bp.route("/reminders/toggle/<int:id>", methods=["POST"])
def toggle_reminder(id):
    reminder = MedicationReminder.query.get_or_404(id)
    reminder.is_active = not reminder.is_active
    db.session.commit()
    flash("Reminder updated.")
    return redirect(url_for("reminder.reminders"))