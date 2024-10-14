from web3 import AsyncWeb3

from app.core.database import Pool


class WalletRepository:
    def __init__(self, blockchain: AsyncWeb3, pool: Pool):
        self.blockchain = blockchain
        self.pool = pool

    async def register_wallet(self) -> None:
        self.blockchain.eth
