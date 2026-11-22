from datetime import datetime, timezone
import re

EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$')
COLOR_PATTERN = re.compile(r'^#[0-9a-fA-F]{6}$')
DATE_FORMAT = '%Y-%m-%d'


def utc_now():
    """Current UTC time as a naive datetime, the format the DateTime columns store."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def validate_email(email):
    return isinstance(email, str) and EMAIL_PATTERN.match(email) is not None


def is_valid_color(color):
    return isinstance(color, str) and COLOR_PATTERN.match(color) is not None


def parse_date(date_string):
    try:
        return datetime.strptime(date_string, DATE_FORMAT)
    except (ValueError, TypeError):
        return None
