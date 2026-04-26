## Authentication and Authorization

Authentication is the process of verifying **who a user is**. Authorization is the process of deciding **what that user is allowed to access or do**.

These two ideas are closely related, but they are not the same. A user may be authenticated successfully, meaning the system knows their identity, but still not be authorized to access a specific resource. For example, a normal user may be logged in but still not allowed to view an admin dashboard.

Authentication and authorization are usually enforced on the server side. The frontend can use authentication information to personalize the interface, but the backend must always make the final access-control decision.

### Auth Process

Authentication and authorization happen through cooperation between the client and server. The client sends credentials, cookies, or tokens. The server verifies identity, checks permissions, and returns either a successful response or an error.

```text
+-------------------------+               +-------------------------+
|                         |               |                         |
|      Client Side        |               |      Server Side        |
|  (Browser / Device)     |               |   (Web Application)     |
|                         |               |                         |
+-------------------------+               +-------------------------+
            |                                         |
            | 1. Request Auth (Login / Access Page)   |
            |---------------------------------------->|
            |                                         |
            |                         2. Authentication Check
            |                            - Verify identity
            |                            - Validate credentials
            |                                         |
            |<----------------------------------------|
            | 3. Response (Token / Session / Error)   |
            |                                         |
            |                         4. Authorization Check
            |                            - Validate permissions
            |                            - Control access
            |                                         |
```

Example login request:

```http
POST /login
Content-Type: application/json

{
  "email": "alice@example.com",
  "password": "correct-password"
}
```

Example successful output:

```json
{
  "status": "success",
  "user": {
    "id": "user-123",
    "role": "admin"
  }
}
```

Example failed output:

```json
{
  "status": "error",
  "message": "Invalid email or password"
}
```

In this flow, authentication happens when the server checks the user’s credentials. Authorization happens later when the server checks whether the authenticated user has permission to access a specific page, API endpoint, or action.

### Rendering in Frontend

The server may send user information, roles, or permissions to the client. The frontend can use this information to decide what to display. For example, an admin user might see an “Admin Panel” link, while a regular user would not.

However, hiding a button in the frontend is not real security by itself. A user could still manually send a request to the backend. The backend must always verify authorization before returning protected data or performing sensitive actions.

```text
+-------------------------+               +-------------------------+
|                         |               |                         |
|      Server Side        |               |      Client Side        |
|   (Web Application)     |               |   (Browser / Device)    |
|                         |               |                         |
+-------------------------+               +-------------------------+
            |                                         |
            | 1. Prepare Response                     |
            |    - User roles                         |
            |    - Permissions                        |
            |---------------------------------------->|
            |                                         |
            |                         2. Receive Data
            |                            - Auth info
            |                            - User state
            |                                         |
            |                         3. Process Data
            |                            - Evaluate permissions
            |                                         |
            |                         4. Render UI
            |                            - Show/hide components
            |                            - Personalize content
            |                                         |
```

Example server response:

```json
{
  "user": {
    "id": "user-123",
    "name": "Alice",
    "role": "admin",
    "permissions": ["read:users", "create:users", "delete:users"]
  }
}
```

Example frontend behavior:

```text
Show:
- Dashboard
- Profile
- Admin Panel
- User Management

Hide:
- Billing settings if user lacks billing permission
```

The frontend uses the returned auth data to improve the user experience. The backend still needs to enforce the same permissions on every protected API request.

### Frontend Auth Flow

A common frontend authentication flow uses secure cookies. After login, the server sends a cookie to the browser. The browser stores it and automatically includes it on future requests to the same site.

1. **Initial Page Load** The user opens the application for the first time.
2. **Sign-in** The user submits credentials, and the server verifies them.
3. **Cookie Storage** The server sends a secure cookie, and the browser stores it.
4. **Future Requests** The browser includes the cookie automatically on later requests.

Example login response with cookie:

```http
HTTP/1.1 200 OK
Set-Cookie: session_id=abc123; HttpOnly; Secure; SameSite=Lax

{
  "message": "Login successful"
}
```

Example future request:

