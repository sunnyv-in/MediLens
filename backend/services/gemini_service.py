"""MediLens AI medicine extraction and explanation router.

Provider order:
1. Google Gemini
2. Groq (only when ENABLE_GROQ_FALLBACK=true)
3. OpenRouter free-model router
4. Local OCR-based fallback

The local fallback deliberately does not infer indications, dosage, side effects,
or patient-specific precautions from incomplete OCR text.
"""

from __future__ import annotations

import json
import os
import re
import time
from typing import Any

import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types

from backend.services.fallback_extractor import extract_medicine_info_fallback


# Load .env without overriding variables already provided by the environment.
load_dotenv(override=False)


# -----------------------------------------------------------------------------
# Provider configuration
# -----------------------------------------------------------------------------

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Current model IDs are checked against the providers' model documentation.
# If a provider retires a model, update this list rather than changing the router.
GEMINI_MODELS = (
    # Flash-Lite is the first choice for a faster, lower-cost response.
    "gemini-3.5-flash-lite",
    # Use the more capable Flash model only if Flash-Lite is unavailable.
    "gemini-3.8-flash",
)

GROQ_MODELS = (
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
)

# OpenRouter's router selects from available free models. This avoids silently
# selecting a paid model when the application is intended to be free-first.
OPENROUTER_MODELS = ("openrouter/free",)

MEDICINE_FIELDS = (
    "medicine_name",
    "manufacturer",
    "generic_name",
    "strength",
    "composition",
    "batch_number",
    "manufacturing_date",
    "expiry_date",
    "dosage",
    "storage",
    "warnings",
    "pack_size",
)

REQUEST_TIMEOUT = (5, 25)  # connect timeout, response timeout
GEMINI_TIMEOUT_MS = 20000
MAX_OCR_CHARACTERS = 9000


# -----------------------------------------------------------------------------
# Prompt construction
# -----------------------------------------------------------------------------




def _build_prompt(combined_text):

    return f"""
You are MediLens, an intelligent medicine understanding assistant.

Your purpose is to help ordinary people understand their scanned
medicine in a detailed, useful and easy-to-understand way.

The user may have no medical or pharmaceutical background.

Your explanation should feel like a knowledgeable pharmacist
personally explaining the medicine to someone who wants to understand
more than what is printed on the medicine package.

Be informative without sounding like a medical textbook.
Be conversational without becoming vague or overly simplistic.

The OCR text comes from a medicine package and may contain:
spelling mistakes, missing letters, broken words, incorrect spacing,
duplicated text and partially recognized information.

Carefully examine all OCR information before identifying the medicine.

==================================================
PART 1 — STRUCTURED MEDICINE INFORMATION
==================================================

Extract these fields:

- medicine_name:
  Exact commercial brand name printed on the packaging.
  Do not replace it with a generic ingredient name.

- manufacturer:
  Pharmaceutical company or manufacturer.

- generic_name:
  All identifiable active pharmaceutical ingredients.

- strength:
  Strength of every active ingredient, preserving its correct
  numerical value and unit.

- composition:
  Complete composition information visible on the packaging.

- batch_number:
  Extract only when distinguishable from manufacturing licence
  numbers and other printed numbers.

- manufacturing_date:
  Extract only when clearly visible.

- expiry_date:
  Extract only when clearly visible.

- dosage:
  Extract printed dosage instructions only.
  Never invent a dose, frequency or treatment duration.

- storage:
  Extract actual storage instructions printed on the pack.

- warnings:
  Extract actual medicine-specific packaging warnings.

- pack_size:
  Extract the number of tablets, capsules, respules, bottles
  or other units when visible.

IDENTIFICATION RULES:

1. Do not confuse brand names with generic ingredients.
2. Do not confuse manufacturing licence numbers with batch numbers.
3. Do not confuse manufacturing dates with expiry dates.
4. Identify the correct medicine form: tablet, capsule, syrup,
   injection, inhalation solution, cream, drops, etc.
5. Never assume the form or route of administration from
   ingredients alone.
6. Never invent missing packaging information.
7. Use an empty string when a field cannot be identified reliably.

==================================================
PART 2 — MEDICINE EXPLANATION
==================================================

Write an informative explanation of approximately 190–240 words.

The explanation should contain useful, medicine-specific information
that a person may not understand just by reading the packaging.

Cover the following naturally within 3–4 connected paragraphs.

PARAGRAPH 1 — MEDICINE AND ITS PURPOSE

Introduce the medicine by its brand name and explain its formulation,
active ingredients and main medical purpose.

Explain why doctors commonly prescribe this particular medicine
and what condition, symptoms or medical process it addresses.

Do not simply list its ingredients or say that it is used for
general health improvement.

PARAGRAPH 2 — HOW IT WORKS

Explain how the active ingredients work inside the body.

For a medicine containing multiple ingredients:
- Explain what each ingredient does.
- Explain the difference between their actions.
- Explain why the combination may be useful when established.

Translate difficult medical terminology into everyday language.

Do not merely state technical names such as bronchodilator,
antiplatelet or proton pump inhibitor without explaining
what these terms mean.

PARAGRAPH 3 — BENEFITS AND PRACTICAL USE

Explain what the medicine is intended to help with and what
realistic benefit a patient may expect.

Where relevant, distinguish between immediate symptom relief,
longer-term management and reduction of medical risks.

Explain the general method of administration based on the
actual medicine formulation.

Include useful instructions specific to the formulation
when reliably established.

Never invent an individual dose, frequency or treatment duration.

PARAGRAPH 4 — WHAT THE USER SHOULD KNOW

Explain the most relevant common side effects and important
medicine-specific precautions.

Mention serious warning signs only when supported by
reliable medicine knowledge.

Include relevant interactions, pregnancy precautions and
storage instructions when appropriate.

Avoid generic warnings that do not apply to the medicine.

Do not add information just to fill space.

==================================================
PART 3 — WRITING AND FORMATTING STYLE
==================================================

THIS IS EXTREMELY IMPORTANT.

The final explanation must read like a well-written,
easy-to-understand medicine guide rather than a medical report.

WRITING STYLE:

- Write 3–4 natural paragraphs.
- Do not create separate section headings.
- Do not use numbered sections.
- Do not use bullet points or lists.
- Do not use uppercase headings.
- Use connected sentences and natural transitions.
- Keep paragraphs reasonably short and readable.
- Explain important details without repeating information.
- Do not make the explanation unnecessarily long.
- Do not make the explanation so short that it becomes generic.
- Give the user useful knowledge specific to this medicine.

USE INLINE EMPHASIS:

Use Markdown formatting selectively.

Use **bold** for:
- The commercial medicine name when first introduced.
- Important active ingredients.
- Important differences between ingredient actions.
- Particularly useful medical information.
- Important medicine-specific precautions.

Use *italics* for:
- Technical medical terms that deserve subtle emphasis.
- Brief scientific terms or concepts that may need explanation.

FORMATTING LIMITS:

- Do not bold entire sentences.
- Do not italicize complete paragraphs.
- Do not overuse emphasis.
- Never use standalone headings.
- Keep the formatting natural and professional.

==================================================
PART 4 — MEDICAL ACCURACY AND SAFETY
==================================================

- Be specific to the identified medicine.
- Explain why each active ingredient matters.
- Explain combination medicines accurately.
- Never invent dosage instructions.
- Never tell users to start, stop or change medication.
- Do not diagnose the user.
- Do not assume why the individual user is taking the medicine.
- Do not promise a cure or guaranteed result.
- Never invent side effects or interactions.
- Mention pregnancy, alcohol, driving and other precautions
  only when genuinely relevant.
- Do not confuse formulation or route of administration.
- Do not make unsupported medical claims.
- If medicine identification is uncertain, say so.
- If information cannot be reliably established, do not guess.
- Never fill space with generic medical advice.
- Avoid claiming that a medicine prevents a medical event
  for every person who takes it.

Use accurate, established medicine knowledge.
Prioritize information supported by the identified active ingredients
and packaging. Clearly communicate uncertainty where needed.

End with this exact sentence:

This information is for educational purposes only.
Always consult your doctor or pharmacist before starting or
stopping any medicine.

==================================================
OCR TEXT FROM THE MEDICINE PACKAGE
==================================================

{combined_text}

==================================================
FINAL OUTPUT FORMAT
==================================================

Return ONLY valid JSON.

Use exactly this structure:

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

The explanation must be a single JSON string containing
3–4 natural paragraphs with appropriate inline Markdown
bold and italic markers.

Preserve paragraph breaks using valid escaped newline characters.
Do not include separate headings, numbered sections or lists.
"""

# -----------------------------------------------------------------------------
# OCR text preparation
# -----------------------------------------------------------------------------


def _get_text(item: Any) -> str:
    """Accept OCR entries represented as dictionaries or plain strings."""

    if isinstance(item, str):
        return item.strip()

    if isinstance(item, dict):
        value = item.get("text", "")
        return str(value).strip() if value is not None else ""

    return ""


def _combine_ocr_text(cleaned_data: Any, ranked_data: Any) -> str:
    """Prioritize ranked OCR lines, then append unique cleaned OCR lines."""

    lines: list[str] = []
    seen: set[str] = set()

    for item in (ranked_data or [])[:25]:
        text = _get_text(item)
        normalized = re.sub(r"\s+", " ", text).casefold()
        if text and normalized not in seen:
            lines.append(text)
            seen.add(normalized)

    for item in cleaned_data or []:
        text = _get_text(item)
        normalized = re.sub(r"\s+", " ", text).casefold()
        if text and normalized not in seen:
            lines.append(text)
            seen.add(normalized)

    combined = "\n".join(lines)
    return combined[:MAX_OCR_CHARACTERS]


# -----------------------------------------------------------------------------
# JSON parsing and result normalization
# -----------------------------------------------------------------------------


def _normalize_medicine_info(value: Any) -> dict[str, str]:
    """Return all expected template fields as strings."""

    if not isinstance(value, dict):
        raise ValueError("AI response does not contain a valid medicine object.")

    normalized: dict[str, str] = {}
    for field in MEDICINE_FIELDS:
        item = value.get(field, "")
        if item is None:
            normalized[field] = ""
        elif isinstance(item, (str, int, float)):
            normalized[field] = str(item).strip()
        else:
            # Avoid rendering arbitrary nested model output in the template.
            normalized[field] = json.dumps(item, ensure_ascii=False)

    return normalized


def _format_explanation(text):

    text = str(text or "")

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Preserve natural paragraph breaks without adding headings.
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()

def _parse_llm_json(raw_text: str) -> tuple[dict[str, str], str]:
    """Parse JSON from model output, tolerating a surrounding code fence."""

    raw = (raw_text or "").strip()
    if not raw:
        raise ValueError("Empty response from AI.")

    # Remove common Markdown code fences without altering JSON string values.
    raw = re.sub(r"^\s*```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```\s*$", "", raw)

    # Models occasionally add a short sentence before the JSON object.
    # raw_decode parses one complete JSON value from the first opening brace.
    decoder = json.JSONDecoder()
    start = raw.find("{")
    if start < 0:
        raise ValueError("AI response does not contain a JSON object.")

    try:
        result, _end = decoder.raw_decode(raw[start:])
    except json.JSONDecodeError as exc:
        raise ValueError(f"AI returned invalid JSON: {exc.msg}") from exc

    if not isinstance(result, dict):
        raise ValueError("AI JSON response must be an object.")

    medicine_value = result.get("medicine", result)
    medicine_info = _normalize_medicine_info(medicine_value)

    explanation_value = result.get("explanation", "")
    if explanation_value is None:
        explanation = ""
    elif isinstance(explanation_value, str):
        explanation = explanation_value.strip()
    else:
        explanation = str(explanation_value).strip()

    if not explanation:
        raise ValueError("AI response did not contain an explanation.")

    return medicine_info, explanation


# -----------------------------------------------------------------------------
# OpenAI-compatible provider call (Groq / OpenRouter)
# -----------------------------------------------------------------------------


