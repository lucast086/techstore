# ADR-004: API-First Authentication Pattern

## Status
~~Accepted~~ **Superseded by ADR-005**

> **Note**: This ADR has been superseded by [ADR-005: Service Layer as Single Source of Truth](./ADR-005-service-layer-architecture.md).
> The API-First pattern caused issues with HTTP redirects in production. We now use direct service calls from all endpoints.

## Date
2025-07-28

## Context

When implementing authentication for TechStore, we needed to decide how to handle authentication across different client types:
- Web browsers (using HTMX)
- Future mobile applications
- Third-party API integrations

We had two options for the web authentication flow:

1. **Direct Service Call**: Web endpoints directly call the authentication service
2. **API-First**: Web endpoints call the API endpoints, which return JSON tokens

## Decision

We will use an **API-First authentication pattern** where:
- All authentication logic flows through the API endpoints
- API endpoints return JWT tokens as JSON
- Web endpoints call API endpoints and handle web-specific concerns (cookies)

## Implementation

### API Endpoint (`/api/v1/auth/login`)
```python
# Returns JSON response with tokens
{
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 28800
}
```

### Web Endpoints
```python
# Login: /login-htmx - Calls API endpoint
api_response = await client.post("/api/v1/auth/login", json={...})
tokens = api_response.json()

# Converts tokens to secure cookies for browser
response.set_cookie("access_token", tokens["access_token"], httponly=True, ...)

# Logout: /logout - Web-specific endpoint for cookie handling
# (API logout expects Authorization header, web uses cookies)
response.delete_cookie("access_token", httponly=True, ...)
response.headers["HX-Redirect"] = "/login"
```

### Mobile Apps
```javascript
// Store tokens in secure device storage
const { access_token } = await response.json();
await SecureStore.setItemAsync('access_token', access_token);
```

## Web-Specific Endpoints

While most operations go through the API, some web endpoints are needed for cookie-based operations:

- **Login** (`/login-htmx`): Calls API then converts tokens to cookies
- **Logout** (`/logout`): Clears cookies directly (API expects Authorization header)
- **Protected Pages**: Check cookies instead of headers

This is necessary because:
1. Browsers automatically send cookies but not Authorization headers
2. HTMX forms can't easily add Authorization headers
3. Cookie operations must happen at the web layer

## Consequences

### Positive
- **Single Source of Truth**: All authentication logic in API endpoints
- **Consistency**: Same authentication flow for all clients
- **Testability**: API can be tested independently
- **Dogfooding**: We use our own API like external clients would
- **Future-Proof**: Ready for mobile apps and third-party integrations
- **Standards Compliance**: Follows OAuth2/JWT patterns

### Negative
- **Performance**: Slight overhead from internal HTTP call (negligible on same server)
- **Complexity**: Additional layer of abstraction

### Neutral
- Web endpoints become thin wrappers handling web-specific concerns
- Each client type manages token storage according to platform best practices

## Token Storage by Client Type

| Client Type | Storage Method | Security Features | Token Transmission |
|------------|----------------|-------------------|-------------------|
| Web Browser (HTMX) | httpOnly cookies | CSRF protection, secure flag | Cookie header |
| Mobile App | Secure device storage | iOS Keychain, Android Keystore | Authorization header |
| SPA | Memory or localStorage | XSS considerations | Authorization header |
| API Client | Client's choice | Client's responsibility | Authorization header |

## References
- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [JWT Best Practices RFC 8725](https://tools.ietf.org/html/rfc8725)
- OWASP Authentication Cheat Sheet
