import typing
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.whatsapp_service import WhatsAppService

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

# Static Tenant ID fallback
DEMO_TENANT_ID = uuid.UUID("d3b07384-d113-4956-a5d2-64be7357c11d")

class WhatsAppWebhookPayload(BaseModel):
    tenant_id: typing.Optional[uuid.UUID] = None
    phone_number: typing.Optional[str] = None
    sender_phone: typing.Optional[str] = None
    message_text: str

@router.post("/webhook", status_code=status.HTTP_202_ACCEPTED)
def receive_whatsapp_webhook(
    payload: WhatsAppWebhookPayload,
    db: Session = Depends(get_db)
):
    """
    Receives incoming WhatsApp order messages from WABA webhook.
    Processes the raw payload dynamically (supporting sender_phone / phone_number aliases).
    """
    # 1. Resolve Tenant ID context
    resolved_tenant_id = payload.tenant_id or DEMO_TENANT_ID

    # 2. Resolve Phone Number alias
    resolved_phone = payload.phone_number or payload.sender_phone
    if not resolved_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'phone_number' or 'sender_phone' must be provided in the payload."
        )

    service = WhatsAppService()
    job = service.process_whatsapp_message(
        db=db,
        tenant_id=resolved_tenant_id,
        phone_number=resolved_phone,
        message_text=payload.message_text
    )

    # Fetch staging error if job failed
    error_msg = None
    if job.failed_rows > 0 and job.staging_rows:
        error_msg = job.staging_rows[0].error_message

    return {
        "job_id": str(job.id),
        "status": job.status,
        "successful_rows": job.successful_rows,
        "failed_rows": job.failed_rows,
        "error_message": error_msg
    }

