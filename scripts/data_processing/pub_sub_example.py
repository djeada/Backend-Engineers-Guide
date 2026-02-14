"""
Publish/Subscribe pattern demonstration.

Implements a simple in-process pub/sub message broker to illustrate
the decoupled communication pattern used in systems like Kafka, Redis
Pub/Sub, and cloud messaging services.

No external dependencies required.

Usage:
    python pub_sub_example.py
"""

import threading
import time
from collections import defaultdict


class MessageBroker:
    """A simple thread-safe in-process pub/sub message broker."""

    def __init__(self):
        self._subscribers = defaultdict(list)
        self._lock = threading.Lock()

    def subscribe(self, topic: str, callback):
        """Register a callback for a given topic."""
        with self._lock:
            self._subscribers[topic].append(callback)

    def unsubscribe(self, topic: str, callback):
        """Remove a callback from a topic."""
        with self._lock:
            self._subscribers[topic].remove(callback)

    def publish(self, topic: str, message):
        """Deliver a message to all subscribers of a topic."""
        with self._lock:
            handlers = list(self._subscribers[topic])
        for handler in handlers:
            handler(topic, message)


# ---------- Subscriber helpers ----------

def make_logger(name: str):
    """Return a subscriber callback that prints received messages."""
    def handler(topic, message):
        print(f"  [{name}] received on '{topic}': {message}")
    return handler


# ---------- Main ----------

def main():
    broker = MessageBroker()

    print("=" * 55)
    print("Pub/Sub Pattern Demo")
    print("=" * 55)
    print()

    # Create named subscribers
    order_logger = make_logger("OrderService")
    inventory_logger = make_logger("InventoryService")
    analytics_logger = make_logger("AnalyticsService")

    # Subscribe to topics
    broker.subscribe("order.created", order_logger)
    broker.subscribe("order.created", inventory_logger)
    broker.subscribe("order.created", analytics_logger)
    broker.subscribe("order.shipped", order_logger)
    broker.subscribe("order.shipped", analytics_logger)

    # Publish messages
    print("Publishing 'order.created' ...")
    broker.publish("order.created", {"order_id": 101, "item": "Laptop", "qty": 1})
    print()

    print("Publishing 'order.shipped' ...")
    broker.publish("order.shipped", {"order_id": 101, "carrier": "FedEx"})
    print()

    # Unsubscribe demonstration
    print("Unsubscribing AnalyticsService from 'order.created' ...")
    broker.unsubscribe("order.created", analytics_logger)
    print()

    print("Publishing 'order.created' again ...")
    broker.publish("order.created", {"order_id": 102, "item": "Keyboard", "qty": 2})
    print()

    print("Key takeaway: Pub/Sub decouples publishers from subscribers,")
    print("allowing independent scaling and flexible message routing.")


if __name__ == "__main__":
    main()
