from pydantic import BaseModel

from app.common.models.job.model import JobDomain
from app.common.models.user_job_position.model import UserJobPositionDomain


class UserJobBase(BaseModel):
    user_id: int
    job_id: int


class UserJobDomain(UserJobBase):
    id: int
    job: JobDomain
    positions: list[UserJobPositionDomain]
