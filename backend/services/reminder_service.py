from backend.extensions import db

from backend.models.reminder import MedicationReminder


def get_all_reminders():

    return MedicationReminder.query.order_by(
        MedicationReminder.reminder_time.asc()
    ).all()


def get_reminder_by_id(reminder_id):

    return MedicationReminder.query.get_or_404(
        reminder_id
    )


def add_reminder(data):

    reminder = MedicationReminder(

        medicine_id=data["medicine_id"],

        reminder_time=data["reminder_time"],

        frequency=data["frequency"],

        instructions=data.get(
            "instructions",
            ""
        ),

        is_active=True

    )

    db.session.add(reminder)

    db.session.commit()

    return reminder


def update_reminder(reminder_id, data):

    reminder = get_reminder_by_id(
        reminder_id
    )

    reminder.medicine_id = data["medicine_id"]

    reminder.reminder_time = data[
        "reminder_time"
    ]

    reminder.frequency = data[
        "frequency"
    ]

    reminder.instructions = data.get(
        "instructions",
        ""
    )

    db.session.commit()

    return reminder


def delete_reminder(reminder_id):

    reminder = get_reminder_by_id(
        reminder_id
    )

    db.session.delete(reminder)

    db.session.commit()


def toggle_reminder(reminder_id):

    reminder = get_reminder_by_id(
        reminder_id
    )

    reminder.is_active = not reminder.is_active

    db.session.commit()

    return reminder

from datetime import datetime


def reminder_status(reminder):
    """
    Returns the current status of a reminder.
    """

    if not reminder.is_active:
        return "Disabled"

    current_time = datetime.now().time()

    if reminder.reminder_time <= current_time:
        return "Due"

    return "Upcoming"