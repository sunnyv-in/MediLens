from flask import Blueprint, flash, redirect, render_template, request, url_for

from backend.services.email_service import send_medicine_shelf_email
from backend.services.medicine_service import (
    delete_medicine,
    get_all_medicines,
    get_medicine_by_id,
    save_medicine,
    update_medicine,
)

medicine_shelf_bp = Blueprint("medicine_shelf", __name__)


@medicine_shelf_bp.route("/medicine-shelf")
def medicine_shelf():
    medicines = get_all_medicines()

    return render_template(
        "medicine/medicine_shelf.html",
        medicines=medicines,
    )


@medicine_shelf_bp.route("/medicine/add")
def add_medicine_page():
    return render_template("medicine/add_medicine.html")


@medicine_shelf_bp.route("/medicine/add", methods=["POST"])
def add_medicine():
    medicine_data = {
        "medicine_name": request.form.get("medicine_name"),
        "generic_name": request.form.get("generic_name"),
        "strength": request.form.get("strength"),
        "manufacturer": request.form.get("manufacturer"),
        "batch_number": request.form.get("batch_number"),
        "expiry_date": request.form.get("expiry_date"),
        "quantity": request.form.get("quantity"),
        "dosage": request.form.get("dosage"),
        "usage": request.form.get("usage"),
        "side_effects": request.form.get("side_effects"),
        "image_filename": None,
        "counterfeit_score": 0,
    }

    save_medicine(medicine_data)
    flash("Medicine added successfully.", "success")

    return redirect(url_for("medicine_shelf.medicine_shelf"))


@medicine_shelf_bp.route("/medicine/<int:medicine_id>")
def medicine_details(medicine_id):
    medicine = get_medicine_by_id(medicine_id)

    return render_template(
        "medicine/medicine_details.html",
        medicine=medicine,
    )


@medicine_shelf_bp.route("/medicine/edit/<int:medicine_id>")
def edit_medicine_page(medicine_id):
    medicine = get_medicine_by_id(medicine_id)

    # Scanned medicines must be edited through their History record.
    if medicine.history_id:
        return redirect(
            url_for(
                "medicine_history.edit_history",
                history_id=medicine.history_id,
            )
        )

    return render_template(
        "medicine/edit_medicine.html",
        medicine=medicine,
    )


@medicine_shelf_bp.route(
    "/medicine/edit/<int:medicine_id>",
    methods=["POST"],
)
def edit_medicine(medicine_id):
    medicine = get_medicine_by_id(medicine_id)

    # Do not allow a scanned medicine to be updated only in the Shelf.
    if medicine.history_id:
        return redirect(
            url_for(
                "medicine_history.edit_history",
                history_id=medicine.history_id,
            )
        )

    update_medicine(medicine_id, request.form)

    flash("Medicine updated successfully.", "success")

    return redirect(
        url_for(
            "medicine_shelf.medicine_details",
            medicine_id=medicine_id,
        )
    )


@medicine_shelf_bp.route(
    "/medicine/delete/<int:medicine_id>",
    methods=["POST"],
)
def remove_medicine(medicine_id):
    delete_medicine(medicine_id)
    flash("Medicine deleted successfully.", "success")

    return redirect(url_for("medicine_shelf.medicine_shelf"))


@medicine_shelf_bp.route(
    "/medicine-shelf/email",
    methods=["POST"],
)
def email_medicine_shelf():
    recipient = request.form.get("recipient_email", "").strip()

    try:
        medicines = get_all_medicines()
        send_medicine_shelf_email(medicines, recipient)
        flash("Your medicine shelf was emailed successfully.", "success")
    except Exception as error:
        flash(f"Could not send the medicine shelf email: {error}", "error")

    return redirect(url_for("medicine_shelf.medicine_shelf"))
