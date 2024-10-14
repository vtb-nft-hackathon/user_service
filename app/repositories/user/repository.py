from app.common.models import User
from app.core.database import Pool
from app.repositories.wallet.queries import CREATE_WALLET


class UserRepository:
    def __init__(self, pool: Pool):
        self.pool = pool

    async def create_user(self, name: str) -> User:
        user = await self.pool.fetchrow(CREATE_WALLET, name)
        return User(**user)

