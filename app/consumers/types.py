from typing import Any

from faststream.broker.wrapper.call import HandlerCallWrapper
from faststream.rabbit import RabbitBroker, RabbitExchange, RabbitQueue

ConsumerFactoryReturnType = tuple[RabbitBroker, RabbitExchange, RabbitQueue, HandlerCallWrapper[Any, Any, Any]]
