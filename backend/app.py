
import os

from flask import Flask, jsonify
from sqlalchemy import text
from apscheduler.schedulers.background import BackgroundScheduler

from backend.config import Config
from backend.extensions import db, login_manager, mail

# ============================================================
# DATABASE MODELS
# ============================================================

from backend.models.user import (
    User,
    CareCircleContact,
    DoseLog,
)
from backend.models.medicine import Medicine
from backend.models.drug_interaction import DrugInteraction
from backend.models.medicine_history import MedicineHistory
from backend.models.reminder import MedicationReminder

# ============================================================
# BLUEPRINTS
# ============================================================

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

from backend.services.reminder_scheduler import send_due_reminders


# ============================================================
# SQLITE SCHEMA MIGRATIONS
# ============================================================

SQLITE_MIGRATIONS = {
    # USERS
    "users": {
        "first_name": "VARCHAR(60)",
        "last_name": "VARCHAR(60)",
        "role": "VARCHAR(30) DEFAULT 'patient'",
        "patient_name": "VARCHAR(100)",
        "phone_number": "VARCHAR(20)",
    },

    # CARE CIRCLE CONTACTS
    "care_circle_contacts": {
        "notify_on_reminder": "BOOLEAN DEFAULT 1",
        "notify_on_taken": "BOOLEAN DEFAULT 1",
    },

    # DOSE LOGS
    "dose_logs": {
        "guest_id": "VARCHAR(36)",
        "reminder_id": (
            "INTEGER REFERENCES medication_reminders(id)"
        ),
        "medicine_id": "INTEGER REFERENCES medicines(id)",
        "taken_by_name": "VARCHAR(100) DEFAULT 'Self'",
        "administered_by": "VARCHAR(100) DEFAULT 'Self'",
        "taken_at": "DATETIME",
        "status": "VARCHAR(30) DEFAULT 'taken'",
    },

    # MEDICINES
    "medicines": {
        "history_id": (
            "INTEGER REFERENCES medicine_history(id)"
        ),
    },

    # MEDICINE HISTORY
    "medicine_history": {
        "scan_data": "JSON",
    },

    # MEDICATION REMINDERS
    "medication_reminders": {
        "lead_minutes": "INTEGER NOT NULL DEFAULT 30",
        "repeat_minutes": "INTEGER NOT NULL DEFAULT 5",
        "last_sent_at": "DATETIME",
        "last_sent_date": "DATE",
    },
}


# Indexes expected by the models.
SQLITE_INDEXES = (
    ("ix_dose_logs_guest_id", "dose_logs", "guest_id"),
    ("ix_medicines_guest_id", "medicines", "guest_id"),
    ("ix_medicines_history_id", "medicines", "history_id"),
    (
        "ix_medicine_history_guest_id",
        "medicine_history",
        "guest_id",
    ),
    (
        "ix_medication_reminders_guest_id",
        "medication_reminders",
        "guest_id",
    ),
)


def get_sqlite_columns(connection, table_name):
    """
    Return existing column names for a SQLite table.

    Table names are supplied only by the fixed migration dictionary.
    """
    rows = connection.exec_driver_sql(
        f'PRAGMA table_info("{table_name}")'
    ).fetchall()

    return {row[1] for row in rows}


