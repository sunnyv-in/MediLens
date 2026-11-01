from datetime import datetime
from backend.extensions import db


class Medicine(db.Model):

    __tablename__ = "medicines"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    medicine_name = db.Column(
        db.String(120),
        nullable=False
    )

    generic_name = db.Column(
        db.String(120)
    )

    strength = db.Column(
        db.String(50)
    )

    manufacturer = db.Column(
        db.String(120)
    )

    batch_number = db.Column(
        db.String(80)
    )

    expiry_date = db.Column(
        db.String(30)
    )

    dosage = db.Column(
        db.String(120)
    )

    usage = db.Column(
        db.Text
    )

    side_effects = db.Column(
        db.Text
    )

    counterfeit_score = db.Column(
        db.Integer,
        default=0
    )

    image_filename = db.Column(
        db.String(255)
    )

    quantity = db.Column(
    db.Integer,
    default=1
)
  

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )