from typing import Protocol, TypedDict


class UserContext(TypedDict):
    uid: str
    tenantId: str
    role: str
    claims: dict


class IAuth(Protocol):
    def verify(self, bearer_token: str) -> UserContext: ...


class IAuthorizer(Protocol):
    def can_cross_tenant(self, user: UserContext, target_tenant: str) -> bool: ...
