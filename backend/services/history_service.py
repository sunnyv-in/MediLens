from backend.extensions import db
from backend.models.medicine_history import MedicineHistory


def save_history(data):

    history = MedicineHistory(

        medicine_name=data.get("medicine_name"),

        manufacturer=data.get("manufacturer"),

        expiry_date=data.get("expiry_date"),

        counterfeit_score=data.get(
            "counterfeit_score",
            0
        ),

        image_filename=data.get(
            "image_filename"
        )

    )

    db.session.add(history)

    db.session.commit()

    return history


def get_all_history():

    return MedicineHistory.query.order_by(
        MedicineHistory.scan_time.desc()
    ).all()


def get_history_by_id(history_id):

    return MedicineHistory.query.get_or_404(
        history_id
    )


def update_history(history_id, data):

    history = get_history_by_id(
        history_id
    )

    history.medicine_name = data.get(
        "medicine_name"
    )

    history.manufacturer = data.get(
        "manufacturer"
    )

    history.expiry_date = data.get(
        "expiry_date"
    )

    history.counterfeit_score = data.get(
        "counterfeit_score"
    )

    history.image_filename = data.get(
        "image_filename"
    )

    db.session.commit()

    return history


def delete_history(history_id):

    history = get_history_by_id(
        history_id
    )

    db.session.delete(history)

    db.session.commit()

    return True