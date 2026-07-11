from datetime import datetime
from backend.extensions import db



class DrugInteraction(db.Model):

    __tablename__ = "drug_interactions"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    drug_one = db.Column(
        db.String(120),
        nullable=False
    )

    drug_two = db.Column(
        db.String(120),
        nullable=False
    )

    severity = db.Column(
        db.String(50),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    recommendation = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )