from pydantic import BaseModel

from app.common.models.skill.model import SkillDomain


class UserSkillBase(BaseModel):
    user_id: int
    skill_id: int


class UserSkillDomain(UserSkillBase):
    id: int
    skill: SkillDomain
