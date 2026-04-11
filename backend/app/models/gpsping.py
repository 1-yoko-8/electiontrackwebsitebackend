from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class GPSPing(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    userId: str = Field(index=True)
    timestamp: datetime
    latitude: float
    longitude: float
    currentTask: str