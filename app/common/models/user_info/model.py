import datetime

from pydantic import BaseModel

from app.common.models.city.model import CityDomain
from app.common.models.feedback.model import FeedBackDomain
from app.common.models.user_job.model import UserJobDomain
from app.common.models.user_skill.model import UserSkillDomain
from app.common.models.user_study.model import UserStudyDomain


class UserInfoBase(BaseModel):
    first_name: str
    last_name: str
    third_name: str | None
    city_id: int | None
    date_of_birth: datetime.date | None
    about: str | None


class UserInfoDomain(UserInfoBase):
    id: int
    city: CityDomain
    skills: list[UserSkillDomain]
    jobs: list[UserJobDomain]
    feedbacks: list[FeedBackDomain]
    study: list[UserStudyDomain]
