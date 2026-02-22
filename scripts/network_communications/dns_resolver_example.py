"""
Simplified DNS resolution walkthrough.

Simulates the hierarchical DNS lookup process (root -> TLD -> authoritative)
using in-memory zone tables.  Demonstrates caching, TTLs, and how recursive
queries traverse the DNS tree.

No external dependencies required.

Usage:
    python dns_resolver_example.py
"""

import time


class DNSRecord:
    def __init__(self, name: str, rtype: str, value: str, ttl: int = 300):
        self.name = name
        self.rtype = rtype
        self.value = value
        self.ttl = ttl

    def __repr__(self):
        return f"{self.name} {self.rtype} {self.value} TTL={self.ttl}"


class DNSZone:
    """A DNS zone that answers queries for records it holds."""

    def __init__(self, name: str):
        self.name = name
        self.records: list[DNSRecord] = []

    def add(self, record: DNSRecord):
        self.records.append(record)

    def query(self, qname: str, qtype: str) -> DNSRecord | None:
        for r in self.records:
            if r.name == qname and r.rtype == qtype:
                return r
        return None


class DNSCache:
    """Simple cache that respects TTL."""

    def __init__(self):
        self._store: dict[tuple[str, str], tuple[DNSRecord, float]] = {}

    def get(self, qname: str, qtype: str) -> DNSRecord | None:
        key = (qname, qtype)
        if key in self._store:
            record, expires = self._store[key]
            if time.monotonic() < expires:
                return record
            del self._store[key]
        return None

    def put(self, record: DNSRecord):
        key = (record.name, record.rtype)
        self._store[key] = (record, time.monotonic() + record.ttl)


class RecursiveResolver:
    """Walks the DNS hierarchy: root -> TLD -> authoritative."""

    def __init__(self, root_zone: DNSZone, tld_zones: dict[str, DNSZone],
                 auth_zones: dict[str, DNSZone]):
        self.root = root_zone
        self.tld_zones = tld_zones
        self.auth_zones = auth_zones
        self.cache = DNSCache()

    def resolve(self, qname: str, qtype: str = "A") -> DNSRecord | None:
        cached = self.cache.get(qname, qtype)
        if cached:
            print(f"    [cache HIT] {cached}")
            return cached

        parts = qname.rsplit(".", 1)
        tld = parts[-1] if len(parts) > 1 else parts[0]

        print(f"    -> root server: referral to .{tld} TLD")
        tld_zone = self.tld_zones.get(tld)
        if not tld_zone:
            print(f"    <- NXDOMAIN (unknown TLD .{tld})")
            return None

        domain = qname.split(".")[-2] + "." + tld if "." in qname else qname
        ns_record = tld_zone.query(domain, "NS")
        if not ns_record:
            print(f"    <- NXDOMAIN (no NS for {domain})")
            return None
        print(f"    -> TLD .{tld}: NS is {ns_record.value}")

        auth_zone = self.auth_zones.get(domain)
        if not auth_zone:
            print(f"    <- SERVFAIL (no authoritative zone for {domain})")
            return None

        answer = auth_zone.query(qname, qtype)
        if answer:
            print(f"    -> authoritative: {answer}")
            self.cache.put(answer)
            return answer
        print(f"    <- NXDOMAIN ({qname} not found)")
        return None


def main():
    print("=" * 60)
    print("DNS Resolution Walkthrough")
    print("=" * 60)
    print()

    root = DNSZone("root")
    root.add(DNSRecord("com", "NS", "tld-com-server"))
    root.add(DNSRecord("org", "NS", "tld-org-server"))

    com_tld = DNSZone(".com")
    com_tld.add(DNSRecord("example.com", "NS", "ns1.example.com"))
    com_tld.add(DNSRecord("shop.com", "NS", "ns1.shop.com"))

    org_tld = DNSZone(".org")
    org_tld.add(DNSRecord("wiki.org", "NS", "ns1.wiki.org"))

    example_zone = DNSZone("example.com")
    example_zone.add(DNSRecord("example.com", "A", "93.184.216.34", ttl=3600))
    example_zone.add(DNSRecord("api.example.com", "A", "93.184.216.35", ttl=300))
    example_zone.add(DNSRecord("example.com", "MX", "mail.example.com", ttl=3600))

    shop_zone = DNSZone("shop.com")
    shop_zone.add(DNSRecord("shop.com", "A", "198.51.100.10", ttl=600))

    wiki_zone = DNSZone("wiki.org")
    wiki_zone.add(DNSRecord("wiki.org", "A", "203.0.113.50", ttl=1800))

    resolver = RecursiveResolver(
        root,
        tld_zones={"com": com_tld, "org": org_tld},
        auth_zones={
            "example.com": example_zone,
            "shop.com": shop_zone,
            "wiki.org": wiki_zone,
        },
    )

    queries = [
        ("example.com", "A"),
        ("api.example.com", "A"),
        ("example.com", "A"),
        ("shop.com", "A"),
        ("wiki.org", "A"),
        ("example.com", "MX"),
        ("unknown.com", "A"),
    ]

    for qname, qtype in queries:
        print(f"  resolve({qname}, {qtype}):")
        result = resolver.resolve(qname, qtype)
        if result:
            print(f"    => {result.value}")
        else:
            print("    => (no answer)")
        print()

    print("Key takeaway: DNS resolution is a hierarchical lookup from root")
    print("to TLD to authoritative servers; caching with TTLs avoids")
    print("repeating the full chain for every query.")


if __name__ == "__main__":
    main()
