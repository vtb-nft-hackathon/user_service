from pydantic import BaseModel

from app.common.models.skill.contracts import SkillResponse


class UserSkillResponse(BaseModel):
    id: int
    skill: SkillResponse
