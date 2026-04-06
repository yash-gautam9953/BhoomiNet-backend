from app.core.config import settings


def build_metadata_qr_payload(cid: str) -> str:
    return f"{settings.IPFS_GATEWAY_BASE_URL.rstrip('/')}/{cid}"
