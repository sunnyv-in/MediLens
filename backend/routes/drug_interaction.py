from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from backend.services.interaction_service import (
    get_all_interactions,
    get_interaction_by_id,
    add_interaction,
    update_interaction,
    delete_interaction,
    find_interaction
)

from backend.services.medicine_service import get_all_medicines

drug_interaction_bp = Blueprint(
    "drug_interaction",
    __name__
)


@drug_interaction_bp.route("/drug-interactions")
def interaction_list():

    interactions = get_all_interactions()

    return render_template(
        "interaction/interaction_list.html",
        interactions=interactions
    )


@drug_interaction_bp.route(
    "/drug-interactions/add",
    methods=["GET", "POST"]
)
def add_interaction_page():

    if request.method == "POST":

        interaction_data = {

            "drug_one": request.form.get("drug_one"),

            "drug_two": request.form.get("drug_two"),

            "severity": request.form.get("severity"),

            "description": request.form.get("description"),

            "recommendation": request.form.get("recommendation")

        }

        add_interaction(interaction_data)

        flash("Interaction added successfully.", "success")

        return redirect(
            url_for("drug_interaction.interaction_list")
        )

    return render_template(
        "interaction/add_interaction.html"
    )


@drug_interaction_bp.route(
    "/drug-interactions/<int:interaction_id>"
)
def interaction_details(interaction_id):

    interaction = get_interaction_by_id(
        interaction_id
    )

    return render_template(
        "interaction/interaction_details.html",
        interaction=interaction
    )


@drug_interaction_bp.route(
    "/drug-interactions/edit/<int:interaction_id>",
    methods=["GET", "POST"]
)
def edit_interaction(interaction_id):

    interaction = get_interaction_by_id(
        interaction_id
    )

    if request.method == "POST":

        update_interaction(
            interaction_id,
            request.form
        )

        flash("Interaction updated successfully.", "success")

        return redirect(
            url_for(
                "drug_interaction.interaction_details",
                interaction_id=interaction_id
            )
        )

    return render_template(
        "interaction/edit_interaction.html",
        interaction=interaction
    )


@drug_interaction_bp.route(
    "/drug-interactions/delete/<int:interaction_id>",
    methods=["POST"]
)
def remove_interaction(interaction_id):

    delete_interaction(interaction_id)

    flash("Interaction deleted successfully.", "success")

    return redirect(
        url_for(
            "drug_interaction.interaction_list"
        )
    )



@drug_interaction_bp.route(
    "/check-interaction",
    methods=["GET", "POST"]
)
def check_interaction():

    medicines = get_all_medicines()

    result = None

    if request.method == "POST":

        drug_one = request.form.get("drug_one")
        drug_two = request.form.get("drug_two")

        result = find_interaction(
            drug_one,
            drug_two
        )

    return render_template(
        "interaction/check_interaction.html",
        medicines=medicines,
        result=result
    )