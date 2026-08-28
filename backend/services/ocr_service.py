import easyocr
import difflib
import re
import os

import torch

USE_GPU = torch.cuda.is_available()

print(f"EasyOCR GPU Enabled: {USE_GPU}")

try:

    reader = easyocr.Reader(
        ['en'],
        gpu=USE_GPU
    )

except Exception:

    print("GPU unavailable. Using CPU.")

    reader = easyocr.Reader(
        ['en'],
        gpu=False
    )

CONFIDENCE_THRESHOLD = 0.30
DEBUG = False


IMPORTANT_KEYWORDS = [
    "TABLET", "TABLETS",
    "CAPSULE", "CAPSULES",
    "SYRUP",
    "INJECTION",
    "CREAM",
    "OINTMENT",
    "GEL",
    "USP",
    "IP",
    "MG",
    "MCG",
    "ML",
    "IU",
    "PHARMA",
    "PHARMACEUTICAL",
    "LABORATORIES",
    "LTD",
    "LIMITED",
    "MANUFACTURED",
    "MARKETED",
    "BATCH",
    "MFG",
    "EXP"
]

BAD_KEYWORDS = [
    "WARNING",
    "STORE",
    "KEEP",
    "CHILDREN",
    "SCHEDULE",
    "CAUTION",
    "READ",
    "DISTRICT",
    "ROAD",
    "PHONE"
]

DATE_KEYWORDS = [

    "B.NO",
    "BATCH",
    "LOT",
    "MFG",
    "MFD",
    "EXP",
    "EXPIRY"

]

def _read_single_image(path):

    if DEBUG:
        print(f"Reading: {os.path.basename(path)}")

    results = reader.readtext(
        path,
        detail=1,
        paragraph=False,
        decoder="beamsearch",
        batch_size=8,
        text_threshold=0.6,
        low_text=0.3,
        link_threshold=0.4
    )

    detections = []

    for bbox, text, confidence in results:

        text = text.strip()

        if not text:
            continue

        if len(text) == 1 and text.upper() not in ["C", "%"]:
            continue

        if confidence < CONFIDENCE_THRESHOLD:
            continue

        if not re.search(r"[A-Za-z0-9]", text):
            continue

        detections.append({

            "text": text,

            "confidence": confidence,

            "source": os.path.basename(path)

        })

    if DEBUG:
        print(f"{os.path.basename(path)} -> {len(detections)} detections")

    return detections


def extract_text(image_paths):

    detections = []

    for path in image_paths:

        detections.extend(_read_single_image(path))

    return detections

def _is_ocr_sufficient(detections):
    """
    Conservative medicine-specific OCR quality check.

    This function only decides whether the current OCR
    result is strong enough to stop additional OCR passes.

    It does NOT identify or modify medicine information.

    Existing OCR cleaning, ranking, Gemini extraction,
    and database logic remain unchanged.
    """

    if not detections:
        return False

    # --------------------------------------------------
    # 1. Keep reasonably confident OCR detections
    # --------------------------------------------------

    useful = [
        item
        for item in detections
        if item["confidence"] >= 0.45
    ]

    if len(useful) < 3:
        return False

    # --------------------------------------------------
    # 2. Ignore obvious non-medicine text
    # --------------------------------------------------

    ignored_terms = [
        "CAUTION",
        "WARNING",
        "STORE",
        "KEEP",
        "CHILDREN",
        "PRESCRIPTION",
        "PHYSICIAN",
        "REGISTERED",
        "SCHEDULE",
        "READ",
        "DISTRICT",
        "ROAD",
        "PHONE",
        "LIC",
        "LICENSE",
        "MFG",
        "MFD",
        "EXP",
        "EXPIRY",
        "BATCH",
        "LOT"
    ]

    medicine_candidates = []

    for item in useful:

        text = item["text"].strip()
        upper = text.upper()

        # Ignore very short fragments
        if len(text) < 5:
            continue

        # --------------------------------------------------
        # Ignore lines that contain only a strength/unit
        # --------------------------------------------------

        strength_only = re.fullmatch(
            r"\s*\d+(?:\.\d+)?\s*(MG|MCG|ML|GM|G|IU)\s*",
            upper
        )

        if strength_only:
            continue

        # --------------------------------------------------
        # Require meaningful alphabetic content
        # --------------------------------------------------

        alphabetic_count = sum(
            character.isalpha()
            for character in text
        )

        if alphabetic_count < 3:
            continue

        # Ignore very short all-uppercase fragments
        # that are unlikely to be a medicine/brand name.
        if len(text) <= 4 and text.isupper():
            continue

        # --------------------------------------------------
        # Ignore obvious instructions, warnings,
        # addresses and manufacturing information.
        # --------------------------------------------------

        if any(
            term in upper
            for term in ignored_terms
        ):
            continue

        medicine_candidates.append(item)

    # --------------------------------------------------
    # 3. We need at least one plausible medicine-like line
    # --------------------------------------------------

    if not medicine_candidates:
        return False

    # --------------------------------------------------
    # 4. Find strongest medicine-like candidate
    # --------------------------------------------------

    best_candidate = max(
        medicine_candidates,
        key=lambda item: item["confidence"]
    )

    best_confidence = best_candidate["confidence"]

    # --------------------------------------------------
    # 5. Detect medicine strength
    # --------------------------------------------------

    combined_text = " ".join(
        item["text"]
        for item in useful
    ).upper()

    has_strength = bool(
        re.search(
            r"\b\d+(?:\.\d+)?\s*(MG|MCG|ML|GM|G|IU)\b",
            combined_text
        )
    )

    # --------------------------------------------------
    # 6. Detect pharmaceutical/package terminology
    # --------------------------------------------------

    pharmaceutical_keywords = [
        "TABLET",
        "TABLETS",
        "CAPSULE",
        "CAPSULES",
        "SYRUP",
        "INJECTION",
        "CREAM",
        "OINTMENT",
        "GEL",
        "PHARMA",
        "PHARMACEUTICAL",
        "LABORATORIES",
        "LIMITED",
        "LTD"
    ]

    pharmaceutical_keyword_count = sum(
        1
        for keyword in pharmaceutical_keywords
        if keyword in combined_text
    )

    # --------------------------------------------------
    # 7. Strong stopping condition
    #
    # A medicine-like line must have reasonable
    # confidence AND either a strength or pharmaceutical
    # context.
    # --------------------------------------------------

    if best_confidence >= 0.65:

        if has_strength:
            return True

        if pharmaceutical_keyword_count >= 1:
            return True

    # --------------------------------------------------
    # 8. Very strong OCR can stop even without a strength
    #
    # Require multiple pharmaceutical signals.
    # --------------------------------------------------

    if (
        best_confidence >= 0.80
        and pharmaceutical_keyword_count >= 2
    ):
        return True

    # --------------------------------------------------
    # 9. Otherwise continue to fallback OCR
    # --------------------------------------------------

    return False

def extract_text_fast(image_paths):
    """
    Fast OCR path.

    Runs OCR on the primary image first.
    If the result appears insufficient, progressively
    processes additional variants.

    IMPORTANT:
    The returned detection format is identical to
    extract_text(), so downstream OCR cleaning,
    ranking, Gemini extraction, and database logic
    remain unchanged.
    """

    if not image_paths:
        return []

    detections = []

    # --------------------------------------------------
    # 1. Primary OCR pass
    # --------------------------------------------------

    primary_path = image_paths[0]

    if DEBUG:
        print("\nFAST OCR - Primary pass")
        print(f"Image: {os.path.basename(primary_path)}")

    primary_detections = _read_single_image(primary_path)

    detections.extend(primary_detections)

    # --------------------------------------------------
    # 2. Check whether the primary OCR is useful
    # --------------------------------------------------

    if _is_ocr_sufficient(primary_detections):

        if DEBUG:
            print("FAST OCR - Primary result sufficient.")
            print("FAST OCR - Skipping fallback images.")

        return detections

    # --------------------------------------------------
    # 3. Fallback OCR
    # --------------------------------------------------

    if DEBUG:
        print("FAST OCR - Primary result insufficient.")
        print("FAST OCR - Running fallback OCR.")

    for path in image_paths[1:]:

        fallback_detections = _read_single_image(path)

        detections.extend(fallback_detections)

        # Stop early if enough useful OCR has been obtained
        if _is_ocr_sufficient(detections):

            if DEBUG:
                print(
                    "FAST OCR - Sufficient OCR obtained from:",
                    os.path.basename(path)
                )

            break

    return detections

def clean_ocr_text(detections):

    groups = []

    for detection in detections:

        text = detection["text"]

        placed = False

        for group in groups:

            representative = group[0]["text"]

            rep = re.sub(r'[^A-Z0-9]', '', representative.upper())
            cur = re.sub(r'[^A-Z0-9]', '', text.upper())

            similarity = difflib.SequenceMatcher(
                None,
                rep,
                cur
            ).ratio()

            if similarity >= 0.88:
                group.append(detection)
                placed = True
                break

        if not placed:
            groups.append([detection])

    cleaned_lines = []


    for group in groups:

        best = max(group, key=lambda x: x["confidence"])
        votes = len(group)

        cleaned_lines.append({
            "text": best["text"],
            "confidence": best["confidence"],
            "source": best["source"],
            "votes": votes
        })

        if DEBUG:
            print(
                f"{best['text']} | "
                f"Confidence: {best['confidence']:.2f} | "
                f"Votes: {votes}"
            )

    return cleaned_lines

def rank_ocr_lines(cleaned_data):


    ranked = []

    for item in cleaned_data:

        score = 0

        text = item["text"]
        upper = text.upper()

        score += item["confidence"] * 10
        score += item["votes"] * 2
        # Medicine names are usually short
        # Medicine names are usually short
        word_count = len(text.split())

        if 1 <= word_count <= 3:
            score += 3

        # Reward medicine strengths
        if re.search(r"\d+\s*(MG|MCG|ML|GM|G|IU)", upper):
            score += 4

        for word in IMPORTANT_KEYWORDS:
            if word in upper:
                score += 5

        for word in DATE_KEYWORDS:
            if word in upper:
                score += 4

        # Give extra priority to date-like patterns
        date_patterns = [
            r"\b\d{1,2}[/-]\d{2,4}\b",   # 03/2026 or 03-2026
            r"\b\d{2,4}[/-]\d{1,2}\b",   # 2026/03 or 2026-03
            r"\b(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*[\s./-]*\d{2,4}\b"
        ]

        for pattern in date_patterns:
            if re.search(pattern, upper):
                score += 5
                break


        for word in BAD_KEYWORDS:
            if word in upper:
                score -= 4

        ranked.append({
            "text": text,
            "confidence": item["confidence"],
            "votes": item["votes"],
            "score": score
        })

    ranked.sort(key=lambda x: x["score"], reverse=True)


    if DEBUG:
        for item in ranked[:50]:
            print(f'{item["score"]:.2f} | {item["text"]}')

    print("\nTOP OCR LINES")
    for item in ranked[:20]:
        print(item["text"])

    return ranked