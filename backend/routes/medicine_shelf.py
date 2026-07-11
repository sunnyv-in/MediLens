from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for
)

from backend.services.medicine_service import (
    get_all_medicines,
    get_medicine_by_id,
    save_medicine,
    update_medicine,
    delete_medicine
)

medicine_shelf_bp = Blueprint(
    "medicine_shelf",
    __name__
)

@medicine_shelf_bp.route("/medicine-shelf")
def medicine_shelf():

    medicines = get_all_medicines()

    return render_template(
        "medicine/medicine_shelf.html",
        medicines=medicines
    )

@medicine_shelf_bp.route("/medicine/add")
def add_medicine_page():

    return render_template(
        "medicine/add_medicine.html"
    )


@medicine_shelf_bp.route(
    "/medicine/add",
    methods=["POST"]
)
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

        "counterfeit_score": 0

    }

    save_medicine(
        medicine_data
    )

    return redirect(
        url_for(
            "medicine_shelf.medicine_shelf"
        )
    )

@medicine_shelf_bp.route("/medicine/<int:medicine_id>")
def medicine_details(medicine_id):

    medicine = get_medicine_by_id(
        medicine_id
    )

    return render_template(
        "medicine/medicine_details.html",
        medicine=medicine
    )


@medicine_shelf_bp.route(
    "/medicine/edit/<int:medicine_id>"
)
def edit_medicine_page(medicine_id):

    medicine = get_medicine_by_id(
        medicine_id
    )

    return render_template(
        "medicine/edit_medicine.html",
        medicine=medicine
    )


@medicine_shelf_bp.route(
    "/medicine/edit/<int:medicine_id>",
    methods=["POST"]
)
def edit_medicine(medicine_id):

    update_medicine(
        medicine_id,
        request.form
    )

    return redirect(
        url_for(
            "medicine_shelf.medicine_details",
            medicine_id=medicine_id
        )
    )


@medicine_shelf_bp.route(
    "/medicine/delete/<int:medicine_id>",
    methods=["POST"]
)
def remove_medicine(medicine_id):

    delete_medicine(
        medicine_id
    )

    return redirect(
        url_for(
            "medicine_shelf.medicine_shelf"
        )
    )