from httpx import AsyncClient
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from app.common.models import BoneBase, BoneCreate, BoneKind
from app.repositories import BonesRepository


async def test_get_bone_by_id(test_client: AsyncClient, bones_repository: BonesRepository) -> None:
    # Arrange
    bone = await bones_repository.add(BoneBase(kind=BoneKind.SKULL, owner_id=1, size=1))

    # Act
    response = await test_client.get(f"/api/v1/bones/{bone.id}")

    # Assert
    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "result": {"id": bone.id, "kind": "skull", "owner_id": 1, "size": 1},
        "errors": [],
        "success": True,
    }


async def test_create_bone(test_client: AsyncClient) -> None:
    # Arrange
    bone = BoneCreate(kind=BoneKind.SKULL, owner_id=1, size=1)

    # Act
    response = await test_client.post("/api/v1/bones", json=bone.model_dump())

    # Assert
    assert response.status_code == HTTP_201_CREATED
    assert response.json() == {
        "result": {"id": 1, "kind": "skull", "owner_id": 1, "size": 1},
        "errors": [],
        "success": True,
    }
