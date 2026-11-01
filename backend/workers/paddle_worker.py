import sys
import json
import os

from paddleocr import PaddleOCR


def run_ocr(ocr, image_path):

    if not os.path.exists(image_path):
        return {
            "success": False,
            "error": "Image not found"
        }

    try:

        output = ocr.predict(image_path)

        detections = []

        for result in output:

            data = result.json

            if callable(data):
                data = data()

            if not isinstance(data, dict):
                continue

            res = data.get(
                "res",
                data
            )

            texts = res.get(
                "rec_texts",
                []
            )

            scores = res.get(
                "rec_scores",
                []
            )

            for index, text in enumerate(texts):

                text = str(text).strip()

                if not text:
                    continue

                confidence = (
                    float(scores[index])
                    if index < len(scores)
                    else 0.0
                )

                detections.append({
                    "text": text,
                    "confidence": confidence,
                    "source": os.path.basename(
                        image_path
                    )
                })

        return {
            "success": True,
            "detections": detections
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


def main():

    print(
        "PADDLE WORKER: Loading PaddleOCR...",
        file=sys.stderr,
        flush=True
    )

    ocr = PaddleOCR(
        lang="en",
        device="gpu:0"
    )

    print(
        "PADDLE WORKER: Ready",
        file=sys.stderr,
        flush=True
    )

    # --------------------------------------------------------
    # PERSISTENT REQUEST LOOP
    # --------------------------------------------------------

    for line in sys.stdin:

        line = line.strip()

        if not line:
            continue

        try:

            request = json.loads(line)

            image_path = request.get(
                "image_path"
            )

            if not image_path:

                response = {
                    "success": False,
                    "error": "No image path provided"
                }

            else:

                response = run_ocr(
                    ocr,
                    image_path
                )

        except Exception as e:

            response = {
                "success": False,
                "error": str(e)
            }

        print(
            json.dumps(response),
            flush=True
        )


if __name__ == "__main__":
    main()