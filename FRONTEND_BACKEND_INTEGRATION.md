# Frontend Integration Guide

This guide is for frontend developers who need to consume the Provectus backend APIs.

## 1) Base URLs

- Local API base URL: `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## 2) Authentication Model

The backend uses JWT bearer tokens.

- Login endpoint: `POST /auth/login`
- Swagger authorize type: `HTTP Bearer`
- Header format for protected APIs:

```http
Authorization: Bearer <access_token>
```

## 3) Roles

- `admin`: can approve/reject/update issuer status and whitelist wallet
- `issuer`: can connect wallet and create certificates (only when status is `approved`)

Issuer login rule:

- `approved` -> login allowed
- `pending` or `rejected` -> login denied with 403

## 4) Endpoints Frontend Will Use

### Auth

#### POST `/auth/login`

Request:

```json
{
  "email": "admin@example.com",
  "password": "provectus"
}
```

Response:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "role": "issuer",
  "issuer_id": 3,
  "wallet_connected": false,
  "wallet_address": null
}
```

Use `wallet_connected` immediately after login to decide whether to show "Connect Wallet" screen.

### Issuer Public

#### POST `/issuer/register`

Request:

```json
{
  "college_name": "ABC University",
  "college_address": "MG Road, Indore",
  "college_id": "ABC-IND-001",
  "document": "https://example.com/docs/affiliation.pdf",
  "document_id": "DOC-2026-001",
  "phone_number": "+919876543210",
  "email": "issuer@abc.edu",
  "password": "StrongPass123"
}
```

Response (201):

```json
{
  "id": 1,
  "college_name": "ABC University",
  "college_address": "MG Road, Indore",
  "college_id": "ABC-IND-001",
  "document": "https://example.com/docs/affiliation.pdf",
  "document_id": "DOC-2026-001",
  "phone_number": "+919876543210",
  "email": "issuer@abc.edu",
  "status": "pending",
  "wallet_address": null
}
```

### Admin Protected

#### PATCH `/admin/issuers/{issuer_id}/status`

Headers: `Authorization: Bearer <admin_token>`

Request:

```json
{
  "status": "approved"
}
```

Allowed values:

- `pending`
- `approved`
- `rejected`

Response:

```json
{
  "issuer_id": 1,
  "status": "approved"
}
```

#### GET `/admin/issuers`

Headers: `Authorization: Bearer <admin_token>`

Optional query:

- `/admin/issuers?status=approved`

#### GET `/admin/issuers/{issuer_id}`

Headers: `Authorization: Bearer <admin_token>`

Use this endpoint for the "View Details" button in admin panel.

Example:

- `/admin/issuers/5`

Response:

```json
{
  "id": 5,
  "college_name": "New Tech College",
  "college_address": "Ring Road, Bhopal",
  "college_id": "NTC-BPL-002",
  "document": "https://example.com/docs/ntc-affiliation.pdf",
  "document_id": "NTC-DOC-002",
  "phone_number": "+919000000002",
  "email": "issuer-new-fields@example.com",
  "status": "pending",
  "wallet_address": null
}
```

#### POST `/admin/whitelist-wallet`

Headers: `Authorization: Bearer <admin_token>`

Request:

```json
{
  "issuer_id": 1,
  "wallet_address": "0x1234567890abcdef1234567890abcdef12345678"
}
```

### Issuer Protected

#### GET `/issuer/me`

Headers: `Authorization: Bearer <issuer_token>`

Response:

```json
{
  "id": 5,
  "college_name": "New Tech College",
  "college_address": "Ring Road, Bhopal",
  "college_id": "NTC-BPL-002",
  "document": "https://example.com/docs/ntc-affiliation.pdf",
  "document_id": "NTC-DOC-002",
  "phone_number": "+919000000002",
  "email": "issuer-new-fields@example.com",
  "status": "pending",
  "wallet_address": null
}
```

Use this endpoint to populate issuer profile/dashboard page.

#### POST `/issuer/connect-wallet`

Headers: `Authorization: Bearer <issuer_token>`

Request:

```json
{
  "wallet_address": "0x1234567890abcdef1234567890abcdef12345678"
}
```

#### GET `/issuer/wallet-status`

Headers: `Authorization: Bearer <issuer_token>`

Response:

```json
{
  "issuer_id": 3,
  "issuer_status": "approved",
  "wallet_connected": false,
  "wallet_address": null
}
```

#### GET `/issuer/issued-certificate-count`

Headers: `Authorization: Bearer <issuer_token>`

Response:

```json
{
  "issuer_id": 3,
  "issued_certificates": 12
}
```

### Certificate Protected (Issuer)

#### POST `/certificate/create`

Headers: `Authorization: Bearer <issuer_token>`

Request:

```json
{
  "roll_number": "UNI123",
  "student_name": "Akshit Singh",
  "course_program": "B.Tech",
  "passing_year": 2026,
  "cgpa": 8.74
}
```

Response:

```json
{
  "certificate_id": 12,
  "cid": "Qm...",
  "hash": "0x...",
  "metadata_url": "https://gateway.pinata.cloud/ipfs/Qm...",
  "token_id": null
}
```

#### POST `/certificate/link-token`

Headers: `Authorization: Bearer <issuer_token>`

Request:

```json
{
  "certificate_id": 12,
  "token_id": "12345"
}
```

Response:

```json
{
  "certificate_id": 12,
  "cid": "Qm...",
  "hash": "0x...",
  "token_id": "12345"
}
```

