from web3 import AsyncWeb3

from app.core.database import Pool
from app.repositories.wallet.queries import CREATE_WALLET


class WalletRepository:
    def __init__(self, blockchain: AsyncWeb3, pool: Pool):
        self.blockchain = blockchain
        self.pool = pool

    async def register_wallet(self, user_id: int) -> None:
        account = self.blockchain.eth.account.create()
        await self.pool.fetchrow(CREATE_WALLET, user_id, account.address, account.key)

