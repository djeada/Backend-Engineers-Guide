# Security Controls Lab

This mini-project groups core security demos into a lab on **credential safety**, **token verification**, **confidentiality**, and **abuse prevention**.

## What you will practice

1. How password hashing and constant-time comparison protect credentials
2. How JWT-like tokens are signed, verified, and expired
3. How symmetric encryption uses derived keys, IVs, and integrity checks
4. How rate limiting reduces abuse while still allowing short bursts

## Quick start

Run all demos at once:

```bash
cd projects/security_controls_lab
./run.sh
```

Or run individual demos from the repository root:

```bash
python scripts/security/hashing_example.py
python scripts/security/jwt_example.py
python scripts/security/encryption_example.py
python scripts/security/rate_limiter_example.py
```

## Suggested walkthrough

### 1. Hash passwords safely

```bash
python scripts/security/hashing_example.py
```

Focus on:

- why salts and slow KDFs make brute-force attacks harder
- why constant-time comparison matters for secret validation
- why secure random tokens should come from dedicated APIs

Read next:

- [`scripts/security/hashing_example.py`](../../scripts/security/hashing_example.py)
- [`notes/08_security/`](../../notes/08_security/)

### 2. Verify signed tokens

```bash
python scripts/security/jwt_example.py
```

Focus on:

- how a header, payload, and signature form a token
- why tampering breaks signature verification
- why expiration is part of token validation, not an optional check

Read next:

- [`scripts/security/jwt_example.py`](../../scripts/security/jwt_example.py)
- [`notes/08_security/01_auth.md`](../../notes/08_security/01_auth.md)

### 3. Encrypt and authenticate data

```bash
python scripts/security/encryption_example.py
```

Focus on:

- how key derivation turns a password into a stable encryption key
- why a unique IV prevents repeated ciphertext for the same plaintext
- why integrity checks are required in addition to encryption

Read next:

- [`scripts/security/encryption_example.py`](../../scripts/security/encryption_example.py)
- [`notes/08_security/04_security_best_practices_and_measures.md`](../../notes/08_security/04_security_best_practices_and_measures.md)

### 4. Throttle abusive traffic

```bash
python scripts/security/rate_limiter_example.py
```

Focus on:

- how token buckets allow bursts but enforce a steady average rate
- how cooldown periods refill capacity
- where per-user or per-IP limits fit in backend systems

Read next:

- [`scripts/security/rate_limiter_example.py`](../../scripts/security/rate_limiter_example.py)

## Extension ideas

- Add refresh-token logic to the JWT demo
- Compare token-bucket and fixed-window limiting strategies
- Replace the toy encryption routine with an authenticated-encryption library in a real service
