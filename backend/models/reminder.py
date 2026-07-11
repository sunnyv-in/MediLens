from backend.extensions import db


class MedicationReminder(db.Model):

    __tablename__ = "medication_reminders"

    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey("medicines.id"), nullable=False)
    reminder_time = db.Column(db.Time, nullable=False)
    frequency = db.Column(db.String(50))
    instructions = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)