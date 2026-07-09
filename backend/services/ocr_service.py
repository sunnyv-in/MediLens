import easyocr
import difflib
import re

reader = easyocr.Reader(['en'])

CONFIDENCE_THRESHOLD = 0.15

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
    "DOSAGE",
    "PROTECT",
    "DISTRICT",
    "ROAD",
    "PHONE"
]

def extract_text(image_paths):

    detections = []

    for path in image_paths:

        print(f"\nReading: {path}")

        results = reader.readtext(path)

        print(f"Detected {len(results)} text regions")

        for bbox, text, confidence in results:

            text = text.strip()

            # Remove empty strings
            if not text:
                continue

            # Remove single characters except units
            if len(text) == 1 and text.upper() not in ["C", "%"]:
                continue

            # Remove garbage confidence
            if confidence < CONFIDENCE_THRESHOLD:
                continue

            # Remove only-symbol text
            if not re.search(r"[A-Za-z0-9]", text):
                continue

            detections.append({
                "text": text,
                "confidence": confidence,
                "source": path.split("\\")[-1]
            })

    print(f"\nTotal Valid Detections : {len(detections)}")

    return detections

def clean_ocr_text(detections):

    groups = []

    for detection in detections:

        text = detection["text"]

        placed = False

        for group in groups:

            representative = group[0]["text"]

            similarity = difflib.SequenceMatcher(
                None,
                representative.upper(),
                text.upper()
            ).ratio()

            if similarity >= 0.80:
                group.append(detection)
                placed = True
                break

        if not placed:
            groups.append([detection])

    cleaned_lines = []

    print("\n========== CLEANED OCR ==========\n")

    for group in groups:

        best = max(group, key=lambda x: x["confidence"])
        votes = len(group)

        cleaned_lines.append({
            "text": best["text"],
            "confidence": best["confidence"],
            "source": best["source"],
            "votes": votes
        })

        print(
            f"{best['text']} | "
            f"Confidence: {best['confidence']:.2f} | "
            f"Votes: {votes}"
        )

    return cleaned_lines

def rank_ocr_lines(cleaned_data):

    IMPORTANT_KEYWORDS = [
    "TABLET", "TABLETS", "CAPSULE", "CAPSULES",
    "SYRUP", "INJECTION",
    "MG", "MCG", "ML",
    "PHARMA", "PHARMACEUTICAL",
    "MARKETED", "MANUFACTURED",
    "USP", "IP",
    "B.NO", "BATCH", "LOT",
    "MFG", "MFD",
    "EXP", "EXPIRY"
    ]

    BAD_KEYWORDS = [
        "WARNING",
        "STORE",
        "KEEP",
        "CHILDREN",
        "CAUTION",
        "SCHEDULE"
    ]

    ranked = []

    for item in cleaned_data:

        score = 0

        text = item["text"]
        upper = text.upper()

        score += item["confidence"] * 10
        score += item["votes"] * 2

        for word in IMPORTANT_KEYWORDS:
            if word in upper:
                score += 5

        DATE_KEYWORDS = [
        "B.NO", "BATCH", "LOT",
        "MFG", "MFD",
        "EXP", "EXPIRY"
        ]

        for word in DATE_KEYWORDS:
            if word in upper:
                score += 10

        # Give extra priority to date-like patterns
        date_patterns = [
            r"\b\d{1,2}[/-]\d{2,4}\b",   # 03/2026 or 03-2026
            r"\b\d{2,4}[/-]\d{1,2}\b",   # 2026/03 or 2026-03
            r"\b(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*[\s./-]*\d{2,4}\b"
        ]

        for pattern in date_patterns:
            if re.search(pattern, upper):
                score += 10
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

    print("\n========== RANKED OCR ==========\n")

    for item in ranked[:20]:
        print(f'{item["score"]:.2f} | {item["text"]}')

    return ranked