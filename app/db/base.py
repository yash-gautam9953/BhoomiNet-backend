from sqlalchemy import text
from sqlmodel import SQLModel

from app.db.session import engine
from app.models.certificate import Certificate  # noqa: F401
from app.models.issuer import Issuer  # noqa: F401


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
    _sync_issuer_table_columns()
    _sync_certificate_table_columns()


def _sync_issuer_table_columns() -> None:
    postgres_defs = {
        "college_address": "VARCHAR(500) NOT NULL DEFAULT ''",
        "college_id": "VARCHAR(100) NOT NULL DEFAULT ''",
        "document": "VARCHAR(1000) NOT NULL DEFAULT ''",
        "document_id": "VARCHAR(255) NOT NULL DEFAULT ''",
        "phone_number": "VARCHAR(20) NOT NULL DEFAULT ''",
    }
    sqlite_defs = {
        "college_address": "TEXT NOT NULL DEFAULT ''",
        "college_id": "TEXT NOT NULL DEFAULT ''",
        "document": "TEXT NOT NULL DEFAULT ''",
        "document_id": "TEXT NOT NULL DEFAULT ''",
        "phone_number": "TEXT NOT NULL DEFAULT ''",
    }

    with engine.begin() as conn:
        dialect = conn.dialect.name
        if dialect == "postgresql":
            for column_name, column_def in postgres_defs.items():
                conn.execute(text(f"ALTER TABLE issuers ADD COLUMN IF NOT EXISTS {column_name} {column_def}"))
            return

        if dialect == "sqlite":
            existing_columns = {
                row[1]
                for row in conn.execute(text("PRAGMA table_info(issuers)")).fetchall()
            }
            for column_name, column_def in sqlite_defs.items():
                if column_name not in existing_columns:
                    conn.execute(text(f"ALTER TABLE issuers ADD COLUMN {column_name} {column_def}"))


def _sync_certificate_table_columns() -> None:
    postgres_defs = {
        "token_id": "VARCHAR(100)",
    }
    sqlite_defs = {
        "token_id": "TEXT",
    }

    with engine.begin() as conn:
        dialect = conn.dialect.name
        if dialect == "postgresql":
            for column_name, column_def in postgres_defs.items():
                conn.execute(text(f"ALTER TABLE certificates ADD COLUMN IF NOT EXISTS {column_name} {column_def}"))
            return

        if dialect == "sqlite":
            existing_columns = {
                row[1]
                for row in conn.execute(text("PRAGMA table_info(certificates)")).fetchall()
            }
            for column_name, column_def in sqlite_defs.items():
                if column_name not in existing_columns:
                    conn.execute(text(f"ALTER TABLE certificates ADD COLUMN {column_name} {column_def}"))
