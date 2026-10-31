import easyocr
import difflib
import re
import os
import torch
import subprocess
import json

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

PADDLE_WORKER = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "workers",
        "paddle_worker.py"
    )
)

PADDLE_PYTHON = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "experiments",
        "paddleocr",
        "paddle_venv",
        "Scripts",
        "python.exe"
    )
)

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
    if not os.path.exists(path):
        return []

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
            "confidence": float(confidence),
            "source": os.path.basename(path)
        })

    if DEBUG:
        print(f"{os.path.basename(path)} -> {len(detections)} detections")

    return detections


# ============================================================
# PERSISTENT PADDLEOCR WORKER
# ============================================================

_paddle_process = None


def _get_paddle_worker():
    global _paddle_process

    if _paddle_process is not None:
        if _paddle_process.poll() is None:
            return _paddle_process

    if not os.path.exists(PADDLE_PYTHON) or not os.path.exists(PADDLE_WORKER):
        return None

    paddle_root = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "experiments",
            "paddleocr",
            "paddle_venv"
        )
    )

    paddle_cuda_bin = os.path.join(
        paddle_root,
        "Lib",
        "site-packages",
        "nvidia",
        "cu13",
        "bin",
        "x86_64"
    )

    worker_env = os.environ.copy()
    worker_env["PATH"] = (
        paddle_cuda_bin
        + os.pathsep
        + worker_env.get("PATH", "")
    )

    _paddle_process = subprocess.Popen(
        [
            PADDLE_PYTHON,
            PADDLE_WORKER
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=worker_env
    )

    return _paddle_process


# Pre-warm PaddleOCR worker when server starts to eliminate first-scan delay
try:
    _get_paddle_worker()
except Exception as _e:
    print("PaddleOCR warmup skipped:", _e)


def _read_paddle_image(path):
    try:
        worker = _get_paddle_worker()
        if worker is None:
            return []

        request = json.dumps({
            "image_path": path
        })

        worker.stdin.write(request + "\n")
        worker.stdin.flush()

        response_line = worker.stdout.readline()

        if not response_line:
            print("PaddleOCR worker returned no response.")
            return []

        data = json.loads(response_line)

        if not data.get("success", False):
            print("PaddleOCR error:", data.get("error"))
            return []

        return data.get("detections", [])

    except Exception as e:
        print("PaddleOCR bridge error:", e)
        return []


def extract_text(image_paths):
    detections = []
    for path in image_paths:
        detections.extend(_read_single_image(path))
    return detections


def _is_ocr_sufficient(detections):
    """
    Medicine-specific OCR quality check.
    Accepts 3-4 letter medicine brands (DOLO, PAN, AZI, OMEE) while filtering
    short packaging abbreviations.
    """
    if not detections:
        return False

    useful = [
        item
        for item in detections
        if item["confidence"] >= 0.45
    ]

    if len(useful) < 3:
        return False

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
        "LICENSE"
    ]

    short_packaging_abbr = {
        "EXP", "MFG", "MFD", "TAB", "CAP", "LOT", "MRP",
        "FOR", "USE", "AND", "NET", "QTY", "USP", "BP", "IP"
    }

    medicine_candidates = []

    for item in useful:
        text = item["text"].strip()
        upper = text.upper()

        if len(text) < 3:
            continue

        strength_only = re.fullmatch(
            r"\s*\d+(?:\.\d+)?\s*(MG|MCG|ML|GM|G|IU)\s*",
            upper
        )
        if strength_only:
            continue

        alphabetic_count = sum(
            character.isalpha()
            for character in text
        )
        if alphabetic_count < 3:
            continue

        if len(text) <= 4 and upper in short_packaging_abbr:
            continue

        if any(term in upper for term in ignored_terms):
            continue

        medicine_candidates.append(item)

    if not medicine_candidates:
        return False

    best_candidate = max(
        medicine_candidates,
        key=lambda item: item["confidence"]
    )
    best_confidence = best_candidate["confidence"]

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

    if best_confidence >= 0.65:
        if has_strength:
            return True
        if pharmaceutical_keyword_count >= 1:
            return True

    if best_confidence >= 0.80 and pharmaceutical_keyword_count >= 2:
        return True

    return False


