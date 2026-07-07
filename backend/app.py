import os
from flask import send_from_directory
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename


app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/scan', methods = ['GET', 'POST'])
def scan():
    if request.method == "POST":
        image = request.files.get("medicine_image")
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return render_template(
            "result.html",
            filename=filename
)
    return render_template("scan.html")

@app.route('/results')
def result():
    return render_template("result.html")

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == '__main__':
    app.run(debug=True)