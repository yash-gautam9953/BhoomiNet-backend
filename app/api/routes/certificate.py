from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api.deps import TokenUser, require_issuer
from app.db.session import get_session
from app.schemas.certificate import (
    CertificateCreateRequest,
    CertificateCreateResponse,
    CertificateHistoryResponse,
    CertificateTokenLinkRequest,
    CertificateTokenLinkResponse,
    CertificateVerifyResponse,
)
from app.services import certificate_service

router = APIRouter()


@router.get("/verify/{token_id}", response_model=CertificateVerifyResponse)
def verify_certificate_by_token_id(
    token_id: str,
    session: Annotated[Session, Depends(get_session)],
) -> CertificateVerifyResponse:
    try:
        return certificate_service.verify_certificate_by_token_id(session, token_id)
    except ValueError as exc:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc


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


@router.get("/history", response_model=CertificateHistoryResponse)
def get_certificate_history(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[TokenUser, Depends(require_issuer)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> CertificateHistoryResponse:
    try:
        return certificate_service.get_certificate_history(
            session=session,
            issuer_id=current_user.issuer_id,
            limit=limit,
            offset=offset,
        )
    except ValueError as exc:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
