from sqlmodel import Session
from passlib.context import CryptContext
from backend.app.models import Admin
from backend.app.db.session import engine

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin():
    with Session(engine) as session:
        admin = Admin(
            username="admin",
            password_hash=pwd_context.hash("admin123"),
        )
        session.add(admin)
        session.commit()
        print("Admin created!")

create_admin()