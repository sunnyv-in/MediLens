import os
from flask import Flask

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

PROCESSED_FOLDER = os.path.join(os.path.dirname(__file__), "processed")
app.config["PROCESSED_FOLDER"] = PROCESSED_FOLDER


# -------------------------
# Register Blueprints
# -------------------------
from routes.home_routes import home_bp
from routes.about_routes import about_bp
from routes.scan_routes import scan_bp

app.register_blueprint(home_bp)
app.register_blueprint(about_bp)
app.register_blueprint(scan_bp)


if __name__ == "__main__":
    app.run(debug=True)