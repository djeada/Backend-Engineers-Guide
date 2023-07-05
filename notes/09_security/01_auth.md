## Understanding Auth

Authentication and authorization, or "auth", are key security features in web applications. Authentication verifies user identity, while authorization controls access to resources.

## Auth Process

Auth occurs server-side, but client-side requests play a role in authentication and authorization.

## Rendering in Frontend

The server responds to client requests with data that includes user authentication and authorization information. The client renders views based on this data.

## Auth Flow on Frontend

1. User opens page for the first time.
2. User signs in, server sends secure cookie.
3. Client stores secure cookie.
4. Future requests include secure cookie.

## Server-side User Authorization Flow

1. User requests data.
2. Server receives request, parses cookie.
3. Server checks user cookie for identity.
4. Server checks user's authorization for action.
5. If authorized, server sends data; otherwise, returns error.

## Authentication Best Practices

* Use JWT or OAuth instead of Basic Auth.
* Implement maximum retry and jail features to prevent brute-force attacks.
* Encrypt sensitive data.
* Use standard libraries and frameworks for token generation and password storage.

## JWT Best Practices

* Use a random, complex JWT secret key.
* Don't extract the algorithm from the header; enforce backend algorithm (HS256 or RS256).
* Set short token expiration.
* Avoid sensitive data in JWT payload.
* Limit data in JWT to avoid exceeding header size limits.

## OAuth Best Practices

* Validate redirect URI server-side, allowing only whitelisted URLs.
* Exchange for code, not tokens (avoid response_type=token).
* Use a random hash state parameter to prevent CSRF attacks during OAuth authentication.
* Define default scope and validate scope parameters for each application.

## Auth Story Example

* Alice finds a task management website.
* She logs in with OAuth authentication.
* The website uses security measures like server-side redirect URI validation and random hash state parameters.
* Once authenticated and authorized, Alice can manage her tasks.
* The browser sends a secure JWT cookie to the server with each request.
* The server uses a random, complex JWT secret key and enforces backend algorithms for added security.
* Alice uses the website confidently, knowing her information is protected.

