from enum import StrEnum, unique
from ipaddress import AddressValueError, IPv4Address
from typing import Annotated

from faststream.rabbit import ExchangeType
from pydantic import AfterValidator, AmqpDsn, AnyHttpUrl, BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

AnyHttpUrlStr = Annotated[str, Annotated[AnyHttpUrl, AfterValidator(str)]]
AmqpDsnStr = Annotated[str, Annotated[AmqpDsn, AfterValidator(str)]]


class ApiSettings(BaseModel):
    address: str = "0.0.0.0"
    port: int = Field(8000, ge=0, le=65535)

    @classmethod
    @field_validator("address")
    def is_address_valid_ip(cls, address: str) -> str:
        try:
            IPv4Address(address)
        except AddressValueError as e:
            raise ValueError("Not a valid IPv4 address.") from e
        return address


class ExternalServiceClientSettings(BaseModel):
    base_url: AnyHttpUrlStr = "http://alo.alo"
    sender_service_name: str = "skeletor"
    authorization_header_value: str = ""
    global_timeout: int = 5


class ClientsSettings(BaseModel):
    offers_api: ExternalServiceClientSettings = ExternalServiceClientSettings(
        base_url="http://alo2.alo",
    )


class ExchangeSettings(BaseModel):
    name: str
    type: ExchangeType = ExchangeType.TOPIC
    routing_key: str = ""
    durable: bool = True
    auto_delete: bool = False


class QueueSettings(BaseModel):
    name: str
    durable: bool = True
    exclusive: bool = False
    auto_delete: bool = False
    routing_key: str = ""
    arguments: dict[str, str] | None = {"x-queue-type": "quorum"}


class SubscriberSettings(BaseModel):
    exchange: ExchangeSettings
    queue: QueueSettings


class UsersPublishersSettings(BaseModel):
    users: ExchangeSettings = ExchangeSettings(name="users")


class UsersSubscribersSettings(BaseModel):
    wallet_registration: SubscriberSettings = SubscriberSettings(
        exchange=ExchangeSettings(name="users"),
        queue=QueueSettings(name="users.registration.event_created", routing_key="v1.event.registration"),
    )


class UsersVhostSettings(BaseModel):
    url: AmqpDsnStr = "amqp://user:password@rmq:5672/users"
    publishers: UsersPublishersSettings = UsersPublishersSettings()
    subscribers: UsersSubscribersSettings = UsersSubscribersSettings()


class BrokersSettings(BaseModel):
    users: UsersVhostSettings = UsersVhostSettings()


class DatabaseSettings(BaseModel):
    dsn: str = "postgres://user:password@pg:5432/skeletor"
    query_acquire_timeout: float = 5.0
    query_execute_timeout: float = 10.0
    min_size: int = 15
    max_size: int = 15
    max_inactive_connection_lifetime: float = 300
    metrics_core_enabled: bool = True  # Метрики на запросы в базу данных
    collect_pool_metrics: bool = False  # Метрики пулов приложения
    collect_database_metrics: bool = False  # Метрики соединений из базы данных
    metrics_collect_interval: float = 1.0


@unique
class Environments(StrEnum):
    local = "local"
    qa = "qa"
    stage = "stage"
    prod = "prod"


class Web3Settings(BaseModel):
    rpc_url: str = "https://arbitrum-sepolia.infura.io/v3/2a852b2d2c174a81ac0d904de44d2aa1"


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=".env.local",
        env_file_encoding="utf-8",
    )

    api: ApiSettings = ApiSettings()
    debug: bool = False
    environment: Environments = Environments.local
    version: str = "local"

    db: DatabaseSettings = DatabaseSettings()
    clients: ClientsSettings = ClientsSettings()
    brokers: BrokersSettings = BrokersSettings()
    web3: Web3Settings = Web3Settings()
    master_key: bytes = b"89w8fiuwupn3ux6vuedcfdzqavr99lmn"
