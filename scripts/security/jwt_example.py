"""
JWT-like token creation and verification demonstration.

Implements a simplified JSON Web Token (JWT) with a header, payload,
and HMAC-SHA256 signature using only the standard library (hmac, hashlib,
base64, json).  Shows token creation, verification, expiration checking,
and tamper detection — without any real JWT library.

No external dependencies required.

Usage:
    python jwt_example.py
"""

import base64
import hashlib
import hmac
import json
import time


# ---------- Base64url helpers (RFC 7515) ----------

def b64url_encode(data: bytes) -> str:
    """Base64url-encode bytes and strip padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64url_decode(s: str) -> bytes:
    """Base64url-decode a string, restoring padding as needed."""
    padding = 4 - len(s) % 4
    if padding != 4:
        s += "=" * padding
    return base64.urlsafe_b64decode(s)


# ---------- Token creation ----------

def create_token(payload: dict, secret: str, ttl_seconds: int = 300) -> str:
    """
    Create a JWT-like token string: header.payload.signature

    *payload* is the claims dict; *secret* is the HMAC key.
    An 'exp' claim is added automatically based on *ttl_seconds*.
    """
    header = {"alg": "HS256", "typ": "JWT"}

    payload = dict(payload)
    payload["iat"] = int(time.time())
    payload["exp"] = payload["iat"] + ttl_seconds

    header_b64 = b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = b64url_encode(json.dumps(payload, separators=(",", ":")).encode())

    signing_input = f"{header_b64}.{payload_b64}"
    signature = hmac.new(
        secret.encode(), signing_input.encode(), hashlib.sha256
    ).digest()
    sig_b64 = b64url_encode(signature)

    return f"{signing_input}.{sig_b64}"


# ---------- Token verification ----------

def verify_token(token: str, secret: str):
    """
    Verify a JWT-like token.  Returns (valid, payload_or_error).

    Checks:
      1. Structure (three dot-separated parts)
      2. HMAC-SHA256 signature
      3. Expiration ('exp' claim)
    """
    parts = token.split(".")
    if len(parts) != 3:
        return False, "Invalid token structure (expected 3 parts)"

    header_b64, payload_b64, sig_b64 = parts

    # Re-compute signature
    signing_input = f"{header_b64}.{payload_b64}"
    expected_sig = hmac.new(
        secret.encode(), signing_input.encode(), hashlib.sha256
    ).digest()
    actual_sig = b64url_decode(sig_b64)

    if not hmac.compare_digest(expected_sig, actual_sig):
        return False, "Signature verification failed (token may be tampered)"

    # Decode payload
    payload = json.loads(b64url_decode(payload_b64))

    # Check expiration
    exp = payload.get("exp")
    if exp is not None and time.time() > exp:
        return False, "Token has expired"

    return True, payload


def decode_token_parts(token: str):
    """Decode and return (header, payload, signature_hex) without verification."""
    parts = token.split(".")
    header = json.loads(b64url_decode(parts[0]))
    payload = json.loads(b64url_decode(parts[1]))
    sig_hex = b64url_decode(parts[2]).hex()
    return header, payload, sig_hex


# ---------- Main ----------

def main():
    secret = "super-secret-key-for-demo"

    print("=" * 60)
    print("JWT-Like Token Demo (HMAC-SHA256)")
    print("=" * 60)
    print()

    # --- Create a token ---
    print("1) Creating a token")
    print("-" * 60)
    claims = {"sub": "user-42", "role": "admin", "name": "Alice"}
    token = create_token(claims, secret, ttl_seconds=3600)
    print(f"  Token ({len(token)} chars):")
    print(f"  {token}")
    print()

    header, payload, sig_hex = decode_token_parts(token)
    print(f"  Header    : {header}")
    print(f"  Payload   : {payload}")
    print(f"  Signature : {sig_hex[:40]}...")
    print()

    # --- Verify valid token ---
    print("2) Verifying valid token")
    print("-" * 60)
    valid, result = verify_token(token, secret)
    print(f"  Valid   : {valid}")
    print(f"  Payload : {result}")
    print()

    # --- Tamper detection ---
    print("3) Tamper detection")
    print("-" * 60)
    parts = token.split(".")
    # Modify the payload (change role to "superadmin")
    tampered_payload = dict(payload)
    tampered_payload["role"] = "superadmin"
    tampered_b64 = b64url_encode(
        json.dumps(tampered_payload, separators=(",", ":")).encode()
    )
    tampered_token = f"{parts[0]}.{tampered_b64}.{parts[2]}"
    print(f"  Original role : {payload['role']}")
    print(f"  Tampered role : {tampered_payload['role']}")
    valid, result = verify_token(tampered_token, secret)
    print(f"  Valid         : {valid}")
    print(f"  Error         : {result}")
    print()

    # --- Wrong secret ---
    print("4) Wrong secret key")
    print("-" * 60)
    valid, result = verify_token(token, "wrong-secret")
    print(f"  Valid : {valid}")
    print(f"  Error : {result}")
    print()

    # --- Expired token ---
    print("5) Expired token")
    print("-" * 60)
    expired_token = create_token(claims, secret, ttl_seconds=-1)
    valid, result = verify_token(expired_token, secret)
    print(f"  Valid : {valid}")
    print(f"  Error : {result}")
    print()

    print("Key takeaway: JWTs use base64url-encoded header and payload with")
    print("an HMAC signature to create stateless, tamper-evident tokens that")
    print("servers can verify without a database lookup.")


if __name__ == "__main__":
    main()
