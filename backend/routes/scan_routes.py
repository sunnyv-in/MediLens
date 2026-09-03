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
    extract_text_fast,
    clean_ocr_text,
    rank_ocr_lines
)

from backend.services.gemini_service import (
    extract_medicine_info_and_explanation
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

        # --------------------------------------------------
        # PERFORMANCE BENCHMARKING
        # --------------------------------------------------

        t0 = time.perf_counter()

        # --------------------------------------------------
        # IMAGE PROCESSING
        # --------------------------------------------------

        processed_images = process_image(image_path)

        t1 = time.perf_counter()

        print(
            f"TIME - Image Processing: "
            f"{t1 - t0:.2f}s"
        )

        print("8")

        # --------------------------------------------------
        # FAST OCR
        # --------------------------------------------------

        detections = extract_text_fast(
            list(processed_images.values())
        )

        t2 = time.perf_counter()

        print(
            f"TIME - Fast OCR (PaddleOCR primary / EasyOCR fallback): "
            f"{t2 - t1:.2f}s"
        )

        print("9")

        # --------------------------------------------------
        # OCR CLEANING
        # --------------------------------------------------

        cleaned_data = clean_ocr_text(
            detections
        )

        t3 = time.perf_counter()

        print(
            f"TIME - OCR Cleaning: "
            f"{t3 - t2:.2f}s"
        )

        print("10")

        # --------------------------------------------------
        # OCR RANKING
        # --------------------------------------------------

        ranked_data = rank_ocr_lines(
            cleaned_data
        )

        t4 = time.perf_counter()

        print(
            f"TIME - OCR Ranking: "
            f"{t4 - t3:.2f}s"
        )

        print("11")

        # --------------------------------------------------
        # GEMINI
        #
        # ONE REQUEST:
        # Medicine Information + Explanation
        # --------------------------------------------------

        t5 = time.perf_counter()

        medicine_info, explanation = (
            extract_medicine_info_and_explanation(
                cleaned_data,
                ranked_data
            )
        )

        t6 = time.perf_counter()

        print(
            f"TIME - Gemini Extraction + Explanation: "
            f"{t6 - t5:.2f}s"
        )

        print("\nMEDICINE INFO")
        print(medicine_info)

        print("12")

        # --------------------------------------------------
        # COUNTERFEIT / PACKAGING RISK ANALYSIS
        # --------------------------------------------------

        counterfeit_result = analyze_counterfeit_risk(
            medicine_info
        )

        t7 = time.perf_counter()

        print(
            f"TIME - Counterfeit Analysis: "
            f"{t7 - t6:.2f}s"
        )

        print("13")

        # --------------------------------------------------
        # MEDICINE RECORD
        # --------------------------------------------------

        medicine_record = build_medicine_record(
            medicine_info=medicine_info,
            explanation=explanation,
            counterfeit_result=counterfeit_result,
            image_filename=filename
        )

        t8 = time.perf_counter()

        print(
            f"TIME - Medicine Record: "
            f"{t8 - t7:.2f}s"
        )

        print(
            f"TIME - TOTAL: "
            f"{t8 - t0:.2f}s"
        )

        print("14")

        # --------------------------------------------------
        # RESULT PAGE
        # --------------------------------------------------

        print("15")

        return render_template(
            "scan/result.html",
            filename=filename,
            medicine=medicine_info,
            explanation=explanation,
            counterfeit_result=counterfeit_result
        )

    return render_template(
        "scan/scan.html"
    )


@scan_bp.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        filename
    )