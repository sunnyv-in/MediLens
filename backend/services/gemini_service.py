import os
import json
from PIL.ImagePalette import raw
from google import genai
from dotenv import load_dotenv
from backend.services.fallback_extractor import extract_medicine_info_fallback
import traceback

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found.")

client = genai.Client(api_key=api_key)



def extract_medicine_info_and_explanation(cleaned_data, ranked_data):
    all_lines = []

    # Highest priority OCR lines
    for item in ranked_data[:20]:
        all_lines.append(item["text"])

    # Add remaining cleaned lines
    for item in cleaned_data:
        if item["text"] not in all_lines:
            all_lines.append(item["text"])

    combined_text = "\n".join(all_lines)

    prompt = f"""
You are an expert pharmacist and medicine identification assistant.

You are given OCR text extracted from a medicine package.
The OCR may contain spelling mistakes, missing letters, wrong characters,
broken words, duplicated text, or partially detected company names.

Your task has TWO parts:

PART 1 — MEDICINE INFORMATION

Extract the following information.

IMPORTANT:

medicine_name means the COMMERCIAL BRAND NAME printed on the package.

Examples:
DOLO 650
AZITHRAL 500
DUOLIN
MAHACEF
ECOSPRIN AV 75
MONOCEF-O

These are examples only. Do not copy them unless they are actually present
in the OCR text.

Do NOT use the generic composition as medicine_name.

If both a brand name and generic composition exist, choose the BRAND NAME.

Correct OCR mistakes only when there is strong evidence.

If OCR already appears correct, preserve the original wording.

Never invent information.

IMPORTANT RULES FOR BATCH NUMBER AND DATES:

- For batch_number, manufacturing_date, and expiry_date, extract values
  only if explicitly supported by OCR text.
- Never guess or invent these values.
- The label and its value may appear on separate consecutive lines.
- Do not confuse manufacturing licence numbers with batch numbers.
- Batch numbers are usually associated with B.NO, BATCH, BATCH NO, or LOT.
- Manufacturing dates are usually associated with MFG, MFD, MFG DATE,
  or MANUFACTURED.
- Expiry dates are usually associated with EXP, EXPIRY, or EXP DATE.
- If there is insufficient evidence, return an empty string.

PART 2 — MEDICINE EXPLANATION

Using the medicine information you extracted, provide a simple explanation
for an ordinary patient.

Include:

What is this medicine?
Uses
How to take it
Common Side Effects
Important Precautions
Storage
Important Note

Do NOT prescribe an exact dosage.

Tell the patient to follow their doctor's prescription or the instructions
on the medicine package.

Mention important precautions such as:
- Pregnancy
- Alcohol
- Driving
- Kidney/Liver problems
- Allergies
- Drug interactions

Use simple English.

Minimum 100 words.
Maximum 300 words.

End the explanation with:

"This information is for educational purposes only. Always consult your doctor or pharmacist before starting or stopping any medicine."

Do not use # symbols.

IMPORTANT:
Base the explanation on the medicine information extracted from the OCR.
Do not invent medicine-specific information when the medicine identity is
uncertain.

OCR TEXT:

{combined_text}

Return ONLY valid JSON in exactly this structure:

{{
    "medicine": {{
        "medicine_name": "",
        "manufacturer": "",
        "generic_name": "",
        "strength": "",
        "composition": "",
        "batch_number": "",
        "manufacturing_date": "",
        "expiry_date": "",
        "dosage": "",
        "storage": "",
        "warnings": "",
        "pack_size": ""
    }},
    "explanation": ""
}}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config={
                "temperature": 0,
                "max_output_tokens": 1400,
                "response_mime_type": "application/json",
                "thinking_config": {
                    "thinking_budget": 0
                }
            }
        )

        raw = response.text.strip()

        if not raw:
            raise ValueError("Gemini returned an empty response.")

        # Remove markdown code fences if Gemini adds them
        if raw.startswith("```"):
            raw = (
                raw
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

        # --------------------------------------------------
        # JSON PARSING
        # --------------------------------------------------

        try:
            result = json.loads(raw)

        except json.JSONDecodeError:

            # Gemini may occasionally return additional text
            # before or after the JSON object.
            start = raw.find("{")
            end = raw.rfind("}")

            if start == -1 or end == -1 or end <= start:
                raise

            json_text = raw[start:end + 1]

            result = json.loads(json_text)

        # --------------------------------------------------
        # EXTRACT MEDICINE INFORMATION + EXPLANATION
        # --------------------------------------------------

        medicine_info = result.get("medicine", {})
        explanation = result.get("explanation", "")

        # Make sure the expected medicine object exists
        if not isinstance(medicine_info, dict):
            raise ValueError(
                "Gemini returned an invalid medicine object."
            )

        # Make sure explanation is a string
        if not isinstance(explanation, str):
            explanation = ""

        return medicine_info, explanation

    except json.JSONDecodeError:
        print(
            "Gemini returned invalid JSON. "
            "Using general fallback extractor."
        )

        medicine_info = extract_medicine_info_fallback(
            cleaned_data,
            ranked_data
        )

        return (
            medicine_info,
            "AI explanation is temporarily unavailable."
        )

    except Exception:
        traceback.print_exc()

        medicine_info = extract_medicine_info_fallback(
            cleaned_data,
            ranked_data
        )

        return (
            medicine_info,
            "AI explanation is temporarily unavailable."
        )