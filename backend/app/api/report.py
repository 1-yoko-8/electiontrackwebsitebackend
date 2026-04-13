from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.report import Report
from app.schema.report import ReportResponse

router = APIRouter()


@router.get("/reports", response_model=List[ReportResponse])
def get_reports(session: Session = Depends(get_session)):
    stmt = select(Report).order_by(Report.username)
    results = session.exec(stmt).all()

    return [ReportResponse.model_validate(r) for r in results]