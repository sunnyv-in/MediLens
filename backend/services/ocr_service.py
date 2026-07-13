import easyocr
import difflib
import re
from concurrent.futures import ThreadPoolExecutor
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

    workers = min(os.cpu_count() or 4, len(image_paths), 6)

    with ThreadPoolExecutor(max_workers=workers) as executor:

        results = executor.map(_read_single_image, image_paths)

        for r in results:
            detections.extend(r)

    if DEBUG:
        print(f"\nTotal Valid Detections : {len(detections)}")

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

    return ranked