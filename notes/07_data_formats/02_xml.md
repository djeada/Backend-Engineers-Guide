# XML Format

XML, or Extensible Markup Language, is a **W3C**-standardized markup language designed to encode documents in a format that is both human-readable and machine-readable. Unlike HTML, which has a fixed set of tags, XML lets you define your own **vocabulary** of elements to represent arbitrary data structures. It remains widely used in enterprise web services, configuration files, and document interchange where strict schema validation matters.

## Basics of XML

1. **Elements** are the building blocks of every XML document; they can nest other elements, hold text content, or carry attributes.
2. **Attributes** provide supplementary metadata about an element, written as name-value pairs inside the opening tag.
3. **Text Content** is the actual data between an opening and closing tag, which the parser delivers to the application.
4. **Comments** follow the `<!-- ... -->` syntax and are ignored by parsers but useful for **documenting** intent inside the file.
5. **Processing Instructions** such as `<?xml-stylesheet ... ?>` give directives to the application **consuming** the document.

## XML Syntax Rules

1. **XML Declaration** a document should begin with `<?xml version="1.0" encoding="UTF-8"?>` to declare the version and **character** encoding.
2. **Single Root** every well-formed document must have exactly one root element that **wraps** all other elements.
3. **Case Sensitivity** tag names are case-sensitive, so `<Name>` and `<name>` are treated as **different** elements.
4. **Proper Nesting** elements must close in the reverse order they were opened, ensuring a **balanced** tree.
5. **Quoted Attributes** attribute values must always be enclosed in single or **double** quotation marks.
6. **Special Characters** reserved characters like `<`, `>`, and `&` must be written as **entity** references (`&lt;`, `&gt;`, `&amp;`).

## Document Tree Structure

Every XML document forms a logical **tree** rooted at the single root element. Understanding this tree is key to querying and transforming XML.

```
document
└── employee
    ├── name
    │   └── "John"
    ├── address
    │   ├── street
    │   │   └── "1234.."
    │   ├── city
    │   │   └── "Any.."
    │   └── zipCode
    │       └── "12345"
    └── skills
        ├── skill
        │   └── "Java"
        └── skill
            └── "C#"
```

- Each **node** in the tree is either an element, a text node, an attribute, or a processing instruction.
- **Parent-child** relationships mirror the nesting of tags in the source document.
- **Sibling** elements share the same parent and are ordered by their position in the document.

## Example

Below is a complete XML document demonstrating **nested** elements, attributes, and namespaces:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<employee id="E1001" xmlns:hr="http://example.com/hr">
  <name>John Doe</name>
  <age>30</age>
  <hr:department code="ENG">Engineering</hr:department>
  <address>
    <street>1234 Main St</street>
    <city>Anytown</city>
    <state>CA</state>
    <zipCode>12345</zipCode>
  </address>
  <skills>
    <skill level="senior">Java</skill>
    <skill level="mid">C#</skill>
    <skill level="junior">Python</skill>
  </skills>
</employee>
```

## XML Namespaces

When multiple XML vocabularies are combined in one document, **name collisions** can occur. Namespaces solve this by qualifying element and attribute names with a URI.

- A **declaration** like `xmlns:hr="http://example.com/hr"` binds the prefix `hr` to a unique namespace URI.
- The **default** namespace (`xmlns="..."`) applies to all unprefixed child elements within its scope.
- Namespace URIs do not need to **resolve** to an actual web page; they serve only as unique identifiers.
- **Prefixed** elements such as `<hr:department>` clearly indicate which vocabulary the element belongs to.

```xml
<root xmlns:app="http://example.com/app"
      xmlns:db="http://example.com/db">
  <app:config>
    <db:connection host="localhost" port="5432"/>
  </app:config>
</root>
```

## DTD vs XSD (Schema Validation)

Validation ensures an XML document conforms to a **predefined** structure. Two main technologies exist:

```
  XML Document
       |
       v
+---------------+      +---------------------+
|  Well-formed? |--No->|  Reject (parse err) |
+-------+-------+      +---------------------+
        | Yes
        v
+---------------+      +---------------------+
| Valid against |--No->| Reject (validation  |
| DTD or XSD?   |      |        error)       |
+-------+-------+      +---------------------+
        | Yes
        v
  Accept Document
```

- **DTD** (Document Type Definition) uses a non-XML syntax to define allowed elements, attributes, and their **ordering** constraints.
- **XSD** (XML Schema Definition) is itself written in XML and supports rich **data types** like integers, dates, and custom patterns.
- XSD offers **namespace-aware** validation, making it the preferred choice for complex, multi-vocabulary documents.
- DTD remains useful for **simple** documents where lightweight validation is sufficient.

| Feature              | DTD                        | XSD                              |
|----------------------|----------------------------|----------------------------------|
| Syntax               | Non-XML, **compact** grammar | XML-based                        |
| Data Types           | Limited (CDATA, ID, IDREF) | Rich (int, date, **regex**, etc.) |
| Namespace Support    | None                       | Full **namespace** awareness      |
| Extensibility        | Low                        | High (inheritance, **groups**)    |
| Industry Adoption    | Legacy systems             | Modern **enterprise** standards   |

## XPath Basics

XPath is a query language for selecting **nodes** from an XML document tree. It is used heavily in XSLT, XQuery, and many programming APIs.

- `/employee/name` selects the `<name>` child using an **absolute** path from the root.
- `//skill` selects every `<skill>` element anywhere in the document with a **recursive** descent.
- `//skill[@level='senior']` filters elements by **attribute** value using a predicate.
- `..` navigates to the **parent** of the current node, similar to filesystem paths.
- `text()` returns the **text** content within the matched element.

