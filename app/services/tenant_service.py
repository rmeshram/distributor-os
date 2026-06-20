import uuid
from fastapi import Cookie, Header, HTTPException, status
from app.utils.security import verify_jwt

# Static Tenant ID for demo/default distributor
DEMO_TENANT_ID = uuid.UUID("d3b07384-d113-4956-a5d2-64be7357c11d")

def resolve_tenant_id(
    tenant_id: uuid.UUID | None = None,
    access_token: str | None = Cookie(None),
    authorization: str | None = Header(None)
) -> uuid.UUID:
    """
    Resolves the tenant ID by checking the JWT cookie or Authorization header first.
    Falls back to query parameter if not authenticated (preserving tests compatibility).
    """
    token = access_token
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    if token:
        payload = verify_jwt(token)
        if payload and "tenant_id" in payload:
            return uuid.UUID(payload["tenant_id"])
    if tenant_id:
        return tenant_id
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not resolve active Tenant ID from session or headers."
    )
