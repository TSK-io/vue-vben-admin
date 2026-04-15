from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet

from app.core.config import get_settings


def _build_fernet() -> Fernet:
    secret = get_settings().app_jwt_secret.encode("utf-8")
    key = base64.urlsafe_b64encode(hashlib.sha256(secret).digest())
    return Fernet(key)


def encrypt_text(value: str) -> str:
    return _build_fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_text(value: str) -> str:
    return _build_fernet().decrypt(value.encode("utf-8")).decode("utf-8")


def mask_phone(phone: str) -> str:
    if len(phone) < 7:
        return "*" * len(phone)
    return f"{phone[:3]}****{phone[-4:]}"
