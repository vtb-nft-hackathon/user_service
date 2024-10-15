from hashlib import sha512

from app.common.models.user_info.model import UserInfoBase
from app.core.database import Pool
from app.repositories.user.queries import CREATE_USER, AUTH_USER


class UserRepository:
    def __init__(self, pool: Pool):
        self.pool = pool

    async def create_user(self, name: str) -> UserInfoBase:
        user = await self.pool.fetchrow(CREATE_USER, name)
        return UserInfoBase(**user)

    async def auth_user(self, login: str, password: str) -> UserInfoBase | None:
        hashed_password = sha512(password.encode('utf-8')).hexdigest()
        user = await self.pool.fetchrow(AUTH_USER, login, hashed_password)
        if not user:
            return None
        return UserInfoBase(**user)

