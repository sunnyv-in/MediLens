from backend.services.image_processor import process_image
from backend.services.ocr_service import extract_text_fast
from backend.services.ocr_service import clean_ocr_text
from backend.services.ocr_service import rank_ocr_lines

IMAGE_PATH = "backend/uploads/4.jpeg"

print("Starting local OCR inspection...")

processed_images = process_image(IMAGE_PATH)

detections = extract_text_fast(
    list(processed_images.values())
)

cleaned_data = clean_ocr_text(detections)

ranked_data = rank_ocr_lines(cleaned_data)

all_lines = []

for item in ranked_data[:20]:
    all_lines.append(item["text"])

for item in cleaned_data:
    if item["text"] not in all_lines:
        all_lines.append(item["text"])

combined_text = "\n".join(all_lines)

print("\n===================================")
print("GEMINI INPUT INSPECTION")
print("===================================")

print("OCR detections:", len(detections))
print("Cleaned lines:", len(cleaned_data))
print("Ranked lines:", len(ranked_data))
print("Characters sent to Gemini:", len(combined_text))
print("Approximate words:", len(combined_text.split()))

print("\nTEXT:")
print(combined_text)