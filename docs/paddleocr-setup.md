# PaddleOCR Setup — MediLens

MediLens uses PaddleOCR as the primary OCR engine and EasyOCR as the fallback OCR engine.

## Tested PaddleOCR Environment

The following environment has been tested successfully with MediLens:

- Python: 3.13.15
- PaddleOCR: 3.7.0
- PaddlePaddle GPU: 3.3.1
- NVIDIA GPU: RTX 3050 6GB
- CUDA dependencies: CUDA 13.x

## Architecture

MediLens does not import PaddleOCR directly into the main Flask environment.

The Flask application communicates with:

`backend/workers/paddle_worker.py`

The Paddle worker runs in a separate Python environment containing PaddleOCR and PaddlePaddle.

```text
Flask Application
       |
       v
ocr_service.py
       |
       v
PaddleOCR Worker
       |
       v
PaddleOCR + PaddlePaddle
       |
       v
OCR detections