```
XPath: /employee/address/city

  <employee>                    
       |                        
    <address>        <-- step 2  
       |                        
     <city>          <-- step 3  
       |                        
    "Anytown"        <-- result  
```

## Parsing XML: DOM vs SAX

Two dominant strategies exist for reading XML, each with distinct **memory** and performance trade-offs.

```
            XML Document
                 |
       +---------+---------+
       |                   |
       v                   v
  DOM Parser           SAX Parser
  (tree in RAM)        (event stream)
       |                   |
       v                   v
  Full node tree      Callbacks fired
  available for       for each start-tag,
  random access       end-tag, and text
```

- **DOM** (Document Object Model) loads the entire document into memory as a tree, allowing **random** access to any node at any time.
- **SAX** (Simple API for XML) reads the document sequentially and fires events, using **constant** memory regardless of file size.
- DOM is ideal for **small-to-medium** documents that need frequent reads, updates, or XPath queries.
- SAX is preferred for **large** files or streaming scenarios where only a subset of elements is needed.
- **StAX** (Streaming API for XML) is a pull-based alternative to SAX that gives the application **control** over when to read the next event.

| Aspect             | DOM                          | SAX                           | StAX                          |
|--------------------|------------------------------|-------------------------------|-------------------------------|
| Memory             | **High** (full tree in RAM)  | **Low** (event-driven)        | **Low** (pull-based)          |
| Access Pattern     | Random                       | **Sequential** only           | Sequential only               |
| Ease of Use        | Simple **navigation** API    | Callback-heavy                | Iterator-style                |
| Write Support      | Yes (modify and **serialize**)| Read-only                    | Read and write                |
| Best For           | Small docs, **editing**      | Large docs, filtering         | **Streaming** pipelines       |

## Security Considerations (XXE)

XML parsers can be exploited if they process **untrusted** input without proper safeguards. The most critical vulnerability is XML External Entity (XXE) injection.

```
  Attacker crafts XML with external entity:

  <?xml version="1.0"?>
  <!DOCTYPE foo [
    <!ENTITY xxe SYSTEM "file:///etc/passwd">
  ]>
  <data>&xxe;</data>

  Parser Flow:
  1. Parser reads DTD   -->  sees ENTITY declaration
  2. Resolves "file://" -->  reads /etc/passwd from disk
  3. Substitutes &xxe;  -->  sensitive data in <data> output
```

- **XXE** (XML External Entity) attacks trick the parser into reading local files or making **network** requests on the server's behalf.
- **Billion Laughs** (entity expansion) defines recursively nested entities that expand into enormous strings, causing **denial-of-service**.
- Always **disable** external entity resolution and DTD processing when parsing untrusted XML.
- In Java, set `XMLConstants.FEATURE_SECURE_PROCESSING` to **true** and disallow doctype declarations.
- In Python, use `defusedxml` instead of the standard library's `xml.etree` for **safe** parsing of untrusted data.

## Benefits of XML

1. **Self-descriptive** tags make the document readable without external documentation, unlike binary formats.
2. **Platform-independent** text encoding ensures data can be exchanged between any operating system or programming language.
3. **Unicode** support allows representation of virtually any human language or symbol set.
4. **Extensible** vocabularies let each domain define its own element names without modifying the core specification.
5. **Mature tooling** across every major language provides robust parsers, validators, and transformation engines.

## Common Uses of XML

- **SOAP Web Services** rely on XML envelopes to encode requests and responses in enterprise **integration** layers.
- **Configuration Files** for tools like Maven (`pom.xml`), Spring, and Android manifests use XML for **structured** settings.
- **Document Formats** such as XHTML, SVG, and Office Open XML (`.docx`) are built on **XML** foundations.
- **RSS and Atom** feeds syndicate web content using well-defined XML **schemas**.
- **Data Interchange** between heterogeneous systems in healthcare (HL7), finance (FIX/FIXML), and government often mandates **XML**.

## Best Practices for XML

1. **Meaningful Names** – choose element and attribute names that clearly describe their content, improving long-term **maintainability**.
2. **Shallow Nesting** – keep the tree depth reasonable to avoid unnecessary complexity and simplify **XPath** queries.
3. **Schema Validation** – always validate documents against an XSD to catch structural errors **before** they reach application logic.
4. **Namespace Discipline** – declare namespaces at the root element and use consistent prefixes to prevent **collision** across vocabularies.
5. **Secure Parsing** – disable external entities and DTD processing on every parser that handles **untrusted** input.
6. **Encoding Declaration** – explicitly set `encoding="UTF-8"` in the XML declaration to avoid **character** misinterpretation.
7. **Prefer Elements Over Attributes** – use attributes for metadata like IDs and elements for **data** to keep the document intuitive.
8. **Version Your Schemas** – include a version attribute or namespace so consumers can handle **backward-compatible** changes gracefully.
