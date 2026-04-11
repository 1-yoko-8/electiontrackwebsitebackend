from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class TaskEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    taskName: str       # Collected | Started | Reached | Handed Over
    timestamp: datetime
    latitude: float
    longitude: float
    location: Optional[str] = None

    class Config:        # used in case of custom datatype i.e. type not present in Pydantic
        arbitrary_types_allowed = True