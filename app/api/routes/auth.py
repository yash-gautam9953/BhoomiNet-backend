from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.auth import LoginRequest, TokenResponse
from app.services import auth_service

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    session: Annotated[Session, Depends(get_session)],
) -> TokenResponse:
    try:
        return auth_service.login(session, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
