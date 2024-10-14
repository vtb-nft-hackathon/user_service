import datetime

from pydantic import BaseModel


class UserJobPosition(BaseModel):
    user_job_id: int
    position: str
    started_at: datetime.date
    ended_at: datetime.date | None


class UserJobPositionDomain(UserJobPosition):
    id: int
