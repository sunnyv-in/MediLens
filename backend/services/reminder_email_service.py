from flask import current_app
from flask_mail import Message

from backend.extensions import mail


def send_reminder_saved_email(recipient, reminder):
    medicine_name = reminder.medicine.medicine_name

    message = Message(
        subject="MediLens dose reminder saved",
        recipients=[recipient],
        body=(
            f"Your MediLens reminder has been saved.\n\n"
            f"Medicine: {medicine_name}\n"
            f"Time: {reminder.reminder_time.strftime('%I:%M %p')}\n"
            f"Frequency: {reminder.frequency}\n"
            f"Instructions: {reminder.instructions or 'None added'}\n\n"
            "This is a confirmation email, not a dose-time alert."
        ),
    )

    mail.send(message)
