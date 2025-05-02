# API Security, Token Passing, and Unified API Architecture

---

## 1. How do I pass secure tokens between layers (UI → API → DB)?

**Short answer:**  
- Use **JWT (JSON Web Tokens)** or similar tokens for authentication/authorization.
- Pass tokens in the `Authorization` HTTP header (`Bearer <token>`) from UI to API.
- The API validates the token before processing requests.
- The DB layer should never see tokens; the API enforces security.

---

## 2. What do I need to install for secure token-based auth?

- `pyjwt` (for JWT token creation/validation)
- `python-jose` (alternative for JWT, used by FastAPI)
- `passlib[bcrypt]` (for password hashing, if needed)
- `cryptography` (for advanced crypto, optional)
- `python-dotenv` (for managing secrets in `.env`)

**Add to requirements.txt:**
```
pyjwt
python-jose
passlib[bcrypt]
cryptography
```

---

## 3. How do I implement token-based security in FastAPI?

- Generate a JWT when a user logs in (or when a service authenticates).
- Require the token in the `Authorization` header for protected endpoints.
- Use FastAPI's `Depends` and `Security` utilities for easy integration.

**Example:**
```python
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

security = HTTPBearer()
SECRET_KEY = "your-secret-key"

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
```
- Add `Depends(verify_token)` to any endpoint that requires authentication.

---

## 4. How do I pass the token from UI to API?

- When the UI authenticates, store the JWT in memory or browser storage.
- For each API call, add the header:
  ```
  Authorization: Bearer <token>
  ```
- In Python (requests):
  ```python
  headers = {"Authorization": f"Bearer {token}"}
  requests.get("http://api:8000/protected/", headers=headers)
  ```

---

## 5. How do I ensure secure communication between containers?

- **Internal Docker networks** (like `crown-network`) are isolated from the outside world by default.
- For **external access**, use HTTPS (TLS). Use a reverse proxy (e.g., Traefik, Nginx) with SSL certificates.
- For internal-only APIs, Docker networking is usually sufficient for dev/test.

---

## 6. How do I build a unified API that can run multiple processes/services?

- Use **FastAPI** or **Flask** to expose multiple endpoints/services in one container.
- For multi-process, use Gunicorn with Uvicorn workers (as discussed previously).
- For microservices, use a gateway API that proxies requests to internal services.
- Use Docker Compose to orchestrate multiple containers, all joined to `crown-network`.

---

## 7. Checklist for Secure, Unified API

- [ ] Add `pyjwt`, `python-jose`, `passlib[bcrypt]`, `cryptography` to requirements.txt.
- [ ] Implement JWT-based authentication in your API.
- [ ] Pass tokens in the `Authorization` header from UI to API.
- [ ] Use Docker internal networks for container-to-container security.
- [ ] Use HTTPS for any external API access.
- [ ] Use Gunicorn/Uvicorn for multi-worker API containers.
- [ ] Document your API endpoints and security model.

---

## 8. Clarifying Questions

- Will you have user logins, or just service-to-service authentication?
- Do you need to support external (internet) clients, or only internal apps?
- Do you want to use OAuth2, or is JWT sufficient?
- Will you use a reverse proxy (Nginx/Traefik) for SSL termination?

---

**Summary:**  
- Use JWT for secure token passing.
- Install `pyjwt`, `python-jose`, etc.
- Pass tokens in the `Authorization` header.
- Use Docker networks for internal security, HTTPS for external.
- Use Gunicorn/Uvicorn for scalable, unified APIs.

---
