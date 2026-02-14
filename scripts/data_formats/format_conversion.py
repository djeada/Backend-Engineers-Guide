"""
Data format conversion demonstration.

Converts the same data structure between JSON, XML, and YAML (via a
minimal serialiser) to illustrate the trade-offs discussed in the
data-formats notes.

No external dependencies required (YAML output uses a simple serialiser
so PyYAML is not needed).

Usage:
    python format_conversion.py
"""

import json
import xml.etree.ElementTree as ET
from xml.dom import minidom


# ---------- Sample data ----------

SAMPLE = {
    "server": {
        "host": "0.0.0.0",
        "port": 8080,
        "debug": False,
    },
    "database": {
        "engine": "postgresql",
        "name": "app_db",
        "pool_size": 5,
    },
    "features": ["caching", "rate_limiting", "logging"],
}


# ---------- JSON ----------

def to_json(data: dict) -> str:
    return json.dumps(data, indent=2)


def from_json(text: str) -> dict:
    return json.loads(text)


# ---------- XML ----------

def _dict_to_xml(tag: str, data) -> ET.Element:
    elem = ET.Element(tag)
    if isinstance(data, dict):
        for key, val in data.items():
            child = _dict_to_xml(key, val)
            elem.append(child)
    elif isinstance(data, list):
        for item in data:
            child = ET.SubElement(elem, "item")
            child.text = str(item)
    else:
        elem.text = str(data)
    return elem


def to_xml(data: dict, root_tag: str = "config") -> str:
    root = _dict_to_xml(root_tag, data)
    rough = ET.tostring(root, encoding="unicode")
    return minidom.parseString(rough).toprettyxml(indent="  ")


def from_xml(text: str) -> dict:
    """Minimal XML-to-dict parser for demonstration purposes."""
    root = ET.fromstring(text)

    def _parse(element):
        children = list(element)
        if not children:
            return element.text
        if all(c.tag == "item" for c in children):
            return [c.text for c in children]
        return {c.tag: _parse(c) for c in children}

    return {root.tag: _parse(root)}


# ---------- YAML (minimal, no dependency) ----------

def to_yaml(data, indent: int = 0) -> str:
    """Minimal YAML-like serialiser (handles dicts, lists, scalars)."""
    lines = []
    prefix = "  " * indent
    if isinstance(data, dict):
        for key, val in data.items():
            if isinstance(val, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.append(to_yaml(val, indent + 1))
            else:
                lines.append(f"{prefix}{key}: {_yaml_scalar(val)}")
    elif isinstance(data, list):
        for item in data:
            lines.append(f"{prefix}- {_yaml_scalar(item)}")
    else:
        lines.append(f"{prefix}{_yaml_scalar(data)}")
    return "\n".join(lines)


def _yaml_scalar(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return f'"{value}"' if " " in value or not value else value
    return str(value)


# ---------- Main ----------

def main():
    print("=" * 55)
    print("Data Format Conversion Demo")
    print("=" * 55)

    # JSON
    print("\n--- JSON ---")
    json_text = to_json(SAMPLE)
    print(json_text)
    roundtrip = from_json(json_text)
    assert roundtrip == SAMPLE, "JSON round-trip failed"
    print("(round-trip OK)")

    # XML
    print("\n--- XML ---")
    xml_text = to_xml(SAMPLE)
    print(xml_text)

    # YAML
    print("--- YAML ---")
    yaml_text = to_yaml(SAMPLE)
    print(yaml_text)

    print()
    print("Key takeaway: JSON is compact and widely supported; XML is verbose")
    print("but self-describing; YAML is human-friendly but indentation-sensitive.")


if __name__ == "__main__":
    main()
