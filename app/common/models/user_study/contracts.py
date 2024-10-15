from pydantic import BaseModel

from app.common.models.user_study_position.contracts import UserStudyPositionResponse


class UserStudyResponse(BaseModel):
    id: int
    name: str
    positions: list[UserStudyPositionResponse]
