from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.app.schemas.taskday import TaskDayRequest
from backend.app.models.taskday import DayConfig
from backend.app.db.session import get_session

router = APIRouter()

@router.post("/set-task-day")
def set_task_day(
    payload: TaskDayRequest,
    session: Session = Depends(get_session)
):
    task_date = payload.date

    # 🔍 Check if already exists
    existing = session.exec(
        select(DayConfig).where(DayConfig.allowedDays == task_date)
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Task day already exists"
        )

    # ✅ Create new entry
    new_day = DayConfig(allowedDays=task_date)

    session.add(new_day)
    session.commit()
    session.refresh(new_day)

    return {
        "message": "Task day set",
        "date": new_day.allowedDays
    }