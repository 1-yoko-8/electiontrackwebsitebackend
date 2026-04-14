from typing import Optional
from datetime import datetime, date
from sqlmodel import SQLModel, Field


class Report(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # --- User Info ---
    username: str = Field(index=True)
    name: Optional[str] = None
    rank: Optional[str] = None
    contact_number: Optional[str] = None

    # --- IMPORTANT: REPORT DATE ---
    report_date: date = Field(index=True)

    # --- Assignment Info ---
    polling_stations: int = Field(default=0, ge=0)
    polling_locations: int = Field(default=0, ge=0)
    ballot_boxes: int = Field(default=0, ge=0)

    # --- Collection ---
    ballot_box_collected_status: str = Field(default="Not Completed")
    collected_timestamp: Optional[datetime] = None

    # --- Handed Over ---
    ballot_box_handed_over_status: str = Field(default="Not Completed")
    handed_over_timestamp: Optional[datetime] = None