import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from sqlalchemy.orm import Session
import uvicorn
import json

# Import custom modules
from classifier import load_classifier, classify
from deepfake import analyze_image
from evidence import lock_evidence
from legal_gen import generate_document

# Database & Auth
from database import get_db, init_db
from models import User, ThreatReport, ScanResult, EvidenceItem, LegalDocument
from auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, get_optional_user
)

# Load env variables
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Kavch Backend")

# Setup CORS
origins = [
    "http://localhost:3000",
    "http://localhost:5500",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models_loaded = False

@app.on_event("startup")
async def startup_event():
    global models_loaded
    print("Initializing on startup...")
    # Initialize database tables
    init_db()
    # Load ML Model into memory
    load_classifier()
    models_loaded = True
    print("Models loaded. Database ready. ✅")


# ═══════════════════════════════════════════════════════════
#  PUBLIC ROUTES (no auth required)
# ═══════════════════════════════════════════════════════════

@app.get("/")
async def root():
    return {
        "message": "Welcome to Kavch AI API",
        "docs": "/docs",
        "health": "/api/health"
    }


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "models_loaded": models_loaded,
        "service": "Kavch AI API"
    }


# ═══════════════════════════════════════════════════════════
#  AUTH ROUTES (register, login, profile)
# ═══════════════════════════════════════════════════════════

