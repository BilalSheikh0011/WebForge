import time
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["CI/CD Pipeline Integration"])

CI_RUN_DATABASE = {}

class CIRunRequest(BaseModel):
    project_id: int = 1
    suite_id: int = 1
    environment: str = "staging"

@router.post("/run")
def trigger_ci_run(req: CIRunRequest, x_api_key: Optional[str] = Header(None)):
    run_id = f"ci_build_{int(time.time())}"
    
    # Store mocked successful pipeline run
    CI_RUN_DATABASE[run_id] = {
        "run_id": run_id,
        "status": "completed",
        "environment": req.environment,
        "summary": {
            "total_tests": 8,
            "passed": 8,
            "failed": 0,
            "duration_ms": 3420
        },
        "exit_code": 0
    }
    
    return {"message": "CI Run Initiated", "run_id": run_id, "status": "completed"}

@router.get("/run/{run_id}")
def check_ci_run_status(run_id: str):
    run = CI_RUN_DATABASE.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="CI Run not found")
    return run