def _call_openai_compatible(
    url: str,
    api_key: str,
    model_name: str,
    prompt: str,
    provider_name: str,
) -> tuple[dict[str, str], str]:
    """Call a provider exposing the OpenAI Chat Completions API format."""

    if not url.startswith("https://"):
        raise ValueError(f"Invalid HTTPS endpoint for {provider_name}.")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    if provider_name.lower() == "openrouter":
        headers["HTTP-Referer"] = os.getenv(
            "OPENROUTER_SITE_URL", "http://localhost"
        )
        headers["X-Title"] = "MediLens"

    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a medicine-packaging information assistant. "
                    "Return valid JSON only. Do not invent medicine details, "
                    "dosages, or patient-specific medical advice."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 2500,
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    response_data = response.json()
    choices = response_data.get("choices") or []
    if not choices:
        raise ValueError(f"{provider_name} returned no completion choices.")

    message = choices[0].get("message") or {}
    response_text = message.get("content")

    # Some OpenAI-compatible APIs may return content as text-part objects.
    if isinstance(response_text, list):
        response_text = "".join(
            part.get("text", "")
            for part in response_text
            if isinstance(part, dict)
        )

    if not isinstance(response_text, str) or not response_text.strip():
        raise ValueError(f"{provider_name} returned empty model content.")

    parsed = _parse_llm_json(response_text)
    print(f"[AI Router] Success using {provider_name} ({model_name}).")
    return parsed


# -----------------------------------------------------------------------------
# Google Gemini provider call
# -----------------------------------------------------------------------------


def _call_gemini(
    api_key: str,
    model_name: str,
    prompt: str,
    env_key: str,
) -> tuple[dict[str, str], str]:
    """Call Gemini with retries disabled to avoid very long 503 waits.

    The router will move to the next model/provider after one failed attempt.
    The SDK's default retry/backoff can otherwise make a scan wait a long time
    during temporary provider overload.
    """

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=GEMINI_TIMEOUT_MS,
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    )

    started = time.perf_counter()
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config={
            "max_output_tokens": 1600,
            "response_mime_type": "application/json",
        },
    )

    response_text = getattr(response, "text", None)
    if not response_text:
        raise ValueError("Gemini returned an empty response.")

    parsed = _parse_llm_json(response_text)
    elapsed = time.perf_counter() - started
    print(
        f"[AI Router] Success using Gemini ({model_name}, {env_key}) "
        f"in {elapsed:.2f}s."
    )
    return parsed


# -----------------------------------------------------------------------------
# Safe local fallback
# -----------------------------------------------------------------------------


def _build_local_explanation(medicine_info: dict[str, str]) -> str:
    """Build a conservative explanation when all cloud providers fail."""

    name = medicine_info.get("medicine_name") or "Not confidently identified"
    generic = medicine_info.get("generic_name") or "Not confirmed from the scan"
    strength = medicine_info.get("strength") or "Not confirmed from the scan"
    manufacturer = medicine_info.get("manufacturer") or "Not confirmed from the scan"
    dosage = medicine_info.get("dosage") or "No dosage instructions were confirmed in the scanned text."
    storage = medicine_info.get("storage") or "No storage instructions were confirmed in the scanned text."

    return (
        "MediLens extracted possible medicine information from the image, "
        "but its cloud AI services were unavailable. This is an OCR-based "
        "summary, not an AI-verified medicine identification.\n\n"
        f"Medicine name: {name}\n"
        f"Possible active ingredients: {generic}\n"
        f"Strength: {strength}\n"
        f"Manufacturer: {manufacturer}\n\n"
        f"Dosage information: {dosage}\n"
        f"Storage information: {storage}\n\n"
        "Please compare every extracted field with the original packaging. "
        "Do not use this fallback to decide what medicine to take or how much "
        "to take. Follow your existing prescription and ask a registered "
        "pharmacist or doctor to confirm the medicine and instructions.\n\n"
        "This information is for educational purposes only. Always consult "
        "your doctor or pharmacist before starting or stopping any medicine."
    )


def _run_local_fallback(cleaned_data: Any, ranked_data: Any) -> tuple[dict[str, str], str]:
    """Run the project's existing local extractor and normalize its fields."""

    try:
        extracted = extract_medicine_info_fallback(
            cleaned_data or [],
            ranked_data or [],
        )
    except Exception as exc:
        print(f"[AI Router] Local fallback extractor failed: {type(exc).__name__}: {exc}")
        extracted = {}

    if not isinstance(extracted, dict):
        extracted = {}

    # Support the older fallback extractor's possible alias, while keeping the
    # exact field names expected by result.html.
    if not extracted.get("medicine_name") and extracted.get("medicine"):
        extracted["medicine_name"] = extracted.get("medicine")

    medicine_info = _normalize_medicine_info(extracted)
    explanation = _build_local_explanation(medicine_info)
    return medicine_info, explanation


