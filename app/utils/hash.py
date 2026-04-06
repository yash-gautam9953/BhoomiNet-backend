from eth_utils import keccak


def generate_hash(data: str) -> str:
    return "0x" + keccak(text=data).hex()
