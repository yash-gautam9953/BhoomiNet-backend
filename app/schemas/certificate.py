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
