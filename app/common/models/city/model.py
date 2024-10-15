from pydantic import BaseModel


class CityBase(BaseModel):
    name: str


class CityDomain(CityBase):
    id: int
