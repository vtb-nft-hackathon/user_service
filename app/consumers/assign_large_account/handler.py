from dishka.entities.depends_marker import FromDishka
from faststream.rabbit import RabbitBroker, RabbitExchange, RabbitQueue

from app.common.events import NewBone
from app.common.models import BoneKind
from app.consumers.types import ConsumerFactoryReturnType
from app.core.settings import Config
from app.repositories import BonesRepository


async def handle_event(event: NewBone, bones_repository: FromDishka[BonesRepository]) -> None:
    bone = await bones_repository.get_by_id(event.bone_id)

    if not bone:
        return

    if bone.kind == BoneKind.SKULL and bone.is_large:
        raise NotImplementedError


def create_subscriber(config: Config) -> ConsumerFactoryReturnType:
    broker = RabbitBroker(config.brokers.skeletor.url)

    exchange = RabbitExchange(**config.brokers.skeletor.subscribers.new_bone.exchange.model_dump())
    queue = RabbitQueue(**config.brokers.skeletor.subscribers.new_bone.queue.model_dump())

    consumer_wrapper = broker.subscriber(queue=queue, exchange=exchange)(handle_event)
    return broker, exchange, queue, consumer_wrapper
