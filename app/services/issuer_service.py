from sqlalchemy import func
from sqlmodel import Session, select

from app.core.security import hash_password
from app.models.certificate import Certificate
from app.models.issuer import Issuer
from app.schemas.issuer import (
    IssuerApprovalResponse,
    IssuerIssuedCertificateCountResponse,
    IssuerRegisterRequest,
    IssuerResponse,
    IssuerStatus,
    WalletStatusResponse,
)


def _to_issuer_response(issuer: Issuer) -> IssuerResponse:
    return IssuerResponse(
        id=issuer.id,
        college_name=issuer.name,
        college_address=issuer.college_address,
        college_id=issuer.college_id,
        document=issuer.document,
        document_id=issuer.document_id,
        phone_number=issuer.phone_number,
        email=issuer.email,
        status=issuer.status,
        wallet_address=issuer.wallet_address,
    )


def _validate_wallet(wallet_address: str) -> None:
    if not wallet_address.startswith("0x") or len(wallet_address) != 42:
        raise ValueError("Invalid wallet address format")


def register_issuer(session: Session, payload: IssuerRegisterRequest) -> IssuerResponse:
    email = payload.email.lower()

    existing = session.exec(select(Issuer).where(Issuer.email == email)).first()
    if existing:
        raise ValueError("Issuer with this email already exists")

    issuer = Issuer(
        name=payload.college_name.strip(),
        college_address=payload.college_address.strip(),
        college_id=payload.college_id.strip(),
        document=payload.document.strip(),
        document_id=payload.document_id.strip(),
        phone_number=payload.phone_number.strip(),
        email=email,
        password_hash=hash_password(payload.password),
        status="pending",
    )
    session.add(issuer)
    session.commit()
    session.refresh(issuer)

    return _to_issuer_response(issuer)


def approve_issuer(session: Session, issuer_id: int) -> IssuerApprovalResponse:
    return update_issuer_status(session, issuer_id, "approved")


def update_issuer_status(
    session: Session,
    issuer_id: int,
    status: IssuerStatus,
) -> IssuerApprovalResponse:
    issuer = session.get(Issuer, issuer_id)
    if not issuer:
        raise ValueError("Issuer not found")

    issuer.status = status
    session.add(issuer)
    session.commit()

    return IssuerApprovalResponse(issuer_id=issuer.id, status=issuer.status)


def list_issuers(session: Session, status: IssuerStatus | None = None) -> list[IssuerResponse]:
    statement = select(Issuer)
    if status:
        statement = statement.where(Issuer.status == status)

    issuers = session.exec(statement.order_by(Issuer.id)).all()
    return [_to_issuer_response(issuer) for issuer in issuers]


def get_issuer_details(session: Session, issuer_id: int) -> IssuerResponse:
    issuer = session.get(Issuer, issuer_id)
    if not issuer:
        raise ValueError("Issuer not found")

    return _to_issuer_response(issuer)


def whitelist_wallet(session: Session, issuer_id: int, wallet_address: str) -> IssuerResponse:
    _validate_wallet(wallet_address)

    issuer = session.get(Issuer, issuer_id)
    if not issuer:
        raise ValueError("Issuer not found")

    issuer.wallet_address = wallet_address
    session.add(issuer)
    session.commit()
    session.refresh(issuer)

    return _to_issuer_response(issuer)


def connect_wallet(session: Session, issuer_id: int, wallet_address: str) -> IssuerResponse:
    _validate_wallet(wallet_address)

    issuer = session.get(Issuer, issuer_id)
    if not issuer:
        raise ValueError("Issuer not found")

    if issuer.status != "approved":
        raise PermissionError("Only approved issuers can connect wallet")

    issuer.wallet_address = wallet_address
    session.add(issuer)
    session.commit()
    session.refresh(issuer)

    return _to_issuer_response(issuer)


def get_issuer_profile(session: Session, issuer_id: int) -> IssuerResponse:
    issuer = session.get(Issuer, issuer_id)
    if not issuer:
        raise ValueError("Issuer not found")

    return _to_issuer_response(issuer)


def get_wallet_status(session: Session, issuer_id: int) -> WalletStatusResponse:
    issuer = session.get(Issuer, issuer_id)
    if not issuer:
        raise ValueError("Issuer not found")

    return WalletStatusResponse(
        issuer_id=issuer.id,
        issuer_status=issuer.status,
        wallet_connected=bool(issuer.wallet_address),
        wallet_address=issuer.wallet_address,
    )


def get_issued_certificate_count(
    session: Session,
    issuer_id: int,
) -> IssuerIssuedCertificateCountResponse:
    issuer = session.get(Issuer, issuer_id)
    if not issuer:
        raise ValueError("Issuer not found")

    issued_certificates = session.exec(
        select(func.count()).select_from(Certificate).where(Certificate.issuer_id == issuer_id)
    ).one()

    return IssuerIssuedCertificateCountResponse(
        issuer_id=issuer_id,
        issued_certificates=int(issued_certificates),
    )
