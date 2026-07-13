from datetime import datetime


def build_medicine_record(
    medicine_info,
    explanation,
    counterfeit_result,
    image_filename
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

    return {
        "medicine_name": medicine_info.get("medicine", ""),
        "manufacturer": medicine_info.get("manufacturer", ""),
        "strength": medicine_info.get("strength", ""),
        "batch_number": medicine_info.get("batch_number", ""),
        "manufacturing_date": medicine_info.get("manufacturing_date", ""),
        "expiry_date": medicine_info.get("expiry_date", ""),

        "ai_explanation": explanation,

        "counterfeit_analysis": counterfeit_result,

        "scan_metadata": {
            "image_filename": image_filename,
            "scanned_at": datetime.now().isoformat()
        }
    }