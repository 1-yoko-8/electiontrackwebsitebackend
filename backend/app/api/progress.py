from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from datetime import timedelta

from app.db.session import get_session
from app.models.report import Report
from app.core.dependencies import get_current_admin
from app.core.config import settings

router = APIRouter()


@router.get("/dashboard")
def get_dashboard(
    admin=Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    # ---------------- STRICT DATE BASED ---------------- #
    polling_date = settings.POLLING_DATE  # must be datetime.date

    today_date = polling_date
    yesterday_date = polling_date - timedelta(days=1)

    # ---------------- HELPER ---------------- #
    def get_status_data(target_date):

        collected_count = session.exec(
            select(func.count(Report.id))
            .where(Report.ballot_box_collected_status == "Completed")
            .where(Report.report_date == target_date)
        ).one_or_none() or 0

        collected_boxes = session.exec(
            select(func.sum(Report.ballot_boxes))
            .where(Report.ballot_box_collected_status == "Completed")
            .where(Report.report_date == target_date)
        ).one_or_none() or 0

        handed_count = session.exec(
            select(func.count(Report.id))
            .where(Report.ballot_box_handed_over_status == "Completed")
            .where(Report.report_date == target_date)
        ).one_or_none() or 0

        handed_boxes = session.exec(
            select(func.sum(Report.ballot_boxes))
            .where(Report.ballot_box_handed_over_status == "Completed")
            .where(Report.report_date == target_date)
        ).one_or_none() or 0

        return {
            "collectedAndDeparted": collected_count,
            "ballotBoxesCollected": collected_boxes,
            "partiesInTransit": max(0, collected_count - handed_count),
            "partiesReached": handed_count,
            "ballotBoxesHandedOver": handed_boxes,
        }

    # ---------------- RESPONSE ---------------- #
    return {
        "districtDetails": {
            "totalPollingLocations": 854,
            "totalPollingStations": 1645,
            "totalMobileParties": 164,
            "totalBallotBoxes": 854,
        },
        "dayBeforeStatus": get_status_data(yesterday_date),
        "pollingDayStatus": get_status_data(today_date),
    }