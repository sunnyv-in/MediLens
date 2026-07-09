import os
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from services.image_processor import process_image
from services.ocr_service import extract_text, clean_ocr_text
from services.gemini_service import extract_medicine_info_ai, get_ai_explanation
from services.ocr_service import rank_ocr_lines
from services.counterfeit_service import analyze_counterfeit_risk
from services.medicine_record_service import build_medicine_record

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

PROCESSED_FOLDER = os.path.join(os.path.dirname(__file__), "processed")
app.config["PROCESSED_FOLDER"] = PROCESSED_FOLDER


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/scan', methods=['GET', 'POST'])
def scan():
    if request.method == "POST":
        image = request.files.get("medicine_image")

        if not image or image.filename == "":
            return render_template("scan.html", error="Please select an image.")

        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image.save(image_path)

        processed_images = process_image(image_path)

        detections = extract_text(list(processed_images.values()))

        cleaned_data = clean_ocr_text(detections)

        ranked_data = rank_ocr_lines(cleaned_data)

        medicine_info = extract_medicine_info_ai(ranked_data)

        explanation = get_ai_explanation(medicine_info.get("medicine", ""))

        counterfeit_result = analyze_counterfeit_risk(medicine_info)

        medicine_record = build_medicine_record(
            medicine_info=medicine_info,
            explanation=explanation,
            counterfeit_result=counterfeit_result,
            image_filename=filename
        )

        print("\n========== STANDARD MEDICINE RECORD ==========")
        print(medicine_record)
        print("==============================================\n")

        return render_template(
            "result.html",
            filename=filename,
            medicine=medicine_info,
            explanation=explanation,
            counterfeit_result=counterfeit_result
        )

    return render_template("scan.html")


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == '__main__':
    app.run(debug=True)