import mimetypes
import os

from flask import current_app
from flask_mail import Message

from flask_mail import Message
from flask import current_app
from backend.extensions import mail

from backend.extensions import mail


def send_history_email(history, recipient):
    recipient = (recipient or "").strip()

    if not recipient:
        raise ValueError("Enter a recipient email address.")

    if not current_app.config.get("MAIL_USERNAME") or not current_app.config.get(
        "MAIL_PASSWORD"
    ):
        raise RuntimeError(
            "Email is not configured. Set MAIL_USERNAME and MAIL_PASSWORD."
        )

    scan_data = history.scan_data or {}
    medicine_info = scan_data.get("medicine_info") or {}
    analysis = scan_data.get("counterfeit_analysis") or {}

    body = f"""
MediLens medicine scan

Medicine: {history.medicine_name}
Manufacturer: {history.manufacturer or "Not recorded"}
Expiry date: {history.expiry_date or "Not recorded"}
Counterfeit score: {
    history.counterfeit_score
    if history.counterfeit_score is not None
    else "Not available"
}

Scan information:
{medicine_info}

Counterfeit analysis:
{analysis}
"""

    message = Message(
        subject=f"MediLens scan: {history.medicine_name}",
        recipients=[recipient],
        body=body,
    )

    if history.image_filename:
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        image_path = os.path.join(upload_folder, history.image_filename)

        if os.path.isfile(image_path):
            filename = os.path.basename(history.image_filename)
            content_type = (
                mimetypes.guess_type(filename)[0] or "application/octet-stream"
            )

            with open(image_path, "rb") as image_file:
                message.attach(
                    filename=filename,
                    content_type=content_type,
                    data=image_file.read(),
                )

    mail.send(message)


def send_medicine_shelf_email(medicines, recipient):
    recipient = (recipient or "").strip()

    if not recipient:
        raise ValueError("Enter a recipient email address.")

    if not current_app.config.get("MAIL_USERNAME") or not current_app.config.get(
        "MAIL_PASSWORD"
    ):
        raise RuntimeError(
            "Email is not configured. Check MAIL_USERNAME and MAIL_PASSWORD."
        )

    if not medicines:
        raise ValueError("Your medicine shelf is empty.")

    lines = [
        "Your saved MediLens medicine shelf",
        "",
        f"Total medicines: {len(medicines)}",
        "",
    ]

    for index, medicine in enumerate(medicines, start=1):
        lines.extend(
            [
                f"{index}. {medicine.medicine_name or 'Unnamed medicine'}",
                f"   Generic name: {medicine.generic_name or 'Not recorded'}",
                f"   Strength: {medicine.strength or 'Not recorded'}",
                f"   Manufacturer: {medicine.manufacturer or 'Not recorded'}",
                f"   Batch number: {medicine.batch_number or 'Not recorded'}",
                f"   Expiry date: {medicine.expiry_date or 'Not recorded'}",
                f"   Quantity: {medicine.quantity if medicine.quantity is not None else 'Not recorded'}",
                f"   Dosage: {medicine.dosage or 'Not recorded'}",
                "",
            ]
        )

    message = Message(
        subject="Your MediLens medicine shelf",
        recipients=[recipient],
        body="\n".join(lines),
    )

    mail.send(message)
