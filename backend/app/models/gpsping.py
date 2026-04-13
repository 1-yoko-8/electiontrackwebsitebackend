from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime

class GPSPing(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    userId: str = Field(index=True)
    timestamp: datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )
    latitude: float
    longitude: float
    currentTask: str