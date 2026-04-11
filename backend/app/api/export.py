from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import date
from fastapi.responses import StreamingResponse
from io import BytesIO
from openpyxl import Workbook

from backend.app.db.session import get_session
from backend.app.models.taskevent import TaskEvent

router = APIRouter()

@router.get("/export-tasks/{task_date}")
def export_tasks(task_date: date, session: Session = Depends(get_session)):
    # Fetch all events
    events = session.exec(select(TaskEvent)).all()

    # Filter by selected date
    filtered_events = [e for e in events if e.timestamp.date() == task_date]

    if not filtered_events:
        raise HTTPException(
            status_code=404,
            detail="No task events found for this date"
        )

    # Create Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Task Events"

    # Header
    ws.append(["ID", "Username", "Task Name", "Timestamp", "Latitude", "Longitude", "Location"])

    # Data
    for e in filtered_events:
        ws.append([
            e.id,
            e.username,
            e.taskName,
            e.timestamp.strftime("%Y-%m-%d %H:%M:%S"),  # format nicely
            e.latitude,
            e.longitude,
            e.location or ""
        ])

    # Save to memory
    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=tasks_{task_date}.xlsx"
        }
    )