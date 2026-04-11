from datetime import date
from pydantic import BaseModel

class TaskDayRequest(BaseModel):
    date: date