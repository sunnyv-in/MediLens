from flask import Flask

from backend.config import Config
from backend.extensions import db

# Import Models
from backend.models.medicine import Medicine
from backend.models.drug_interaction import DrugInteraction
from backend.models.medicine_history import MedicineHistory

# Import Blueprints
from backend.routes.medicine_shelf import medicine_shelf_bp
from backend.routes.drug_interaction import drug_interaction_bp
from backend.routes.medicine_history import medicine_history_bp




def create_app():

    app = Flask(
        __name__,
        template_folder="../frontend/templates",
        static_folder="../frontend/static"
    )

    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(
        medicine_shelf_bp
    )

    app.register_blueprint(
        drug_interaction_bp
    )

    app.register_blueprint(
        medicine_history_bp
    )

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        debug=True
    )