# -----------------------------------------------------------------------------
# Main public function imported by scan_routes.py
# -----------------------------------------------------------------------------


def extract_medicine_info_and_explanation(
    cleaned_data: Any,
    ranked_data: Any,
) -> tuple[dict[str, str], str]:
    """Extract medicine fields and explanation, using provider fallbacks.

    Returns:
        (medicine_info, explanation)

    This return shape matches the existing call in scan_routes.py:
        medicine_info, explanation = extract_medicine_info_and_explanation(...)
    """

    combined_text = _combine_ocr_text(cleaned_data, ranked_data)

    if not combined_text.strip():
        print("[AI Router] No OCR text available. Using local fallback.")
        return _run_local_fallback(cleaned_data, ranked_data)

    prompt = _build_prompt(combined_text)

    # 1. Google Gemini. Additional keys are optional. Keys belonging to the
    # same Google Cloud project share project-level quota; extra keys do not
    # multiply the quota. Use keys only for projects you control/are authorized
    # to use, not to bypass provider limits.
    for env_key in ("GEMINI_API_KEY", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3"):
        api_key = os.getenv(env_key, "").strip()
        if not api_key:
            continue

        for model_name in GEMINI_MODELS:
            try:
                print(f"[AI Router] Trying Gemini ({model_name} via {env_key})...")
                return _call_gemini(api_key, model_name, prompt, env_key)
            except Exception as exc:
                message = str(exc).replace("\n", " ")[:350]
                print(
                    f"[AI Router] Gemini {model_name} ({env_key}) failed: "
                    f"{type(exc).__name__}: {message}"
                )

    # 2. Groq. This is opt-in because Groq model/API pricing and free quotas
    # depend on the account. Set ENABLE_GROQ_FALLBACK=true only after checking
    # your account's current billing and rate limits.
    groq_enabled = os.getenv("ENABLE_GROQ_FALLBACK", "false").strip().lower() in {
        "1", "true", "yes", "on"
    }

    if groq_enabled:
        for env_key in ("GROQ_API_KEY", "GROQ_API_KEY_2"):
            groq_key = os.getenv(env_key, "").strip()
            if not groq_key:
                continue

            for model_name in GROQ_MODELS:
                try:
                    print(f"[AI Router] Trying Groq ({model_name} via {env_key})...")
                    return _call_openai_compatible(
                        GROQ_API_URL,
                        groq_key,
                        model_name,
                        prompt,
                        "Groq",
                    )
                except Exception as exc:
                    message = str(exc).replace("\n", " ")[:350]
                    print(
                        f"[AI Router] Groq {model_name} ({env_key}) failed: "
                        f"{type(exc).__name__}: {message}"
                    )
    else:
        print("[AI Router] Groq fallback disabled. Set ENABLE_GROQ_FALLBACK=true to enable it.")

    # 3. OpenRouter free-model router. This uses only the free router rather
    # than silently falling back to a paid model. Free-model availability and
    # rate limits are controlled by OpenRouter and the selected model provider.
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if openrouter_key:
        for model_name in OPENROUTER_MODELS:
            try:
                print(f"[AI Router] Trying OpenRouter ({model_name})...")
                return _call_openai_compatible(
                    OPENROUTER_API_URL,
                    openrouter_key,
                    model_name,
                    prompt,
                    "OpenRouter",
                )
            except Exception as exc:
                message = str(exc).replace("\n", " ")[:350]
                print(
                    f"[AI Router] OpenRouter {model_name} failed: "
                    f"{type(exc).__name__}: {message}"
                )

    # 4. Local extractor. The UI will still receive all expected fields and
    # a safe explanation, even when every external provider is unavailable.
    print("[AI Router] Cloud APIs exhausted. Using local fallback extractor.")
    return _run_local_fallback(cleaned_data, ranked_data)
