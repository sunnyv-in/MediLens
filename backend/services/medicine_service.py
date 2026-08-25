from flask import abort
from flask_login import current_user

from backend.extensions import db
from backend.models.medicine import Medicine
from backend.utils.owner import get_owner_values


def owner_filter(query):

    owner = get_owner_values()

    if owner["user_id"]:

        return query.filter(Medicine.user_id == owner["user_id"])

    return query.filter(Medicine.guest_id == owner["guest_id"])


def save_medicine(data):

    owner = get_owner_values()

    medicine = Medicine(
        user_id=owner["user_id"],
        guest_id=owner["guest_id"],
        medicine_name=data["medicine_name"],
        generic_name=data.get("generic_name"),
        strength=data.get("strength"),
        manufacturer=data.get("manufacturer"),
        batch_number=data.get("batch_number"),
        expiry_date=data.get("expiry_date"),
        dosage=data.get("dosage"),
        usage=data.get("usage"),
        side_effects=data.get("side_effects"),
        quantity=data.get("quantity", 1),
        counterfeit_score=data.get("counterfeit_score", 0),
        image_filename=data.get("image_filename"),
    )

    db.session.add(medicine)

    db.session.commit()

    return medicine


def get_all_medicines():

    return owner_filter(Medicine.query).order_by(Medicine.created_at.desc()).all()


def get_medicine_by_id(medicine_id):

    medicine = owner_filter(Medicine.query).filter(Medicine.id == medicine_id).first()

    if not medicine:
        abort(404)

    return medicine


def delete_medicine(medicine_id):

    medicine = get_medicine_by_id(medicine_id)

    db.session.delete(medicine)

    db.session.commit()


def update_medicine(medicine_id, data):

    medicine = get_medicine_by_id(medicine_id)

    medicine.medicine_name = data.get("medicine_name", medicine.medicine_name)

    medicine.generic_name = data.get("generic_name", medicine.generic_name)

    medicine.strength = data.get("strength", medicine.strength)

    medicine.manufacturer = data.get("manufacturer", medicine.manufacturer)

    medicine.batch_number = data.get("batch_number", medicine.batch_number)

    medicine.expiry_date = data.get("expiry_date", medicine.expiry_date)

    medicine.dosage = data.get("dosage", medicine.dosage)

    medicine.usage = data.get("usage", medicine.usage)

    medicine.side_effects = data.get("side_effects", medicine.side_effects)

    medicine.quantity = data.get("quantity", medicine.quantity)

    db.session.commit()

    return medicine
