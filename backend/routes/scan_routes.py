import os
import time
import textwrap
from uuid import uuid4

import requests
from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    render_template,
    request,
    send_from_directory,
)
from werkzeug.utils import secure_filename

from backend.services.image_processor import (
    assess_image_quality,
    process_image,
)
from backend.services.ocr_service import (
    clean_ocr_text,
    extract_text_fast,
    is_ocr_unreadable,
    rank_ocr_lines,
)
from backend.services.gemini_service import (
    extract_medicine_info_and_explanation,
)
from backend.services.counterfeit_service import analyze_counterfeit_risk
from backend.services.medicine_record_service import build_medicine_record
from backend.services.history_service import save_history

# TODO: Import this from the module where your project defines it.
# Example only: from backend.services.medicine_service import save_scanned_medicine

scan_bp = Blueprint("scan", __name__)

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
}


@scan_bp.route("/scan", methods=["GET", "POST"])
def scan():
    if request.method == "GET":
        return render_template("scan/scan.html")

    image = request.files.get("medicine_image")

    if not image or not image.filename:
        return render_template(
            "scan/scan.html",
            error="Please select an image.",
        )

    original_name = secure_filename(image.filename) or "scan.jpg"
    extension = os.path.splitext(original_name)[1].lower() or ".jpg"

    if extension not in {".jpg", ".jpeg", ".png", ".webp", ".bmp"}:
        return render_template(
            "scan/scan.html",
            error="Unsupported file type. Please upload a JPG, PNG, WEBP, or BMP image.",
        )

    filename = f"{uuid4().hex[:8]}_{original_name}"
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    image_path = os.path.join(upload_folder, filename)
    image.save(image_path)

    start_time = time.perf_counter()

    is_usable, quality_error = assess_image_quality(image_path)
    if not is_usable:
        return render_template("scan/scan.html", error=quality_error)

    processed_images = process_image(image_path)
    detections = extract_text_fast(list(processed_images.values()))
    cleaned_data = clean_ocr_text(detections)

    if is_ocr_unreadable(cleaned_data):
        return render_template(
            "scan/scan.html",
            error=(
                "This image is not clear enough to read medicine details. "
                "Please upload a clearer, well-lit image of the medicine package."
            ),
        )

    ranked_data = rank_ocr_lines(cleaned_data)

    medicine_info, explanation = extract_medicine_info_and_explanation(
        cleaned_data,
        ranked_data,
    )

    if not any(
        (medicine_info.get(key) or "").strip()
        for key in ("medicine_name", "generic_name", "composition")
    ):
        return render_template(
            "scan/scan.html",
            error=(
                "Could not identify a medicine from this image. "
                "Please upload a clearer photo showing the medicine name."
            ),
        )

    counterfeit_result = analyze_counterfeit_risk(medicine_info)

    medicine_record = build_medicine_record(
        medicine_info=medicine_info,
        explanation=explanation,
        counterfeit_result=counterfeit_result,
        image_filename=filename,
        ocr_text=cleaned_data,
        ranked_ocr=ranked_data,
    )

    score = None
    if isinstance(counterfeit_result, dict):
        score = counterfeit_result.get("risk_score")
        if score is None:
            score = counterfeit_result.get("score")

    # Ensure save_scanned_medicine is imported from its actual module.
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

    try:
        save_history(
            {
                "medicine_name": (
                    medicine_info.get("medicine_name")
                    or medicine_info.get("generic_name", "")
                ),
                "generic_name": medicine_info.get("generic_name", ""),
                "manufacturer": medicine_info.get("manufacturer", ""),
                "strength": medicine_info.get("strength", ""),
                "batch_number": medicine_info.get("batch_number", ""),
                "manufacturing_date": medicine_info.get("manufacturing_date", ""),
                "expiry_date": medicine_info.get("expiry_date", ""),
                "dosage": medicine_info.get("dosage", ""),
                "usage": explanation,
                "image_filename": filename,
                "counterfeit_score": (
                    counterfeit_result.get("risk_score", 0)
                    if isinstance(counterfeit_result, dict)
                    else 0
                ),
            }
        )
    except Exception as history_error:
        current_app.logger.exception(
            "History save skipped: %s",
            history_error,
        )

    current_app.logger.debug(
        "Medicine scan completed in %.2f seconds",
        time.perf_counter() - start_time,
    )

    return render_template(
        "scan/result.html",
        filename=filename,
        medicine=medicine_info,
        medicine_record=medicine_record,
        explanation=explanation,
        counterfeit_result=counterfeit_result,
    )


