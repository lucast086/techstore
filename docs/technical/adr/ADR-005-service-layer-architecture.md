# ADR-005: Service Layer as Single Source of Truth

## Status
Accepted (Supersedes ADR-004)

## Date
2025-07-29

## Context

After implementing ADR-004 (API-First Authentication), we encountered issues in production:

1. **HTTP Redirect Issues**: Railway's HTTP→HTTPS redirect caused POST body loss when HTMX endpoints called API endpoints internally
2. **Performance Overhead**: Unnecessary HTTP calls between endpoints on the same server
3. **Complexity**: Additional abstraction layer without clear benefits
4. **Debugging Difficulty**: Hard to trace issues through multiple HTTP hops

We reconsidered the architecture and identified that the "single source of truth" principle was being applied at the wrong layer.

## Decision

We will adopt a **Service Layer Architecture** where:
- The Service Layer is the single source of truth for all business logic
- Both API and HTMX endpoints call services directly
- No internal HTTP calls between endpoints
- Endpoints are thin adapters that format responses appropriately

## Implementation

### Service Layer (Single Source of Truth)
```python
# app/services/auth_service.py
class AuthService:
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        # ALL authentication logic lives here
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    def create_tokens(self, user: User) -> TokenResponse:
        # Token generation logic
        return TokenResponse(...)
```

### API Endpoint (JSON Adapter)
```python
# app/api/v1/auth.py
@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    return auth_service.create_tokens(user)  # Returns JSON
```

### HTMX Endpoint (HTML Adapter)
```python
# app/web/auth.py
@router.post("/login-htmx")
async def login_htmx(email: str = Form(...), password: str = Form(...),
                     db: Session = Depends(get_db)):
    auth_service = AuthService(db)  # Same service as API
    user = auth_service.authenticate_user(email, password)
    if not user:
        return templates.TemplateResponse("error.html", {"error": "Invalid credentials"})

    tokens = auth_service.create_tokens(user)
    response.set_cookie("access_token", tokens.access_token, httponly=True)
    response.headers["HX-Redirect"] = "/dashboard"
    return ""  # HTMX handles redirect
```

## Architecture Diagram

```
┌─────────────┐     ┌─────────────┐
│   Browser   │     │ Mobile App  │
└──────┬──────┘     └──────┬──────┘
       │                   │
       ▼                   ▼
┌─────────────┐     ┌─────────────┐
│ HTMX Routes │     │ API Routes  │
│   (HTML)    │     │   (JSON)    │
└──────┬──────┘     └──────┬──────┘
       │                   │
       └─────────┬─────────┘
                 ▼
         ┌─────────────┐
         │  Service    │  ← Single Source of Truth
         │   Layer     │
         └──────┬──────┘
                ▼
         ┌─────────────┐
         │  Database   │
         └─────────────┘
```

## Consequences

### Positive
- **True Single Source of Truth**: Business logic exists only in services
- **Better Performance**: No internal HTTP overhead
- **Simpler Architecture**: Fewer moving parts
- **Easier Debugging**: Direct call stack without HTTP boundaries
- **Testability**: Services can be tested in isolation
- **Flexibility**: Easy to add new endpoint types (GraphQL, gRPC, etc.)

### Negative
- **Breaking Change**: Existing code following ADR-004 must be refactored
- **Documentation Update**: All guides must be updated

### Neutral
- Endpoints become even thinner, focusing only on protocol adaptation
- Services must handle all business logic and validation

## Migration Guide

1. **Identify HTTP calls between endpoints**
   ```python
   # Old (ADR-004)
   async with httpx.AsyncClient() as client:
       response = await client.post("/api/v1/auth/login", json={...})
   ```

2. **Replace with direct service calls**
   ```python
   # New (ADR-005)
   auth_service = AuthService(db)
   user = auth_service.authenticate_user(email, password)
   ```

3. **Update tests to mock services instead of HTTP calls**

## Implementation Requirements

1. **Services MUST**:
   - Contain all business logic
   - Be framework-agnostic
   - Use dependency injection for database access
   - Return domain objects, not HTTP responses

2. **Endpoints MUST**:
   - Be thin adapters
   - Handle only request/response formatting
   - Call services for all business logic
   - Add extensive logging for debugging

3. **Documentation MUST**:
   - Clearly state Service Layer as single source of truth
   - Show examples of both endpoint types calling same service
   - Emphasize no internal HTTP calls

## References
- Martin Fowler: Service Layer Pattern
- Clean Architecture by Robert C. Martin
- Previous ADR-004 (superseded)
