from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from datetime import datetime
from app.db.session import get_session
from app.models.gpsping import GPSPing
from app.schemas.gpsping import LocationPingRequest  # your request model

router = APIRouter()


@router.post("/gps/latest")
def create_gps_ping(
    ping: LocationPingRequest,
    session: Session = Depends(get_session),
):
    try:
        # 🚫 Reject invalid coordinates
        if ping.latitude == 0.0 and ping.longitude == 0.0:
            raise HTTPException(status_code=400, detail="Invalid location (0,0)")

        # ✅ Ensure timestamp is timezone-aware
        if ping.timestamp.tzinfo is None:
            raise HTTPException(status_code=400, detail="Timestamp must be timezone-aware")

        # ✅ Create DB object
        db_ping = GPSPing(
            userId=ping.userId,
            timestamp=ping.timestamp,
            latitude=ping.latitude,
            longitude=ping.longitude,
            currentTask=ping.currentTask,
        )

        # ✅ Insert into DB
        session.add(db_ping)
        session.commit()
        session.refresh(db_ping)

        # 🔍 Debug log
        print(f"NEW PING: {db_ping.userId} | {db_ping.timestamp}")

        return {"status": "success"}

    except Exception as e:
        session.rollback()
        print("ERROR inserting GPS ping:", str(e))
        raise HTTPException(status_code=500, detail="Failed to insert GPS ping")