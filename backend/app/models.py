from sqlalchemy import Column, Integer, String, Boolean, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="Tester")  # Admin, Tester, Viewer
    created_at = Column(DateTime, default=datetime.utcnow)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    target_url = Column(String(255), nullable=False)
    owner_id = Column(Integer, default=1)
    
    test_cases = relationship("TestCase", back_populates="project", cascade="all, delete-orphan")

class TestCase(Base):
    __tablename__ = "test_cases"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    code = Column(String(20), index=True)  # e.g., TC-042
    name = Column(String(200), nullable=False)
    precondition = Column(Text, default="")
    priority = Column(String(20), default="Medium")  # Critical, High, Medium, Low
    test_type = Column(String(50), default="Functional")
    feature = Column(String(100), default="General")
    baseline_screenshot_b64 = Column(Text, nullable=True)  # For Visual Regression
    
    project = relationship("Project", back_populates="test_cases")
    steps = relationship("TestStep", back_populates="test_case", cascade="all, delete-orphan")
    runs = relationship("TestRun", back_populates="test_case", cascade="all, delete-orphan")

class TestStep(Base):
    __tablename__ = "test_steps"
    id = Column(Integer, primary_key=True, index=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"))
    order = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)
    selector_type = Column(String(20), default="")
    selector = Column(String(255), default="")
    value = Column(String(255), default="")
    expected = Column(String(255), default="")
    
    test_case = relationship("TestCase", back_populates="steps")

class TestRun(Base):
    __tablename__ = "test_runs"
    id = Column(Integer, primary_key=True, index=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=True)
    environment = Column(String(50), default="Staging")
    status = Column(String(20), default="PENDING")  # PASS, FAIL
    duration_ms = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    
    test_case = relationship("TestCase", back_populates="runs")

class Defect(Base):
    __tablename__ = "defects"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), default="DEF-001")
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    severity = Column(String(20), default="Major")  # Critical, Major, Minor, Trivial
    status = Column(String(20), default="New")  # New, In Progress, Fixed, Verified, Closed
    test_case_id = Column(Integer, nullable=True)
    step_index = Column(Integer, nullable=True)
    screenshot_b64 = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)