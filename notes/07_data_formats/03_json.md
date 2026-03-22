# JSON

JSON, or JavaScript Object Notation, is a lightweight data-interchange format that is easy for humans to read and write and easy for machines to parse and generate. Despite originating from JavaScript, the format is completely **language** independent and supported by virtually every modern programming language. Its simplicity and direct mapping to common data structures like hash maps and arrays have made it the dominant format for APIs, configuration files, and data exchange on the web.

```
+----- JSON Document ----------------------------------------+
|                                                            |
|  {                                                         |
|    "key": "string value",     <-- String                   |
|    "count": 42,               <-- Number                   |
|    "active": true,            <-- Boolean                  |
|    "tags": ["a", "b"],        <-- Array                    |
|    "nested": { ... },         <-- Object                   |
|    "empty": null              <-- Null                     |
|  }                                                         |
|                                                            |
+------------------------------------------------------------+
```

## Data Types

JSON defines six **primitive** value types that combine to represent nearly any data structure:

- A **string** is a sequence of Unicode characters wrapped in double quotes, supporting escape sequences like `\n` and `\uXXXX`.
- A **number** can be an integer or floating-point value, but JSON does not distinguish between the two at the format level.
- A **boolean** is represented by the literal tokens `true` or `false`.
- A **null** value represents the intentional absence of any data.
- An **object** is an unordered collection of key-value pairs enclosed in curly braces `{}`, where every key must be a string.
- An **array** is an ordered list of values enclosed in square brackets `[]`, and its elements can be of any type including mixed types.

## Syntax Rules

- Data is written as **name/value** pairs separated by a colon (e.g., `"name": "John"`).
- Pairs and array elements are separated by **commas**, and trailing commas are not permitted.
- Objects are wrapped in curly **braces** `{}` and arrays in square brackets `[]`.
- All keys must be enclosed in **double** quotes; single quotes are invalid JSON.
- Whitespace outside of strings is **insignificant** and used only for readability.
- The format does not support **comments**, though conventions like `_comment` keys or JSON5 extensions exist as workarounds.

## Example

Here is a JSON document showing nested objects, arrays, and multiple data types working together:

```json
{
  "employee": {
    "name": "John Doe",
    "age": 30,
    "active": true,
    "department": "Engineering",
    "address": {
      "street": "1234 Main St",
      "city": "Anytown",
      "state": "CA",
      "zipCode": "12345"
    },
    "skills": ["Java", "C#", "Python"],
    "certifications": null
  }
}
```

## Parsing Flow

When a backend service receives a JSON payload, the text goes through a well-defined **parsing** pipeline before the application can use the data:

```
 Raw bytes        Decode to       Tokenize         Build AST /       Application
 from network --> UTF-8 text -->  (lexer) -------> data structure --> logic
                                   |                    |
                           Split into tokens:     Map to native
                           { , } , [ , ] ,        types (dict,
                           "key", : , value        list, int, str)
```

- The parser first **decodes** the byte stream, which must be valid UTF-8 (RFC 8259 dropped support for UTF-16/32).
- A lexer then splits the text into **tokens** such as braces, colons, strings, and literals.
- The parser assembles tokens into an in-memory **tree** or native data structure like a dictionary or map.
- Most languages provide a built-in `json` module or popular libraries like **Jackson** (Java), `serde_json` (Rust), or `encoding/json` (Go).

## Benefits of JSON

- The syntax is **readable** by humans without any special tooling or training.
- Parsers exist for every major language, making JSON highly **portable** across technology stacks.
- The format is **lightweight** compared to XML, producing smaller payloads and faster transmission.
- JSON maps **directly** to native data structures like dictionaries and lists, reducing serialization complexity.

## Common Uses

- REST and GraphQL APIs use JSON as the **default** request and response body format.
- Tools like VS Code, ESLint, and Terraform rely on JSON for **configuration** files.
- Document databases like MongoDB store records as **BSON**, a binary-encoded superset of JSON.
- JSON Web Tokens (JWT) encode authentication **claims** as Base64-encoded JSON objects.

## JSON Schema

JSON Schema is a vocabulary that lets you **annotate** and validate the structure of JSON documents. It acts like a contract between producers and consumers of an API.

```
 JSON Document                    JSON Schema
 +------------------+             +---------------------------+
 | {                |   validate  | {                         |
 |   "age": 30     | ----------> |   "type": "object",       |
 | }                |   against   |   "properties": {         |
 +------------------+             |     "age": {              |
        |                         |       "type": "integer",  |
        v                         |       "minimum": 0        |
   Valid / Invalid                |     }                     |
                                  |   },                      |
                                  |   "required": ["age"]     |
                                  | }                         |
                                  +---------------------------+
```

- A schema defines the expected **types**, required fields, and value constraints for each property.
- The `required` keyword lists fields that **must** be present in a valid document.
- Constraints like `minimum`, `maxLength`, and `pattern` enforce **bounds** on individual values.
- The `$ref` keyword allows schemas to reference **reusable** definitions, keeping large schemas maintainable.
- Tools like AJV (JavaScript), jsonschema (Python), and Everit (Java) perform **validation** at runtime or during CI pipelines.

## JSON Streaming (NDJSON / JSON Lines)

