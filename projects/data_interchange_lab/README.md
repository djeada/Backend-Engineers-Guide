# Data Interchange Lab

This mini-project groups the format demos into a short lab on **serialization trade-offs** and **binary efficiency**.

## What you will practice

1. How the same data looks in JSON, XML, and YAML
2. Why binary encodings often use less space than text formats
3. How varints, field tags, and wire types shape compact protocols

## Quick start

Run these commands from the repository root:

```bash
python scripts/data_formats/format_conversion.py
python scripts/data_formats/protocol_buffer_example.py
```

## Suggested walkthrough

### 1. Compare text-based formats

```bash
python scripts/data_formats/format_conversion.py
```

Focus on:

- how JSON balances readability with broad ecosystem support
- why XML is more verbose but explicitly structured
- why YAML is friendly for configs but sensitive to indentation

Read next:

- [`scripts/data_formats/format_conversion.py`](../../scripts/data_formats/format_conversion.py)
- [`notes/07_data_formats/03_json.md`](../../notes/07_data_formats/03_json.md)
- [`notes/07_data_formats/02_xml.md`](../../notes/07_data_formats/02_xml.md)
- [`notes/07_data_formats/04_yaml.md`](../../notes/07_data_formats/04_yaml.md)

### 2. Compare binary serialization

```bash
python scripts/data_formats/protocol_buffer_example.py
```

Focus on:

- how field numbers and wire types become compact binary tags
- why varints shrink small integers
- how binary payload size and speed compare with JSON

Read next:

- [`scripts/data_formats/protocol_buffer_example.py`](../../scripts/data_formats/protocol_buffer_example.py)
- [`notes/07_data_formats/01_protocol_buffers.md`](../../notes/07_data_formats/01_protocol_buffers.md)

## Extension ideas

- Add a repeated nested field to the binary format example
- Measure how format size changes as payloads grow
- Convert the same object graph into more complex XML attributes and nested nodes
