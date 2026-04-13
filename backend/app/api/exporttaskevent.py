from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import date
from fastapi.responses import StreamingResponse
from io import BytesIO
from openpyxl import Workbook

from app.db.session import get_session
from app.models.report import Report

router = APIRouter()


@router.get("/export-tasks/{task_date}")
def export_tasks(task_date: date, session: Session = Depends(get_session)):

    # ---------------- FETCH REPORTS ----------------
    reports = session.exec(select(Report)).all()

    # ---------------- FILTER BY DATE ----------------
    # ⚠️ assumes Report has `timestamp` field
    filtered = [
        r for r in reports
        if r.timestamp.date() == task_date
    ]

    if not filtered:
        raise HTTPException(
            status_code=404,
            detail="No reports found for this date"
        )

    # ---------------- SORT BY USERNAME ----------------
    filtered.sort(key=lambda r: r.username)

    # ---------------- CREATE EXCEL ----------------
    wb = Workbook()
    ws = wb.active
    ws.title = "Reports"

    # HEADER
    ws.append([
        "Username",
        "Phone Number",
        "Ballot Box Status",
        "Timestamp"
    ])

    # DATA
    for r in filtered:
        ws.append([
            r.username,
            getattr(r, "phone_number", ""),
            r.ballot_box_handed_over_status,
            r.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        ])

    # ---------------- STREAM FILE ----------------
    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=reports_{task_date}.xlsx"
        }
    )