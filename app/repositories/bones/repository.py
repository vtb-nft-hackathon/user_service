from app.common.bone import Bone, BoneBase
from app.core.database import Pool
from app.repositories.bones.queries import ADD_BONE, GET_BONE_BY_ID


class BonesRepository:
    def __init__(self, pool: Pool):
        self._pool = pool

    async def get_by_id(self, bones_id: int) -> Bone | None:
        result = await self._pool.fetchrow(GET_BONE_BY_ID, bones_id)
        return Bone(**result) if result else None

    async def add(self, bone: BoneBase) -> Bone:
        inserted_id = await self._pool.fetchval(ADD_BONE, bone.kind, bone.owner_id, bone.size)
        return Bone(id=inserted_id, kind=bone.kind, owner_id=bone.owner_id, size=bone.size)
