from sqlmodel import SQLModel, Field
from datetime import date

class DayConfig(SQLModel, table=True):
    allowedDays: date = Field(primary_key=True)