def extract_text_fast(image_paths):
    """
    3-STAGE PROGRESSIVE OCR PIPELINE:
    - Stage 1 (Fast Path for Good Images): PaddleOCR on original.jpg
    - Stage 2 (Enhancement Path for Blurry/Noisy Images): PaddleOCR on sharpen.jpg & adaptive.jpg
    - Stage 3 (Deep Recovery Path for Hard/Rotated Images): PaddleOCR on rotated_90.jpg + EasyOCR fallback
    """
    print("\nFAST OCR - Starting progressive OCR pipeline")

    path_map = {os.path.basename(p): p for p in image_paths}
    all_detections = []

    # --------------------------------------------------
    # STAGE 1: PADDLEOCR ON ORIGINAL IMAGE
    # --------------------------------------------------
    primary_path = path_map.get("original.jpg", image_paths[0])
    print(f"FAST OCR [Stage 1] - PaddleOCR on: {os.path.basename(primary_path)}")

    paddle_detections = _read_paddle_image(primary_path)
    all_detections.extend(paddle_detections)

    print(f"FAST OCR [Stage 1] - Detections: {len(all_detections)}")

    if _is_ocr_sufficient(all_detections):
        print("FAST OCR [Stage 1] - PaddleOCR result sufficient on first pass.")
        return all_detections

    # --------------------------------------------------
    # STAGE 2: PADDLEOCR ON ENHANCED IMAGES (SHARPEN + ADAPTIVE)
    # --------------------------------------------------
    print("FAST OCR [Stage 2] - Trying enhanced image variants in PaddleOCR...")
    for variant_name in ("sharpen.jpg", "adaptive.jpg"):
        variant_path = path_map.get(variant_name)
        if variant_path:
            extra_dets = _read_paddle_image(variant_path)
            all_detections.extend(extra_dets)
            if _is_ocr_sufficient(all_detections):
                print(f"FAST OCR [Stage 2] - Sufficient after {variant_name}.")
                return all_detections

    # --------------------------------------------------
    # STAGE 3: ROTATED VARIANT + EASYOCR FALLBACK
    # --------------------------------------------------
    print("FAST OCR [Stage 3] - Running deep recovery (rotated_90 + EasyOCR fallback)...")
    rot_path = path_map.get("rotated_90.jpg")
    if rot_path:
        all_detections.extend(_read_paddle_image(rot_path))
        if _is_ocr_sufficient(all_detections):
            print("FAST OCR [Stage 3] - Sufficient after rotated_90.jpg.")
            return all_detections

    # Run EasyOCR incrementally and stop as soon as sufficient text is found
    priority_fallback_order = ["original.jpg", "sharpen.jpg", "threshold.jpg", "adaptive.jpg", "rotated_90.jpg"]
    for variant_name in priority_fallback_order:
        variant_path = path_map.get(variant_name)
        if variant_path:
            all_detections.extend(_read_single_image(variant_path))
            if _is_ocr_sufficient(all_detections):
                print(f"FAST OCR [Stage 3] - Sufficient after EasyOCR ({variant_name}).")
                return all_detections

    print(f"FAST OCR - Returning all available detections ({len(all_detections)}).")
    return all_detections


def is_ocr_unreadable(cleaned_data):
    """
    Returns True if the OCR output after all recovery stages has almost no
    readable alphabetic medicine text (indicating a 'super bad' or non-medicine image).
    """
    if not cleaned_data:
        return True

    meaningful = [
        item for item in cleaned_data
        if item.get("confidence", 0) >= 0.38
        and sum(c.isalpha() for c in item.get("text", "")) >= 3
    ]

    if not meaningful:
        return True

    total_alpha = sum(
        sum(c.isalpha() for c in item.get("text", ""))
        for item in meaningful
    )
    max_conf = max(item.get("confidence", 0) for item in meaningful)

    if total_alpha < 5 or max_conf < 0.42:
        return True

    return False


def clean_ocr_text(detections):
    groups = []

    for detection in detections:
        text = detection["text"].strip()
        placed = False

        # Extract numbers so lines with different strengths/dates (500 vs 650) are never merged
        cur_nums = re.findall(r"\d+", text)

        for group in groups:
            representative = group[0]["text"]
            rep_nums = re.findall(r"\d+", representative)

            if cur_nums != rep_nums:
                continue

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

        word_count = len(text.split())
        if 1 <= word_count <= 3:
            score += 3

        if re.search(r"\d+\s*(MG|MCG|ML|GM|G|IU)", upper):
            score += 4

        for word in IMPORTANT_KEYWORDS:
            if word in upper:
                score += 5

        for word in DATE_KEYWORDS:
            if word in upper:
                score += 4

        date_patterns = [
            r"\b\d{1,2}[/.-]\d{2,4}\b",
            r"\b\d{2,4}[/.-]\d{1,2}\b",
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