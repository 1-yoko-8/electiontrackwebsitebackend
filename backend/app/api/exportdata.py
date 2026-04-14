from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import date
from fastapi.responses import StreamingResponse
from io import BytesIO
from openpyxl import Workbook
from sqlalchemy import func, or_

from app.db.session import get_session
from app.models.report import Report
from app.core.dependencies import get_current_admin

router = APIRouter()

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.task_event import TaskEvent
from app.models.report import Report
from app.core.deps import get_current_user
from app.schemas.tasks import TaskEventRequest

router = APIRouter()


@router.get("/export-tasks")
def export_tasks(session: Session = Depends(get_session), admin = Depends(get_current_admin)):

    # ---------------- DB FILTER ----------------
    stmt = select(Report)
    reports = session.exec(stmt).all()

    if not reports:
        raise HTTPException(
            status_code=404,
            detail="No reports found"
        )

    # ---------------- SORT ----------------
    reports.sort(key=lambda r: r.username)

    # ---------------- CREATE EXCEL ----------------
    wb = Workbook()
    ws = wb.active
    ws.title = "Reports"

    ws.append([
        "Mobile Party",
        "Name",
        "Rank",
        "Contact No.",
        "Collected",
        "Collected Time",
        "Handed Over",
        "Handed Over Time",
    ])

    for r in reports:
        ws.append([
            r.username,
            r.name or "N/A",
            r.rank or "N/A",
            r.contact_number or "N/A",

            r.ballot_box_collected_status,
            r.collected_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            if r.collected_timestamp else "N/A",

            r.ballot_box_handed_over_status,
            r.handed_over_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            if r.handed_over_timestamp else "N/A",
        ])

    # ---------------- STREAM FILE ----------------
    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)

    from datetime import datetime
    filename = f"reports_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )