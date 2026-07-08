import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def extract_medicine_info_ai(cleaned_lines):
    combined_text = "\n".join(cleaned_lines)

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

OCR TEXT:

{combined_text}

Return ONLY valid JSON.

{{
    "medicine": "",
    "manufacturer": "",
    "strength": "",
    "batch_number": "",
    "expiry_date": ""
}}

If a field is missing, return an empty string.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    raw = response.text.strip().replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "medicine": "", "manufacturer": "",
            "strength": "", "batch_number": "", "expiry_date": ""
        }


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
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text.strip()