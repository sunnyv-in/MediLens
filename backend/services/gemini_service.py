import os
import json
from google import genai
from dotenv import load_dotenv
from services.fallback_extractor import extract_medicine_info_fallback

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def extract_medicine_info_ai(ranked_data):
    lines = [item["text"] for item in ranked_data]
    combined_text = "\n".join(lines)

    prompt = f"""
You are an expert pharmacist and medicine identification assistant.

You are given OCR text extracted from a medicine strip.
The OCR may contain spelling mistakes, missing letters, wrong characters,
or partially detected company names.

Your job is to infer the correct medicine information.

Examples:
MEOFZRD -> MEDOFORD
ALEMBLC -> ALEMBIC
SUNPHARMA -> SUN PHARMA
GLAXO -> GLAXOSMITHKLINE

Do NOT simply copy OCR.
Correct obvious OCR mistakes whenever possible.

IMPORTANT RULES FOR BATCH NUMBER AND DATES:

- For batch_number, manufacturing_date, and expiry_date, extract values
  only if they are explicitly supported by the OCR text.

- Never guess, invent, or infer a batch number, manufacturing date,
  or expiry date that is not present in the OCR text.

- Do not confuse manufacturing licence numbers such as
  "Mfg. Lic. No.", "Lic. No.", or values like "MNB/06/291"
  with the medicine batch number.

- Batch numbers are usually associated with labels such as:
  "B.NO", "B. NO.", "BATCH", "BATCH NO", or "LOT".

- Manufacturing dates are usually associated with:
  "MFG", "MFD", "MFG DATE", or "MANUFACTURED".

- Expiry dates are usually associated with:
  "EXP", "EXPIRY", or "EXP DATE".

- OCR may confuse similar characters such as:
  O and 0, I and 1, D and 0, B and 8.
  Correct such mistakes only when there is strong OCR evidence.

- If there is insufficient OCR evidence for any field,
  return an empty string.

OCR TEXT:

{combined_text}

Return ONLY valid JSON.

{{
    "medicine": "",
    "manufacturer": "",
    "strength": "",
    "batch_number": "",
    "manufacturing_date": "",
    "expiry_date": ""
}}

If a field is missing, return an empty string.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        raw = (
            response.text.strip()
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        return json.loads(raw)

    except json.JSONDecodeError:
        print("Gemini returned invalid JSON. Using general fallback extractor.")
        return extract_medicine_info_fallback(ranked_data)

    except Exception as e:
        print(f"Gemini medicine extraction error: {e}")
        print("Using general fallback extractor.")
        return extract_medicine_info_fallback(ranked_data)


def get_ai_explanation(medicine_name):
    """Feature 3: AI Medicine Explanation"""

    if not medicine_name:
        return "Medicine name detect nahi ho paaya, explanation possible nahi."

    prompt = f"""
Explain the medicine "{medicine_name}" in simple language for a common person.
Cover: what it's used for, typical dosage guidance (general, not prescriptive),
and common side effects. Keep it under 120 words. Do not give specific
prescriptive medical advice — mention consulting a doctor/pharmacist.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return response.text.strip()

    except Exception as e:
        print(f"Gemini explanation error: {e}")

        return (
            "AI explanation is temporarily unavailable because the AI service "
            "quota or request limit has been reached. Please try again later."
        )