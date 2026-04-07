from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import require_admin
from app.db.session import get_session
from app.schemas.issuer import (
    IssuerApprovalResponse,
    IssuerResponse,
    IssuerStatus,
    IssuerStatusUpdateRequest,
    WhitelistWalletRequest,
)
from app.services import issuer_service

router = APIRouter()


@router.post("/approve/{issuer_id}", response_model=IssuerApprovalResponse)
def approve_issuer(
    issuer_id: int,
    session: Annotated[Session, Depends(get_session)],
    _admin=Depends(require_admin),
) -> IssuerApprovalResponse:
    try:
        return issuer_service.approve_issuer(session, issuer_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/issuers/{issuer_id}/status", response_model=IssuerApprovalResponse)
def update_issuer_status(
    issuer_id: int,
    payload: IssuerStatusUpdateRequest,
    session: Annotated[Session, Depends(get_session)],
    _admin=Depends(require_admin),
) -> IssuerApprovalResponse:
    try:
        return issuer_service.update_issuer_status(session, issuer_id, payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/issuers", response_model=list[IssuerResponse])
def list_issuers(
    session: Annotated[Session, Depends(get_session)],
    _admin=Depends(require_admin),
    status: IssuerStatus | None = None,
) -> list[IssuerResponse]:
    return issuer_service.list_issuers(session, status)


@router.get("/issuers/{issuer_id}", response_model=IssuerResponse)
def get_issuer_details(
    issuer_id: int,
    session: Annotated[Session, Depends(get_session)],
    _admin=Depends(require_admin),
) -> IssuerResponse:
    try:
        return issuer_service.get_issuer_details(session, issuer_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/whitelist-wallet", response_model=IssuerResponse)
def whitelist_wallet(
    payload: WhitelistWalletRequest,
    session: Annotated[Session, Depends(get_session)],
    _admin=Depends(require_admin),
) -> IssuerResponse:
    try:
        return issuer_service.whitelist_wallet(session, payload.issuer_id, payload.wallet_address)
    except ValueError as exc:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
