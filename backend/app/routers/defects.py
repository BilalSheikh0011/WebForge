from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from ..database import get_db
from ..models import Defect

router = APIRouter(prefix="/defects", tags=["Defects"])

class DefectCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    severity: Optional[str] = "Major"
    test_case_id: Optional[int] = 1
    step_index: Optional[int] = 1
    screenshot_b64: Optional[str] = None
    user_id: Optional[int] = None

@router.get("")
def list_defects(user_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    query = db.query(Defect)
    if user_id is not None and hasattr(Defect, "user_id"):
        query = query.filter(Defect.user_id == user_id)
    return query.all()

@router.post("")
def create_defect(payload: DefectCreate, db: Session = Depends(get_db)):
    defect_count = db.query(Defect).count()
    code = f"DEF-{defect_count + 1:03d}"
    
    new_defect = Defect(
        code=code,
        title=payload.title,
        description=payload.description,
        severity=payload.severity or "Major",
        status="Open",
        test_case_id=payload.test_case_id,
        screenshot_b64=payload.screenshot_b64
    )
    if hasattr(new_defect, "user_id") and payload.user_id:
        new_defect.user_id = payload.user_id

    db.add(new_defect)
    db.commit()
    db.refresh(new_defect)
    return new_defect