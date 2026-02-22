"""
Symmetric encryption demonstration using the standard library.

Shows AES-like XOR-based encryption to illustrate the encrypt/decrypt
round-trip, key generation, and the importance of initialization vectors.
A real backend would use a proper library (e.g. cryptography), but this
script uses only the standard library to show the core concepts.

No external dependencies required.

Usage:
    python encryption_example.py
"""

import hashlib
import hmac
import os


def derive_key(password: str, salt: bytes, length: int = 32) -> bytes:
    """Derive a fixed-length key from a password using PBKDF2-HMAC-SHA256."""
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000, dklen=length)


def xor_bytes(data: bytes, key_stream: bytes) -> bytes:
    """XOR each byte of *data* with the repeating *key_stream*."""
    return bytes(b ^ key_stream[i % len(key_stream)] for i, b in enumerate(data))


def encrypt(plaintext: bytes, key: bytes) -> tuple[bytes, bytes]:
    """Encrypt *plaintext* with a random IV and return (iv, ciphertext)."""
    iv = os.urandom(16)
    key_stream = hashlib.sha256(key + iv).digest()
    ciphertext = xor_bytes(plaintext, key_stream)
    return iv, ciphertext


def decrypt(iv: bytes, ciphertext: bytes, key: bytes) -> bytes:
    """Decrypt *ciphertext* using the same key and IV."""
    key_stream = hashlib.sha256(key + iv).digest()
    return xor_bytes(ciphertext, key_stream)


def main():
    print("=" * 60)
    print("Symmetric Encryption Concepts Demo")
    print("=" * 60)
    print()

    password = "s3cret-backend-key"
    salt = os.urandom(16)
    key = derive_key(password, salt)
    print(f"  Password:  {password}")
    print(f"  Salt:      {salt.hex()}")
    print(f"  Derived key (hex): {key.hex()}")
    print()

    messages = [
        b"Hello, backend world!",
        b'{"user_id": 42, "role": "admin"}',
        b"Sensitive payment token: tok_abc123",
    ]

    print("-" * 60)
    print("Encrypt then decrypt round-trip")
    print("-" * 60)
    for msg in messages:
        iv, ct = encrypt(msg, key)
        recovered = decrypt(iv, ct, key)
        print(f"\n  Plaintext:  {msg.decode()}")
        print(f"  IV:         {iv.hex()}")
        print(f"  Ciphertext: {ct.hex()[:48]}…")
        print(f"  Decrypted:  {recovered.decode()}")
        assert recovered == msg, "round-trip failed!"

    print()
    print("-" * 60)
    print("IV prevents identical ciphertexts")
    print("-" * 60)
    msg = b"same plaintext"
    iv1, ct1 = encrypt(msg, key)
    iv2, ct2 = encrypt(msg, key)
    print(f"\n  Same message encrypted twice:")
    print(f"  Ciphertext 1: {ct1.hex()}")
    print(f"  Ciphertext 2: {ct2.hex()}")
    print(f"  Equal? {ct1 == ct2}  (should be False)")

    print()
    print("-" * 60)
    print("HMAC integrity check")
    print("-" * 60)
    iv, ct = encrypt(b"important data", key)
    tag = hmac.new(key, iv + ct, "sha256").hexdigest()
    print(f"\n  HMAC tag: {tag}")
    valid = hmac.compare_digest(tag, hmac.new(key, iv + ct, "sha256").hexdigest())
    print(f"  Verified: {valid}")

    tampered = bytearray(ct)
    tampered[0] ^= 0xFF
    bad_tag = hmac.new(key, iv + bytes(tampered), "sha256").hexdigest()
    print(f"\n  Tampered HMAC: {bad_tag}")
    print(f"  Matches original? {hmac.compare_digest(tag, bad_tag)} (should be False)")

    print()
    print("Key takeaway: symmetric encryption protects data at rest and in")
    print("transit; always use a unique IV per message and verify integrity")
    print("with an HMAC or authenticated encryption mode.")


if __name__ == "__main__":
    main()
