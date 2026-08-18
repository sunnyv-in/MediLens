from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime

from backend.extensions import db
from backend.models.medicine import Medicine
from backend.models.reminder import MedicationReminder


from backend.models.medicine import Medicine

from backend.services.reminder_service import (
    get_all_reminders,
    get_reminder_by_id,
    add_reminder,
    update_reminder,
    delete_reminder,
    toggle_reminder
)

reminder_bp = Blueprint("reminder", __name__)


@reminder_bp.route("/reminders")
def reminders():

    reminders = get_all_reminders()

    medicines = Medicine.query.all()

    return render_template(
        "reminder/reminder.html",
        reminders=reminders,
        medicines=medicines
    )

@reminder_bp.route(
    "/reminders/add",
    methods=["POST"]
)
def add_new_reminder():

    reminder_data = {

        "medicine_id": request.form.get(
            "medicine_id"
        ),

        "reminder_time": datetime.strptime(

            request.form.get(
                "reminder_time"
            ),

            "%H:%M"

        ).time(),

        "frequency": request.form.get(
            "frequency"
        ),

        "instructions": request.form.get(
            "instructions"
        )

    }

    add_reminder(
        reminder_data
    )

    flash(
        "Reminder added successfully.",
        "success"
    )

    return redirect(
        url_for(
            "reminder.reminders"
        )
    )


@reminder_bp.route(
    "/reminders/edit/<int:reminder_id>",
    methods=["GET", "POST"]
)
def edit_reminder(
    reminder_id
):

    reminder = get_reminder_by_id(
        reminder_id
    )

    if request.method == "POST":

        reminder_data = {

            "medicine_id": request.form.get(
                "medicine_id"
            ),

            "reminder_time": datetime.strptime(

                request.form.get(
                    "reminder_time"
                ),

                "%H:%M"

            ).time(),

            "frequency": request.form.get(
                "frequency"
            ),

            "instructions": request.form.get(
                "instructions"
            )

        }

        update_reminder(
            reminder_id,
            reminder_data
        )

        flash(
            "Reminder updated.",
            "success"
        )

        return redirect(
            url_for(
                "reminder.reminders"
            )
        )

    medicines = Medicine.query.all()

    return render_template(
        "reminder/edit_reminder.html",
        reminder=reminder,
        medicines=medicines
    )


@reminder_bp.route(
    "/reminders/delete/<int:reminder_id>",
    methods=["POST"]
)
def remove_reminder(
    reminder_id
):

    delete_reminder(
        reminder_id
    )

    flash(
        "Reminder deleted.",
        "success"
    )

    return redirect(
        url_for(
            "reminder.reminders"
        )
    )


@reminder_bp.route(
    "/reminders/toggle/<int:reminder_id>",
    methods=["POST"]
)
def toggle_reminder_status(
    reminder_id
):

    toggle_reminder(
        reminder_id
    )

    return redirect(
        url_for(
            "reminder.reminders"
        )
    )