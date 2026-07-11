from datetime import datetime

from backend.extensions import db


class MedicineHistory(db.Model):

    __tablename__ = "medicine_history"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    medicine_name = db.Column(
        db.String(120),
        nullable=False
    )

    scan_time = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    expiry_date = db.Column(
        db.String(30)
    )

    manufacturer = db.Column(
        db.String(120)
    )

    counterfeit_score = db.Column(
        db.Integer
    )

    image_filename = db.Column(
        db.String(255)
    )