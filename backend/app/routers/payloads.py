import string
import random
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/data-generator", tags=["Synthetic Data Generator"])

class PayloadRequest(BaseModel):
    payload_type: str  # "boundary_string", "email_boundary", "sql_injection", "xss"
    length: int = 255

@router.post("/generate")
def generate_payload(req: PayloadRequest):
    ptype = req.payload_type
    length = max(1, min(req.length, 2000))  # limit to safe boundary

    if ptype == "boundary_string":
        # Generates exact length boundary alphanumeric text
        chars = string.ascii_letters + string.digits
        payload = "".join(random.choice(chars) for _ in range(length))
    
    elif ptype == "email_boundary":
        # Standard RFC max email length is 254 chars: local + @ + domain
        prefix_len = max(1, length - 12)
        local_part = "".join(random.choice(string.ascii_lowercase) for _ in range(prefix_len))
        payload = f"{local_part}@example.com"
    
    elif ptype == "sql_injection":
        samples = [
            "' OR '1'='1' --",
            "admin' --",
            "1' UNION SELECT 1, 'admin', 'pass' --",
            "' OR ''='"
        ]
        payload = random.choice(samples)
    
    elif ptype == "xss":
        samples = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert(1)>",
            "\"><svg onload=alert(1)>"
        ]
        payload = random.choice(samples)
    
    else:
        payload = f"test_{random.randint(1000, 9999)}"

    return {
        "status": "success",
        "payload_type": ptype,
        "length": len(payload),
        "payload": payload
    }