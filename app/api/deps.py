from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.core.security import decode_token

bearer_scheme = HTTPBearer(auto_error=False)


class TokenUser(BaseModel):
    sub: str
    role: str
    issuer_id: int | None = None


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]
) -> TokenUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials or credentials.scheme.lower() != "bearer":
        raise credentials_exception

    try:
        payload = decode_token(credentials.credentials)
    except ValueError as exc:
        raise credentials_exception from exc

    subject = payload.get("sub")
    role = payload.get("role")
    issuer_id = payload.get("issuer_id")

    if not subject or role not in {"admin", "issuer"}:
        raise credentials_exception

    if role == "issuer" and issuer_id is None:
        raise credentials_exception

    return TokenUser(sub=subject, role=role, issuer_id=issuer_id)


def require_admin(current_user: Annotated[TokenUser, Depends(get_current_user)]) -> TokenUser:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return current_user


def require_issuer(current_user: Annotated[TokenUser, Depends(get_current_user)]) -> TokenUser:
    if current_user.role != "issuer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Issuer role required")
    return current_user
