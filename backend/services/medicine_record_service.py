from datetime import datetime


def build_medicine_record(
    medicine_info,
    explanation,
    counterfeit_result,
    image_filename,
    ocr_text=None,
    ranked_ocr=None,
):
    """
    Creates one standardized medicine record that can be used by:
    - Result page
    - Medicine history
    - Medicine shelf
    - Expiry alerts
    - Reminder system
    - Database
    - API endpoints
    """
    medicine_info = medicine_info if isinstance(medicine_info, dict) else {}
    counterfeit_result = (
        counterfeit_result if isinstance(counterfeit_result, dict) else {}
    )

    return {
        "medicine_name": (
            medicine_info.get("medicine_name")
            or medicine_info.get("medicine")
            or medicine_info.get("name")
            or "Unknown medicine"
        ),
        "generic_name": medicine_info.get("generic_name", ""),
        "manufacturer": medicine_info.get("manufacturer", ""),
        "strength": medicine_info.get("strength", ""),
        "batch_number": medicine_info.get("batch_number", ""),
        "manufacturing_date": medicine_info.get("manufacturing_date", ""),
        "expiry_date": medicine_info.get("expiry_date", ""),
        "ai_explanation": explanation,
        "counterfeit_analysis": counterfeit_result,
        "ocr_text": ocr_text,
        "ranked_ocr": ranked_ocr,
        "scan_metadata": {
            "image_filename": image_filename,
            "scanned_at": datetime.utcnow().isoformat(),
        },
    }
