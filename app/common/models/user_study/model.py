from pydantic import BaseModel

from app.common.models.user_study_position.model import UserStudyPositionDomain


class UserStudyBase(BaseModel):
    user_id: int
    name: str


class UserStudyDomain(UserStudyBase):
    id: int
    positions: list[UserStudyPositionDomain]