```http
GET /profile HTTP/1.1
Host: example.com
Cookie: session_id=abc123
```

Example output:

```json
{
  "id": "user-123",
  "name": "Alice",
  "email": "alice@example.com"
}
```

The `HttpOnly` flag prevents JavaScript from reading the cookie. The `Secure` flag ensures the cookie is sent only over HTTPS. The `SameSite` setting helps reduce certain cross-site request risks.

### Server-Side User Authorization Flow

Server-side authorization protects resources and actions. The server should verify both identity and permissions for every protected request.

1. **Data Request** The user requests protected data or attempts a protected action.
2. **Request Processing** The server parses the cookie, token, or credential from the request.
3. **Identity Verification** The server identifies the user.
4. **Authorization Check** The server checks whether the user has permission.
5. **Response Handling** Authorized requests receive data. Unauthorized requests receive an error.

Example protected request:

```http
DELETE /users/user-456 HTTP/1.1
Host: example.com
Cookie: session_id=abc123
```

Example authorized output:

```json
{
  "status": "success",
  "message": "User deleted"
}
```

Example unauthorized output:

```json
{
  "status": "error",
  "code": "FORBIDDEN",
  "message": "You do not have permission to delete users"
}
```

In this example, the user may be logged in, but only users with the correct permission should be allowed to delete another user.

### Authentication Best Practices

Authentication systems protect sensitive accounts and data, so they should be designed carefully. A weak authentication system can expose users to account takeover, data theft, and privilege abuse.

Important practices include:

* Prefer modern auth methods such as OAuth, OpenID Connect, secure sessions, or properly implemented JWT flows over Basic Auth for most production systems.
* Use rate limiting, maximum retry limits, and account lockout or delay mechanisms to reduce brute-force attacks.
* Encrypt sensitive data in transit with HTTPS.
* Hash passwords with established password-hashing algorithms such as bcrypt, Argon2, or PBKDF2.
* Use established libraries and frameworks instead of writing token generation, password storage, or cryptographic logic from scratch.
* Never trust frontend-only checks for authorization.

Example rate-limit response:

```json
{
  "status": "error",
  "code": "TOO_MANY_LOGIN_ATTEMPTS",
  "message": "Please wait before trying again"
}
```

Example password-storage concept:

```text
Store password hash: yes
Store plain password: no
```

The server should never store users’ plain-text passwords. It should store only a secure password hash.

### JWT Best Practices

JWT stands for JSON Web Token. A JWT is a signed token that can carry claims such as user ID, role, issuer, audience, and expiration time. JWTs are often used in stateless authentication systems because the server can verify the token signature without looking up a session record.

JWTs should be treated carefully. They are signed, not automatically encrypted. Anyone who has the token may be able to read its payload unless encryption is used separately. For that reason, sensitive data should not be placed inside the JWT payload.

#### Secret Key

Use a complex, random secret key for signing JWTs. Weak or predictable secrets make tokens easier to forge.

```python
import os

jwt_secret_key = os.urandom(64)
```

Example output:

```text
Generated a 64-byte random secret key.
```

In production, the key should be stored securely using environment variables, a secrets manager, or a key management system. It should not be hard-coded in source code.

#### Algorithm Enforcement

Explicitly specify the allowed signing algorithm on the backend. Do not trust the algorithm specified in the JWT header without validation.

```python
import jwt

encoded_jwt = jwt.encode(
    {"some": "payload"},
    "secret",
    algorithm="HS256"
)
```

Example output:

```text
JWT created using the HS256 algorithm.
```

When decoding tokens, the server should also restrict accepted algorithms:

```python
decoded = jwt.decode(
    encoded_jwt,
    "secret",
    algorithms=["HS256"]
)
```

This prevents the backend from accepting unexpected or unsafe algorithms.

#### Token Expiration

JWTs should have expiration times. Short-lived tokens reduce the amount of time an attacker can use a stolen token.

```python
import datetime
import jwt

exp = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

encoded_jwt = jwt.encode(
    {"user_id": "user-123", "exp": exp},
    "secret",
    algorithm="HS256"
)
```

Example decoded payload:

