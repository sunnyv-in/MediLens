from flask import abort

from backend.extensions import db
from backend.models.medicine_history import MedicineHistory
from backend.utils.owner import get_owner_values

from backend.models.medicine import Medicine
from backend.services.medicine_service import owner_filter


def save_history(data):
    history = MedicineHistory(
        **get_owner_values(),
        medicine_name=data.get("medicine_name") or "Unknown medicine",
        manufacturer=data.get("manufacturer"),
        expiry_date=data.get("expiry_date"),
        counterfeit_score=data.get("counterfeit_score"),
        image_filename=data.get("image_filename"),
        scan_data=data.get("scan_data"),
    )

    db.session.add(history)
    db.session.commit()
    return history


def get_all_history():
    return (
        MedicineHistory.query.filter_by(**get_owner_values())
        .order_by(MedicineHistory.scan_time.desc())
        .all()
    )


def get_history_by_id(history_id):
    history = MedicineHistory.query.filter_by(
        id=history_id,
        **get_owner_values(),
    ).first()

    if history is None:
        abort(404)

    return history


def update_history(history_id, data):
    history = get_history_by_id(history_id)

    history.medicine_name = data.get("medicine_name") or "Unknown medicine"
    history.manufacturer = data.get("manufacturer") or None
    history.expiry_date = data.get("expiry_date") or None

    score = data.get("counterfeit_score")
    try:
        history.counterfeit_score = int(score) if score not in (None, "") else None
    except (TypeError, ValueError):
        history.counterfeit_score = None

    # Update only the shelf record linked to this exact history entry.
    medicine = owner_filter(Medicine.query).filter_by(history_id=history.id).first()

    if medicine:
        medicine.medicine_name = history.medicine_name
        medicine.manufacturer = history.manufacturer
        medicine.expiry_date = history.expiry_date
        medicine.counterfeit_score = history.counterfeit_score

    db.session.commit()
    return history


def delete_history(history_id):
    history = get_history_by_id(history_id)

    # Remove only the Shelf medicine linked to this exact scan.
    medicine = owner_filter(Medicine.query).filter_by(history_id=history.id).first()

    if medicine:
        db.session.delete(medicine)

    db.session.delete(history)
    db.session.commit()
    return True