@scan_bp.route("/scan/translate", methods=["POST"])
def translate_explanation():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    target_lang = (data.get("target_lang") or "hi").strip().lower()

    if not text:
        return jsonify({"success": False, "error": "No text provided."}), 400

    if target_lang == "en":
        return jsonify(
            {
                "success": True,
                "translated_text": text,
                "lang": "en",
            }
        )

    if target_lang not in SUPPORTED_LANGUAGES:
        return jsonify({"success": False, "error": "Unsupported language."}), 400

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.post(
            "https://translate.googleapis.com/translate_a/single",
            params={
                "client": "gtx",
                "sl": "auto",
                "tl": target_lang,
                "dt": "t",
            },
            data={"q": text},
            headers=headers,
            timeout=6,
        )

        if response.status_code == 200:
            response_data = response.json()
            translated_text = "".join(
                chunk[0] for chunk in response_data[0] if chunk and chunk[0]
            )

            if translated_text.strip():
                return jsonify(
                    {
                        "success": True,
                        "translated_text": translated_text,
                        "lang": target_lang,
                    }
                )
    except Exception:
        current_app.logger.exception("Google Translate request failed")

    try:
        translated_chunks = []

        for chunk in textwrap.wrap(text, 420):
            response = requests.get(
                "https://api.mymemory.translated.net/get",
                params={
                    "q": chunk,
                    "langpair": f"en|{target_lang}",
                },
                headers=headers,
                timeout=6,
            )

            if response.status_code == 200:
                response_data = response.json()
                translated_chunks.append(
                    response_data.get("responseData", {}).get(
                        "translatedText",
                        chunk,
                    )
                )
            else:
                translated_chunks.append(chunk)

        final_text = " ".join(translated_chunks).strip()

        if final_text:
            return jsonify(
                {
                    "success": True,
                    "translated_text": final_text,
                    "lang": target_lang,
                }
            )
    except Exception:
        current_app.logger.exception("MyMemory translation request failed")

    return (
        jsonify(
            {
                "success": False,
                "error": "Translation service temporarily unavailable.",
            }
        ),
        500,
    )


@scan_bp.route("/scan/tts", methods=["POST"])
def text_to_speech():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    lang = (data.get("lang") or "en").strip().lower()

    if not text:
        return jsonify({"error": "No text"}), 400

    clean_text = text.replace("+", " and ").replace("*", " ").replace("#", " ")
    sentences = [
        sentence.strip()
        for sentence in clean_text.replace("\n", ". ").split(".")
        if sentence.strip()
    ]

    chunks = []
    for sentence in sentences:
        if len(sentence) <= 180:
            chunks.append(sentence)
        else:
            chunks.extend(textwrap.wrap(sentence, 180))

    audio_bytes = bytearray()
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        for chunk in chunks[:25]:
            response = requests.get(
                "https://translate.google.com/translate_tts",
                params={
                    "ie": "UTF-8",
                    "client": "tw-ob",
                    "tl": lang,
                    "q": chunk,
                },
                headers=headers,
                timeout=6,
            )

            if response.status_code == 200 and response.content:
                audio_bytes.extend(response.content)

        if not audio_bytes:
            return jsonify({"error": "TTS empty"}), 500

        return Response(bytes(audio_bytes), mimetype="audio/mpeg")

    except Exception:
        current_app.logger.exception("TTS request failed")
        return jsonify({"error": "TTS failed"}), 500


@scan_bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        filename,
    )
