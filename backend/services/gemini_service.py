import os
import json
from google import genai
from dotenv import load_dotenv
from backend.services.fallback_extractor import extract_medicine_info_fallback
import traceback

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found.")

client = genai.Client(api_key=api_key)
print("Loaded API Key:", api_key[:20])


def extract_medicine_info_ai(cleaned_data, ranked_data):
    all_lines = []

    # Highest priority OCR lines
    for item in ranked_data[:20]:
        all_lines.append(item["text"])

    # Add remaining cleaned lines
    for item in cleaned_data:
        if item["text"] not in all_lines:
            all_lines.append(item["text"])

    combined_text = "\n".join(all_lines)
    print("\n================ CURRENT OCR ================\n")
    print(combined_text)
    print("\n=============================================\n")

    prompt = f"""
You are an expert pharmacist and medicine identification assistant.

You are given OCR text extracted from a medicine strip, in top-to-bottom
reading order. The OCR may contain spelling mistakes, missing letters,
wrong characters, or partially detected company names.

Your job is to infer the correct medicine information.
IMPORTANT:

medicine_name means the COMMERCIAL BRAND NAME printed on the package.

Examples:

Brand Name:
"DOLO 650,
AZITHRAL 500,
DUOLIN 3,
ECOSPRIN AV 75,
AUGMENTIN 625"

Remember, do not confuse the generic composition with the medicine_name.
and also only use Examples for reference, do not copy them. unles or until they are present in the OCR text.

NOT medicine_name:
Paracetamol
Azithromycin
Ipratropium Bromide
Levosalbutamol Sulphate

The medicine_name should ALWAYS be the marketed brand printed prominently.

If both a brand name and generic composition exist, choose the BRAND NAME.

For the uploaded OCR, "Duolin 3" is the medicine name while
"Ipratropium Bromide and Levosalbutamol Sulphate"
is the generic name.

Examples:

DOLO 650
AZITHRAL 500
DUOLIN
MAHACEF
ECOSPRIN AV 75
MONOCEF-O

Examples:
MEOFZRD -> MEDOFORD
ALEMBLC -> ALEMBIC
SUNPHARMA -> SUN PHARMA
GLAXO -> GLAXOSMITHKLINE

Correct OCR mistakes only when there is strong evidence.

If OCR already appears correct,
preserve the original wording.

Never invent information.
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

OCR TEXT (highest-confidence lines appear first)

The OCR may contain:

- spelling mistakes
- broken words
- words split across multiple lines
- duplicated text
- rotated text
- incomplete manufacturer names

Use ALL OCR lines together before deciding that information is missing.

OCR TEXT:

{combined_text}

The first lines are the most reliable OCR results.
Lower lines may still contain useful missing information.
Use all available OCR evidence before deciding a field is missing.

Extract as many fields as possible.

If one field is missing, continue extracting the remaining fields.

Do not leave every field empty simply because one field cannot be determined.

Return ONLY valid JSON.

{{
    "medicine_name":"",
    "manufacturer":"",
    "generic_name":"",
    "strength":"",
    "composition":"",
    "batch_number":"",
    "manufacturing_date":"",
    "expiry_date":"",
    "dosage":"",
    "storage":"",
    "warnings":"",
    "pack_size":""
}}
"""

    try:
        response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
                config={
                    "temperature": 0,
                    "max_output_tokens": 2048,
                    "response_mime_type": "application/json",
                    "thinking_config": {"thinking_budget": 0}
                }
        )
        print("\n================ OCR SENT TO GEMINI ================\n")
        print(combined_text)
        print("\n====================================================\n")
        raw = response.candidates[0].content.parts[0].text.strip()

        if not raw:
            raise ValueError("Gemini returned an empty response.")

        if raw.startswith("```"):
            raw = raw.replace("```json", "").replace("```", "").strip()

        return json.loads(raw)

    except json.JSONDecodeError:
        print("Gemini returned invalid JSON. Using general fallback extractor.")
        return extract_medicine_info_fallback(cleaned_data, ranked_data)

    except Exception:                             #Return with ctrl +z if nothing happen 
        traceback.print_exc()
        return extract_medicine_info_fallback(cleaned_data, ranked_data)


def get_ai_explanation(medicine_info):
    """Feature 3: AI Medicine Explanation"""
    
    medicine_name = medicine_info.get("medicine_name")
    if not medicine_name:
        return (
            "Medicine name could not be detected from the uploaded image. "
            "AI explanation is unavailable."
        )

    prompt = f"""
You are an experienced pharmacist.

Explain the medicine "{medicine_name}" in simple language that an ordinary patient can understand.

Return the explanation in the following format:

## What is this medicine?
Explain what this medicine is.

## Uses
Mention what diseases or conditions it is commonly used to treat.

## How to take it
Explain generally how medicines of this type are usually taken.
Do NOT prescribe an exact dosage.
Mention that patients should always follow the doctor's prescription or the instructions on the medicine strip.

## Common Side Effects
Mention common side effects in bullet points.

## Important Precautions
Mention important precautions like:
- Pregnancy
- Alcohol
- Driving
- Kidney/Liver problems
- Allergies
- Drug interactions

## Storage
Explain how to store the medicine.

## Important Note
End with:

"This information is for educational purposes only. Always consult your doctor or pharmacist before starting or stopping any medicine."

Use simple English.
Minimum 100 words.
Maximum 350 words.

if you can explain the medicine in a way that is easy for an ordinary patient to understand, do so. If you cannot find enough information about this medicine, explain that the information is limited and provide general advice about consulting a doctor or pharmacist.

Don't use any # symbols in the explanation use italic formatting instead.
Return plain text only.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config={
                "temperature": 0.4,
                "max_output_tokens": 900,
                "thinking_config": {"thinking_budget": 0}
            }
        )

        return response.text.strip()

    except Exception as e:
        print(f"Gemini explanation error: {e}")

        return (
            "AI explanation is temporarily unavailable because the AI service "
            "quota or request limit has been reached. Please try again later."
        )