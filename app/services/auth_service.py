from secrets import compare_digest

from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.models.issuer import Issuer
from app.schemas.auth import LoginRequest, TokenResponse


def login(session: Session, payload: LoginRequest) -> TokenResponse:
    email = payload.email.lower()

    if email == settings.ADMIN_EMAIL.lower():
        if not compare_digest(payload.password, settings.ADMIN_PASSWORD):
            raise ValueError("Invalid credentials")

        token = create_access_token(subject=settings.ADMIN_EMAIL, role="admin")
        return TokenResponse(access_token=token, role="admin")

    issuer = session.exec(select(Issuer).where(Issuer.email == email)).first()
    if not issuer or not verify_password(payload.password, issuer.password_hash):
        raise ValueError("Invalid credentials")

    if issuer.status != "approved":
        raise PermissionError("Issuer account is not approved")

    token = create_access_token(subject=issuer.email, role="issuer", issuer_id=issuer.id)
    return TokenResponse(
        access_token=token,
        role="issuer",
        issuer_id=issuer.id,
        wallet_connected=bool(issuer.wallet_address),
        wallet_address=issuer.wallet_address,
    )
