import datetime

from pydantic import BaseModel

from app.common.models.city.contracts import CityResponse
from app.common.models.feedback.contracts import FeedBackResponse
from app.common.models.user_job.contracts import UserJobResponse
from app.common.models.user_skill.contracts import UserSkillResponse
from app.common.models.user_study.contracts import UserStudyResponse


class UserInfoResponseSlim(BaseModel):
    id: int
    first_name: str
    last_name: str
    third_name: str | None


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    third_name: str | None
    date_of_birth: datetime.date | None
    about: str | None

    city: CityResponse
    skills: list[UserSkillResponse]
    jobs: list[UserJobResponse]
    feedbacks: list[FeedBackResponse]
    study: list[UserStudyResponse]
