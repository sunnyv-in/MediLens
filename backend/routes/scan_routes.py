import os
import time
import textwrap
import requests
from uuid import uuid4

from flask import (
    Blueprint,
    render_template,
    request,
    send_from_directory,
    current_app,
    jsonify,
    Response,
)
from werkzeug.utils import secure_filename

from backend.services.image_processor import process_image, assess_image_quality
from backend.services.ocr_service import (
    extract_text_fast,
    clean_ocr_text,
    rank_ocr_lines,
    is_ocr_unreadable,
)
from backend.services.gemini_service import extract_medicine_info_and_explanation
from backend.services.counterfeit_service import analyze_counterfeit_risk
from backend.services.medicine_record_service import build_medicine_record
from backend.services.history_service import save_history

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
    if request.method == "POST":
        image = request.files.get("medicine_image")

        if not image or image.filename == "":
            return render_template("scan/scan.html", error="Please select an image.")

        orig_name = secure_filename(image.filename) or "scan.jpg"
        ext = os.path.splitext(orig_name)[1].lower() or ".jpg"

        if ext not in {".jpg", ".jpeg", ".png", ".webp", ".bmp"}:
            return render_template(
                "scan/scan.html",
                error="Unsupported file type. Please upload a JPG, PNG, or WEBP image.",
            )

        filename = f"{uuid4().hex[:8]}_{orig_name}"
        os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)

        image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

        image.save(image_path)

        t0 = time.perf_counter()

        is_usable, quality_error = assess_image_quality(image_path)
        if not is_usable:
            return render_template("scan/scan.html", error=quality_error)

        processed_images = process_image(image_path)
        t1 = time.perf_counter()

        detections = extract_text_fast(list(processed_images.values()))
        t2 = time.perf_counter()

        cleaned_data = clean_ocr_text(detections)
        t3 = time.perf_counter()

        if is_ocr_unreadable(cleaned_data):
            return render_template(
                "scan/scan.html",
                error=(
                    "This image is not clear enough to read medicine details. "
                    "Please upload a clearer, well-lit image of the medicine package."
                ),
            )

        ranked_data = rank_ocr_lines(cleaned_data)
        t4 = time.perf_counter()

        medicine_info, explanation = extract_medicine_info_and_explanation(
            cleaned_data, ranked_data
        )
        t6 = time.perf_counter()

        if not any(
            [
                (medicine_info.get("medicine_name") or "").strip(),
                (medicine_info.get("generic_name") or "").strip(),
                (medicine_info.get("composition") or "").strip(),
            ]
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

        try:
            save_history(
                {
                    "medicine_name": medicine_info.get("medicine_name")
                    or medicine_info.get("generic_name", ""),
                    "generic_name": medicine_info.get("generic_name", ""),
                    "manufacturer": medicine_info.get("manufacturer", ""),
                    "strength": medicine_info.get("strength", ""),
                    "batch_number": medicine_info.get("batch_number", ""),
                    "manufacturing_date": medicine_info.get("manufacturing_date", ""),
                    "expiry_date": medicine_info.get("expiry_date", ""),
                    "dosage": medicine_info.get("dosage", ""),
                    "usage": explanation,
                    "image_filename": filename,
                    "counterfeit_score": counterfeit_result.get("risk_score", 0),
                }
            )
        except Exception as hist_err:
            print("History save skipped:", hist_err)

        return render_template(
            "scan/result.html",
            filename=filename,
            medicine=medicine_info,
            medicine_record=medicine_record,
            explanation=explanation,
            counterfeit_result=counterfeit_result,
        )

    return render_template("scan/scan.html")


@scan_bp.route("/scan/translate", methods=["POST"])
def translate_explanation():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    target_lang = (data.get("target_lang") or "hi").strip().lower()

    if not text:
        return jsonify({"success": False, "error": "No text provided."}), 400

    if target_lang == "en":
        return jsonify({"success": True, "translated_text": text, "lang": "en"})

    if target_lang not in SUPPORTED_LANGUAGES:
        return jsonify({"success": False, "error": "Unsupported language."}), 400

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:
        gtx_url = "https://translate.googleapis.com/translate_a/single"
        params = {"client": "gtx", "sl": "auto", "tl": target_lang, "dt": "t"}
        response = requests.post(
            gtx_url, params=params, data={"q": text}, headers=headers, timeout=6
        )
        if response.status_code == 200:
            res_data = response.json()
            translated_text = "".join([chunk[0] for chunk in res_data[0] if chunk[0]])
            return jsonify(
                {
                    "success": True,
                    "translated_text": translated_text,
                    "lang": target_lang,
                }
            )
    except Exception as e:
        print("Google Translate fallback triggered:", e)

    try:
        chunks = textwrap.wrap(text, 420)
        translated_chunks = []
        for chunk in chunks:
            my_url = "https://api.mymemory.translated.net/get"
            my_res = requests.get(
                my_url,
                params={"q": chunk, "langpair": f"en|{target_lang}"},
                headers=headers,
                timeout=6,
            )
            if my_res.status_code == 200:
                my_data = my_res.json()
                translated_chunks.append(
                    my_data.get("responseData", {}).get("translatedText", chunk)
                )
        final_text = " ".join(translated_chunks)
        if final_text.strip():
            return jsonify(
                {"success": True, "translated_text": final_text, "lang": target_lang}
            )
    except Exception as my_err:
        print("MyMemory error:", my_err)

    return (
        jsonify(
            {"success": False, "error": "Translation service temporarily unavailable."}
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
    raw_sentences = [
        s.strip() for s in clean_text.replace("\n", ". ").split(".") if s.strip()
    ]
    chunks = []
    for s in raw_sentences:
        if len(s) <= 180:
            chunks.append(s)
        else:
            chunks.extend(textwrap.wrap(s, 180))

    audio_bytes = bytearray()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:
        for chunk in chunks[:25]:
            tts_url = "https://translate.google.com/translate_tts"
            params = {"ie": "UTF-8", "client": "tw-ob", "tl": lang, "q": chunk}
            resp = requests.get(tts_url, params=params, headers=headers, timeout=6)
            if resp.status_code == 200 and resp.content:
                audio_bytes.extend(resp.content)

        if not audio_bytes:
            return jsonify({"error": "TTS empty"}), 500

        return Response(bytes(audio_bytes), mimetype="audio/mpeg")
    except Exception as e:
        print("TTS stream error:", e)
        return jsonify({"error": "TTS failed"}), 500


@scan_bp.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
