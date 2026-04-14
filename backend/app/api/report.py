from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.report import Report
from app.schemas.report import ReportResponse
from app.core.dependencies import get_current_admin

router = APIRouter()


@router.get("/reports", response_model=List[ReportResponse])
def get_reports(session: Session = Depends(get_session), admin = Depends(get_current_admin)):
    stmt = select(Report).order_by(Report.username)
    results = session.exec(stmt).all()

    return [ReportResponse.model_validate(r) for r in results]