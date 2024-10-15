from Crypto.Cipher import AES
from Crypto.Cipher._mode_cbc import CbcMode
from web3 import AsyncWeb3

from app.core.database import Pool
from app.repositories.wallet.queries import CREATE_WALLET


class WalletRepository:
    def __init__(self, blockchain: AsyncWeb3, AES: CbcMode, pool: Pool):
        self.blockchain = blockchain
        self.AES = AES
        self.pool = pool

    async def register_wallet(self, user_id: int) -> None:
        account = self.blockchain.eth.account.create()
        encrypted_key = self.AES.encrypt(account.private_key)
        # TODO: maybe write bytes
        await self.pool.fetchrow(CREATE_WALLET, user_id, account.address, encrypted_key)

