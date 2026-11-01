import os
import time

from flask import Blueprint, render_template, request, send_from_directory, current_app
from werkzeug.utils import secure_filename

from backend.services.image_processor import process_image
from backend.services.ocr_service import (
    extract_text_fast,
    clean_ocr_text,
    rank_ocr_lines,
)
from backend.services.gemini_service import extract_medicine_info_and_explanation
from backend.services.counterfeit_service import analyze_counterfeit_risk
from backend.services.medicine_record_service import build_medicine_record
from backend.services.medicine_service import save_scanned_medicine

scan_bp = Blueprint("scan", __name__)


@scan_bp.route("/scan", methods=["GET", "POST"])
def scan():

    if request.method == "POST":

        image = request.files.get("medicine_image")

        if not image or image.filename == "":
            return render_template("scan/scan.html", error="Please select an image.")

        filename = secure_filename(image.filename)

        image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

        image.save(image_path)

        # -----------------------------------------
        # PERFORMANCE BENCHMARKING
        # -----------------------------------------

        t0 = time.perf_counter()

        # -----------------------------------------
        # IMAGE PROCESSING
        # -----------------------------------------

        processed_images = process_image(image_path)

        t1 = time.perf_counter()

        print(f"TIME - Image Processing: {t1 - t0:.2f}s")

        # -----------------------------------------
        # FAST OCR
        # -----------------------------------------

        detections = extract_text_fast(list(processed_images.values()))

        t2 = time.perf_counter()

        print(
            f"TIME - Fast OCR (PaddleOCR primary / EasyOCR fallback): "
            f"{t2 - t1:.2f}s"
        )

        # -----------------------------------------
        # OCR CLEANING
        # -----------------------------------------

        cleaned_data = clean_ocr_text(detections)

        t3 = time.perf_counter()

        print(f"TIME - OCR Cleaning: {t3 - t2:.2f}s")

        # -----------------------------------------
        # OCR RANKING
        # -----------------------------------------

        ranked_data = rank_ocr_lines(cleaned_data)

        t4 = time.perf_counter()

        print(f"TIME - OCR Ranking: {t4 - t3:.2f}s")

        # -----------------------------------------
        # GEMINI EXTRACTION + EXPLANATION
        # -----------------------------------------

        t5 = time.perf_counter()

        medicine_info, explanation = extract_medicine_info_and_explanation(
            cleaned_data, ranked_data
        )

        t6 = time.perf_counter()

        print(f"TIME - Gemini Extraction + Explanation: " f"{t6 - t5:.2f}s")

        print("\nMEDICINE INFO")
        print(medicine_info)

        # -----------------------------------------
        # COUNTERFEIT / PACKAGING RISK ANALYSIS
        # -----------------------------------------

        counterfeit_result = analyze_counterfeit_risk(medicine_info)

        t7 = time.perf_counter()

        print(f"TIME - Counterfeit Analysis: " f"{t7 - t6:.2f}s")

        # -----------------------------------------
        # MEDICINE RECORD
        # -----------------------------------------

        medicine_record = build_medicine_record(
            medicine_info=medicine_info,
            explanation=explanation,
            counterfeit_result=counterfeit_result,
            image_filename=filename,
            ocr_text=cleaned_data,
            ranked_ocr=ranked_data,
        )

        # -----------------------------------------
        # SAVE SCANNED MEDICINE
        # -----------------------------------------

        score = None

        if isinstance(counterfeit_result, dict):
            score = counterfeit_result.get("risk_score") or counterfeit_result.get(
                "score"
            )

        save_scanned_medicine(
            {
                "medicine_name": (
                    medicine_info.get("medicine_name")
                    or medicine_info.get("medicine")
                    or medicine_info.get("name")
                ),
                "generic_name": medicine_info.get("generic_name"),
                "strength": medicine_info.get("strength"),
                "manufacturer": medicine_info.get("manufacturer"),
                "batch_number": medicine_info.get("batch_number"),
                "expiry_date": medicine_info.get("expiry_date"),
                "counterfeit_score": score,
                "image_filename": filename,
                "history_id": medicine_record.get("history_id"),
            }
        )

        t8 = time.perf_counter()

        print(f"TIME - Medicine Record: {t8 - t7:.2f}s")

        print(f"TIME - TOTAL: {t8 - t0:.2f}s")

        # -----------------------------------------
        # RESULT PAGE
        # -----------------------------------------

        return render_template(
            "scan/result.html",
            filename=filename,
            medicine=medicine_info,
            explanation=explanation,
            counterfeit_result=counterfeit_result,
        )

    return render_template("scan/scan.html")


@scan_bp.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
