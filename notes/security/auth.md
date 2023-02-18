# Making Sense of Auth

Authentication and authorization, commonly known as "auth", are two critical security components in any web application. Authentication is the process of verifying that the user is who they claim to be, while authorization determines if the user is allowed to access the requested resources.

## Where Does Auth Happen?

Authentication and authorization occur on the server-side, but the client-side also plays a vital role in making requests, which are authenticated and authorized.

## How to Know What to Render in Frontend

When a client makes a request, the server responds with the requested data. The response can include the user's authorization level or data that indicates whether the user is authenticated. The client then renders the appropriate view based on the data received.

## Auth Flow on the Frontend

1. The user opens the page for the first time.
2. The user signs in, and the server returns a secure cookie.
3. The client stores the secure cookie.
4. All future requests to the server will include the secure cookie.

## Authorizing User Flow on the Server-side

1. The user makes a request for data.
2. The server receives the request and parses the cookie from it.
3. The server checks the user cookie to determine their identity.
4. The server checks if the user is authorized to perform the requested action.
5. The server returns the requested data if authorized, otherwise, it throws an error.

## Best Practices for Authentication

Here are some best practices for implementing authentication:

* Use standard authentication, such as JWT or OAuth, instead of Basic Auth.
* Use maximum retry and jail features to protect against brute-force attacks.
* Use encryption on all sensitive data.
* Do not reinvent the wheel when it comes to token generation and password storage. Use industry-standard libraries and frameworks.

## Best Practices for JWT

Here are some best practices for implementing JWT:

* Use a random, complex key (JWT secret) to make brute-forcing the token more difficult.
* Do not extract the algorithm from the header. Force the algorithm on the backend (HS256 or RS256).
* Keep the token expiration as short as possible.
* Do not store sensitive data in the JWT payload; it can be easily decoded.
* Avoid storing too much data in the JWT as it is usually shared in headers, which have size limits.

## Best Practices for OAuth

Here are some best practices for implementing OAuth:

* Always validate the redirect URI server-side to allow only whitelisted URLs.
* Always try to exchange for code and not tokens (do not allow response_type=token).
* Use a state parameter with a random hash to prevent CSRF attacks during the OAuth authentication process.
* Define the default scope and validate the scope parameters for each application.

## Story to Understand How It Works

To help you better understand how auth works, here's a little story:

* Alice stumbled upon a new website designed to help her manage her tasks.
* As she navigated the site, she was asked to log in with her credentials to access her tasks.
* Alice wondered what the "auth" thing was and why she needed it.
* The website's server explained that they needed to verify her identity using a standard authentication method called OAuth.
* Alice asked what would happen if someone else tried to log in with her information.
* The server explained that they had implemented various security measures, like validating the redirect-uri server-side and using a state parameter with a random hash, to prevent unauthorized access to her account.
* Alice felt relieved and proceeded to log in.
* Once authenticated and authorized, Alice was able to see her tasks and manage them efficiently.
* Alice noticed that her browser was sending a secure cookie to the server with each request and asked what it was for.
* The server explained that they used a technique called JWT, which is a secure way to encode information in a token format.
* The token was stored in a cookie, sent with each request to the server to verify that it was really Alice making the request and not someone else.
* Alice was fascinated by this technology but worried that JWTs could be easily hacked.
* The server explained that they used a random and complicated key called the JWT Secret to make it nearly impossible to hack, and verified the algorithm in the backend to prevent header extraction.
* Alice continued to use the website with confidence, knowing that her information was safe and secure.
