from pydantic import BaseModel


class SkillBase(BaseModel):
    name: str


class SkillDomain(SkillBase):
    id: int
