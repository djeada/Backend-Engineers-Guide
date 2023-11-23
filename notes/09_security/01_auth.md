# Understanding Authentication and Authorization (Auth) in Web Applications
Authentication is the process of verifying a user's identity, while authorization is the management of access rights to resources.

## Auth Process
Authentication and authorization occur server-side, with client-side requests contributing to the process.

```
+-------------------------+               +------------------------+
|                         |               |                        |
|     Client Side         |               |      Server Side       |
| (User's Device/Browser) |               |   (Web Application)    |
|                         |               |                        |
+-------------------------+               +------------------------+
        ||                                            ||
        ||                                            ||
        \/                                            \/
+----------------------+                  +-------------------------+
|                      |                  |                         |
|  User Requests Auth  |                  |  Authentication Check   |
| (Login, Access Page) |----------------> |  Verifies User Identity |
|                      |                  |                         |
+----------------------+                  +-------------------------+
        ||                                             ||
        ||                                             ||
        \/                                             \/
+----------------------+                  +------------------------+
|                      |                  |                        |
|   Server Responds    |                  |  Authorization Check   |
| (Token, Permissions) | <--------------- |  Controls Resource     |
|                      |                  |  Access                |
+----------------------+                  +------------------------+
```

## Rendering in Frontend
The server responds with data that includes user auth information, which the client uses to render appropriate views.

```
+---------------------+                   +-------------------------+
|                     |                   |                         |
|    Server Side      |                   |    Client Side          |
| (Web Application)   |                   | (User's Device/Browser) |
|                     |                   |                         |
+---------------------+                   +-------------------------+
         ||                                             ||
         ||                                             ||
         ||  Sends Data with Auth Info                  ||
         \/                                             \/
+---------------------+                   +-------------------------+
|                     |                   |                         |
|  Prepares Response  |                   |  Receives Data and      |
|  with Auth Details  |-----------------> |  Auth Information       |
|  (e.g., User Roles, |                   |                         |
|   Permissions)      |                   |                         |
+---------------------+                   +-------------------------+
                                                       ||
                                                       || Process Data
                                                       \/
                                          +----------------------+
                                          |                      |
                                          |  Render Appropriate  |
                                          |  Views Based on      |
                                          |  Auth Information    |
                                          |                      |
                                          +----------------------+
```

## Frontend Auth Flow

1. **Initial Page Load**: User opens the page for the first time.
2. **Sign-in**: User signs in, and the server sends a secure cookie.
3. **Cookie Storage**: Client stores the secure cookie.
4. **Future Requests**: Subsequent requests include the secure cookie for authentication.

## Server-side User Authorization Flow

1. **Data Request**: User requests data from the server.
2. **Request Processing**: Server parses the user's cookie from the request.
3. **Identity Verification**: Server checks the cookie to identify the user.
4. **Authorization Check**: Server verifies if the user is authorized for the requested action.
5. **Response Handling**: Authorized requests receive data; unauthorized attempts get an error response.

## Authentication Best Practices

- **Auth Methods**: Prefer JWT or OAuth over Basic Auth.
- **Security Measures**: Implement maximum retry limits and account lock features against brute-force attacks.
- **Data Protection**: Encrypt sensitive data.
- **Framework Utilization**: Use established libraries and frameworks for token generation and password storage.

## JWT Best Practices

### Secret Key
Utilize a complex, random secret key for JWT.

```python
import os
jwt_secret_key = os.urandom(64)
```

### Algorithm Enforcement
Explicitly specify the backend algorithm (e.g., HS256 or RS256) and avoid trusting the algorithm specified in the JWT header.

```python
import jwt
encoded_jwt = jwt.encode({'some': 'payload'}, 'secret', algorithm='HS256')
```

### Token Expiration
Set short expiration times for tokens to reduce the risk of misuse.

```python
import datetime
exp = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
encoded_jwt = jwt.encode({'exp': exp}, 'secret', algorithm='HS256')
```

### Payload Security
Avoid including sensitive data in the JWT payload.

```python
user_data = {'user_id': user_id, 'username': username} # Do not include sensitive info
encoded_jwt = jwt.encode(user_data, 'secret', algorithm='HS256')
```

### Size Limitation
Limit the data in JWT to prevent exceeding header size limits.

```python
minimal_payload = {'user_id': user_id}
encoded_jwt = jwt.encode(minimal_payload, 'secret', algorithm='HS256')
```

## OAuth Best Practices

### URI Validation
Perform server-side validation of redirect URIs, only allowing whitelisted URLs.

```python
allowed_uris = ['https://example.com/callback', 'https://anotherdomain.com/auth']
if redirect_uri not in allowed_uris:
    raise ValueError('Invalid redirect URI')
```

### Code Exchange

Prefer using code exchange rather than direct token grants (avoid response_type=token).

```python
from requests_oauthlib import OAuth2Session
oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)
authorization_url, state = oauth.authorization_url(authorization_base_url)
# Redirect user to authorization_url and then exchange code for token
```

### CSRF Prevention

Utilize a random hash state parameter in OAuth authentication to prevent CSRF.

```python
import os
state = os.urandom(32).hex()
authorization_url = f"{authorization_base_url}?response_type=code&state={state}"
# Store 'state' and validate it when receiving the callback
```

### Scope Management

Clearly define default scopes and validate scope parameters for each OAuth application.

```python
default_scopes = ['read', 'write']
if not all(scope in default_scopes for scope in requested_scopes):
    raise ValueError('Invalid scope requested')
```
