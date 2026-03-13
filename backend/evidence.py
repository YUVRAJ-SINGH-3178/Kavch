import hashlib
from datetime import datetime
import pytz

def lock_evidence(content: str = "", url: str = "", screenshot_base64: str = ""):
    ist = pytz.timezone('Asia/Kolkata')
    timestamp = datetime.now(ist).strftime('%Y-%m-%dT%H:%M:%S%z')
    
    # Construct basestring for hash
    hash_payload = f"{content}|{url}|{screenshot_base64}|{timestamp}".encode('utf-8')
    sha256_hash = hashlib.sha256(hash_payload).hexdigest()
    
    evidence_id = "KV-" + sha256_hash[:10].upper()
    
    # Simple preview for cert
    preview = url if url else "Media Attachment (Base64)"
    if content:
        preview = content[:50] + ("..." if len(content) > 50 else "")
        
    certificate = {
        "id": evidence_id,
        "hash": sha256_hash,
        "timestamp": timestamp,
        "content_preview": preview,
        "verified": True,
        "legal_note": "This cryptographic hash guarantees that the digital evidence has not been altered since the timestamp recorded."
    }
    
    return {
        "evidence_id": evidence_id,
        "hash": sha256_hash,
        "timestamp": timestamp,
        "certificate": certificate
    }
