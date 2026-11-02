import json
import time
import hmac
import base64
import binascii
import hashlib

from src.config import SECRET_KEY


ALGORITHM = "HS256"
TOKEN_LIFETIME = 3600


def b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.b64decode(
        data + padding,
        altchars=b"-_",
        validate=True,
    )


def create_jwt(user_id: int) -> str:
    header = {
        "alg": ALGORITHM,
        "typ": "JWT",
    }

    payload = {
        "sub": str(user_id),
        "iat": int(time.time()),
        "exp": int(time.time()) + TOKEN_LIFETIME,
    }

    header_encoded = b64encode(json.dumps(header).encode())
    payload_encoded = b64encode(json.dumps(payload).encode())

    message = f"{header_encoded}.{payload_encoded}"

    signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        message.encode("ascii"),
        hashlib.sha256
    ).digest()

    return f"{message}.{b64encode(signature)}"


def verify_jwt(token: str) -> dict:
    try:
        if len(token) > 4096:
            raise ValueError("Token too long")

        header_part, payload_part, signature_part = token.split(".")

        header = json.loads(b64decode(header_part))
        if not isinstance(header, dict):
            raise ValueError("Invalid header")

        if header.get("alg") != ALGORITHM or header.get("typ") != "JWT":
            raise ValueError("Invalid algorithm or type")

        message = f"{header_part}.{payload_part}"

        expected_signature = hmac.new(
            SECRET_KEY.encode("utf-8"),
            message.encode("ascii"),
            hashlib.sha256
        ).digest()

        actual_signature = b64decode(signature_part)

        if not hmac.compare_digest(expected_signature, actual_signature):
            raise ValueError("Invalid signature")

        payload = json.loads(b64decode(payload_part))

        if not isinstance(payload, dict):
            raise ValueError("Invalid payload")

        exp = payload.get("exp")
        sub = payload.get("sub")

        if type(exp) is not int or exp <= time.time():
            raise ValueError("Token expired or invalid")

        if not isinstance(sub, str) or not sub:
            raise ValueError("Invalid subject")

        return payload

    except (ValueError, TypeError, UnicodeError, binascii.Error) as exc:
        raise ValueError("Invalid JWT") from exc
