from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Issuer(SQLModel, table=True):
    __tablename__ = "issuers"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, index=True)
    college_address: str = Field(default="", max_length=500)
    college_id: str = Field(default="", max_length=100, index=True)
    document: str = Field(default="", max_length=1000)
    document_id: str = Field(default="", max_length=255, index=True)
    phone_number: str = Field(default="", max_length=20)
    email: str = Field(max_length=255, index=True, sa_column_kwargs={"unique": True})
    password_hash: str
    status: str = Field(default="pending", max_length=20, index=True)
    wallet_address: str | None = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
