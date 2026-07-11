import os
import time

from flask import (
    Blueprint,
    render_template,
    request,
    send_from_directory,
    current_app
)

from werkzeug.utils import secure_filename

from backend.services.image_processor import process_image

from backend.services.ocr_service import (
    extract_text,
    clean_ocr_text,
    rank_ocr_lines
)

from backend.services.gemini_service import (
    extract_medicine_info_ai,
    get_ai_explanation
)

from backend.services.counterfeit_service import (
    analyze_counterfeit_risk
)

from backend.services.medicine_record_service import (
    build_medicine_record
)

scan_bp = Blueprint("scan", __name__)


@scan_bp.route("/scan", methods=["GET", "POST"])
def scan():

    if request.method == "POST":

        image = request.files.get("medicine_image")

        if not image or image.filename == "":
            return render_template(
                "scan.html",
                error="Please select an image."
            )

        filename = secure_filename(image.filename)

        image_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            filename
        )

        image.save(image_path)

        processed_images = process_image(image_path)

        detections = extract_text(
            list(processed_images.values())
        )

        cleaned_data = clean_ocr_text(detections)

        ranked_data = rank_ocr_lines(cleaned_data)

        medicine_info = extract_medicine_info_ai(
            cleaned_data,
            ranked_data
        )

        explanation = get_ai_explanation(
            medicine_info.get("medicine", "")
        )

        counterfeit_result = analyze_counterfeit_risk(
            medicine_info
        )

        medicine_record = build_medicine_record(
            medicine_info=medicine_info,
            explanation=explanation,
            counterfeit_result=counterfeit_result,
            image_filename=filename
        )

        print("\n========== STANDARD MEDICINE RECORD ==========")
        print(medicine_record)
        print("==============================================\n")

        return render_template(
            "result.html",
            filename=filename,
            medicine=medicine_info,
            explanation=explanation,
            counterfeit_result=counterfeit_result
        )

    return render_template("scan.html")


@scan_bp.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        filename
    )