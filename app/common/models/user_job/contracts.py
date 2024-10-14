from pydantic import BaseModel

from app.common.models.job.contracts import JobResponse
from app.common.models.user_job_position.contracts import UserJobPositionResponse


class UserJobResponse(BaseModel):
    id: int
    job: JobResponse
    positions: list[UserJobPositionResponse]
