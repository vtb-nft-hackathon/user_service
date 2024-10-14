from dishka.entities.depends_marker import FromDishka
from faststream.rabbit import RabbitBroker, RabbitExchange, RabbitQueue

from app.common.events import UserRegistration
from app.consumers.types import ConsumerFactoryReturnType
from app.core.settings import Config
from app.repositories import WalletRepository


async def handle_event(event: UserRegistration, wallet_repository: FromDishka[WalletRepository]) -> None:
    bone = await wallet_repository.register_wallet()



def create_subscriber(config: Config) -> ConsumerFactoryReturnType:
    broker = RabbitBroker(config.brokers.skeletor.url)

    exchange = RabbitExchange(**config.brokers.skeletor.subscribers.new_bone.exchange.model_dump())
    queue = RabbitQueue(**config.brokers.skeletor.subscribers.new_bone.queue.model_dump())

    consumer_wrapper = broker.subscriber(queue=queue, exchange=exchange)(handle_event)
    return broker, exchange, queue, consumer_wrapper
