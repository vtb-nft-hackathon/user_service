from pydantic import BaseModel


class CityBase(BaseModel):
    city: str


class CityDomain(CityBase):
    id: int
