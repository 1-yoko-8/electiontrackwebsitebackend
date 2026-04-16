from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db.session import get_session
from app.models.gpsping import GPSPing
from app.schemas.gpsping import LocationPingRequest

router = APIRouter()


@router.post("/location-ping")
def upsert_location_ping(
    ping: LocationPingRequest,
    session: Session = Depends(get_session),
):
    try:
        # 🚫 Reject invalid coords
        if ping.latitude == 0.0 and ping.longitude == 0.0:
            raise HTTPException(status_code=400, detail="Invalid location")

        if ping.timestamp.tzinfo is None:
            raise HTTPException(status_code=400, detail="Timestamp must be timezone-aware")

        # 🔍 Check if user already exists
        existing = session.exec(
            select(GPSPing).where(GPSPing.userId == ping.userId)
        ).first()

        if existing:
            # ✅ UPDATE
            existing.timestamp = ping.timestamp
            existing.latitude = ping.latitude
            existing.longitude = ping.longitude
            existing.currentTask = ping.currentTask

            print(f"UPDATED: {existing.userId}")

        else:
            # ✅ INSERT
            new_ping = GPSPing(
                userId=ping.userId,
                timestamp=ping.timestamp,
                latitude=ping.latitude,
                longitude=ping.longitude,
                currentTask=ping.currentTask,
            )
            session.add(new_ping)

            print(f"CREATED: {ping.userId}")

        session.commit()

        return {"status": "success"}

    except Exception as e:
        session.rollback()
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Failed to upsert GPS ping")