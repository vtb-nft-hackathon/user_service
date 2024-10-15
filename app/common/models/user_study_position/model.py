import datetime

from pydantic import BaseModel


class UserStudyPositionBase(BaseModel):
    user_study_id: int
    position: str
    started_at: datetime.date
    ended_at: datetime.date | None


class UserStudyPositionDomain(UserStudyPositionBase):
    id: int
