from pydantic import BaseModel


class NewBone(BaseModel):
    bone_id: int
