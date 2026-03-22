# YAML

YAML, which stands for "YAML Ain't Markup Language," is a **human-readable** data serialization format designed for configuration files and data exchange between systems. Unlike XML or JSON, YAML relies on whitespace and indentation rather than brackets or tags, making it feel closer to natural **prose** than to code. Its design emphasizes readability and conciseness, which is why it has become the dominant format for **infrastructure-as-code** tooling across the DevOps ecosystem.

## YAML Document Structure

A YAML stream can contain one or more documents, each separated by **directive** markers. The `---` marker begins a new document, while `...` optionally ends one. A single file with no markers is treated as one **implicit** document.

```
+--------------------------------------------------+
|                  YAML Stream                      |
|                                                   |
|  +--------------------------------------------+  |
|  | --- (document start)                       |  |
|  |                                             |  |
|  |  key: value          # mapping              |  |
|  |  list:               # sequence             |  |
|  |    - item1                                  |  |
|  |    - item2                                  |  |
|  |                                             |  |
|  | ... (document end, optional)                |  |
|  +--------------------------------------------+  |
|                                                   |
|  +--------------------------------------------+  |
|  | --- (second document)                       |  |
|  |                                             |  |
|  |  another_key: another_value                 |  |
|  |                                             |  |
|  +--------------------------------------------+  |
+--------------------------------------------------+
```

## Basics of YAML

- YAML supports **scalar** types such as strings, integers, floats, booleans, null, and timestamps out of the box.
- Complex data is represented through **mappings** (key-value pairs, similar to dictionaries) and **sequences** (ordered lists of items).
- The syntax uses **indentation** instead of braces or brackets, producing a visual hierarchy that mirrors the data structure itself.
- YAML is a **superset** of JSON, meaning any valid JSON document is also valid YAML.

## YAML Syntax Rules

- **Indentation** controls the hierarchy; only spaces are allowed (tabs will cause a parse error), and the amount of indentation determines nesting depth.
- **Scalars** are single values such as `42`, `3.14`, `true`, `null`, or `"hello world"` and can be unquoted, single-quoted, or double-quoted.
- **Mappings** use a colon followed by a space (`: `) to separate keys from their values, forming associative pairs.
- **Sequences** begin each item with a hyphen and a space (`- `), creating ordered lists that a parser converts into arrays.
- Lines starting with the `#` symbol are treated as **comments** and ignored by the parser entirely.
- Multi-line strings use the `|` (literal block) character to preserve **newlines** or `>` (folded block) to collapse them into spaces.

## Example

```yaml
employee:
  name: John Doe
  age: 30
  department: Engineering
  address:
    street: 1234 Main St
    city: Anytown
    state: CA
    zipCode: "12345"          # quoted to prevent octal interpretation
  skills:
    - Java
    - C#
    - Python
  bio: |
    John is a senior engineer
    with 10 years of experience
    in distributed systems.
```

## Advanced YAML Features

### Anchors and Aliases

Anchors (`&`) let you mark a node so it can be **reused** elsewhere with an alias (`*`), eliminating duplication. The merge key (`<<`) combines an alias into a mapping, which is especially useful for sharing **defaults** across multiple blocks.

```yaml
defaults: &default_settings
  timeout: 30
  retries: 3
  log_level: info

production:
  <<: *default_settings        # merges all default keys
  log_level: warn              # overrides one value

staging:
  <<: *default_settings
  timeout: 60
```

### Multi-Document Streams

A single YAML file can hold several **independent** documents separated by `---`, which is useful for bundling related resources. Tools like `kubectl apply -f` natively handle multi-document files, deploying every **resource** in sequence.

```yaml
---
apiVersion: v1
kind: Namespace
metadata:
  name: app
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: app
data:
  LOG_LEVEL: "info"
```

## YAML Parsing Flow

```
  +------------------+     +------------------+     +------------------+
  |  Raw YAML Text   | --> |    Scanner /     | --> |    Parser /      |
  |  (UTF-8 stream)  |     |    Tokenizer     |     |    Event Stream  |
  +------------------+     +------------------+     +------------------+
                                                            |
                                                            v
                                                    +------------------+
                                                    |   Composer /     |
                                                    |   Node Graph     |
                                                    +------------------+
                                                            |
                                                            v
                                                    +------------------+
                                                    |   Constructor /  |
                                                    |   Native Objects |
                                                    |   (dict, list)   |
                                                    +------------------+
```

The scanner breaks raw text into **tokens** (indentation, scalars, indicators). The parser turns tokens into an **event** stream (MappingStart, Scalar, SequenceEnd, etc.). The composer assembles events into a node graph, and the constructor maps nodes to **native** language objects like dicts and lists.

## YAML in DevOps

### Kubernetes

Nearly every Kubernetes resource is declared in YAML, from **Deployments** and Services to ConfigMaps and Ingress rules. Operators write manifests that the API server parses, validates, and reconciles against the **desired** cluster state.

