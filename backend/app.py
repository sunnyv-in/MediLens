import os
from flask import Flask

from backend.config import Config
from backend.extensions import db

# Import Models
from backend.models.medicine import Medicine
from backend.models.drug_interaction import DrugInteraction
from backend.models.medicine_history import MedicineHistory
from backend.models.reminder import MedicationReminder

# Import Blueprints
from backend.routes.medicine_shelf import medicine_shelf_bp
from backend.routes.drug_interaction import drug_interaction_bp
from backend.routes.medicine_history import medicine_history_bp
from backend.routes.reminder_routes import reminder_bp
from backend.routes.expiry_routes import expiry_bp
from backend.routes.home_routes import home_bp
from backend.routes.about_routes import about_bp
from backend.routes.scan_routes import scan_bp


def create_app():

    app = Flask(
        __name__,
        template_folder="../frontend/templates",
        static_folder="../frontend/static"
    )

    app.config.from_object(Config)

    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    PROCESSED_FOLDER = os.path.join(os.path.dirname(__file__), "processed")
    app.config["PROCESSED_FOLDER"] = PROCESSED_FOLDER

    db.init_app(app)

    app.register_blueprint(medicine_shelf_bp)
    app.register_blueprint(drug_interaction_bp)
    app.register_blueprint(medicine_history_bp)
    app.register_blueprint(reminder_bp)
    app.register_blueprint(expiry_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(about_bp)
    app.register_blueprint(scan_bp)

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)

