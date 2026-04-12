from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Report(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # --- User Info ---
    username: str = Field(index=True, unique=True)
    name: str
    rank: str
    contact_number: str = Field(min_length=10, max_length=15)

    # --- Assignment Info ---
    polling_stations: int = Field(ge=0)
    polling_locations: int = Field(ge=0)
    ballot_boxes: int = Field(ge=0)

    # --- Collection ---
    ballot_box_collected_status: str = Field(default="Not Completed")
    collected_timestamp: Optional[datetime] = Field(default=None)

    # --- Handed Over ---
    ballot_box_handed_over_status: str = Field(default="Not Completed")
    handed_over_timestamp: Optional[datetime] = Field(default=None)