### Docker Compose

Docker Compose uses a `docker-compose.yml` file to define multi-container **applications**, describing services, networks, and volumes in one place. The declarative format lets teams spin up identical **environments** locally and in CI with a single command.

### CI/CD Pipelines

Platforms such as GitHub Actions, GitLab CI, and CircleCI all use YAML to describe **pipeline** stages, jobs, and steps. Defining CI/CD as YAML files stored alongside source code gives teams **version-controlled** build and deploy workflows.

## Benefits of YAML

- YAML's indentation-based syntax makes files immediately **readable** without prior knowledge of the format.
- The format can represent deeply nested and **complex** data structures without excessive punctuation.
- Virtually every modern DevOps tool provides first-class **support** for YAML configuration.
- Because YAML is a superset of JSON, existing JSON data can be used **directly** without conversion.

## Common Uses of YAML

- Infrastructure-as-code tools like Ansible, Kubernetes, and Terraform (via HCL-to-YAML bridges) rely on YAML for **configuration** management.
- Application settings and feature flags are often stored in YAML for easy **serialization** and human editing.
- CI/CD systems use YAML to define build **pipelines**, deployment steps, and environment matrices.

## YAML vs JSON

Both YAML and JSON serialize structured data, yet they target different **audiences**. YAML favors human authors who edit files by hand, while JSON favors machines that produce and consume data at **scale** over APIs.

| **Feature**               | **YAML**                                                                 | **JSON**                                                              |
|---------------------------|--------------------------------------------------------------------------|-----------------------------------------------------------------------|
| **Readability**           | Highly readable; indentation mirrors data hierarchy.                     | Readable, but bracket-heavy for deeply nested structures.             |
| **Comments**              | Supports `#` inline comments.                                           | No comment support in the specification.                              |
| **Data Types**            | Rich types: dates, timestamps, binary, sets, and custom tags.            | Limited to string, number, boolean, null, array, and object.          |
| **Multi-line Strings**    | Native literal (`\|`) and folded (`>`) block scalars.                    | Requires `\n` escape sequences inside a single string.                |
| **Anchors / Aliases**     | Supports `&` / `*` for node reuse.                                      | No equivalent; data must be duplicated.                               |
| **Multi-Document**        | One file can hold multiple `---`-separated documents.                    | One value per file.                                                   |
| **Parsing Complexity**    | Full spec is complex; multiple parser implementations vary.              | Simple grammar; parsers are fast and consistent.                      |
| **Native Browser Support**| Requires a library.                                                      | Built-in `JSON.parse()` / `JSON.stringify()`.                         |
| **File Extensions**       | `.yaml` or `.yml`                                                        | `.json`                                                               |
| **Trailing Commas**       | Not applicable (no commas).                                              | Not allowed; causes parse errors.                                     |
| **Security Surface**      | Larger attack surface due to tags and object instantiation.              | Minimal surface; data-only by design.                                 |
| **Primary Use Cases**     | Configuration files, infrastructure-as-code, CI/CD definitions.          | Web APIs, data interchange, client-server communication.              |

## Common Pitfalls

- The infamous **Norway** problem: the unquoted value `NO` is parsed as boolean `false` by YAML 1.1 parsers because `NO`, `Yes`, `on`, and `off` are all implicit booleans—country codes and abbreviations must be quoted.
- Implicit **type** coercion silently converts values like `1.0` to a float and `010` to an octal integer, producing unexpected results when strings were intended.
- Inconsistent **indentation** (mixing two-space and four-space levels, or accidentally using tabs) causes cryptic parse errors that are hard to trace in large files.
- Unquoted strings containing colons or special characters can cause the parser to misinterpret **structure**, splitting one value into a key-value pair.

## Security Considerations

- Many YAML libraries support **deserialization** of arbitrary objects via custom tags (e.g., `!!python/object`), which can lead to remote code execution if untrusted input is parsed.
- Always use a **safe** loader (e.g., `yaml.safe_load()` in Python or `YAML.safe_load` in Ruby) that restricts construction to basic data types only.
- Billion-laughs-style attacks exploit **anchors** and aliases to create exponential data expansion, consuming memory and CPU during parsing.
- Treat YAML configuration files with the same **rigor** as executable code: validate schemas, limit file sizes, and review changes in pull requests.

## Best Practices for YAML

- Pick either two or four spaces and enforce **consistent** indentation across the project with a linter such as `yamllint`.
- Always **quote** strings that could be misread as booleans, nulls, or numbers (e.g., `"yes"`, `"null"`, `"3.0"`).
- Use comments sparingly to explain **intent** rather than restating what the data already shows.
- Keep nesting to three or four levels at most; excessive **depth** makes files hard to read and diff.
- Run a YAML **validator** in CI to catch syntax errors before they reach production.
- Prefer `yaml.safe_load` or equivalent **safe** parsers to eliminate deserialization attack vectors.
- Store YAML files in version control and treat configuration changes as **code** that requires review.

