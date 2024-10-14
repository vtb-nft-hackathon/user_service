from faststream.rabbit import TestRabbitBroker
from respx import MockRouter

from app.common.events import UserRegistration
from app.consumers.types import ConsumerFactoryReturnType
from app.repositories import WalletRepository


async def test_handle_event(
    assign_large_account_consumer: ConsumerFactoryReturnType,
    offers_api_router: MockRouter,
    bones_repository: WalletRepository,
) -> None:
    # Arrange
    bone = BoneBase(kind=BoneKind.SKULL, owner_id=1, size=5)
    bone = await bones_repository.add(bone)
    event = UserRegistration(bone_id=bone.id)
    offers_api_router.put(f"/api/v1/large_accounts/{bone.owner_id}").respond(json={"answer": True})
    broker, exchange, queue, handler = assign_large_account_consumer

    # Act
    async with TestRabbitBroker(broker) as test_broker:
        await test_broker.publish(event, queue, exchange)

        # Assert
        handler.mock.assert_called_once_with({"bone_id": bone.id})  # type: ignore[union-attr]
