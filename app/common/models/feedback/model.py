from pydantic import BaseModel

from app.common.models.job.model import JobDomain
from app.common.models.user_info.model import UserInfoDomain


class FeedBackBase(BaseModel):
    author_id: int
    job_id: int
    feedback: str
    recommend: bool


class FeedBackDomain(FeedBackBase):
    id: int
    author: UserInfoDomain
    job: JobDomain
