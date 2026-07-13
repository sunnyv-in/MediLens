from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for
)

from backend.services.history_service import (
    get_all_history,
    get_history_by_id,
    save_history,
    update_history,
    delete_history
)

medicine_history_bp = Blueprint(
    "medicine_history",
    __name__
)


@medicine_history_bp.route("/medicine-history")
def medicine_history():

    history = get_all_history()

    return render_template(
        "history/medicine_history.html",
        history=history
    )


@medicine_history_bp.route("/medicine-history/<int:history_id>")
def history_details(history_id):

    history = get_history_by_id(
        history_id
    )

    return render_template(
        "history/history_details.html",
        history=history
    )


@medicine_history_bp.route(
    "/medicine-history/edit/<int:history_id>",
    methods=["GET", "POST"]
)
def edit_history(history_id):

    history = get_history_by_id(
        history_id
    )

    if request.method == "POST":

        update_history(
            history_id,
            request.form
        )

        return redirect(
            url_for(
                "medicine_history.history_details",
                history_id=history_id
            )
        )

    return render_template(
        "history/edit_history.html",
        history=history
    )


@medicine_history_bp.route(
    "/medicine-history/delete/<int:history_id>",
    methods=["POST"]
)
def remove_history(history_id):

    delete_history(
        history_id
    )

    return redirect(
        url_for(
            "medicine_history.medicine_history"
        )
    )