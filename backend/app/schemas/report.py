from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import Optional


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    name: Optional[str]
    rank: Optional[str]
    contact_number: Optional[str]

    report_date: date

    ballot_box_collected_status: str
    collected_timestamp: Optional[datetime]

    ballot_box_handed_over_status: str
    handed_over_timestamp: Optional[datetime]