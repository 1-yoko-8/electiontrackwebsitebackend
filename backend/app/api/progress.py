from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.db.session import get_session
from app.models.report import Report
from app.core.dependencies import get_current_admin
from app.core.config import settings

router = APIRouter()

IST = ZoneInfo("Asia/Kolkata")


@router.get("/dashboard")
def get_dashboard(
    admin=Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    # ---------------- TIME SETUP (FROM .env) ---------------- #
    polling_date = settings.POLLING_DATE

    start_today = datetime.combine(polling_date, datetime.min.time(), tzinfo=IST)
    end_today = start_today + timedelta(days=1)

    start_day_before = start_today - timedelta(days=1)

    # ---------------- DISTRICT DETAILS ---------------- #
    total_polling_locations = session.exec(
        select(func.sum(Report.polling_locations))
    ).one_or_none() or 0

    total_polling_stations = session.exec(
        select(func.sum(Report.polling_stations))
    ).one_or_none() or 0

    total_mobile_parties = session.exec(
        select(func.count(Report.id))
    ).one_or_none() or 0

    total_ballot_boxes = session.exec(
        select(func.sum(Report.ballot_boxes))
    ).one_or_none() or 0

    # ---------------- HELPER FUNCTION ---------------- #
    def get_status_data(time_filter):

        collected_count = session.exec(
            select(func.count(Report.id))
            .where(Report.ballot_box_collected_status == "Completed")
            .where(Report.collected_timestamp.isnot(None))
            .where(*time_filter(Report.collected_timestamp))
        ).one_or_none() or 0

        collected_boxes = session.exec(
            select(func.sum(Report.ballot_boxes))
            .where(Report.ballot_box_collected_status == "Completed")
            .where(Report.collected_timestamp.isnot(None))
            .where(*time_filter(Report.collected_timestamp))
        ).one_or_none() or 0

        handed_count = session.exec(
            select(func.count(Report.id))
            .where(Report.ballot_box_handed_over_status == "Completed")
            .where(Report.handed_over_timestamp.isnot(None))
            .where(*time_filter(Report.handed_over_timestamp))
        ).one_or_none() or 0

        handed_boxes = session.exec(
            select(func.sum(Report.ballot_boxes))
            .where(Report.ballot_box_handed_over_status == "Completed")
            .where(Report.handed_over_timestamp.isnot(None))
            .where(*time_filter(Report.handed_over_timestamp))
        ).one_or_none() or 0

        return {
            "collectedAndDeparted": collected_count,
            "ballotBoxesCollected": collected_boxes,
            "partiesInTransit": max(0, collected_count - handed_count),
            "partiesReached": handed_count,
            "ballotBoxesHandedOver": handed_boxes,
        }

    # ---------------- TIME FILTERS ---------------- #
    def is_today(column):
        return [column >= start_today, column < end_today]

    def is_day_before(column):
        return [column >= start_day_before, column < start_today]

    # ---------------- RESPONSE ---------------- #
    return {
        "districtDetails": {
            "totalPollingLocations": total_polling_locations,
            "totalPollingStations": total_polling_stations,
            "totalMobileParties": total_mobile_parties,
            "totalBallotBoxes": total_ballot_boxes,
        },
        "dayBeforeStatus": get_status_data(is_day_before),
        "pollingDayStatus": get_status_data(is_today),
    }