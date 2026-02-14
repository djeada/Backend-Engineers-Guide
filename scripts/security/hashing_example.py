"""
Password hashing and verification demonstration.

Shows how to securely hash and verify passwords using Python's built-in
hashlib and secrets modules – the same principles behind bcrypt/scrypt
used in production systems.

No external dependencies required.

Usage:
    python hashing_example.py
"""

import hashlib
import hmac
import os
import secrets
import time


def hash_password(password: str) -> str:
    """
    Hash a password with a random salt using PBKDF2-HMAC-SHA256.

    Returns a string in the format: salt_hex$iterations$hash_hex
    """
    salt = os.urandom(16)
    iterations = 100_000
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return f"{salt.hex()}${iterations}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Verify a password against a stored hash string."""
    salt_hex, iterations_str, hash_hex = stored.split("$")
    salt = bytes.fromhex(salt_hex)
    iterations = int(iterations_str)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return hmac.compare_digest(dk.hex(), hash_hex)


def demo_hashing():
    """Demonstrate password hashing and verification."""
    print("=" * 55)
    print("1) Password Hashing (PBKDF2-HMAC-SHA256)")
    print("=" * 55)

    password = "S3cureP@ss!"
    stored = hash_password(password)
    print(f"  Password:    {password}")
    print(f"  Stored hash: {stored[:60]}...")
    print()
    print(f"  Verify correct password:   {verify_password(password, stored)}")
    print(f"  Verify wrong   password:   {verify_password('wrong', stored)}")
    print()


def demo_timing_safe_comparison():
    """Show the importance of constant-time comparison."""
    print("=" * 55)
    print("2) Constant-Time Comparison")
    print("=" * 55)

    secret_token = secrets.token_hex(32)
    correct = secret_token
    wrong = "a" * len(secret_token)

    # hmac.compare_digest runs in constant time
    result_correct = hmac.compare_digest(secret_token, correct)
    result_wrong = hmac.compare_digest(secret_token, wrong)

    print(f"  Token:   {secret_token[:20]}...")
    print(f"  Correct: {result_correct}")
    print(f"  Wrong:   {result_wrong}")
    print()
    print("  hmac.compare_digest prevents timing attacks by always")
    print("  taking the same amount of time regardless of input.")
    print()


def demo_token_generation():
    """Show secure random token generation."""
    print("=" * 55)
    print("3) Secure Token Generation")
    print("=" * 55)

    print(f"  Hex token (32 bytes):  {secrets.token_hex(32)}")
    print(f"  URL-safe token:        {secrets.token_urlsafe(32)}")
    print(f"  Random integer:        {secrets.randbelow(1_000_000)}")
    print()


def main():
    demo_hashing()
    demo_timing_safe_comparison()
    demo_token_generation()
    print("Key takeaway: Never store plaintext passwords. Use salted hashes")
    print("with a slow KDF (PBKDF2/bcrypt/scrypt) and constant-time comparison.")


if __name__ == "__main__":
    main()
