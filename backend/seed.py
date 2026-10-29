from app.database import SessionLocal, engine, Base
from app.models import User, Project
from app.security import get_password_hash

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Seed default users
if not db.query(User).filter_by(email="admin@webforge.io").first():
    db.add(User(name="Admin User", email="admin@webforge.io", password_hash=get_password_hash("Admin123!"), role="Admin"))
    db.add(User(name="Tester User", email="tester@webforge.io", password_hash=get_password_hash("Tester123!"), role="Tester"))
    db.add(User(name="Viewer User", email="viewer@webforge.io", password_hash=get_password_hash("Viewer123!"), role="Viewer"))

# Seed sample project
if not db.query(Project).first():
    db.add(Project(
        name="SauceDemo E-Commerce",
        description="Demo project for testing authentication & cart flows",
        target_url="https://www.saucedemo.com",
        owner_id=1
    ))

db.commit()
db.close()
print("Database successfully seeded!")