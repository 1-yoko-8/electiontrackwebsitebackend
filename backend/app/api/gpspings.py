from sqlalchemy import func
from sqlmodel import select, Session
from fastapi import APIRouter, Depends

from app.db.session import get_session
from app.models.gpsping import GPSPing
from app.core.dependencies import get_current_admin

router = APIRouter()

@router.get("/gps/latest")
def get_latest_gps(
    session: Session = Depends(get_session),
    admin = Depends(get_current_admin)
):
    # Subquery to get latest timestamp per user
    subquery = (
        select(
            GPSPing.userId,
            func.max(GPSPing.timestamp).label("max_time")
        )
        .group_by(GPSPing.userId)
        .subquery()
    )

    # Join with main table to get full row
    query = (
        select(GPSPing)
        .join(
            subquery,
            (GPSPing.userId == subquery.c.userId) &
            (GPSPing.timestamp == subquery.c.max_time)
        )
    )

    results = session.exec(query).all()

    return [r.model_dump() for r in results]