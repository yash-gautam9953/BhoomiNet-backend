# Provectus Certificate Backend

Production-focused FastAPI backend for issuer onboarding, certificate metadata generation, IPFS storage, and token-based verification.

For frontend integration details, see `FRONTEND_BACKEND_INTEGRATION.md`.

## What This Service Does

- Authenticates admin and issuers using JWT bearer tokens.
- Handles issuer registration, approval workflow, and wallet linking.
- Generates canonical certificate payload hash and uploads metadata to Pinata IPFS.
- Stores certificate records and links on-chain token id after frontend minting.
- Verifies issued certificate metadata integrity by token id.

This backend does not mint certificates on-chain. Minting is handled by frontend wallet flows.

## Tech Stack

- FastAPI
- SQLModel + SQLAlchemy
- PostgreSQL (primary) and sqlite compatibility for local sync logic
- python-jose (JWT)
- passlib + PBKDF2 password hashing support
- requests (Pinata + metadata fetch)

## Project Structure

```text
app/
  main.py                    # FastAPI app, CORS, middleware, exception handler
  api/
    deps.py                  # auth dependencies (current user, role guards)
    routes/
      auth.py
      admin.py
      issuer.py
      certificate.py
  core/
    config.py                # env-driven settings
    security.py              # password hashing + JWT encode/decode
  db/
    session.py               # engine + session dependency
    base.py                  # create_all + schema sync helpers
  models/
    issuer.py
    certificate.py
  schemas/
    auth.py
    issuer.py
    certificate.py
  services/
    auth_service.py
    issuer_service.py
    certificate_service.py
    ipfs_service.py
  utils/
    hash.py
    qr.py
```

## API Surface

### Auth

- POST `/auth/login`

### Admin

- POST `/admin/approve/{issuer_id}`
- PATCH `/admin/issuers/{issuer_id}/status`
- GET `/admin/issuers`
- GET `/admin/issuers/{issuer_id}`
- POST `/admin/whitelist-wallet`

Allowed status values for issuer update:

- `pending`
- `approved`
- `rejected`

### Issuer

- POST `/issuer/register`
- GET `/issuer/me`
- POST `/issuer/connect-wallet`
- GET `/issuer/wallet-status`
- GET `/issuer/issued-certificate-count`

### Certificate

- POST `/certificate/create`
- POST `/certificate/link-token`
- GET `/certificate/history`
- GET `/certificate/verify/{token_id}`

## Authentication and Roles

- Admin role:
  - Approve/reject issuers
  - Review issuer records
  - Whitelist wallet
- Issuer role:
  - Access own profile
  - Link wallet
  - Create and manage certificate records

JWT is expected as:

- `Authorization: Bearer <access_token>`

## Environment Variables

Configure with `.env` in repository root.

### Security-Critical (must set in production)

- `JWT_SECRET`
  - Use a long random value (do not keep default fallback).
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`
  - Use a strong secret and rotate periodically.
- `PINATA_JWT`
  - Required for metadata upload to Pinata.

### Core Runtime

- `DATABASE_URL`
  - Example: `postgresql+psycopg://user:password@host:5432/dbname`
- `JWT_ALGORITHM` (default: `HS256`)
- `ACCESS_TOKEN_EXPIRE_HOURS` (default: `8`)
- `DEBUG` (default: `False`)

### External Integrations

- `PINATA_BASE_URL` (default: `https://api.pinata.cloud`)
- `IPFS_GATEWAY_BASE_URL` (default: `https://gateway.pinata.cloud/ipfs`)
- `POLYGON_RPC_URL` (currently kept for ecosystem compatibility)

### CORS

- `CORS_ORIGINS`
  - Supports JSON array or comma-separated string.
- `CORS_ALLOW_ORIGIN_REGEX`

Production recommendation: restrict CORS to exact frontend origins only.

## Production Setup

### 1. Prerequisites

- Python 3.11+
- PostgreSQL instance
- Valid Pinata JWT

### 2. Install Dependencies

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment

- Create/update `.env`
- Set all security-critical variables
- Verify `DATABASE_URL` connectivity

### 4. Start Service

Development:

```bash
uvicorn app.main:app --reload
```

Production (basic multi-worker):

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

### 5. Expose Behind Reverse Proxy

- Use Nginx/Caddy/ingress controller for TLS termination.
- Restrict inbound access to required ports.
- Enable request size/time limits at proxy layer.

## Startup and Database Behavior

On startup, the app does:

- `SQLModel.metadata.create_all(engine)`
- lightweight column sync for selected issuer/certificate columns

This is useful for bootstrapping, but for strict production change control, add versioned migrations (for example Alembic) before large schema evolution.

## Operational Notes

- Request logging middleware records request start/end with timing and request id.
- Global unhandled exceptions return HTTP 500 with generic detail.
- Certificate verification endpoint fetches metadata from IPFS gateway and validates hash integrity.

## Security Checklist for Production

- Replace all default secrets and credentials from config fallbacks.
- Use strong admin password and rotate credentials.
- Keep `DEBUG=false`.
- Use managed PostgreSQL with TLS (`sslmode=require` where applicable).
- Restrict CORS origins.
- Rotate and protect `PINATA_JWT`.

## Useful URLs

- OpenAPI docs: `/docs`
- OpenAPI JSON: `/openapi.json`

## License and Ownership

Internal project for Provectus certificate workflows.