Standard JSON requires loading the entire document into memory before parsing, which is problematic for large datasets. Newline-Delimited JSON (NDJSON), also called JSON **Lines**, solves this by placing one valid JSON object per line:

```
{"event": "click", "ts": 1700000001}
{"event": "view",  "ts": 1700000002}
{"event": "click", "ts": 1700000003}
```

- Each line is a self-contained JSON **object**, so the parser can process records one at a time.
- This format enables **streaming** ingestion, where producers append lines and consumers tail the file.
- Log aggregation systems like Fluentd and Logstash commonly use NDJSON for structured **log** output.
- NDJSON is well suited for **pipelines** where tools like `jq`, `grep`, or `awk` process records line by line.

## Common Pitfalls

### Number Precision

- JSON numbers have no size **limit** in the spec, but most parsers map them to IEEE 754 double-precision floats.
- Doubles safely represent integers only up to 2^53, so large IDs like `9007199254740993` may lose **precision** silently.
- A common workaround is to encode large numbers as **strings** (e.g., `"id": "9007199254740993"`) and parse them explicitly.

### Encoding Issues

- RFC 8259 mandates **UTF-8** encoding; other encodings like Latin-1 will cause parsing failures.
- Characters like `\u0000` (null byte) can break parsers or cause **security** issues in some languages.
- Emoji and supplementary Unicode characters outside the BMP must be represented as **surrogate** pairs in escape sequences (e.g., `\uD83D\uDE00`).

### Structural Mistakes

- Trailing **commas** after the last element in an object or array are the most common syntax error.
- Using single **quotes** instead of double quotes is valid JavaScript but invalid JSON.
- Forgetting that object keys are **unordered** can lead to bugs when code depends on insertion order.

## Performance Considerations

- Parsing speed varies significantly across **libraries**; benchmarks show simdjson and sonic-json can be 5-10x faster than standard library parsers.
- For high-throughput services, consider binary formats like **Protocol Buffers** or MessagePack to reduce serialization overhead.
- Minifying JSON by removing whitespace can reduce payload **size** by 10-20% for typical API responses.
- Enabling gzip or Brotli **compression** on HTTP responses often reduces JSON payloads by 70-90%.
- Reusing parser instances and pre-allocated **buffers** avoids garbage collection pressure in hot paths.
- Lazy or streaming parsers like **SAX-style** JSON readers (e.g., `ijson` in Python) keep memory usage constant for large documents.

## JSON vs XML

Both JSON and XML are text-based data interchange formats, but they serve different **niches**. JSON dominates in web APIs and microservices, while XML remains common in enterprise systems, document markup, and contexts that require schemas with namespaces.

| **Feature**            | **JSON (JavaScript Object Notation)**                                                                 | **XML (eXtensible Markup Language)**                                    |
|------------------------|-------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| **Format**             | Lightweight and text-based.                                                                           | Verbose and document-based format.                                      |
| **Readability**        | Generally easier to read due to its concise format.                                                   | Less human-readable due to more verbose nature.                         |
| **Data Types**         | Supports string, number, array, boolean, object, and null.                                            | Does not have built-in data types; everything is a string.              |
| **Parsing**            | Native support in browsers; fast parsers in every language.                                           | Requires dedicated XML parsers (DOM, SAX, StAX).                       |
| **Size**               | Typically smaller, making it faster to transmit.                                                      | Larger file sizes due to additional markup and closing tags.            |
| **Schema Validation**  | JSON Schema (draft standard, widely adopted).                                                         | XSD and DTD (mature, W3C standards).                                    |
| **Extensibility**      | Limited; fixed structure of objects and arrays.                                                        | Highly extensible with custom tags, namespaces, and attributes.         |
| **Metadata**           | Limited support; metadata mixed into the data structure.                                              | Excellent support via attributes and processing instructions.           |
| **Comments**           | Does not support comments natively.                                                                   | Supports comments with `<!-- -->` syntax.                               |
| **Security**           | Less attack surface; no entity expansion vulnerabilities.                                             | Prone to XXE (XML External Entity) and billion-laughs attacks.          |
| **Array Support**      | First-class arrays with square brackets `[]`.                                                         | No built-in array; relies on repeated child elements.                   |
| **Namespace Support**  | No namespace mechanism.                                                                               | Full namespace support for avoiding naming collisions.                  |
| **Use Cases**          | Web APIs, microservices, configuration files, mobile apps.                                            | Enterprise integrations (SOAP), document markup, RSS/Atom feeds.        |

## Best Practices

- Choose **descriptive** key names that clearly convey the meaning of each field (e.g., `createdAt` over `ca`).
- Keep nesting depth **shallow**; deeply nested structures are harder to query, validate, and evolve.
- Always **validate** incoming JSON against a schema before processing it in business logic.
- Use consistent **casing** conventions for keys, such as camelCase for JavaScript-centric APIs or snake_case for Python-centric ones.
- Treat JSON parsing as an **untrusted** input boundary and enforce size limits to prevent denial-of-service via oversized payloads.
- Prefer `null` over **missing** keys when a field has no value, so consumers can distinguish "absent" from "not provided".
- Version your JSON APIs by including a schema **version** field or using URL-based versioning to manage breaking changes.
