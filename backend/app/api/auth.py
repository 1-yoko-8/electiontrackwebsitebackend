from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.admin import Admin
from app.core.security import verify_password, create_access_token
from app.core.dependencies import get_current_admin
from app.schemas.auth import LoginRequest,LogoutRequest

router = APIRouter()


@router.post("/login")
def admin_login(data: LoginRequest, session: Session = Depends(get_session)):

    admin = session.exec(
        select(Admin).where(Admin.username == data.username)
    ).first()

    if not admin:
        raise HTTPException(status_code=401, detail="No such admin exits")

    if not verify_password(data.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    session.add(admin)
    session.commit()

    token = create_access_token({"sub": admin.username})

    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout")
def admin_logout(data: LogoutRequest, session: Session = Depends(get_session)):

    admin = session.exec(
        select(Admin).where(Admin.username == data.username)
    ).first()

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    admin.is_logged_in = False
    session.add(admin)
    session.commit()

    return {"message": "Logged out successfully"}