"""Email and phone validation helpers."""
import re
import phonenumbers
from email_validator import validate_email as _validate_email, EmailNotValidError
from utils.logger import log


def validate_email(email: str) -> bool:
    try:
        _validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError as e:
        log(f"VALIDATION_ERROR: invalid email '{email}' — {e}", level="ERROR")
        return False


def validate_phone(phone: str) -> bool:
    try:
        parsed = phonenumbers.parse(phone, None)
        if phonenumbers.is_valid_number(parsed):
            return True
        log(f"VALIDATION_ERROR: invalid phone '{phone}'", level="ERROR")
        return False
    except Exception as e:
        log(f"VALIDATION_ERROR: phone parse failed '{phone}' — {e}", level="ERROR")
        return False
