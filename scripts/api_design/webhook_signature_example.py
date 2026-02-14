"""
Webhook signature verification demonstration.

Shows how providers sign webhook payloads with HMAC and how receivers verify
the signature to reject tampered requests.

Usage:
    python webhook_signature_example.py
"""

import hashlib
import hmac


def sign_payload(secret: str, payload: str) -> str:
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()


def verify_signature(secret: str, payload: str, signature: str) -> bool:
    expected = sign_payload(secret, payload)
    return hmac.compare_digest(expected, signature)


def main():
    secret = "webhook-secret"
    payload = '{"event":"invoice.paid","id":"evt_123"}'
    signature = sign_payload(secret, payload)

    print("Valid payload check:", verify_signature(secret, payload, signature))
    tampered = '{"event":"invoice.refunded","id":"evt_123"}'
    print("Tampered payload check:", verify_signature(secret, tampered, signature))
    print("Key takeaway: verify webhook signatures before processing events.")


if __name__ == "__main__":
    main()
