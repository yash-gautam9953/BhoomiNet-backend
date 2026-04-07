from datetime import datetime

from pydantic import BaseModel, Field


class CertificateCreateRequest(BaseModel):
    roll_number: str = Field(min_length=1, max_length=100)
    student_name: str = Field(min_length=1, max_length=255)
    course_program: str = Field(min_length=1, max_length=255)
    passing_year: int = Field(ge=1900, le=2100)
    cgpa: float = Field(ge=0, le=10)


class CertificateCreateResponse(BaseModel):
    certificate_id: int
    cid: str
    hash: str
    metadata_url: str
    token_id: str | None = None


class CertificateTokenLinkRequest(BaseModel):
    certificate_id: int
    token_id: str = Field(min_length=1, max_length=100)


class CertificateTokenLinkResponse(BaseModel):
    certificate_id: int
    cid: str
    hash: str
    token_id: str


class CertificateHistoryItem(BaseModel):
    certificate_id: int
    cid: str
    hash: str
    token_id: str | None = None
    created_at: datetime


class CertificateHistoryResponse(BaseModel):
    issuer_id: int
    total_generated: int
    total_minted: int
    limit: int
    offset: int
    certificates: list[CertificateHistoryItem]


class CertificateVerifyResponse(BaseModel):
    token_id: str
    certificate_id: int
    cid: str
    hash: str
    metadata_url: str
    created_at: datetime
    issuer_id: int
    issuer_name: str | None = None
    metadata_accessible: bool
    metadata_hash: str | None = None
    metadata_hash_matches: bool | None = None
    recomputed_hash: str | None = None
    recomputed_hash_matches: bool | None = None
    certificate_payload: dict | None = None
    is_verified: bool
