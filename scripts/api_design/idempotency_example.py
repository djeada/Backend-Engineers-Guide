"""
Idempotency key demonstration for retry-safe POST operations.

Simulates an API endpoint that creates payments. Without an idempotency key,
retries can create duplicate payments. With an idempotency key, retries return
the original response.

Usage:
    python idempotency_example.py
"""

import uuid


class PaymentAPI:
    def __init__(self):
        self.payments = {}
        self.idempotent_responses = {}

    def create_payment(self, amount: int, idempotency_key: str | None = None) -> dict:
        if idempotency_key and idempotency_key in self.idempotent_responses:
            return self.idempotent_responses[idempotency_key]

        payment_id = str(uuid.uuid4())
        response = {"payment_id": payment_id, "amount": amount, "status": "created"}
        self.payments[payment_id] = response

        if idempotency_key:
            self.idempotent_responses[idempotency_key] = response

        return response


def main():
    api = PaymentAPI()

    print("1) Retry without idempotency key (duplicate side effects)")
    first = api.create_payment(100)
    retry = api.create_payment(100)
    print(f"   First response: {first}")
    print(f"   Retry response: {retry}")
    print(f"   Total payments stored: {len(api.payments)}\n")

    print("2) Retry with idempotency key (safe retry)")
    key = "payment-123-attempt-1"
    first = api.create_payment(200, idempotency_key=key)
    retry = api.create_payment(200, idempotency_key=key)
    print(f"   First response: {first}")
    print(f"   Retry response: {retry}")
    print(f"   Total payments stored: {len(api.payments)}\n")

    print("Key takeaway: idempotency keys make retrying non-idempotent operations safe.")


if __name__ == "__main__":
    main()
