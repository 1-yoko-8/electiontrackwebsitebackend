from sqlmodel import SQLModel, Field
from typing import Optional


class PollingStation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    dataset_id: Optional[int] = None
    s_no: Optional[int] = None

    username: str = Field(index=True, nullable=False)  # required fields
    location_name: str

    polling_areas: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None