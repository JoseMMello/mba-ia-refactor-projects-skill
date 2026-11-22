import os


def _as_bool(value):
    return value.strip().lower() in ("1", "true", "yes", "on")


class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY", "")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5001"))
    DEBUG = _as_bool(os.environ.get("DEBUG", "false"))
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
    AMBIENTE = os.environ.get("APP_ENV", "producao")

    # Token required in the X-Admin-Token header by the admin routes.
    # When empty, the admin routes are disabled.
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")

    # Passwords given to the sample users when a new database is seeded.
    SEED_ADMIN_PASSWORD = os.environ.get("SEED_ADMIN_PASSWORD", "")
    SEED_USER_PASSWORD = os.environ.get("SEED_USER_PASSWORD", "")


settings = Settings()
