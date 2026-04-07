# Bhoomi Certificate Backend

Production-ready FastAPI backend for issuer onboarding and certificate metadata/IPFS workflows.

For frontend integration, see `FRONTEND_BACKEND_INTEGRATION.md`.

## Responsibilities

This backend is intentionally scoped to:

- Admin and issuer authentication (JWT)
- Issuer registration and approval workflows
- Certificate metadata hash generation and Pinata IPFS upload
- Returning `cid` and `hash` to frontend for MetaMask-based minting

This backend does **not** mint on-chain certificates. Blockchain minting must be handled by frontend wallet flows.

## Tech Stack

- FastAPI
- SQLModel + PostgreSQL
- JWT (`python-jose`)
- Pinata IPFS API (`requests`)

## Folder Structure

```text
app/
  main.py
  core/
    config.py
    security.py
  api/
    deps.py
    routes/
      auth.py
      admin.py
      issuer.py
      certificate.py
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
    ipfs_service.py
    certificate_service.py
  db/
    session.py
    base.py
  utils/
    hash.py
    qr.py
```

## Environment Variables

Required:

- `PINATA_JWT`
- `JWT_SECRET`
- `PINATA_BASE_URL`

Also used:

- `IPFS_GATEWAY_BASE_URL`
- `DATABASE_URL`
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`
- `ACCESS_TOKEN_EXPIRE_HOURS`

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Ensure PostgreSQL database exists and `DATABASE_URL` is correct.

3. Run API:

```bash
uvicorn app.main:app --reload
```

## API Flow

### Auth

- `POST /auth/login`

### Admin

- `POST /admin/approve/{issuer_id}`
- `PATCH /admin/issuers/{issuer_id}/status`
- `GET /admin/issuers`
- `GET /admin/issuers/{issuer_id}`
- `POST /admin/whitelist-wallet`

For `PATCH /admin/issuers/{issuer_id}/status`, allowed values are:

- `pending`
- `approved`
- `rejected`

### Issuer

- `POST /issuer/register`
- `GET /issuer/me`
- `POST /issuer/connect-wallet`
- `GET /issuer/wallet-status`

`POST /issuer/register` request body fields:

- `college_name`
- `college_address`
- `college_id`
- `document`
- `document_id`
- `phone_number`
- `email`
- `password`

`password` is required because issuer authentication currently uses email + password in `POST /auth/login`.

`POST /auth/login` for issuer now also returns wallet connectivity fields:

- `issuer_id`
- `wallet_connected`
- `wallet_address`

### Certificate

- `POST /certificate/create`
- `POST /certificate/link-token`
- `GET /certificate/history`
- `GET /certificate/verify/{token_id}`

Request body example for certificate creation:

```json
{
  "roll_number": "UNI123",
  "student_name": "Akshit Singh",
  "course_program": "B.Tech",
  "passing_year": 2026,
  "cgpa": 8.74
}
```

Response shape:

```json
{
  "certificate_id": 12,
  "cid": "Qm...",
  "hash": "0x...",
  "metadata_url": "https://gateway.pinata.cloud/ipfs/Qm...",
  "token_id": null
}
```

After frontend mints on Polygon, send token id to backend:

```json
{
  "certificate_id": 12,
  "token_id": "12345"
}
```

Issuer certificate history with counts:

`GET /certificate/history?limit=50&offset=0`

Response shape:

```json
{
  "issuer_id": 3,
  "total_generated": 12,
  "total_minted": 10,
  "limit": 50,
  "offset": 0,
  "certificates": [
    {
      "certificate_id": 12,
      "cid": "Qm...",
      "hash": "0x...",
      "token_id": "12345",
      "created_at": "2026-04-07T12:25:10.123456Z"
    }
  ]
}
```

Public verification by token id:

`GET /certificate/verify/12345`

Response shape:

```json
{
  "token_id": "12345",
  "certificate_id": 12,
  "cid": "Qm...",
  "hash": "0x...",
  "metadata_url": "https://gateway.pinata.cloud/ipfs/Qm...",
  "created_at": "2026-04-07T12:25:10.123456Z",
  "issuer_id": 3,
  "issuer_name": "ABC University",
  "metadata_accessible": true,
  "metadata_hash": "0x...",
  "metadata_hash_matches": true,
  "recomputed_hash": "0x...",
  "recomputed_hash_matches": true,
  "certificate_payload": {
    "roll_number": "UNI123",
    "student_name": "Akshit Singh",
    "course_program": "B.Tech",
    "passing_year": 2026,
    "cgpa": 8.74
  },
  "is_verified": true
}
```

## Notes

- Issuer must be approved before login and certificate creation.
- Wallet format validation expects Ethereum-style `0x` address with 42 chars.
- Errors are mapped to proper HTTP status codes across routes.
