from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func

from backend.app.db.session import get_session
from backend.app.models.taskevent import TaskEvent
from backend.app.models.polling_station import PollingStation
from backend.app.models.officer import Officer
from backend.app.core.dependencies import get_current_admin

router = APIRouter()

@router.get("/progress")
def get_progress(
    admin=Depends(get_current_admin),
    session: Session = Depends(get_session)
):

    # ---- Total Users ----
    total_workers = session.exec(
        select(func.count()).select_from(Officer)
    ).one()

    # ---- Collected ----
    collected_completed = session.exec(
        select(func.count(func.distinct(TaskEvent.username)))
        .where(TaskEvent.taskName == "COLLECTED")
    ).one()

    # ---- Started ----
    started_completed = session.exec(
        select(func.count(func.distinct(TaskEvent.username)))
        .where(TaskEvent.taskName == "STARTED")
    ).one()

    # ---- Handed Over ----
    handed_completed = session.exec(
        select(func.count(func.distinct(TaskEvent.username)))
        .where(TaskEvent.taskName == "Handed_OVER")
    ).one()

    # ---- Locations (Reached) ----
    total_locations = session.exec(
        select(func.count()).select_from(PollingStation)
    ).one()

    reached_completed = session.exec(
        select(func.count(func.distinct(TaskEvent.location)))
        .where(TaskEvent.taskName == "REACHED")
        .where(TaskEvent.location.isnot(None))   # safety
        .where(TaskEvent.location != "")
    ).one()

    # ---- Response ----
    return {
        "collected": {
            "total": total_workers,
            "completed": collected_completed,
            "pending": total_workers - collected_completed
        },
        "started": {
            "total": total_workers,
            "completed": started_completed,
            "pending": total_workers - started_completed
        },
        "reached": {
            "totalLocations": total_locations,
            "covered": reached_completed,
            "pending": total_locations - reached_completed
        },
        "handedOver": {
            "total": total_workers,
            "completed": handed_completed,
            "pending": total_workers - handed_completed
        },
    }