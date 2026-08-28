from backend.services.image_processor import process_image
from backend.services.ocr_service import extract_text_fast

IMAGE_PATH = "backend/uploads/4.jpeg"

print("Starting fast OCR test...")

processed_images = process_image(IMAGE_PATH)

print("Images:")
print(list(processed_images.keys()))

detections = extract_text_fast(
    list(processed_images.values())
)

print()
print("Detections:", len(detections))

print()
print("Sources used:")
print(
    sorted(
        set(
            item["source"]
            for item in detections
        )
    )
)

print()
print("Top detections:")

for item in detections[:20]:

    print(
        f'{item["confidence"]:.2f} | '
        f'{item["text"]} | '
        f'{item["source"]}'
    )