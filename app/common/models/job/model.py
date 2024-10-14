from pydantic import BaseModel


class JobBase(BaseModel):
    name: str


class JobDomain(JobBase):
    id: int
