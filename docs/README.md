# Kavch

AI-assisted digital safety platform focused on cyber harassment reporting, deepfake/image misuse triage, evidence preservation, and legal document drafting workflows for India.

## What Kavch Does

- Classifies abusive/threatening text into severity tiers.
- Scans uploaded images and computes a manipulation risk score.
- Stores evidence with SHA-256 fingerprints in a vault.
- Generates legal drafts (FIR, platform takedown, legal notice, NCW complaint).
- Provides support-path routing (helplines and escalation guidance).

## Key Capabilities

### 1. Threat Analysis
- Endpoint: `POST /api/classify-threat`
- Returns tier, confidence, extracted phrases, applicable legal sections, and recommended actions.
- Supports rule-based fallback if external model/API confidence is low.

### 2. Image / Deepfake Triage
- Endpoint: `POST /api/scan-image`
- Produces:
  - `manipulation_score` (0-100)
  - `deepfake_detected` (boolean)
  - `found_urls` (trace leads when available)
  - `analysis_notes` and recommendation
- Uses deterministic heuristic analysis for stable local behavior.

### 3. Evidence Vault
- Endpoints:
  - `POST /api/lock-evidence`
  - `GET /api/vault`
  - `DELETE /api/vault/{evidence_id}`
- Evidence is timestamped and hashed (SHA-256).
- Certificate view/export available from vault UI.

### 4. Legal Drafting
- Endpoint: `POST /api/generate-legal-docs`
- Document types:
  - FIR Draft
  - Platform Takedown
  - Legal Notice
  - NCW Complaint
- Supports multilingual output with backend and frontend fallback templates.

### 5. Account + History
- JWT-based auth with bcrypt password hashing.
- User-specific history and dashboard stats for threats, scans, evidence, and legal docs.

## Tech Stack

- Backend: FastAPI, SQLAlchemy, SQLite
- Auth: JWT + bcrypt
- ML/Analysis: Scikit-learn model + deterministic fallback logic
- Frontend: Vanilla JavaScript + Tailwind CSS (CDN)
- AI integration: Anthropic Claude (optional, graceful fallback when missing)

## Project Layout

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

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### Frontend

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
- App runs without optional API keys using local fallback logic.
- Without external keys, quality may be lower but workflows stay functional.

## API Overview

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

## Security Notes

- SHA-256 hashing used for evidence integrity checks.
- JWT required for protected user routes.
- Passwords stored as bcrypt hashes.
- Data access scoped by authenticated user ID on protected endpoints.

## Current Limitations

- Deepfake scoring is heuristic and not a forensic-grade model.
- Legal drafts are assistive templates and require legal review before filing.
- Some capabilities degrade gracefully when optional external APIs are not configured.

## Recommended Next Improvements

- Add test suite (unit + API integration + frontend smoke).
- Add migrations (Alembic) for versioned DB evolution.
- Add rate limiting and structured audit logging.
- Add confidence calibration and evaluation dataset for scan/classifier output.

## License

This repository currently does not expose a license file in workspace root. Add a `LICENSE` file before public distribution.

---

Last updated: March 2026
