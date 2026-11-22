import os
import secrets

from dotenv import load_dotenv

load_dotenv()


def _read_bool(name, default='false'):
    return os.environ.get(name, default).strip().lower() in ('1', 'true', 'yes', 'on')


class Settings:
    # A key generated at start is used when none is configured, so no secret lives in the code.
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///tasks.db')

    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', '5000'))
    DEBUG = _read_bool('DEBUG')
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()

    # Administrative user operations are refused while this is empty.
    ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', '')

    SMTP_HOST = os.environ.get('SMTP_HOST', '')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
    SMTP_USER = os.environ.get('SMTP_USER', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')

    SEED_ADMIN_PASSWORD = os.environ.get('SEED_ADMIN_PASSWORD', '')
    SEED_USER_PASSWORD = os.environ.get('SEED_USER_PASSWORD', '')
    SEED_MANAGER_PASSWORD = os.environ.get('SEED_MANAGER_PASSWORD', '')


settings = Settings()
