# Streamlit to Streamlit+Flask API+DB Conversion Checklist

## 1. Preparation
- [ ] Backup your project and database.
- [ ] List all features/endpoints your UI needs (CRUD, analytics, etc.).

## 2. Refactor Data Logic
- [ ] Move all database logic from Streamlit into a new Flask API (`main_flask.py`).
- [ ] Expose endpoints for all needed operations (upload, list, get, update, delete, etc.).
- [ ] Use absolute imports in Flask API (e.g., `from app.database import ...`).

## 3. Update Streamlit UI
- [ ] Replace all direct DB calls with HTTP requests to the Flask API using `requests`.
- [ ] Use environment variable (e.g., `API_URL`) to configure API endpoint.
- [ ] Handle API errors gracefully in the UI.

## 4. Dockerization
- [ ] Create/modify Dockerfiles for both Streamlit and Flask API.
- [ ] Add both services to `docker-compose.yml`:
    - [ ] Assign unique container names and ports.
    - [ ] Use a shared Docker network (e.g., `crown-network`).
    - [ ] Set environment variables for DB/API config.
- [ ] Ensure the DB service is present and accessible to both containers.

## 5. Requirements & Dependencies
- [ ] Ensure `requirements.txt` includes:
    - `flask`, `requests`, `psycopg2-binary`, `python-dotenv`, etc.
    - Any other libraries used by your API or UI.
- [ ] Rebuild containers after any requirements change.

## 6. Database Schema
- [ ] Use an init script or migration to ensure all tables/columns exist.
- [ ] If using extensions (e.g., `pgvector`), enable them in your init SQL.

## 7. Testing & Validation
- [ ] Build and start all containers: `docker compose up --build`
- [ ] Test API endpoints directly (e.g., with Postman or `/docs` if using FastAPI).
- [ ] Test Streamlit UI to ensure all features work via the API.
- [ ] Check logs for errors in all containers.

## 8. Security & Best Practices
- [ ] Never expose DB credentials in the UI.
- [ ] Use Docker secrets or environment variables for sensitive data.
- [ ] Plan for authentication (JWT/OAuth2) if needed.

## 9. Documentation
- [ ] Document all API endpoints and expected request/response formats.
- [ ] Update this checklist as you refine your process.

---

**Repeat this checklist for each new Streamlit app you convert to a microservice architecture.**
