from typing import Any

import requests

from app.core.config import settings


PINATA_PIN_JSON_PATH = "/pinning/pinJSONToIPFS"


def upload_to_ipfs(metadata: dict[str, Any]) -> str:
    if not settings.PINATA_JWT:
        raise ValueError("PINATA_JWT is not configured")

    url = f"{settings.PINATA_BASE_URL.rstrip('/')}{PINATA_PIN_JSON_PATH}"
    headers = {
        "Authorization": f"Bearer {settings.PINATA_JWT}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, json=metadata, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError("Failed to upload metadata to Pinata") from exc

    body = response.json()
    cid = body.get("IpfsHash")
    if not cid:
        raise RuntimeError("Pinata response did not include IpfsHash")

    return cid
