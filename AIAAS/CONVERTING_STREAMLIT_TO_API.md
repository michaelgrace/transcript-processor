# Converting Streamlit Apps to API + UI Microservices

This guide provides a **step-by-step checklist** and **Q&A** for converting Streamlit apps into a scalable, Dockerized architecture with separate API and UI containers, all joined via the `crown-network`.

---

## 1. What is the recommended architecture?

- **API Container**: FastAPI or Flask REST API, exposes business/data logic.
- **UI Container**: Streamlit or Flask UI, communicates with API via HTTP.
- **DB Container**: Postgres (optionally with pgvector).
- **Network**: All containers joined to `crown-network` for inter-service communication.

---

## 2. Checklist: Converting a Streamlit App to API + UI

### Preparation

- [ ] Backup your project and database volumes.
- [ ] Identify the core logic in your Streamlit app (data processing, DB access, etc.).

### API Service

- [ ] Create a new API (FastAPI or Flask) in `/app/main_fastapi.py` or `/app/main_flask.py`.
- [ ] Move all business/data logic from Streamlit to the API.
- [ ] Expose endpoints for all needed operations (upload, process, list, update, etc.).
- [ ] Use only HTTP requests for communication—**no direct DB access from UI**.

### UI Service

- [ ] Refactor Streamlit UI to use `requests` to call the API endpoints.
- [ ] Remove all direct DB access from the UI.
- [ ] Ensure all user actions (upload, fetch, update) go through the API.

### Dockerization

- [ ] Create/modify `Dockerfile-api` for the API container.
- [ ] Update `docker-compose.yml`:
  - [ ] Add a unique service name for each API/UI pair.
  - [ ] Map unique ports for each API/UI to avoid conflicts.
  - [ ] Join all services to `crown-network`.
- [ ] Add/verify `requirements.txt` includes:
  - `fastapi` or `flask`
  - `uvicorn` (for FastAPI)
  - `requests`
  - `psycopg2-binary`, `pgvector`, `python-dotenv`, `openai`, etc. as needed.

### Database

- [ ] Use a single Postgres container for all apps (unless isolation is required).
- [ ] Enable `pgvector` if using embeddings.
- [ ] Ensure each app uses a unique DB schema/table prefix if sharing the DB.

### Testing

- [ ] Build and run all containers with `docker compose up --build`.
- [ ] Validate:
  - [ ] API endpoints work (test with `/docs` for FastAPI).
  - [ ] UI works and only functions when API is running.
  - [ ] No port or network conflicts.
- [ ] Stop the API container and confirm UI fails gracefully (proves UI is using API).

---

## 3. Q&A: Common Conversion Questions

**Q: How do I avoid port conflicts?**  
A: Assign a unique host port for each API and UI in `docker-compose.yml` (e.g., `api1:8001`, `ui1:8501`, `api2:8002`, etc.).

**Q: How do I ensure network isolation?**  
A: Use `crown-network` for all containers. Later, you can segment by creating additional Docker networks.

**Q: What requirements should be in requirements.txt?**  
A: At minimum:
  - `fastapi` or `flask`
  - `uvicorn` (for FastAPI)
  - `requests`
  - `psycopg2-binary`
  - `pgvector` (if using vector search)
  - `python-dotenv`
  - `openai`
  - Any other app-specific libraries

**Q: How do I structure imports/namespaces?**  
A: Use absolute imports (e.g., `from app.processor import ...`) in all API and UI code to avoid module errors in Docker.

**Q: How do I connect UI to API?**  
A: Use the Docker service name (e.g., `api1:8001`) in your UI code, or set `API_URL` in `.env` and use `os.getenv("API_URL")`.

**Q: Can multiple apps share the same DB?**  
A: Yes, but use unique table names or schemas to avoid collisions.

**Q: How do I scale this pattern?**  
A: Repeat the pattern: each app gets its own API and UI container, unique ports, and joins `crown-network`.

---

## 4. Example: docker-compose.yml snippet for multiple apps

```yaml
services:
  api1:
    build: .
    dockerfile: Dockerfile-api
    ports: ["8001:8000"]
    networks: [crown-network]
    # ...other config...

  ui1:
    build: .
    dockerfile: Dockerfile-ui
    ports: ["8501:8501"]
    networks: [crown-network]
    environment:
      - API_URL=http://api1:8000

  api2:
    build: .
    dockerfile: Dockerfile-api
    ports: ["8002:8000"]
    networks: [crown-network]

  ui2:
    build: .
    dockerfile: Dockerfile-ui
    ports: ["8502:8501"]
    networks: [crown-network]
    environment:
      - API_URL=http://api2:8000

  db:
    image: ankane/pgvector:latest
    ports: ["5432:5432"]
    networks: [crown-network]

networks:
  crown-network:
    external: true
```

---

## 5. Final Checklist

- [ ] All containers use unique ports and service names.
- [ ] All containers join `crown-network`.
- [ ] All UI code uses HTTP to communicate with its API.
- [ ] All API code uses absolute imports.
- [ ] All requirements are in `requirements.txt`.
- [ ] No direct DB access from UI containers.
- [ ] All apps are tested together with `docker compose up --build`.

---

## 6. Clarifying Questions

- Will each app have its own database schema, or will they share tables?
- Do you want to use FastAPI or Flask for all APIs, or mix and match?
- Will you eventually want to add authentication/gateway in front of the APIs?
- Do you want to use a shared `.env` or per-app config?

---

**This document is your living reference for converting Streamlit apps to scalable API+UI microservices.**
