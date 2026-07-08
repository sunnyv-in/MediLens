import easyocr

reader = easyocr.Reader(['en'])

def extract_text(image_paths):

    extracted_text = []

    for path in image_paths:

        print(f"\nReading: {path}")

        results = reader.readtext(path)

        for result in results:
            extracted_text.append(result[1])

    print("\n========== OCR TEXT ==========\n")

    for text in extracted_text:
        print(text)

    return extracted_text

def extract_medicine_info(ocr_text):

    medicine = ""
    manufacturer = ""
    strength = ""

    for line in ocr_text:

        text = line.upper()

        if "PHARMA" in text or "PHARM" in text:
            medicine = line

        if "PHARMACEUTICAL" in text:
            manufacturer = line

        if "MG" in text:
            strength = line

    return {
        "medicine": medicine,
        "manufacturer": manufacturer,
        "strength": strength
    }