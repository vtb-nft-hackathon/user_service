import datetime

from pydantic import BaseModel


class UserStudyPositionResponse(BaseModel):
    id: int
    position: str
    started_at: datetime.date
    ended_at: datetime.date | None
