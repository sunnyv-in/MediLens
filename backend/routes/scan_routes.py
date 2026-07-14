import os
import time
from backend.services.medicine_service import save_medicine
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

    print("1")

    if request.method == "POST":

        print("2")

        image = request.files.get("medicine_image")

        print("3")

        if not image or image.filename == "":
            print("NO IMAGE")
            return render_template(
                "scan/scan.html",
                error="Please select an image."
            )

        print("4")

        filename = secure_filename(image.filename)

        print("5")

        image_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            filename
        )

        print("6")

        image.save(image_path)

        print("7")

        processed_images = process_image(image_path)

        print("8")

        detections = extract_text(
            list(processed_images.values())
        )

        print("9")

        cleaned_data = clean_ocr_text(detections)

        print("10")

        ranked_data = rank_ocr_lines(cleaned_data)

        print("11")

        medicine_info = extract_medicine_info_ai(
            cleaned_data,
            ranked_data
        )

        print("12")

        explanation = get_ai_explanation(medicine_info)

        print("13")

        counterfeit_result = analyze_counterfeit_risk(
            medicine_info
        )

        print("14")

        medicine_record = build_medicine_record(
            medicine_info=medicine_info,
            explanation=explanation,
            counterfeit_result=counterfeit_result,
            image_filename=filename
        )

        print("15")

        return render_template(
            "scan/result.html",
            filename=filename,
            medicine=medicine_info,
            explanation=explanation,
            counterfeit_result=counterfeit_result
        )

    return render_template("scan/scan.html")


@scan_bp.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        filename
    )