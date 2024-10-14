from web3 import AsyncWeb3


class WalletRepository:
    def __init__(self, blockchain: AsyncWeb3):
        self.blockchain = blockchain

    async def register_wallet(self) -> None:
        self.blockchain.eth
