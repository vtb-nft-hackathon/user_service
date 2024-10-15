from enum import IntEnum

from pydantic import BaseModel


class User(BaseModel):
    name: str

class OrganizationType(IntEnum):
    COMPANY = 1
    SCHOOL = 2

class Organization(BaseModel):
    name: str
    organization_type: OrganizationType
