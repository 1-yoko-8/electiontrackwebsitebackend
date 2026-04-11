from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlmodel import Session, select

from backend.app.core.config import settings
from backend.app.db.session import get_session
from backend.app.models.admin import Admin

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")


def get_current_admin(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
):

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        username = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    admin = session.exec(
        select(Admin).where(Admin.username == username)
    ).first()

    if not admin:
        raise HTTPException(status_code=401, detail="Admin not found")

    return admin