import easyocr

reader = easyocr.Reader(['en'])

def extract_text(image_path):

    results = reader.readtext(image_path)

    extracted_text = []

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

        if "PANTOPRAZOLE" in text:
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