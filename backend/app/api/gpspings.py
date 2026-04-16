from sqlmodel import select, func
from app.models.gps_ping import GPSPing

@router.get("/gps/latest")
def get_latest_gps(session: Session = Depends(get_session)):
    subquery = (
        select(
            GPSPing.userId,
            func.max(GPSPing.timestamp).label("latest_ts")
        )
        .group_by(GPSPing.userId)
        .subquery()
    )

    result = session.exec(
        select(GPSPing).join(
            subquery,
            (GPSPing.userId == subquery.c.userId) &
            (GPSPing.timestamp == subquery.c.latest_ts)
        )
    ).all()

    return result