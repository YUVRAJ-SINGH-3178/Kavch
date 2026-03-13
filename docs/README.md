# Kavch

Kavch is an AI-assisted digital safety platform designed to help users move from cyber harassment detection to evidence preservation and legal action in one workflow.

It combines threat analysis, deepfake/image misuse triage, tamper-evident vaulting, and legal draft generation with India-focused escalation guidance.

## Why Kavch

Victims of cyber harassment often face four problems:

- Abuse is hard to classify for urgency.
- Evidence is lost, edited, or not documented correctly.
- Legal filing language is complex and time-consuming.
- Support channels are fragmented.

Kavch addresses this by turning incidents into structured outputs: tiered analysis, hash-backed evidence records, and draft legal documents linked to those records.

## Core Features

### 1. Threat Analysis Engine

- Endpoint: `POST /api/classify-threat`
- Returns:
  - severity tier (`1` to `4`)
  - confidence
  - key phrases
  - applicable legal sections
  - recommended actions
- Includes deterministic fallback logic when external AI/model confidence is low, so the UI still returns actionable results.

### 2. Image / Deepfake Triage

- Endpoint: `POST /api/scan-image`
- Produces:
  - `manipulation_score` (0-100)
  - `deepfake_detected` boolean
  - potential trace leads (`found_urls`)
  - forensic notes and recommendation
- Current implementation is heuristic (fast and deterministic), intended for triage and escalation support rather than forensic finality.

### 3. Tamper-Evident Evidence Vault

- Endpoints:
  - `POST /api/lock-evidence`
  - `GET /api/vault`
  - `DELETE /api/vault/{evidence_id}`
- Uses SHA-256 hashing to fingerprint evidence payloads.
- Provides certificate rendering from vault items (platform/source, hash, timestamp).
- Supports API + local fallback continuity for frontend sessions.

### 4. Legal Draft Generation

- Endpoint: `POST /api/generate-legal-docs`
- Supported draft types:
  - FIR Draft
  - Platform Takedown
  - Legal Notice
  - NCW Complaint
- Multilingual support with backend and frontend fallback templates.
- Designed as assistive drafting; final filing should be reviewed by legal counsel.

### 5. Account, Dashboard, and History

- JWT auth with bcrypt-hashed passwords.
- Per-user history and stats:
  - threats
  - scans
  - evidence items
  - legal documents

## Architecture Snapshot

```text
Frontend (Vanilla JS + Tailwind CDN)
  -> API wrapper in components.js
    -> FastAPI backend
      -> classifier.py (text risk)
      -> deepfake.py (image risk)
      -> evidence.py (SHA-256 evidence IDs)
      -> legal_gen.py (legal draft generation)
      -> SQLite via SQLAlchemy models
```

Detailed architecture reference: `docs/ARCHITECTURE.md`.

## Tech Stack

- Backend: FastAPI, SQLAlchemy, SQLite
- Authentication: JWT, bcrypt
- Analysis: Scikit-learn model + deterministic fallback pipelines
- Frontend: Static HTML + Vanilla JS + Tailwind CSS (CDN)
- Optional AI integration: Anthropic Claude API

## Project Structure

```text
ShiledHer/
  backend/
    main.py
    auth.py
    classifier.py
    deepfake.py
    evidence.py
    legal_gen.py
    database.py
    models.py
    requirements.txt
    ml/
      train_threat.py
    data/
      legal_templates/

  frontend/
    public/
      index.html
      report.html
      threat-result.html
      image-scan.html
      vault.html
      legal.html
      safe-net.html
      dashboard.html
      login.html
      signup.html
      components.js

  docs/
    README.md
    ARCHITECTURE.md
```

## Local Setup

### Prerequisites

- Python 3.10+
- Node.js 18+

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend/public
npx -y serve -p 3000 --no-clipboard
```

Open `http://localhost:3000`.

## Environment Variables

Create `backend/.env`:

```env
SECRET_KEY=replace_with_long_random_secret
ANTHROPIC_API_KEY=optional_for_ai_generation
GOOGLE_VISION_API_KEY=optional
```

Notes:

- App runs without optional API keys using fallback logic.
- External keys improve generation quality and context, but are not mandatory for core flows.

## API Summary

### Public / Utility

- `GET /`
- `GET /api/health`
- `GET /api/support-contacts`

### Auth

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

### Threat + Scan

- `POST /api/classify-threat`
- `POST /api/scan-image`
- `POST /api/detect-coordination`

### Evidence

- `POST /api/lock-evidence`
- `GET /api/vault`
- `DELETE /api/vault/{evidence_id}`

### Legal

- `POST /api/generate-legal-docs`
- `GET /api/legal-docs`

### History

- `GET /api/history/threats`
- `GET /api/history/scans`

## Security and Integrity Notes

- SHA-256 hashing is used for evidence integrity.
- Protected routes require JWT bearer auth.
- Passwords are stored with bcrypt hashes.
- User-scoped DB filtering is enforced on protected data routes.

## Legal and Product Disclaimer

Kavch is an assistive safety and documentation tool. It does not replace legal representation, law enforcement processes, or certified forensic examination. Always verify details before formal filing.

## Current Limitations

- Deepfake scoring is currently heuristic and not a certified forensic model.
- Legal output quality depends on context completeness and optional AI availability.
- The repository does not currently expose a production hardening baseline (tests/migrations/CI) by default.

## Recommended Next Improvements

- Add unit + API integration tests.
- Add schema migration tooling (Alembic).
- Add request audit logging and rate limits.
- Add confidence calibration datasets for classifier/scan outputs.
- Add root-level `LICENSE` and deployment templates.

## Contributors

- Yuvraj Singh
- Akshat Srivastava
- Adarsh Kumar Pandey
- Chigulla Eshita 

---

Last updated: March 2026
