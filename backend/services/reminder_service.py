from flask import abort

from backend.extensions import db
from backend.models.reminder import MedicationReminder
from backend.models.medicine import Medicine
from backend.utils.owner import get_owner_values


def _owned_medicine(medicine_id):
    owner = get_owner_values()
    medicine = Medicine.query.filter_by(
        id=medicine_id,
        **owner,
    ).first()

    if medicine is None:
        abort(404)

    return medicine


def get_all_reminders():
    owner = get_owner_values()

    return (
        MedicationReminder.query.filter_by(**owner)
        .order_by(MedicationReminder.reminder_time.asc())
        .all()
    )


def get_reminder_by_id(reminder_id):
    reminder = MedicationReminder.query.filter_by(
        id=reminder_id,
        **get_owner_values(),
    ).first()

    if reminder is None:
        abort(404)

    return reminder


def add_reminder(data):
    owner = get_owner_values()
    _owned_medicine(data["medicine_id"])

    reminder = MedicationReminder(
        **owner,
        medicine_id=data["medicine_id"],
        reminder_time=data["reminder_time"],
        frequency=data["frequency"],
        instructions=data.get("instructions", ""),
        lead_minutes=data.get("lead_minutes", 30),
        repeat_minutes=data.get("repeat_minutes", 5),
        is_active=True,
    )

    db.session.add(reminder)
    db.session.commit()
    return reminder


def update_reminder(reminder_id, data):
    reminder = get_reminder_by_id(reminder_id)
    _owned_medicine(data["medicine_id"])

    reminder.medicine_id = data["medicine_id"]
    reminder.reminder_time = data["reminder_time"]
    reminder.frequency = data["frequency"]
    reminder.instructions = data.get("instructions", "")
    reminder.lead_minutes = data.get("lead_minutes", 30)
    reminder.repeat_minutes = data.get("repeat_minutes", 5)

    # Reset send tracking so the changed schedule can send again.
    reminder.last_sent_at = None
    reminder.last_sent_date = None

    db.session.commit()
    return reminder


def delete_reminder(reminder_id):
    reminder = get_reminder_by_id(reminder_id)
    db.session.delete(reminder)
    db.session.commit()


def toggle_reminder(reminder_id):
    reminder = get_reminder_by_id(reminder_id)
    reminder.is_active = not reminder.is_active

    if reminder.is_active:
        reminder.last_sent_at = None
        reminder.last_sent_date = None

    db.session.commit()
    return reminder


def reminder_status(user_id=None):
    reminders = get_all_reminders()
    active_reminders = [r for r in reminders if r.is_active]

    return {
        "total": len(reminders),
        "active": len(active_reminders),
        "next_reminder": (
            min(active_reminders, key=lambda r: r.reminder_time)
            if active_reminders
            else None
        ),
    }
