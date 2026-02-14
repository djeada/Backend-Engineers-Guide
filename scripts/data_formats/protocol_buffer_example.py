"""
Protocol-buffer-like binary serialization demonstration.

Implements a minimal binary encoding/decoding scheme using the struct
module that illustrates core protobuf concepts: field tags, wire types,
and variable-length integer encoding (varint).  Compares the size and
speed of this compact binary format against JSON serialization.

No external dependencies required.

Usage:
    python protocol_buffer_example.py
"""

import json
import struct
import time


# ---------- Wire types (subset of real protobuf) ----------

WIRE_VARINT = 0  # int / bool
WIRE_FIXED64 = 1  # double / fixed64
WIRE_LENGTH_DELIMITED = 2  # string / bytes


# ---------- Varint encoding / decoding ----------

def encode_varint(value: int) -> bytes:
    """Encode an unsigned integer as a variable-length byte sequence."""
    parts = []
    while value > 0x7F:
        parts.append((value & 0x7F) | 0x80)
        value >>= 7
    parts.append(value & 0x7F)
    return bytes(parts)


def decode_varint(data: bytes, offset: int):
    """Decode a varint starting at *offset*; return (value, new_offset)."""
    result = 0
    shift = 0
    while True:
        byte = data[offset]
        result |= (byte & 0x7F) << shift
        offset += 1
        if (byte & 0x80) == 0:
            break
        shift += 7
    return result, offset


# ---------- Field tag helpers ----------

def make_tag(field_number: int, wire_type: int) -> int:
    """Combine a field number and wire type into a single tag value."""
    return (field_number << 3) | wire_type


def parse_tag(tag: int):
    """Split a tag into (field_number, wire_type)."""
    return tag >> 3, tag & 0x07


# ---------- Encoder ----------

def encode_message(fields: dict) -> bytes:
    """
    Encode a dict of {field_number: (wire_type, value)} into binary.

    Supported wire types:
        WIRE_VARINT           – value is a non-negative int
        WIRE_FIXED64          – value is a float (encoded as double)
        WIRE_LENGTH_DELIMITED – value is a str or bytes
    """
    buf = bytearray()
    for field_number in sorted(fields):
        wire_type, value = fields[field_number]
        tag = make_tag(field_number, wire_type)
        buf.extend(encode_varint(tag))

        if wire_type == WIRE_VARINT:
            buf.extend(encode_varint(value))
        elif wire_type == WIRE_FIXED64:
            buf.extend(struct.pack("<d", value))
        elif wire_type == WIRE_LENGTH_DELIMITED:
            if isinstance(value, str):
                value = value.encode("utf-8")
            buf.extend(encode_varint(len(value)))
            buf.extend(value)
        else:
            raise ValueError(f"Unknown wire type {wire_type}")

    return bytes(buf)


# ---------- Decoder ----------

def decode_message(data: bytes) -> dict:
    """Decode binary data back into {field_number: (wire_type, value)}."""
    fields = {}
    offset = 0
    while offset < len(data):
        tag, offset = decode_varint(data, offset)
        field_number, wire_type = parse_tag(tag)

        if wire_type == WIRE_VARINT:
            value, offset = decode_varint(data, offset)
        elif wire_type == WIRE_FIXED64:
            value = struct.unpack_from("<d", data, offset)[0]
            offset += 8
        elif wire_type == WIRE_LENGTH_DELIMITED:
            length, offset = decode_varint(data, offset)
            value = data[offset : offset + length]
            try:
                value = value.decode("utf-8")
            except UnicodeDecodeError:
                pass
            offset += length
        else:
            raise ValueError(f"Unknown wire type {wire_type} at offset {offset}")

        fields[field_number] = (wire_type, value)

    return fields


# ---------- Demo helpers ----------

def build_user_message(user_id: int, name: str, email: str, score: float):
    """Build a protobuf-style field dict for a 'User' message."""
    return {
        1: (WIRE_VARINT, user_id),
        2: (WIRE_LENGTH_DELIMITED, name),
        3: (WIRE_LENGTH_DELIMITED, email),
        4: (WIRE_FIXED64, score),
    }


def build_user_json(user_id: int, name: str, email: str, score: float):
    """Build the equivalent JSON representation."""
    return json.dumps(
        {"user_id": user_id, "name": name, "email": email, "score": score}
    )


# ---------- Main ----------

def main():
    print("=" * 60)
    print("Protocol-Buffer-Like Binary Serialization Demo")
    print("=" * 60)
    print()

    # --- Varint encoding ---
    print("1) Variable-length integer encoding (varint)")
    print("-" * 60)
    for num in [1, 127, 128, 300, 100_000]:
        encoded = encode_varint(num)
        decoded, _ = decode_varint(encoded, 0)
        print(f"  {num:>7}  ->  {encoded.hex(' ')}  ({len(encoded)} byte(s))  "
              f"->  decoded: {decoded}")
    print()

    # --- Encode / decode a message ---
    print("2) Encoding a 'User' message")
    print("-" * 60)
    fields = build_user_message(42, "Alice Smith", "alice@example.com", 98.6)
    binary = encode_message(fields)
    json_str = build_user_json(42, "Alice Smith", "alice@example.com", 98.6)

    print(f"  Fields       : {fields}")
    print(f"  Binary ({len(binary):>3}B) : {binary.hex(' ')}")
    print(f"  JSON  ({len(json_str):>3}B) : {json_str}")
    print()

    decoded_fields = decode_message(binary)
    print("  Decoded fields:")
    wire_names = {WIRE_VARINT: "varint", WIRE_FIXED64: "fixed64",
                  WIRE_LENGTH_DELIMITED: "length-delimited"}
    for fn in sorted(decoded_fields):
        wt, val = decoded_fields[fn]
        print(f"    field {fn}  [{wire_names[wt]:<17}]  =  {val}")
    print()

    # --- Size comparison ---
    print("3) Size comparison: binary vs JSON")
    print("-" * 60)
    savings = (1 - len(binary) / len(json_str)) * 100
    print(f"  Binary size : {len(binary)} bytes")
    print(f"  JSON size   : {len(json_str)} bytes")
    print(f"  Savings     : {savings:.1f}%")
    print()

    # --- Speed comparison ---
    print("4) Speed comparison (10,000 encode/decode cycles)")
    print("-" * 60)
    iterations = 10_000

    start = time.perf_counter()
    for _ in range(iterations):
        b = encode_message(fields)
        decode_message(b)
    binary_time = time.perf_counter() - start

    start = time.perf_counter()
    for _ in range(iterations):
        j = json.dumps({"user_id": 42, "name": "Alice Smith",
                        "email": "alice@example.com", "score": 98.6})
        json.loads(j)
    json_time = time.perf_counter() - start

    print(f"  Binary : {binary_time:.4f}s")
    print(f"  JSON   : {json_time:.4f}s")
    ratio = json_time / binary_time if binary_time else float("inf")
    print(f"  Ratio  : binary is {ratio:.2f}x vs JSON")
    print()

    print("Key takeaway: Binary encodings like Protocol Buffers use field")
    print("tags, wire types, and varint encoding to produce compact, fast")
    print("serialization — often significantly smaller and faster than JSON.")


if __name__ == "__main__":
    main()
