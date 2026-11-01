from backend.extensions import db
from backend.models.medicine import Medicine


def save_medicine(data):
    """
    Save a new medicine into the database.
    """

    medicine = Medicine(
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
        image_filename=data.get("image_filename")
    )

    db.session.add(medicine)
    db.session.commit()

    return medicine


def get_all_medicines():
    """
    Return all medicines ordered by newest first.
    """

    return Medicine.query.order_by(
        Medicine.created_at.desc()
    ).all()


def get_medicine_by_id(medicine_id):
    """
    Return one medicine using its ID.
    """

    return Medicine.query.get_or_404(medicine_id)


def delete_medicine(medicine_id):
    """
    Delete a medicine.
    """

    medicine = get_medicine_by_id(medicine_id)

    db.session.delete(medicine)
    db.session.commit()


def update_medicine(medicine_id, data):
    """
    Update an existing medicine.
    """

    medicine = get_medicine_by_id(medicine_id)

    medicine.medicine_name = data.get(
        "medicine_name",
        medicine.medicine_name
    )

    medicine.generic_name = data.get(
        "generic_name",
        medicine.generic_name
    )

    medicine.strength = data.get(
        "strength",
        medicine.strength
    )

    medicine.manufacturer = data.get(
        "manufacturer",
        medicine.manufacturer
    )

    medicine.batch_number = data.get(
        "batch_number",
        medicine.batch_number
    )

    medicine.expiry_date = data.get(
        "expiry_date",
        medicine.expiry_date
    )

    medicine.dosage = data.get(
        "dosage",
        medicine.dosage
    )

    medicine.usage = data.get(
        "usage",
        medicine.usage
    )

    medicine.side_effects = data.get(
        "side_effects",
        medicine.side_effects
    )

    medicine.image_filename = data.get(
        "image_filename",
        medicine.image_filename
    )

    medicine.quantity = data.get(
        "quantity",
        medicine.quantity
    )

    medicine.counterfeit_score = data.get(
        "counterfeit_score",
        medicine.counterfeit_score
    )

    db.session.commit()

    return medicine


def search_medicine(keyword):
    """
    Search medicines by name.
    """

    return Medicine.query.filter(
        Medicine.medicine_name.ilike(
            f"%{keyword}%"
        )
    ).all()


def medicine_exists(medicine_name):
    """
    Check whether a medicine already exists.
    """

    return Medicine.query.filter_by(
        medicine_name=medicine_name
    ).first()


def increase_quantity(medicine_id):
    """
    Increase medicine quantity by one.
    """

    medicine = get_medicine_by_id(medicine_id)

    medicine.quantity += 1

    db.session.commit()

    return medicine



def decrease_quantity(medicine_id):
    """
    Decrease medicine quantity.
    """

    medicine = get_medicine_by_id(medicine_id)

    if medicine.quantity > 0:
        medicine.quantity -= 1

    db.session.commit()

    return medicine