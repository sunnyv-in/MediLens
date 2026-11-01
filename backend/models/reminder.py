from datetime import datetime

from backend.extensions import db


class MedicationReminder(db.Model):

    __tablename__ = "medication_reminders"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    guest_id = db.Column(db.String(36), nullable=True, index=True)

    id = db.Column(db.Integer, primary_key=True)

    medicine_id = db.Column(db.Integer, db.ForeignKey("medicines.id"), nullable=False)

    reminder_time = db.Column(db.Time, nullable=False)

    frequency = db.Column(db.String(50), nullable=False)

    instructions = db.Column(db.Text)

    is_active = db.Column(db.Boolean, default=True)

    medicine = db.relationship("Medicine", backref="reminders")

    lead_minutes = db.Column(db.Integer, nullable=False, default=30)
    repeat_minutes = db.Column(db.Integer, nullable=False, default=5)
    last_sent_at = db.Column(db.DateTime, nullable=True)
    last_sent_date = db.Column(db.Date, nullable=True)
