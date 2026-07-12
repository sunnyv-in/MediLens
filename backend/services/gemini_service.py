import os
import json
from google import genai
from dotenv import load_dotenv
from backend.services.fallback_extractor import extract_medicine_info_fallback

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found.")

client = genai.Client(api_key=api_key)


def extract_medicine_info_ai(cleaned_data, ranked_data):
    sequential_lines = [item["text"] for item in cleaned_data]
    combined_text = "\n".join(sequential_lines)

    prompt = f"""
You are an expert pharmacist and medicine identification assistant.

You are given OCR text extracted from a medicine strip, in top-to-bottom
reading order. The OCR may contain spelling mistakes, missing letters,
wrong characters, or partially detected company names.

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

- The label and its value may appear on separate consecutive lines
  because OCR sometimes splits them (e.g. "B.No:" then "GP2409A" on
  the next line). Treat such adjacent lines as belonging together.

- Do not confuse manufacturing licence numbers such as
  "Mfg. Lic. No.", "Lic. No.", or values like "MNB/06/291"
  with the medicine batch number.

- Batch numbers are usually associated with labels such as:
  "B.NO", "B. NO.", "BATCH", "BATCH NO", or "LOT".

- Manufacturing dates are usually associated with:
  "MFG", "MFD", "MFG DATE", or "MANUFACTURED".

- Expiry dates are usually associated with:
  "EXP", "EXPIRY", or "EXP DATE".

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
"""

    try:
        response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    "temperature": 0,
                    "max_output_tokens": 300
                }
        )
        raw = (response.text or "").strip()

        if not raw:
            raise ValueError("Gemini returned an empty response.")

        if raw.startswith("```"):
            raw = raw.replace("```json", "").replace("```", "").strip()

        return json.loads(raw)

    except json.JSONDecodeError:
        print("Gemini returned invalid JSON. Using general fallback extractor.")
        return extract_medicine_info_fallback(cleaned_data, ranked_data)

    except Exception as e:
        print(f"Gemini medicine extraction error: {e}")
        print("Using general fallback extractor.")
        return extract_medicine_info_fallback(cleaned_data, ranked_data)


def get_ai_explanation(medicine_name):
    """Feature 3: AI Medicine Explanation"""

    if not medicine_name:
        return (
            "Medicine name could not be detected from the uploaded image. "
            "AI explanation is unavailable."
        )

    prompt = f"""
Explain the medicine "{medicine_name}" in simple language.

Return only:

• What it is used for
• Common side effects
• Important precautions

Maximum 100 words.

Do not prescribe dosage.

End with:
'Consult a healthcare professional before using any medicine.'
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "temperature": 0.2,
                "max_output_tokens": 180
            }
        )

        return response.text.strip()

    except Exception as e:
        print(f"Gemini explanation error: {e}")

        return (
            "AI explanation is temporarily unavailable because the AI service "
            "quota or request limit has been reached. Please try again later."
        )