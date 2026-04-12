from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


# ---------------- CREATE ----------------
class ReportCreate(BaseModel):
    username: str
    name: str
    rank: str
    contact_number: str = Field(min_length=10, max_length=15)

    polling_stations: int = Field(ge=0)
    polling_locations: int = Field(ge=0)
    ballot_boxes: int = Field(ge=0)


# ---------------- UPDATE ----------------
class ReportUpdateCollected(BaseModel):
    ballot_box_collected_status: Optional[Literal["Completed", "Not Completed"]] = None
    timestamp: datetime

class ReportUpdateHandedOver(BaseModel):
    ballot_box_handed_over_status: Optional[Literal["Completed", "Not Completed"]] = None
    timestamp: datetime


# ---------------- RESPONSE ----------------
class ReportResponse(BaseModel):
    id: int

    username: str
    name: str
    rank: str
    contact_number: str

    polling_stations: int
    polling_locations: int
    ballot_boxes: int

    ballot_box_collected_status: str
    collected_timestamp: Optional[datetime]

    ballot_box_handed_over_status: str
    handed_over_timestamp: Optional[datetime]

    class Config:
        from_attributes = True