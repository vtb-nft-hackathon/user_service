from typing import NewType

from faststream.rabbit import RabbitBroker, RabbitExchange
from faststream.rabbit.publisher.asyncapi import AsyncAPIPublisher

SkeletorBroker = NewType("SkeletorBroker", RabbitBroker)
SkeletorBonesExchange = NewType("SkeletorBonesExchange", RabbitExchange)
BonesPublisher = NewType("BonesPublisher", AsyncAPIPublisher)
