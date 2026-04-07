import json

import requests
from sqlalchemy import func
from sqlmodel import select
from sqlmodel import Session

from app.core.config import settings
from app.models.certificate import Certificate
from app.models.issuer import Issuer
from app.schemas.certificate import (
    CertificateCreateRequest,
    CertificateCreateResponse,
    CertificateHistoryItem,
    CertificateHistoryResponse,
    CertificateTokenLinkResponse,
    CertificateVerifyResponse,
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


def _normalize_payload_from_metadata(metadata: dict) -> dict[str, str | int | float]:
    return {
        "roll_number": str(metadata["roll_number"]).strip().upper(),
        "student_name": " ".join(str(metadata["student_name"]).split()),
        "course_program": " ".join(str(metadata["course_program"]).split()),
        "passing_year": int(metadata["passing_year"]),
        "cgpa": round(float(metadata["cgpa"]), 2),
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


def get_certificate_history(
    session: Session,
    issuer_id: int,
    limit: int = 50,
    offset: int = 0,
) -> CertificateHistoryResponse:
    issuer = session.get(Issuer, issuer_id)
    if not issuer:
        raise ValueError("Issuer not found")

    total_generated = session.exec(
        select(func.count()).select_from(Certificate).where(Certificate.issuer_id == issuer_id)
    ).one()

    total_minted = session.exec(
        select(func.count())
        .select_from(Certificate)
        .where(Certificate.issuer_id == issuer_id, Certificate.token_id.is_not(None))
    ).one()

    certificates = session.exec(
        select(Certificate)
        .where(Certificate.issuer_id == issuer_id)
        .order_by(Certificate.created_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    history_items = [
        CertificateHistoryItem(
            certificate_id=certificate.id,
            cid=certificate.cid,
            hash=certificate.hash,
            token_id=certificate.token_id,
            created_at=certificate.created_at,
        )
        for certificate in certificates
    ]

    return CertificateHistoryResponse(
        issuer_id=issuer_id,
        total_generated=total_generated,
        total_minted=total_minted,
        limit=limit,
        offset=offset,
        certificates=history_items,
    )


def verify_certificate_by_token_id(
    session: Session,
    token_id: str,
) -> CertificateVerifyResponse:
    clean_token_id = token_id.strip()
    if not clean_token_id:
        raise ValueError("Token ID is required")

    certificate = session.exec(select(Certificate).where(Certificate.token_id == clean_token_id)).first()
    if not certificate:
        raise ValueError("Certificate not found for the provided token ID")

    issuer = session.get(Issuer, certificate.issuer_id)

    metadata_url = f"{settings.IPFS_GATEWAY_BASE_URL.rstrip('/')}/{certificate.cid}"
    metadata_accessible = False
    metadata_hash: str | None = None
    metadata_hash_matches: bool | None = None
    recomputed_hash: str | None = None
    recomputed_hash_matches: bool | None = None
    certificate_payload: dict | None = None

    try:
        response = requests.get(metadata_url, timeout=20)
        response.raise_for_status()
        metadata = response.json()

        if isinstance(metadata, dict):
            metadata_accessible = True
            metadata_hash_value = metadata.get("hash")
            if isinstance(metadata_hash_value, str) and metadata_hash_value.strip():
                metadata_hash = metadata_hash_value.strip()
                metadata_hash_matches = metadata_hash.lower() == certificate.hash.lower()

            try:
                normalized_payload = _normalize_payload_from_metadata(metadata)
                certificate_payload = normalized_payload
                canonical_payload = json.dumps(normalized_payload, sort_keys=True, separators=(",", ":"))
                recomputed_hash = generate_hash(canonical_payload)
                recomputed_hash_matches = recomputed_hash.lower() == certificate.hash.lower()
            except (KeyError, TypeError, ValueError):
                recomputed_hash_matches = False
    except (requests.RequestException, ValueError):
        metadata_accessible = False

    is_verified = bool(metadata_accessible and metadata_hash_matches and recomputed_hash_matches)

    return CertificateVerifyResponse(
        token_id=clean_token_id,
        certificate_id=certificate.id,
        cid=certificate.cid,
        hash=certificate.hash,
        metadata_url=metadata_url,
        created_at=certificate.created_at,
        issuer_id=certificate.issuer_id,
        issuer_name=issuer.name if issuer else None,
        metadata_accessible=metadata_accessible,
        metadata_hash=metadata_hash,
        metadata_hash_matches=metadata_hash_matches,
        recomputed_hash=recomputed_hash,
        recomputed_hash_matches=recomputed_hash_matches,
        certificate_payload=certificate_payload,
        is_verified=is_verified,
    )
