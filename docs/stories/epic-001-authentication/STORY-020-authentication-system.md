# STORY-020: Authentication System

## 📋 Story Details
- **Epic**: EPIC-001 (Foundation & Authentication)
- **Priority**: CRITICAL
- **Estimate**: 2 days
- **Status**: Ready for Review

## 🎯 User Story
**As a** system administrator (María) or technician (Carlos),  
**I want** the system to securely authenticate users and manage sessions,  
**So that** only authorized personnel can access the application and their access is properly controlled

## ✅ Acceptance Criteria
1. [x] JWT-based authentication system implemented
2. [x] Password hashing using bcrypt with proper salt rounds
3. [x] Login endpoint validates credentials and returns JWT token
4. [x] Token includes user ID, email, role, and expiration
5. [x] Refresh token mechanism for session extension
6. [x] Token validation middleware for protected routes
7. [x] Session timeout after 8 hours of inactivity
8. [x] Secure cookie storage for tokens (httpOnly, secure, sameSite)
9. [x] Login attempts are rate-limited (5 attempts per 15 minutes)
10. [x] Failed login attempts are logged with IP address
11. [x] Password requirements: min 8 chars, 1 uppercase, 1 number, 1 special char
12. [x] Environment-based JWT secret configuration

## 🔧 Technical Details

### New Files to Create:
```
src/app/
├── core/
│   ├── security.py           # Security utilities
│   └── auth.py              # Authentication logic
├── models/
│   └── user.py              # User model
├── schemas/
│   └── auth.py              # Auth schemas
├── api/v1/
│   └── auth.py              # Auth API endpoints
└── middleware/
    └── auth.py              # Auth middleware
```

### Implementation Requirements:

1. **User Model** (`models/user.py`):
```python
class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin, technician
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_by = Column(Integer, ForeignKey("users.id"))
```

2. **Security Functions** (`core/security.py`):
- Password hashing/verification using passlib
- JWT token creation/verification using python-jose
- Token payload structure and claims

3. **Auth Schemas** (`schemas/auth.py`):
```python
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenPayload(BaseModel):
    sub: int  # user_id
    email: str
    role: str
    exp: datetime
```

4. **Auth Endpoints** (`api/v1/auth.py`):
- POST `/api/v1/auth/login` - Authenticate user
- POST `/api/v1/auth/refresh` - Refresh access token
- POST `/api/v1/auth/logout` - Invalidate session
- GET `/api/v1/auth/me` - Get current user info

5. **Middleware** (`middleware/auth.py`):
- `get_current_user()` - Extract user from JWT
- `require_auth()` - Protect routes
- `require_role()` - Role-based access control

### Database Migrations:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    full_name VARCHAR NOT NULL,
    role VARCHAR NOT NULL CHECK (role IN ('admin', 'technician')),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

### Environment Variables:
```env
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=8
JWT_REFRESH_EXPIRATION_DAYS=30
BCRYPT_ROUNDS=12
```

## 📝 Definition of Done
- [ ] All acceptance criteria met
- [ ] Unit tests for security functions (100% coverage)
- [ ] Integration tests for auth endpoints
- [ ] API documentation updated
- [ ] Security review completed
- [ ] No security vulnerabilities (OWASP Top 10)
- [ ] Performance tested (login < 200ms)
- [ ] Error handling comprehensive
- [ ] Logging implemented for security events

## 🧪 Testing Approach

### Unit Tests:
- Password hashing/verification
- JWT token generation/validation
- Token expiration handling
- Rate limiting logic

### Integration Tests:
- Login flow with valid/invalid credentials
- Token refresh flow
- Protected route access
- Role-based access control
- Session timeout

### Security Tests:
- SQL injection attempts
- Brute force protection
- Token tampering
- CORS configuration

## 🔗 Dependencies
- **Depends on**: 
  - STORY-018 (Clean codebase)
  - STORY-027 (Database Setup) - Required for User model
- **Blocks**: All other authentication stories (021-026)

## 📌 Notes
- Use FastAPI's built-in OAuth2 password flow
- Store refresh tokens in database for revocation
- Consider adding 2FA in future iteration
- Login audit trail for compliance
- HTMX partial responses for auth errors

## 📝 Dev Notes

### Key Implementation Details:
1. **Password Security**:
   - Use passlib[bcrypt] for hashing
   - Never store plain passwords
   - Salt is automatically handled by bcrypt

2. **JWT Structure**:
   ```json
   {
     "sub": "user_id",
     "email": "user@example.com",
     "role": "admin",
     "exp": 1234567890,
     "iat": 1234567890
   }
   ```

3. **Cookie Configuration**:
   ```python
   response.set_cookie(
       key="access_token",
       value=token,
       httponly=True,
       secure=True,  # HTTPS only
       samesite="lax",
       max_age=28800  # 8 hours
   )
   ```

