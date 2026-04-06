import json

from sqlmodel import Session

from app.core.config import settings
from app.models.certificate import Certificate
from app.models.issuer import Issuer
from app.schemas.certificate import (
    CertificateCreateRequest,
    CertificateCreateResponse,
    CertificateTokenLinkResponse,
)
from app.services.ipfs_service import upload_to_ipfs
from app.utils.hash import generate_hash


def _normalize_certificate_payload(payload: CertificateCreateRequest) -> dict[str, str | int | float]:
    return {
        "roll_number": payload.roll_number.strip().upper(),
        "student_name": " ".join(payload.student_name.split()),
        "course_program": " ".join(payload.course_program.split()),
        "passing_year": payload.passing_year,
        "cgpa": round(payload.cgpa, 2),
    }


def create_certificate(
    session: Session,
    issuer_id: int,
    payload: CertificateCreateRequest,
) -> CertificateCreateResponse:
    issuer = session.get(Issuer, issuer_id)
    if not issuer:
        raise ValueError("Issuer not found")

    if issuer.status != "approved":
        raise PermissionError("Only approved issuers can create certificates")

    normalized = _normalize_certificate_payload(payload)
    canonical_payload = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    certificate_hash = generate_hash(canonical_payload)

    metadata = {
        **normalized,
        "hash": certificate_hash,
        "issuer": {
            "id": issuer.id,
            "name": issuer.name,
            "email": issuer.email,
            "wallet_address": issuer.wallet_address,
        },
    }

    cid = upload_to_ipfs(metadata)

    certificate = Certificate(issuer_id=issuer.id, cid=cid, hash=certificate_hash)
    session.add(certificate)
    session.commit()
    session.refresh(certificate)

    metadata_url = f"{settings.IPFS_GATEWAY_BASE_URL.rstrip('/')}/{cid}"
    return CertificateCreateResponse(
        certificate_id=certificate.id,
        cid=cid,
        hash=certificate_hash,
        metadata_url=metadata_url,
        token_id=certificate.token_id,
    )


def link_token_id(
    session: Session,
    issuer_id: int,
    certificate_id: int,
    token_id: str,
) -> CertificateTokenLinkResponse:
    certificate = session.get(Certificate, certificate_id)
    if not certificate:
        raise ValueError("Certificate not found")

    if certificate.issuer_id != issuer_id:
        raise PermissionError("Issuer cannot update this certificate")

    certificate.token_id = token_id.strip()
    session.add(certificate)
    session.commit()
    session.refresh(certificate)

    return CertificateTokenLinkResponse(
        certificate_id=certificate.id,
        cid=certificate.cid,
        hash=certificate.hash,
        token_id=certificate.token_id,
    )
