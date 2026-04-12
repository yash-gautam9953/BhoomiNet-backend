from typing import Literal

from pydantic import BaseModel, EmailStr, Field


IssuerStatus = Literal["pending", "approved", "rejected"]


class IssuerRegisterRequest(BaseModel):
    college_name: str = Field(min_length=2, max_length=255)
    college_address: str = Field(min_length=5, max_length=500)
    college_id: str = Field(min_length=2, max_length=100)
    document: str = Field(min_length=3, max_length=1000)
    document_id: str = Field(min_length=2, max_length=255)
    phone_number: str = Field(min_length=7, max_length=20)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class IssuerResponse(BaseModel):
    id: int
    college_name: str
    college_address: str
    college_id: str
    document: str
    document_id: str
    phone_number: str
    email: EmailStr
    status: IssuerStatus
    wallet_address: str | None = None


class IssuerIssuedCertificateCountResponse(BaseModel):
    issuer_id: int
    issued_certificates: int


class WalletConnectRequest(BaseModel):
    wallet_address: str = Field(min_length=10, max_length=100)


class WhitelistWalletRequest(BaseModel):
    issuer_id: int
    wallet_address: str = Field(min_length=10, max_length=100)


class IssuerApprovalResponse(BaseModel):
    issuer_id: int
    status: IssuerStatus


class IssuerStatusUpdateRequest(BaseModel):
    status: IssuerStatus


class WalletStatusResponse(BaseModel):
    issuer_id: int
    issuer_status: IssuerStatus
    wallet_connected: bool
    wallet_address: str | None = None
