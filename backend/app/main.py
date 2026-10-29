from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, projects, testcases, runs, ai, ci, payloads, defects

# Create database tables automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WebForge API",
    description="Automated Functional Testing Platform Backend",
    version="1.0.0"
)

# Configure CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register All Core and Feature Routers
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(testcases.router)
app.include_router(runs.router)
app.include_router(ai.router)
app.include_router(ci.router)
app.include_router(payloads.router)
app.include_router(defects.router)

@app.get("/ping")
def ping():
    return {"status": "ok", "message": "WebForge Backend is running!"}