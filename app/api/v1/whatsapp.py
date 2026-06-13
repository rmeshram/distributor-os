import uuid
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.whatsapp_service import WhatsAppService

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

class WhatsAppWebhookPayload(BaseModel):
    tenant_id: uuid.UUID
    phone_number: str
    message_text: str

@router.post("/webhook", status_code=status.HTTP_202_ACCEPTED)
def receive_whatsapp_webhook(
    payload: WhatsAppWebhookPayload,
    db: Session = Depends(get_db)
):
    """
    Receives incoming WhatsApp order messages from WABA webhook.
    Processes the raw payload asynchronously (simulated) into the staging and order ledger.
    """
    service = WhatsAppService()
    job = service.process_whatsapp_message(
        db=db,
        tenant_id=payload.tenant_id,
        phone_number=payload.phone_number,
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
