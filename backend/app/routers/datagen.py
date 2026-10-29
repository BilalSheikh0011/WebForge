import random
import string
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/data-generator", tags=["Synthetic Data Generator"])

class GenerateRequest(BaseModel):
    data_type: str
    length: int = 255

@router.post("/generate")
def generate_synthetic_payload(req: GenerateRequest):
    if req.data_type == "boundary_string":
        chars = string.ascii_letters + string.digits
        val = "".join(random.choice(chars) for _ in range(req.length))
        desc = f"Boundary string of length {req.length}"
    elif req.data_type == "sql_injection":
        val = "' OR '1'='1' --"
        desc = "SQL Injection payload"
    elif req.data_type == "xss":
        val = "<script>alert('XSS')</script>"
        desc = "XSS payload"
    elif req.data_type == "email_boundary":
        val = f"{''.join(random.choice(string.ascii_lowercase) for _ in range(240))}@domain.com"
        desc = "254-character email boundary"
    else:
        val = "test_value"
        desc = "Default"

    return {"payload": val, "description": desc}