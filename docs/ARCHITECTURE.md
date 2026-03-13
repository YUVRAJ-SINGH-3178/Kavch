# Kavch Architecture

Technical reference for maintainers and contributors.

## 1. System Overview

Kavch is a two-tier web application:

- Frontend: static HTML/JS/CSS pages in `frontend/public/`
- Backend: FastAPI service in `backend/`

The frontend communicates with backend JSON endpoints over HTTP.

```text
Browser (Vanilla JS + Tailwind)
  -> REST API (FastAPI)
    -> Service modules (classifier, deepfake, evidence, legal_gen)
      -> SQLite via SQLAlchemy
      -> Optional external AI/API providers
```

## 2. Runtime Components

### Frontend (`frontend/public`)

- `components.js`
  - Navbar/footer injection
  - Auth helpers (localStorage token/user)
  - `apiCall()` wrapper (timeout, auth headers, error handling)
- Page modules
  - `report.html` -> threat input
  - `threat-result.html` -> threat output + actions
  - `image-scan.html` -> upload + scan pipeline
  - `vault.html` -> evidence listing/certificates/deletion
  - `legal.html` -> legal document generation
  - `dashboard.html` -> user stats/history
  - `login.html` / `signup.html`

### Backend (`backend`)

- `main.py`
  - App startup
  - Route definitions
  - DTO shaping for frontend
- `auth.py`
  - Password hashing (bcrypt)
  - JWT issue/verify
  - auth dependencies for protected routes
- `classifier.py`
  - Threat tier classification
  - fallback path for low confidence / provider failures
- `deepfake.py`
  - image heuristic metrics
  - manipulation scoring and trace synthesis
- `evidence.py`
  - SHA-256 evidence ID/hash creation
- `legal_gen.py`
  - legal draft generation (provider-backed + local fallback templates)
- `database.py`, `models.py`
  - ORM models + DB session lifecycle

## 3. API Surface

### Auth
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me` (protected)

### Threat and Image
- `POST /api/classify-threat`
- `POST /api/scan-image`

### Evidence
- `POST /api/lock-evidence`
- `GET /api/vault` (protected)
- `DELETE /api/vault/{evidence_id}` (protected)

### Legal
- `POST /api/generate-legal-docs`
- `GET /api/legal-docs` (protected)

### History and Utility
- `GET /api/history/threats` (protected)
- `GET /api/history/scans` (protected)
- `GET /api/health`
- `GET /api/support-contacts`

## 4. Core Flows

### A. Threat Report Flow

1. User submits text in `report.html`.
2. Frontend calls `POST /api/classify-threat`.
3. Backend returns tier + phrases + legal sections + actions.
4. Result stored in `sessionStorage` and rendered in `threat-result.html`.

### B. Image Scan Flow

1. User uploads image in `image-scan.html`.
2. Frontend sends multipart file to `POST /api/scan-image`.
3. Backend computes manipulation score and trace candidates.
4. UI renders score, notes, traces, and allows save to vault/legal flow.

### C. Evidence Vault Flow

1. Evidence created by scan/report/manual lock.
2. Hash generated (SHA-256).
3. Item stored in backend DB (if authenticated) and merged with local cache for continuity.
4. Certificate generated client-side from evidence payload.

### D. Legal Draft Flow

1. User selects document type + city + platform + language.
2. Frontend calls `POST /api/generate-legal-docs`.
3. Backend returns provider-based draft or fallback template.
4. User copies/downloads document and files manually.

## 5. Data Model

### `users`
- id, name, email, hashed_password, created_at

### `threat_reports`
- id, user_id, text, language, tier, label, confidence, raw_result, created_at

### `scan_results`
- id, user_id, filename, is_clean, manipulation_score, analysis_notes, raw_result, created_at

### `evidence_vault`
- id, user_id, evidence_id, type, title, platform, hash, content_preview, raw_data, locked_at

### `legal_documents`
- id, user_id, doc_type, city, platform, language, content, created_at

## 6. Security Model

- JWT bearer auth for protected routes.
- Password hashing via bcrypt.
- Evidence integrity via SHA-256 hash fingerprints.
- User-scoped filtering for vault/history/legal documents.

## 7. Resilience and Fallbacks

- Threat classification has fallback path when model/provider fails.
- Legal generation supports offline templates if provider unavailable.
- Image scan returns deterministic heuristic output without external connectors.
- Frontend keeps local evidence fallback cache for continuity.

## 8. Deployment Considerations

### Backend
- Use ASGI server (`uvicorn`/`gunicorn+uvicorn workers`).
- Move from SQLite to managed DB for concurrent production usage.
- Configure CORS origins explicitly for deployed frontend domain.

### Frontend
- Static hosting (Netlify/Vercel/GitHub Pages/S3+CloudFront).
- Set API base URL via `window.API_URL` or environment-aware injection.

### Secrets
- Keep `.env` out of source control.
- Rotate `SECRET_KEY` and API tokens periodically.

## 9. Known Risks

- Heuristic image scan is not forensic-court-grade by itself.
- Client-generated certificates must be paired with backend records for stronger auditability.
- No formal migration system currently visible for schema evolution.

## 10. Recommended Engineering Next Steps

- Add automated tests for all critical API routes.
- Add structured logging and request IDs.
- Add schema migrations (Alembic).
- Add input validation limits and abuse-rate controls.
- Add signed server-side certificate artifacts with verification endpoint.

---

Last updated: March 2026
