
import os

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

# Persistent data directory.
# Local development: D:\MediLens\database
# Railway: /app/data
DATA_DIR = os.path.abspath(
    os.getenv(
        "MEDILENS_DATA_DIR",
        os.path.join(BASE_DIR, "database"),
    )
)

os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_PATH = os.path.join(DATA_DIR, "medilens.db")

DEFAULT_DATABASE_URL = (
    "sqlite:///" + DATABASE_PATH.replace("\\", "/")
)


class Config:

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "medilens-local-development-key",
    )

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_USERNAME")

    WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
    WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

    WHATSAPP_TEMPLATE_NAME = os.getenv(
        "WHATSAPP_TEMPLATE_NAME",
        "medicine_reminder",
    )

    WHATSAPP_GRAPH_VERSION = os.getenv(
        "WHATSAPP_GRAPH_VERSION",
        "v23.0",
    )

    SQLALCHEMY_DATABASE_URI = (
        os.getenv("DATABASE_URL") or DEFAULT_DATABASE_URL
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
