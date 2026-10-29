from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from ..database import get_db
from ..models import Project

router = APIRouter(prefix="/projects", tags=["Projects"])

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    target_url: str

class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    target_url: str
    class Config:
        from_attributes = True

@router.get("", response_model=List[ProjectOut])
def get_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()

@router.post("", response_model=ProjectOut)
def create_project(proj: ProjectCreate, db: Session = Depends(get_db)):
    new_proj = Project(
        name=proj.name,
        description=proj.description,
        target_url=proj.target_url,
        owner_id=1
    )
    db.add(new_proj)
    db.commit()
    db.refresh(new_proj)
    return new_proj


from ..models import TestRun, Defect

@router.get("/{project_id}/dashboard")
def get_project_dashboard(project_id: int, db: Session = Depends(get_db)):
    # Fetch recent runs
    runs = db.query(TestRun).order_by(TestRun.id.desc()).limit(10).all()
    
    # Calculate pass rate trend
    trend_labels = [f"Run #{r.id}" for r in reversed(runs)]
    trend_data = [100 if r.status == "PASS" else 0 for r in reversed(runs)]
    
    # Calculate defects distribution by severity
    defects = db.query(Defect).all()
    severity_counts = {"Critical": 0, "Major": 0, "Minor": 0, "Trivial": 0}
    for d in defects:
        if d.severity in severity_counts:
            severity_counts[d.severity] += 1
        else:
            severity_counts["Major"] += 1

    # Recent activities
    recent_activity = []
    for r in runs[:5]:
        recent_activity.append({
            "id": r.id,
            "status": r.status,
            "duration": f"{r.duration_ms}ms",
            "time": r.started_at.strftime("%H:%M:%S") if r.started_at else "Just now"
        })

    return {
        "total_runs": len(runs),
        "open_defects": len(defects),
        "trend": {
            "labels": trend_labels if trend_labels else ["Run #1", "Run #2"],
            "data": trend_data if trend_data else [100, 100]
        },
        "defects_by_severity": severity_counts,
        "recent_activity": recent_activity
    }
