## Data Conversion and Sharing

Encoding means changing data into a format that can be sent over a network or saved in a file. It's important because it lets different machines and systems talk to each other by changing data into a shared format.

### Popular Encodings

* JSON (JavaScript Object Notation) and XML are common encodings for sending data. They're popular because they're easy to read, simple to understand, and work with many programming languages.
* Sometimes, custom binary encoding is better. Binary encodings can save space and make data transfer faster.

### Custom Binary Encoding

* Custom binary encodings are helpful when you have lots of unique data.
* One big advantage of custom binary encodings is they can use less space.
* To get this efficiency, custom binary encodings often need a preset schema for the data. The schema explains the data structure and the types of fields.
* Having a collection of schemas can help track compatibility and allow for checking data types during the programming process.

### Compatibility

* When making a schema, make sure the applications using it can work with old and new versions.
* To keep working with older versions, if you add a new field to a schema, it can't be required (or it needs a default value).
* This is important so older versions of the application can still understand the data sent with the new schema.
