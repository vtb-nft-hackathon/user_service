import enum

from pydantic import BaseModel

LARGE_BONE = 3


class BoneKind(enum.StrEnum):
    SKULL = enum.auto()
    JAW = enum.auto()


class BoneBase(BaseModel):
    kind: BoneKind
    owner_id: int
    size: float

    @property
    def is_large(self) -> bool:
        return self.size >= LARGE_BONE


class Bone(BoneBase):
    id: int


class BoneCreate(BoneBase):
    pass
