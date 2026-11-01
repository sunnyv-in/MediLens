import os

from flask import Flask

from backend.config import Config
from backend.extensions import db, login_manager

# Import Models
from backend.models.user import User, CareCircleContact, DoseLog
from backend.models.medicine import Medicine
from backend.models.drug_interaction import DrugInteraction
from backend.models.medicine_history import MedicineHistory
from backend.models.reminder import MedicationReminder

# Import Blueprints
from backend.routes.auth_routes import auth_bp
from backend.routes.medicine_shelf import medicine_shelf_bp
from backend.routes.drug_interaction import drug_interaction_bp
from backend.routes.medicine_history import medicine_history_bp
from backend.routes.reminder_routes import reminder_bp
from backend.routes.expiry_routes import expiry_bp
from backend.routes.emergency_routes import emergency_bp
from backend.routes.home_routes import home_bp
from backend.routes.about_routes import about_bp
from backend.routes.scan_routes import scan_bp
from backend.extensions import db, login_manager, mail

from apscheduler.schedulers.background import BackgroundScheduler
from backend.services.reminder_scheduler import send_due_reminders


def create_app():

    app = Flask(
        __name__,
        template_folder="../frontend/templates",
        static_folder="../frontend/static",
    )

    # Load configuration
    app.config.from_object(Config)

    # Upload folder
    upload_folder = os.path.join(os.path.dirname(__file__), "uploads")
    app.config["UPLOAD_FOLDER"] = upload_folder
    os.makedirs(upload_folder, exist_ok=True)

    # Processed images folder
    processed_folder = os.path.join(os.path.dirname(__file__), "processed")
    app.config["PROCESSED_FOLDER"] = processed_folder
    os.makedirs(processed_folder, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(medicine_shelf_bp)
    app.register_blueprint(drug_interaction_bp)
    app.register_blueprint(medicine_history_bp)
    app.register_blueprint(reminder_bp)
    app.register_blueprint(expiry_bp)
    app.register_blueprint(emergency_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(about_bp)
    app.register_blueprint(scan_bp)

    # Create database tables and perform lightweight schema updates
    with app.app_context():
        db.create_all()
        try:
            from sqlalchemy import text
            with db.engine.connect() as conn:
                # Users table migrations
                u_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(users)")).fetchall()]
                if "first_name" not in u_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN first_name VARCHAR(60)"))
                if "last_name" not in u_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN last_name VARCHAR(60)"))
                if "role" not in u_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(30) DEFAULT 'patient'"))
                if "patient_name" not in u_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN patient_name VARCHAR(100)"))

                # CareCircleContacts migrations
                c_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(care_circle_contacts)")).fetchall()]
                if "notify_on_reminder" not in c_cols:
                    conn.execute(text("ALTER TABLE care_circle_contacts ADD COLUMN notify_on_reminder BOOLEAN DEFAULT 1"))
                if "notify_on_taken" not in c_cols:
                    conn.execute(text("ALTER TABLE care_circle_contacts ADD COLUMN notify_on_taken BOOLEAN DEFAULT 1"))

                # DoseLogs migrations
                d_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(dose_logs)")).fetchall()]
                if "taken_by_name" not in d_cols:
                    conn.execute(text("ALTER TABLE dose_logs ADD COLUMN taken_by_name VARCHAR(100) DEFAULT 'Self'"))

                conn.commit()
        except Exception:
            pass

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app = create_app()


def start_reminder_scheduler(app):
    # Avoid starting a second scheduler in Flask's development reloader.
    if app.debug and os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        return

    if app.extensions.get("reminder_scheduler"):
        return

    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(
        func=lambda: send_due_reminders(app),
        trigger="interval",
        minutes=1,
        id="medicine_whatsapp_reminders",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
    app.extensions["reminder_scheduler"] = scheduler
