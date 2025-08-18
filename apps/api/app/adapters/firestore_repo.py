"""Firestore repository adapter for tenant configuration and user data."""

import logging
from typing import Any, Dict, Optional

from google.cloud import firestore

from ..domain.models import Tenant, User

logger = logging.getLogger(__name__)


class FirestoreRepository:
    """Firestore repository for tenant and user data."""

    def __init__(self, project_id: str):
        self.db = firestore.Client(project=project_id)

    async def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID."""
        try:
            doc_ref = self.db.collection("tenants").document(tenant_id)
            doc = doc_ref.get()

            if doc.exists:
                data = doc.to_dict()
                return Tenant(
                    id=doc.id,
                    name=data["name"],
                    domain=data.get("domain"),
                    settings=data.get("settings", {}),
                    created_at=data["created_at"],
                    updated_at=data.get("updated_at"),
                    is_active=data.get("is_active", True),
                )
            return None
        except Exception as e:
            logger.error(f"Error getting tenant {tenant_id}: {e}")
            return None

    async def create_tenant(self, tenant: Tenant) -> bool:
        """Create a new tenant."""
        try:
            doc_ref = self.db.collection("tenants").document(tenant.id)
            doc_ref.set(
                {
                    "name": tenant.name,
                    "domain": tenant.domain,
                    "settings": tenant.settings,
                    "created_at": tenant.created_at,
                    "updated_at": tenant.updated_at,
                    "is_active": tenant.is_active,
                }
            )
            return True
        except Exception as e:
            logger.error(f"Error creating tenant: {e}")
            return False

    async def update_tenant(self, tenant: Tenant) -> bool:
        """Update an existing tenant."""
        try:
            doc_ref = self.db.collection("tenants").document(tenant.id)
            doc_ref.update(
                {
                    "name": tenant.name,
                    "domain": tenant.domain,
                    "settings": tenant.settings,
                    "updated_at": tenant.updated_at,
                    "is_active": tenant.is_active,
                }
            )
            return True
        except Exception as e:
            logger.error(f"Error updating tenant: {e}")
            return False

    async def get_user(self, user_id: str, tenant_id: str) -> Optional[User]:
        """Get user by ID within tenant."""
        try:
            doc_ref = (
                self.db.collection("tenants")
                .document(tenant_id)
                .collection("users")
                .document(user_id)
            )
            doc = doc_ref.get()

            if doc.exists:
                data = doc.to_dict()
                return User(
                    id=doc.id,
                    email=data["email"],
                    name=data.get("name"),
                    tenant_id=tenant_id,
                    roles=data.get("roles", []),
                    created_at=data["created_at"],
                    last_login=data.get("last_login"),
                )
            return None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None

    async def create_user(self, user: User) -> bool:
        """Create a new user."""
        try:
            doc_ref = (
                self.db.collection("tenants")
                .document(user.tenant_id)
                .collection("users")
                .document(user.id)
            )
            doc_ref.set(
                {
                    "email": user.email,
                    "name": user.name,
                    "roles": user.roles,
                    "created_at": user.created_at,
                    "last_login": user.last_login,
                }
            )
            return True
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False

    async def update_user_last_login(self, user_id: str, tenant_id: str, last_login) -> bool:
        """Update user's last login timestamp."""
        try:
            doc_ref = (
                self.db.collection("tenants")
                .document(tenant_id)
                .collection("users")
                .document(user_id)
            )
            doc_ref.update({"last_login": last_login})
            return True
        except Exception as e:
            logger.error(f"Error updating user last login: {e}")
            return False

    async def get_tenant_settings(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant-specific settings."""
        tenant = await self.get_tenant(tenant_id)
        return tenant.settings if tenant else {}