@app.post("/api/auth/register")
async def register(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        name = data.get("name", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        # Validation
        if not name or not email or not password:
            raise HTTPException(status_code=400, detail="Name, email, and password are required")
        
        if len(password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

        # Check if email already exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise HTTPException(status_code=409, detail="An account with this email already exists")

        # Create user
        user = User(
            name=name,
            email=email,
            hashed_password=hash_password(password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Generate token
        token = create_access_token(user.id, user.email)

        return {
            "message": "Account created successfully",
            "token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/login")
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password are required")

        # Find user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Verify password
        if not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Generate token
        token = create_access_token(user.id, user.email)

        return {
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/auth/me")
async def get_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user's profile and stats."""
    threat_count = db.query(ThreatReport).filter(ThreatReport.user_id == user.id).count()
    scan_count = db.query(ScanResult).filter(ScanResult.user_id == user.id).count()
    evidence_count = db.query(EvidenceItem).filter(EvidenceItem.user_id == user.id).count()
    legal_count = db.query(LegalDocument).filter(LegalDocument.user_id == user.id).count()

    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None
        },
        "stats": {
            "threat_reports": threat_count,
            "scans": scan_count,
            "evidence_items": evidence_count,
            "legal_documents": legal_count
        }
    }


# ═══════════════════════════════════════════════════════════
#  THREAT CLASSIFICATION (auth optional — saves if logged in)
# ═══════════════════════════════════════════════════════════

@app.post("/api/classify-threat")
async def api_classify_threat(
    request: Request,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    try:
        data = await request.json()
        text = data.get("text", "")
        language = data.get("language", "English")

        if not text:
            raise HTTPException(status_code=400, detail="Text field is required")

        result = classify(text, language)

        # Save to DB if user is logged in
        if user:
            report = ThreatReport(
                user_id=user.id,
                text=text,
                language=language,
                tier=result.get("tier", 1),
                label=result.get("label", ""),
                confidence=result.get("confidence", 0.0),
                raw_result=result
            )
            db.add(report)
            db.commit()
            db.refresh(report)
            result["report_id"] = report.id
            result["saved"] = True
        else:
            result["saved"] = False

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
#  IMAGE SCAN (auth optional — saves if logged in)
# ═══════════════════════════════════════════════════════════

@app.post("/api/scan-image")
async def api_scan_image(
    image: UploadFile = File(...),
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    try:
        contents = await image.read()
        result = analyze_image(contents)

        response = {
            "isClean": not result["deepfake_detected"],
            "foundCount": len(result["found_urls"]),
            "manipulationScore": result["manipulation_score"],
            "urls": result["found_urls"],
            "notes": result["analysis_notes"]
        }

        # Save to DB if user is logged in
        if user:
            scan = ScanResult(
                user_id=user.id,
                filename=image.filename or "uploaded_image",
                is_clean=not result["deepfake_detected"],
                manipulation_score=result["manipulation_score"],
                analysis_notes=result["analysis_notes"],
                raw_result=response
            )
            db.add(scan)
            db.commit()
            db.refresh(scan)
            response["scan_id"] = scan.id
            response["saved"] = True
        else:
            response["saved"] = False

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
#  EVIDENCE VAULT (auth required for persistence)
# ═══════════════════════════════════════════════════════════

@app.post("/api/lock-evidence")
async def api_lock_evidence(
    request: Request,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    try:
        data = await request.json()
        url = data.get("url", "")
        screenshot_base64 = data.get("screenshot_base64", "")
        content = data.get("content", "")

        if not url and not screenshot_base64 and not content:
            raise HTTPException(status_code=400, detail="Must provide url, content or screenshot")

        result = lock_evidence(content=content, url=url, screenshot_base64=screenshot_base64)

        # Save to DB if user is logged in
        if user:
            # Determine type and title
            ev_type = "url" if url else ("image" if screenshot_base64 else "text")
            title = url if url else ("Screenshot Evidence" if screenshot_base64 else content[:100])
            platform = ""
            if url:
                try:
                    from urllib.parse import urlparse
                    platform = urlparse(url).hostname or ""
                    platform = platform.replace("www.", "")
                except:
                    platform = "Web Link"

            evidence = EvidenceItem(
                user_id=user.id,
                evidence_id=result["evidence_id"],
                type=ev_type,
                title=title,
                platform=platform,
                hash=result["hash"],
                content_preview=result["certificate"]["content_preview"],
                raw_data=url or screenshot_base64[:500] or content[:500],  # Store limited data
                locked_at=None  # Will use default
            )
            db.add(evidence)
            db.commit()
            db.refresh(evidence)
            result["saved"] = True
            result["db_id"] = evidence.id
        else:
            result["saved"] = False

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/vault")
async def get_vault(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all evidence items for the logged-in user."""
    items = db.query(EvidenceItem).filter(
        EvidenceItem.user_id == user.id
    ).order_by(EvidenceItem.locked_at.desc()).all()

    return {
        "count": len(items),
        "items": [
            {
                "id": item.evidence_id,
                "type": item.type,
                "title": item.title,
                "platform": item.platform,
                "hash": item.hash,
                "content_preview": item.content_preview,
                "timestamp": item.locked_at.isoformat() if item.locked_at else None,
                "icon": "lucide:link" if item.type == "url" else (
                    "lucide:image" if item.type == "image" else "lucide:file-text"
                )
            }
            for item in items
        ]
    }


@app.delete("/api/vault/{evidence_id}")
async def delete_evidence(
    evidence_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific evidence item (only if it belongs to the user)."""
    item = db.query(EvidenceItem).filter(
        EvidenceItem.evidence_id == evidence_id,
        EvidenceItem.user_id == user.id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Evidence not found")

    db.delete(item)
    db.commit()
    return {"message": "Evidence deleted", "evidence_id": evidence_id}


# ═══════════════════════════════════════════════════════════
#  LEGAL DOCUMENT GENERATION (auth optional — saves if logged in)
# ═══════════════════════════════════════════════════════════

@app.post("/api/generate-legal-docs")
async def api_generate_legal_docs(
    request: Request,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    try:
        data = await request.json()
        doc_type = data.get("doc_type")
        city = data.get("city")
        platform = data.get("platform")
        date = data.get("date")
        language = data.get("language", "English")

        evidence_ids = data.get("evidence_ids", [])
        threat_data = data.get("threat_data", {})

        incident_text = "N/A"
        if "phrases" in threat_data:
            incident_text = " ".join(threat_data["phrases"])

        result = generate_document(
            doc_type=doc_type,
            city=city,
            platform=platform,
            date=date,
            language=language,
            incident_text=incident_text,
            evidence_ids=evidence_ids
        )

        # Save to DB if user is logged in
        if user:
            legal_doc = LegalDocument(
                user_id=user.id,
                doc_type=doc_type or "",
                city=city or "",
                platform=platform or "",
                language=language,
                content=result.get("content", "")
            )
            db.add(legal_doc)
            db.commit()
            db.refresh(legal_doc)
            result["doc_id"] = legal_doc.id
            result["saved"] = True
        else:
            result["saved"] = False

        return {
            "document_text": result["content"],
            "metadata": result
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/legal-docs")
async def get_legal_docs(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all legal documents for the logged-in user."""
    docs = db.query(LegalDocument).filter(
        LegalDocument.user_id == user.id
    ).order_by(LegalDocument.created_at.desc()).all()

    return {
        "count": len(docs),
        "documents": [
            {
                "id": doc.id,
                "doc_type": doc.doc_type,
                "city": doc.city,
                "platform": doc.platform,
                "language": doc.language,
                "content_preview": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                "created_at": doc.created_at.isoformat() if doc.created_at else None
            }
            for doc in docs
        ]
    }


# ═══════════════════════════════════════════════════════════
#  HISTORY (auth required)
# ═══════════════════════════════════════════════════════════

@app.get("/api/history/threats")
async def get_threat_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all threat reports for the logged-in user."""
    reports = db.query(ThreatReport).filter(
        ThreatReport.user_id == user.id
    ).order_by(ThreatReport.created_at.desc()).all()

    return {
        "count": len(reports),
        "reports": [
            {
                "id": r.id,
                "text_preview": r.text[:100] + "..." if len(r.text) > 100 else r.text,
                "tier": r.tier,
                "label": r.label,
                "confidence": r.confidence,
                "language": r.language,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in reports
        ]
    }


@app.get("/api/history/scans")
async def get_scan_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all scan results for the logged-in user."""
    scans = db.query(ScanResult).filter(
        ScanResult.user_id == user.id
    ).order_by(ScanResult.created_at.desc()).all()

    return {
        "count": len(scans),
        "scans": [
            {
                "id": s.id,
                "filename": s.filename,
                "is_clean": s.is_clean,
                "manipulation_score": s.manipulation_score,
                "notes_preview": s.analysis_notes[:100] if s.analysis_notes else "",
                "created_at": s.created_at.isoformat() if s.created_at else None
            }
            for s in scans
        ]
    }


# ═══════════════════════════════════════════════════════════
#  STUBS (unchanged)
# ═══════════════════════════════════════════════════════════

@app.post("/api/detect-coordination")
async def api_detect_coordination(request: Request):
    try:
        data = await request.json()
        return {
            "brigading_detected": False,
            "cluster_count": 0,
            "message": "Pattern detection clustering stub successful."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/support-contacts")
async def api_support_contacts():
    try:
        return {
            "status": "ok",
            "contacts": [
                {"name": "iCall", "type": "Mental Health", "contact": "1234"}
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
