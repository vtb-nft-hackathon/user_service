import datetime

from pydantic import BaseModel


class UserJobPositionResponse(BaseModel):
    id: int
    position: str
    started_at: datetime.date
    ended_at: datetime.date | None