```json
{
  "user_id": "user-123",
  "exp": 1713465600
}
```

The `exp` claim tells the server when the token should stop being accepted. For long-lived sessions, systems often use short-lived access tokens together with refresh tokens.

#### Payload Security

Avoid including sensitive data in the JWT payload. A JWT payload can often be decoded by anyone who has the token, even if they cannot modify it.

```python
user_data = {
    "user_id": user_id,
    "username": username
}

encoded_jwt = jwt.encode(user_data, "secret", algorithm="HS256")
```

Example safe payload:

```json
{
  "user_id": "user-123",
  "username": "alice"
}
```

Example unsafe payload:

```json
{
  "user_id": "user-123",
  "password": "secret",
  "credit_card": "4111111111111111"
}
```

The unsafe payload should never be used. Sensitive values should stay on the server or be protected with appropriate encryption and access controls.

#### Size Limitation

Keep JWT payloads small. Large tokens increase request header size because the token is usually sent with every request.

```python
minimal_payload = {
    "user_id": user_id
}

encoded_jwt = jwt.encode(minimal_payload, "secret", algorithm="HS256")
```

Example request with JWT:

```http
GET /profile HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

A minimal token is easier to transmit and less likely to exceed proxy, gateway, or server header limits.

### OAuth Best Practices

OAuth is commonly used to grant applications access to resources without directly sharing user passwords with the application. It is often used for “Sign in with Google,” third-party integrations, delegated API access, and authorization flows between services.

For user login, OAuth is often paired with OpenID Connect, which adds identity information on top of OAuth.

#### URI Validation

Redirect URI validation is essential. The server should allow only pre-registered redirect URIs. This prevents attackers from redirecting authorization codes or tokens to malicious domains.

```python
allowed_uris = [
    "https://example.com/callback",
    "https://anotherdomain.com/auth"
]

if redirect_uri not in allowed_uris:
    raise ValueError("Invalid redirect URI")
```

Example invalid output:

```json
{
  "error": "Invalid redirect URI"
}
```

The check should happen on the server side. Client-side validation is not enough.

#### Code Exchange

Prefer the authorization code flow over direct token grants. Avoid `response_type=token` for modern web applications. The authorization code flow is safer because the client receives a short-lived code and exchanges it for tokens through a controlled backend or secure client flow.

```python
from requests_oauthlib import OAuth2Session

oauth = OAuth2Session(
    client_id,
    redirect_uri=redirect_uri,
    scope=scopes
)

authorization_url, state = oauth.authorization_url(authorization_base_url)
```

Example authorization URL output:

```text
https://auth.example.com/authorize?response_type=code&client_id=abc123&state=random-state
```

After the user approves access, the authorization server redirects back with a code. The application then exchanges that code for tokens.

#### CSRF Prevention

Use a random `state` parameter in OAuth flows to help prevent CSRF attacks. The application should store the state value before redirecting the user and verify it when the callback returns.

```python
import os

state = os.urandom(32).hex()
authorization_url = f"{authorization_base_url}?response_type=code&state={state}"
```

Example callback:

```http
GET /callback?code=auth-code-123&state=stored-random-state
```

Example validation output:

```json
{
  "stateValid": true,
  "message": "OAuth callback accepted"
}
```

If the returned state does not match the stored state, the server should reject the callback.

#### Scope Management

Scopes define what access an application is requesting. For example, one scope may allow reading a profile, while another may allow writing data.

Applications should request only the scopes they need. Servers should validate requested scopes and reject unknown or excessive scopes.

```python
default_scopes = ["read", "write"]

if not all(scope in default_scopes for scope in requested_scopes):
    raise ValueError("Invalid scope requested")
```

Example valid scope request:

```json
{
  "requestedScopes": ["read"],
  "status": "accepted"
}
```

Example invalid scope request:

```json
{
  "requestedScopes": ["admin", "delete_all"],
  "status": "rejected",
  "reason": "Invalid scope requested"
}
```

Careful scope management limits damage if a token is leaked or misused. Applications should follow the principle of least privilege and request only the access they truly need.
