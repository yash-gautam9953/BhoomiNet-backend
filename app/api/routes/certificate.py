from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import TokenUser, require_issuer
from app.db.session import get_session
from app.schemas.certificate import (
    CertificateCreateRequest,
    CertificateCreateResponse,
    CertificateTokenLinkRequest,
    CertificateTokenLinkResponse,
)
from app.services import certificate_service

router = APIRouter()


@router.post("/create", response_model=CertificateCreateResponse)
def create_certificate(
    payload: CertificateCreateRequest,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[TokenUser, Depends(require_issuer)],
) -> CertificateCreateResponse:
    try:
        return certificate_service.create_certificate(session, current_user.issuer_id, payload)
    except ValueError as exc:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post("/link-token", response_model=CertificateTokenLinkResponse)
def link_token(
    payload: CertificateTokenLinkRequest,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[TokenUser, Depends(require_issuer)],
) -> CertificateTokenLinkResponse:
    try:
        return certificate_service.link_token_id(
            session,
            current_user.issuer_id,
            payload.certificate_id,
            payload.token_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