Frontend should use `cid` and `hash` for wallet-side minting (MetaMask flow).

#### GET `/certificate/history`

Headers: `Authorization: Bearer <issuer_token>`

Optional query params:

- `limit` (default: 50, max: 200)
- `offset` (default: 0)

Response:

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

#### GET `/certificate/verify/{token_id}`

Public endpoint. No auth token required.

Example:

- `/certificate/verify/12345`

Response:

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

Verification field meanings:

- `token_id`: On-chain token id submitted by user.
- `certificate_id`: Backend certificate row id linked to this token.
- `cid`: IPFS CID linked to the certificate.
- `hash`: Hash stored in backend for this certificate.
- `metadata_url`: Gateway URL used to fetch IPFS metadata.
- `metadata_accessible`: `true` if IPFS metadata is reachable and valid JSON.
- `metadata_hash`: `hash` value found inside metadata JSON (if present).
- `metadata_hash_matches`: `true` when metadata hash equals backend hash.
- `recomputed_hash`: Hash recomputed by backend from metadata fields.
- `recomputed_hash_matches`: `true` when recomputed hash equals backend hash.
- `certificate_payload`: Normalized payload extracted from metadata.
- `is_verified`: Final result. `true` only when all verification checks pass.

Demo response: Verified certificate

```json
{
  "token_id": "12345",
  "certificate_id": 12,
  "cid": "QmValidCid111",
  "hash": "0x9aabccddeeff00112233445566778899aabbccddeeff001122334455667788",
  "metadata_url": "https://gateway.pinata.cloud/ipfs/QmValidCid111",
  "created_at": "2026-04-07T12:25:10.123456Z",
  "issuer_id": 3,
  "issuer_name": "ABC University",
  "metadata_accessible": true,
  "metadata_hash": "0x9aabccddeeff00112233445566778899aabbccddeeff001122334455667788",
  "metadata_hash_matches": true,
  "recomputed_hash": "0x9aabccddeeff00112233445566778899aabbccddeeff001122334455667788",
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

Demo response: Tampered or mismatched metadata

```json
{
  "token_id": "12345",
  "certificate_id": 12,
  "cid": "QmValidCid111",
  "hash": "0x9aabccddeeff00112233445566778899aabbccddeeff001122334455667788",
  "metadata_url": "https://gateway.pinata.cloud/ipfs/QmValidCid111",
  "created_at": "2026-04-07T12:25:10.123456Z",
  "issuer_id": 3,
  "issuer_name": "ABC University",
  "metadata_accessible": true,
  "metadata_hash": "0x0000000000000000000000000000000000000000000000000000000000000000",
  "metadata_hash_matches": false,
  "recomputed_hash": "0x1111111111111111111111111111111111111111111111111111111111111111",
  "recomputed_hash_matches": false,
  "certificate_payload": {
    "roll_number": "UNI123",
    "student_name": "Changed Name",
    "course_program": "B.Tech",
    "passing_year": 2026,
    "cgpa": 8.74
  },
  "is_verified": false
}
```

Demo response: Token id not found

```json
{
  "detail": "Certificate not found for the provided token ID"
}
```

## 5) Recommended Frontend Flow

1. Issuer signs up via `/issuer/register` (status starts as `pending`)
2. Admin logs in and sets issuer status to `approved`
3. Issuer logs in and stores JWT token
4. Issuer connects wallet
5. Issuer creates certificate and gets `cid` + `hash`
6. Frontend triggers smart contract minting with MetaMask

## 6) JavaScript Example (Fetch)

```js
const API_BASE = "http://127.0.0.1:8000";

async function login(email, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Login failed");
  }

  return res.json();
}

async function createCertificate(token, payload) {
  const res = await fetch(`${API_BASE}/certificate/create`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Certificate create failed");
  }

  return res.json();
}

async function getCertificateHistory(token, limit = 50, offset = 0) {
  const res = await fetch(
    `${API_BASE}/certificate/history?limit=${limit}&offset=${offset}`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Certificate history fetch failed");
  }

  return res.json();
}

async function verifyByTokenId(tokenId) {
  const res = await fetch(
    `${API_BASE}/certificate/verify/${encodeURIComponent(tokenId)}`,
    {
      method: "GET",
    },
  );

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Certificate verification failed");
  }

  return res.json();
}

// Demo UI decision logic
function mapVerifyResult(result) {
  if (result.is_verified) {
    return { status: "VERIFIED", color: "green" };
  }

  if (result.metadata_accessible === false) {
    return { status: "UNVERIFIED_IPFS_UNREACHABLE", color: "amber" };
  }

  return { status: "UNVERIFIED_HASH_MISMATCH", color: "red" };
}
```

## 7) Common Errors and Meanings

- `401 Could not validate credentials`: token missing/invalid/expired
- `403 Issuer account is not approved`: issuer status is not `approved`
- `403 Admin role required`: admin-only endpoint called with non-admin token
- `400 Invalid wallet address format`: wallet must be Ethereum `0x` + 40 hex chars
- `502 Failed to upload metadata to Pinata`: Pinata config/network issue

## 8) Frontend Checklist

- Always send bearer token for protected routes
- Store token securely (avoid localStorage in high-security contexts)
- Handle `401/403` globally and redirect to login
- Validate form inputs before API call
- Keep `issue_date` in `YYYY-MM-DD` format
- For verification page: accept `token_id` input and call public verify endpoint
- Display both final status (`is_verified`) and reason flags (`metadata_hash_matches`, `recomputed_hash_matches`)
