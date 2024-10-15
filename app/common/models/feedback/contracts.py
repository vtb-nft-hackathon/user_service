import datetime

from pydantic import BaseModel

from app.common.models.job.contracts import JobResponse
from app.common.models.user_info.contracts import UserInfoResponseSlim


class FeedBackResponse(BaseModel):
    recommend: bool
    author: UserInfoResponseSlim
    job: JobResponse
    date: datetime.date
