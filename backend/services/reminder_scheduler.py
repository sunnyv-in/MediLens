from datetime import datetime, timedelta

from backend.extensions import db
from backend.models.reminder import MedicationReminder
from backend.services.whatsapp_service import send_whatsapp_template


def send_due_reminders(app):
    with app.app_context():
        now = datetime.now()
        today = now.date()

        reminders = MedicationReminder.query.filter_by(
            is_active=True,
            frequency="Daily",
        ).all()

        for reminder in reminders:
            medicine = reminder.medicine
            if medicine is None:
                continue

            # The medicine's user is the owner of the reminder.
            user = medicine.user
            phone_number = getattr(user, "phone_number", None) if user else None

            if not phone_number:
                app.logger.warning(
                    "Reminder %s skipped: no owner WhatsApp number.",
                    reminder.id,
                )
                continue

            scheduled_at = datetime.combine(today, reminder.reminder_time)
            start_at = scheduled_at - timedelta(minutes=reminder.lead_minutes or 30)

            # Only send inside the configured lead-time window.
            if not (start_at <= now < scheduled_at):
                continue

            if reminder.last_sent_date == today and reminder.last_sent_at:
                elapsed_seconds = (now - reminder.last_sent_at).total_seconds()
                repeat_seconds = (reminder.repeat_minutes or 5) * 60

                if elapsed_seconds < repeat_seconds:
                    continue

            try:
                send_whatsapp_template(
                    phone_number=phone_number,
                    medicine_name=medicine.medicine_name,
                    scheduled_time=reminder.reminder_time.strftime("%I:%M %p"),
                    status="Your scheduled medicine time is approaching.",
                )

                reminder.last_sent_at = now
                reminder.last_sent_date = today
                db.session.commit()

            except Exception:
                db.session.rollback()
                app.logger.exception(
                    "Failed to send WhatsApp reminder %s",
                    reminder.id,
                )
