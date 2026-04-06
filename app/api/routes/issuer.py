from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import TokenUser, require_issuer
from app.db.session import get_session
from app.schemas.issuer import (
    IssuerRegisterRequest,
    IssuerResponse,
    WalletConnectRequest,
    WalletStatusResponse,
)
from app.services import issuer_service

router = APIRouter()


@router.post("/register", response_model=IssuerResponse, status_code=status.HTTP_201_CREATED)
def register_issuer(
    payload: IssuerRegisterRequest,
    session: Annotated[Session, Depends(get_session)],
) -> IssuerResponse:
    try:
        return issuer_service.register_issuer(session, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/connect-wallet", response_model=IssuerResponse)
def connect_wallet(
    payload: WalletConnectRequest,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[TokenUser, Depends(require_issuer)],
) -> IssuerResponse:
    try:
        return issuer_service.connect_wallet(session, current_user.issuer_id, payload.wallet_address)
    except ValueError as exc:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.get("/me", response_model=IssuerResponse)
def get_issuer_profile(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[TokenUser, Depends(require_issuer)],
) -> IssuerResponse:
    try:
        return issuer_service.get_issuer_profile(session, current_user.issuer_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/wallet-status", response_model=WalletStatusResponse)
def get_wallet_status(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[TokenUser, Depends(require_issuer)],
) -> WalletStatusResponse:
    try:
        return issuer_service.get_wallet_status(session, current_user.issuer_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
