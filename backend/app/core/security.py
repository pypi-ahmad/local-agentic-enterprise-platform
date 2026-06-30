import base64
import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from app.core.config import get_settings

PBKDF2_PREFIX = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 390000
SALT_BYTES = 16


class TokenPayloadError(Exception):
    pass


def _b64_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"{PBKDF2_PREFIX}${PBKDF2_ITERATIONS}${_b64_encode(salt)}${_b64_encode(digest)}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        prefix, iterations_raw, salt_raw, digest_raw = hashed_password.split("$", 3)
        if prefix != PBKDF2_PREFIX:
            return False
        iterations = int(iterations_raw)
        salt = _b64_decode(salt_raw)
        expected_digest = _b64_decode(digest_raw)
        computed_digest = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt,
            iterations,
        )
        return hmac.compare_digest(computed_digest, expected_digest)
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str, roles: list[str], user_id: int | None = None) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_minutes)
    to_encode: dict[str, Any] = {"sub": subject, "roles": roles, "exp": expire}
    if user_id is not None:
        to_encode["uid"] = user_id
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        msg = "Invalid token"
        raise TokenPayloadError(msg) from exc
