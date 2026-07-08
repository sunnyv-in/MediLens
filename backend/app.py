import os
from flask import send_from_directory
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from services.image_processor import process_image
from services.ocr_service import extract_text, extract_medicine_info


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

        filename = secure_filename(image.filename)

        image_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        image.save(image_path)

        processed_images = process_image(image_path)

        ocr_text = extract_text(list(processed_images.values()))

        medicine_info = extract_medicine_info(ocr_text)

        return render_template(
        "result.html",
        filename=filename,
        medicine=medicine_info
        )

        # return render_template(
        # "result.html",
        # filename=filename,
        # ocr_text=ocr_text
        # )
    
    return render_template("scan.html")

@app.route('/results')
def result():
    return render_template("result.html")

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)



if __name__ == '__main__':
    app.run(debug=True)