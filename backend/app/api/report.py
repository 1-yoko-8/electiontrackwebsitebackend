from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.report import Report
from app.schemas.report import ReportResponse
from app.core.dependencies import get_current_admin

router = APIRouter()


@router.get("/reports", response_model=List[ReportResponse])
def get_reports(
    report_date: Optional[date] = Query(None),
    session: Session = Depends(get_session),
    admin=Depends(get_current_admin)
):
    stmt = select(Report)

    if report_date:
        stmt = stmt.where(Report.report_date == report_date)

    stmt = stmt.order_by(Report.username.asc())

    results = session.exec(stmt).all()

    return [ReportResponse.model_validate(r) for r in results]