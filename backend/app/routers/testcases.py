from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from ..database import get_db
from ..models import TestCase, TestStep, Project
from ..services.generator import generate_script

router = APIRouter(prefix="/testcases", tags=["Test Cases"])

class StepSchema(BaseModel):
    order: int
    action: str
    selector_type: Optional[str] = ""
    selector: Optional[str] = ""
    value: Optional[str] = ""
    expected: Optional[str] = ""

class TestCaseCreate(BaseModel):
    project_id: int
    code: str
    name: str
    precondition: Optional[str] = ""
    priority: str = "Medium"
    test_type: str = "Functional"
    feature: Optional[str] = "General"
    steps: List[StepSchema]

@router.post("")
def create_test_case(payload: TestCaseCreate, db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == payload.project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    tc = TestCase(
        project_id=payload.project_id,
        code=payload.code,
        name=payload.name,
        precondition=payload.precondition,
        priority=payload.priority,
        test_type=payload.test_type,
        feature=payload.feature
    )
    db.add(tc)
    db.commit()
    db.refresh(tc)

    for s in payload.steps:
        step_entry = TestStep(
            test_case_id=tc.id,
            order=s.order,
            action=s.action,
            selector_type=s.selector_type,
            selector=s.selector,
            value=s.value,
            expected=s.expected
        )
        db.add(step_entry)

    db.commit()
    return {"message": "Test Case created successfully", "id": tc.id}

@router.get("/project/{project_id}")
def get_project_cases(project_id: int, db: Session = Depends(get_db)):
    return db.query(TestCase).filter(TestCase.project_id == project_id).all()

@router.post("/preview")
def preview_script(payload: TestCaseCreate):
    code = generate_script(payload.dict(), base_url="https://www.saucedemo.com")
    return {"script": code}