from datetime import datetime

from backend.services.history_service import save_history


def build_medicine_record(
    medicine_info, explanation, counterfeit_result, image_filename
    medicine_info,
    explanation,
    counterfeit_result,
    image_filename,
    ocr_text=None,
    ranked_ocr=None,
):
    medicine_info = medicine_info if isinstance(medicine_info, dict) else {}
    counterfeit_result = (
        counterfeit_result if isinstance(counterfeit_result, dict) else {}
    )

    medicine_name = (
        medicine_info.get("medicine_name")
        or medicine_info.get("medicine")
        or medicine_info.get("name")
        or "Unknown medicine"
    )

    score = counterfeit_result.get("risk_score")
    if score is None:
        score = counterfeit_result.get("score")

    scanned_at = datetime.utcnow().isoformat()

    scan_data = {
        "medicine_info": medicine_info,
        "ai_explanation": explanation,
        "counterfeit_analysis": counterfeit_result,
        "ocr_text": ocr_text,
        "ranked_ocr": ranked_ocr,
        "scan_metadata": {
            "image_filename": image_filename,
            "scanned_at": scanned_at,
        },
    }

    history = save_history(
        {
            "medicine_name": medicine_name,
            "manufacturer": medicine_info.get("manufacturer"),
            "expiry_date": medicine_info.get("expiry_date"),
            "counterfeit_score": score,
            "image_filename": image_filename,
            "scan_data": scan_data,
        }
    )

    return {
        "medicine_name": (
            medicine_info.get("medicine_name") or medicine_info.get("medicine") or ""
        ),
        "medicine_name": medicine_name,
        "manufacturer": medicine_info.get("manufacturer", ""),
        "strength": medicine_info.get("strength", ""),
        "batch_number": medicine_info.get("batch_number", ""),
        "manufacturing_date": medicine_info.get("manufacturing_date", ""),
        "expiry_date": medicine_info.get("expiry_date", ""),
        "ai_explanation": explanation,
        "counterfeit_analysis": counterfeit_result,
        "scan_metadata": {
            "image_filename": image_filename,
            "scanned_at": datetime.now().isoformat(),
        },
        "scan_metadata": scan_data["scan_metadata"],
        "history_id": history.id,
    }
