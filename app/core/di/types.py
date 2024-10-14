from typing import NewType

from faststream.rabbit import RabbitBroker, RabbitExchange
from faststream.rabbit.publisher.asyncapi import AsyncAPIPublisher

UserServiceBroker = NewType("SkeletorBroker", RabbitBroker)
UserEventsExchange = NewType("SkeletorBonesExchange", RabbitExchange)
UserEventsPublisher = NewType("BonesPublisher", AsyncAPIPublisher)
