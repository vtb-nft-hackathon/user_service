from app.common.models import OrganizationType, Organization
from app.core.database import Pool
from app.repositories.organizations.queries import CREATE_ORGANIZATION


class OrganizationRepository:
    def __init__(self, pool: Pool):
        self.pool = pool

    async def create_organization(self, name: str, organization_type: OrganizationType) -> Organization:
        organization = await self.pool.fetchrow(CREATE_ORGANIZATION, name, organization_type)
        return Organization(**organization)

