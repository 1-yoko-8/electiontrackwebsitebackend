from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Officer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)  # only required field
    name: Optional[str] = None
    rank: Optional[str] = None
    police_station: Optional[str] = None
    sub_division: Optional[str] = None
    mobile_station: Optional[str] = None
    cugphno: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)