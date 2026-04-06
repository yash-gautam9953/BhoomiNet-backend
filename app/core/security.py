import base64
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
PBKDF2_ALGORITHM = "sha256"
PBKDF2_ITERATIONS = 390000
PBKDF2_PREFIX = "pbkdf2_sha256"


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        PBKDF2_ALGORITHM,
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    salt_b64 = base64.urlsafe_b64encode(salt).decode("ascii")
    digest_b64 = base64.urlsafe_b64encode(digest).decode("ascii")
    return f"{PBKDF2_PREFIX}${PBKDF2_ITERATIONS}${salt_b64}${digest_b64}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if hashed_password.startswith(f"{PBKDF2_PREFIX}$"):
        try:
            _, iterations_str, salt_b64, digest_b64 = hashed_password.split("$", 3)
            iterations = int(iterations_str)
            salt = base64.urlsafe_b64decode(salt_b64.encode("ascii"))
            expected_digest = base64.urlsafe_b64decode(digest_b64.encode("ascii"))
        except (ValueError, TypeError):
            return False

        actual_digest = hashlib.pbkdf2_hmac(
            PBKDF2_ALGORITHM,
            plain_password.encode("utf-8"),
            salt,
            iterations,
        )
        return hmac.compare_digest(actual_digest, expected_digest)

    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def create_access_token(subject: str, role: str, issuer_id: int | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    payload: dict[str, Any] = {"sub": subject, "role": role, "exp": expire}

    if issuer_id is not None:
        payload["issuer_id"] = issuer_id

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc
