from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Certificate(SQLModel, table=True):
    __tablename__ = "certificates"

    id: int | None = Field(default=None, primary_key=True)
    issuer_id: int = Field(foreign_key="issuers.id", index=True)
    cid: str = Field(max_length=255, index=True)
    hash: str = Field(max_length=100, index=True)
    token_id: str | None = Field(default=None, max_length=100, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
