from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from backend.extensions import db


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(60), nullable=True)
    last_name = db.Column(db.String(60), nullable=True)

    email = db.Column(db.String(150), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    phone_number = db.Column(db.String(20), nullable=True)

    role = db.Column(db.String(30), default="patient")  # 'patient' or 'caregiver'
    patient_name = db.Column(db.String(100), nullable=True)  # Name of loved one if role is caregiver

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class CareCircleContact(db.Model):
    """
    Care Circle Contact: Additional phone numbers (e.g., secondary caregiver,
    home nurse, family members) who receive dose notifications and confirmation broadcasts.
    """
    __tablename__ = "care_circle_contacts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    name = db.Column(db.String(100), nullable=False)
    relationship = db.Column(db.String(50), default="Caregiver")  # 'Daughter', 'Son', 'Nurse', 'Spouse', 'Doctor'
    phone_number = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("care_circle_contacts", cascade="all, delete-orphan", lazy=True))


class DoseLog(db.Model):
    """
    Shared Dose Log / Notification Closer:
    Tracks when a medication was administered, by whom, to prevent duplicate feeding/double-dosing.
    """
    __tablename__ = "dose_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    guest_id = db.Column(db.String(36), nullable=True, index=True)

    medicine_id = db.Column(db.Integer, db.ForeignKey("medicines.id"), nullable=True)
    reminder_id = db.Column(db.Integer, db.ForeignKey("medication_reminders.id"), nullable=True)

    medicine_name = db.Column(db.String(120), nullable=False)
    administered_by = db.Column(db.String(100), default="Self")
    taken_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(30), default="taken")  # 'taken', 'skipped'