def initialize_database(app):
    """
    Create missing tables and incrementally update existing SQLite schemas.

    Existing database records are preserved.
    Missing columns are added only once.
    """
    with app.app_context():

        if db.engine.dialect.name != "sqlite":
            raise RuntimeError(
                "The current database migration system supports SQLite only. "
                "Configure a proper Alembic migration before using another "
                "database engine."
            )

        try:
            # Create tables that do not exist.
            db.create_all()

            # Apply all column migrations in one transaction.
            with db.engine.begin() as connection:

                for table_name, columns in SQLITE_MIGRATIONS.items():

                    existing_columns = get_sqlite_columns(
                        connection,
                        table_name,
                    )

                    if not existing_columns:
                        raise RuntimeError(
                            f"Expected database table is missing: {table_name}"
                        )

                    for column_name, definition in columns.items():

                        if column_name in existing_columns:
                            continue

                        connection.exec_driver_sql(
                            f'ALTER TABLE "{table_name}" '
                            f'ADD COLUMN "{column_name}" {definition}'
                        )

                        app.logger.info(
                            "Database migration applied: %s.%s",
                            table_name,
                            column_name,
                        )

                        existing_columns.add(column_name)

                # Restore indexes that may be missing from older databases.
                for index_name, table_name, column_name in SQLITE_INDEXES:

                    existing_columns = get_sqlite_columns(
                        connection,
                        table_name,
                    )

                    if column_name not in existing_columns:
                        raise RuntimeError(
                            f"Cannot create index {index_name}: "
                            f"{table_name}.{column_name} is missing."
                        )

                    connection.exec_driver_sql(
                        f'CREATE INDEX IF NOT EXISTS "{index_name}" '
                        f'ON "{table_name}"("{column_name}")'
                    )

                # Check referential integrity.
                violations = connection.exec_driver_sql(
                    "PRAGMA foreign_key_check"
                ).fetchall()

                if violations:
                    app.logger.warning(
                        "SQLite foreign-key violations detected: %s",
                        violations,
                    )

            app.logger.info(
                "Database initialization and migrations completed."
            )

        except Exception:
            app.logger.exception(
                "Database initialization or migration failed."
            )
            raise


# ============================================================
# FLASK APPLICATION FACTORY
# ============================================================

def create_app():

    app = Flask(
        __name__,
        template_folder="../frontend/templates",
        static_folder="../frontend/static",
    )

    # --------------------------------------------------------
    # CONFIGURATION
    # --------------------------------------------------------

    app.config.from_object(Config)

    # --------------------------------------------------------
    # PERSISTENT FILE STORAGE
    # --------------------------------------------------------

    persistent_data_dir = os.getenv("MEDILENS_DATA_DIR")

    if persistent_data_dir:

        os.makedirs(persistent_data_dir, exist_ok=True)

        upload_folder = os.path.join(
            persistent_data_dir,
            "uploads",
        )

        processed_folder = os.path.join(
            persistent_data_dir,
            "processed",
        )

    else:

        # Local development paths.
        upload_folder = os.path.join(
            os.path.dirname(__file__),
            "uploads",
        )

        processed_folder = os.path.join(
            os.path.dirname(__file__),
            "processed",
        )

    app.config["UPLOAD_FOLDER"] = upload_folder
    app.config["PROCESSED_FOLDER"] = processed_folder

    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(processed_folder, exist_ok=True)

    # --------------------------------------------------------
    # INITIALIZE EXTENSIONS
    # --------------------------------------------------------

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # --------------------------------------------------------
    # REGISTER BLUEPRINTS
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # HEALTH CHECK
    # --------------------------------------------------------

    @app.get("/health")
    def health_check():

        try:
            db.session.execute(text("SELECT 1"))

        except Exception:
            app.logger.exception(
                "Health check failed: database unavailable."
            )

            return jsonify({
                "status": "unhealthy",
                "application": "MediLens",
            }), 503

        return jsonify({
            "status": "healthy",
            "application": "MediLens",
        }), 200

    # --------------------------------------------------------
    # DATABASE INITIALIZATION
    # --------------------------------------------------------

    initialize_database(app)

    return app


# ============================================================
# LOGIN MANAGER
# ============================================================

@login_manager.user_loader
def load_user(user_id):

    try:
        return db.session.get(User, int(user_id))

    except (TypeError, ValueError):
        return None


# ============================================================
# REMINDER SCHEDULER
# ============================================================

def start_reminder_scheduler(app):
    """
    Start the reminder scheduler when explicitly requested.

    IMPORTANT:
    Run only one scheduler instance for the deployment.
    Do not start one scheduler per Gunicorn worker.
    """

    if app.extensions.get("reminder_scheduler"):
        app.logger.warning(
            "Reminder scheduler is already running."
        )
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

    try:
        scheduler.start()

        app.extensions["reminder_scheduler"] = scheduler

        app.logger.info(
            "Medication reminder scheduler started."
        )

    except Exception:
        app.logger.exception(
            "Could not start medication reminder scheduler."
        )
        raise


# ============================================================
# CREATE FLASK APPLICATION
# ============================================================

app = create_app()