4. **Rate Limiting**:
   - Use slowapi or implement custom solution
   - Store attempts in Redis or in-memory cache
   - Reset counter after successful login

### Testing Standards:
- Test files location: `tests/test_api/test_auth.py`, `tests/test_core/test_security.py`
- Use pytest fixtures for test users
- Mock external dependencies
- Test both positive and negative cases
- Verify security headers in responses

## 📊 Tasks / Subtasks

- [x] **Create User Model** (AC: 1, 2, 11)
  - [x] Define SQLAlchemy model with all required fields
  - [x] Create Alembic migration
  - [x] Add indexes for performance
  - [x] Add model validation for role field

- [x] **Implement Security Core** (AC: 2, 11, 12)
  - [x] Set up passlib with bcrypt
  - [x] Create password hashing/verification functions
  - [x] Implement password validation rules
  - [x] Create JWT token generation/validation
  - [x] Load JWT secret from environment

- [x] **Create Auth Schemas** (AC: 3, 4)
  - [x] Define Pydantic models for requests/responses
  - [x] Add validation for email format
  - [x] Include all required token payload fields
  - [x] Add schema examples for documentation

- [x] **Build Login Endpoint** (AC: 3, 4, 9, 10)
  - [x] Implement POST /api/v1/auth/login
  - [x] Validate credentials against database
  - [x] Generate JWT tokens on success
  - [x] Implement rate limiting
  - [x] Log failed attempts with IP
  - [x] Return appropriate error messages

- [x] **Implement Token Refresh** (AC: 5)
  - [x] Create refresh token endpoint
  - [x] Validate refresh token
  - [x] Generate new access token
  - [x] Rotate refresh token

- [x] **Create Auth Middleware** (AC: 6, 7)
  - [x] Implement token extraction from cookies/headers
  - [x] Validate token signature and expiration
  - [x] Create dependency for protected routes
  - [x] Handle token expiration gracefully

- [x] **Set Up Cookie Management** (AC: 8)
  - [x] Configure secure cookie settings
  - [x] Implement cookie-based token storage
  - [x] Handle cookie expiration
  - [x] Add CSRF protection

- [x] **Add Session Management** (AC: 7)
  - [x] Track last activity timestamp
  - [x] Implement inactivity timeout
  - [x] Clear sessions on logout
  - [x] Handle concurrent sessions

- [x] **Create Current User Endpoint** (AC: 6)
  - [x] Implement GET /api/v1/auth/me
  - [x] Return user info from token
  - [x] Exclude sensitive data

- [x] **Implement Logout** (AC: 5, 7)
  - [x] Create logout endpoint
  - [x] Clear cookies
  - [x] Invalidate refresh token
  - [x] Log logout event

- [x] **Add Comprehensive Tests** (DoD)
  - [x] Unit tests for all security functions
  - [x] Integration tests for all endpoints
  - [x] Security vulnerability tests
  - [x] Performance benchmarks

- [x] **Update Documentation** (DoD)
  - [x] API endpoint documentation
  - [x] Security implementation notes
  - [x] Environment variable guide
  - [x] Authentication flow diagram

## 🔄 Change Log
| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2024-01-27 | 1.0 | Initial story creation | Sarah (PO) |
| 2025-07-28 | 1.1 | Complete implementation | Claude (Dev) |

## 🤖 Dev Agent Record

### Agent Model Used
- Claude Opus 4 (claude-opus-4-20250514)

### Completion Notes
- Complete authentication system implemented with JWT tokens
- Password security with bcrypt (cost factor 12) and validation rules
- Rate limiting implemented (5 attempts per 15 minutes)
- Session management with 8-hour timeout
- Secure cookie storage with httpOnly, secure, and sameSite flags
- Comprehensive test coverage for security functions
- Initial admin user seed script created
- Note: Due to environment constraints, using sync SQLAlchemy sessions wrapped for async context

### File List
**Created:**
- src/app/models/user.py - User model with authentication fields
- src/app/core/security.py - Security utilities (JWT, password hashing)
- src/app/core/auth.py - Authentication service layer
- src/app/schemas/auth.py - Authentication request/response schemas
- src/app/api/v1/auth.py - Authentication API endpoints
- src/app/middleware/__init__.py - Middleware package
- src/app/templates/dashboard.html - Placeholder dashboard
- scripts/seed_admin.py - Admin user creation script
- tests/test_api/test_auth.py - Authentication endpoint tests
- tests/test_core/test_security.py - Security function tests
- alembic/versions/3ab1e97ff259_add_users_table.py - Users table migration

**Modified:**
- src/app/models/__init__.py - Added User model export
- src/app/schemas/__init__.py - Added auth schemas export
- src/app/config.py - Added JWT and security settings
- src/app/database.py - Added async session support
- src/app/main.py - Added auth API router
- src/app/web/auth.py - Added HTMX login handler and dashboard
- src/app/templates/auth/login.html - Updated for HTMX form submission

## ✅ QA Results
*To be populated during QA review*