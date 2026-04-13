from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.report import Report

router = APIRouter()


@router.get("/reports")
def get_reports(session: Session = Depends(get_session)):
    stmt = select(Report)
    results = session.exec(stmt).all()

    return [
        {
            "username": r.username,
            "phone_number": r.phone_number or None,
            "ballot_box_handed_over_status": r.ballot_box_handed_over_status,
        }
        for r in results
    ]