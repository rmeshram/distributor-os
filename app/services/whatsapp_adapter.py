import uuid
import typing
import logging
import os
import requests
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models.tenant import DistributorTenant

logger = logging.getLogger("uvicorn.error")

class CanonicalWhatsAppMessage(BaseModel):
    tenant_id: typing.Optional[uuid.UUID] = None
    sender_phone: str
    receiver_phone: typing.Optional[str] = None
    message_text: str
    correlation_id: typing.Optional[str] = None

def adapt_to_canonical(payload: typing.Any) -> CanonicalWhatsAppMessage:
    """
    Adapts various raw payload formats (e.g. flat Pydantic model, nested Meta webhook dict)
    into a single canonical CanonicalWhatsAppMessage internal model.
    """
    # 1. If it's a Pydantic model (with potential extra fields stored in model_extra)
    if hasattr(payload, "message_text") or hasattr(payload, "sender_phone"):
        tenant_id = getattr(payload, "tenant_id", None)
        sender_phone = getattr(payload, "sender_phone", None) or getattr(payload, "phone_number", None) or getattr(payload, "sender", None) or ""
        receiver_phone = getattr(payload, "receiver", None)
        message_text = getattr(payload, "message_text", None) or getattr(payload, "message", None) or ""
        
        # Check if there are extra attributes in model_extra (e.g. nested Meta format parsed as model with extra fields)
        extra = getattr(payload, "model_extra", None)
        if extra and "entry" in extra:
            try:
                # Delegate to dictionary parsing of model_extra
                nested_adapted = adapt_to_canonical(extra)
                if nested_adapted.sender_phone:
                    sender_phone = nested_adapted.sender_phone
                if nested_adapted.message_text:
                    message_text = nested_adapted.message_text
                if nested_adapted.receiver_phone:
                    receiver_phone = nested_adapted.receiver_phone
                if tenant_id is None and "tenant_id" in extra and extra["tenant_id"]:
                    tenant_id = uuid.UUID(str(extra["tenant_id"]))
            except Exception as e:
                logger.error("Failed to adapt model_extra in webhook payload: %s", str(e))
        
        return CanonicalWhatsAppMessage(
            tenant_id=tenant_id,
            sender_phone=str(sender_phone),
            receiver_phone=str(receiver_phone) if receiver_phone else None,
            message_text=str(message_text)
        )

    # 2. If it's a dictionary
    if isinstance(payload, dict):
        # Case A: Nested Meta/Simulator payload format
        # LEGACY_META_CODE_START
        if "entry" in payload:
            logger.warning("Meta nested array payload received but Meta Integration is disabled/deprecated.")
            # Bypass warning and parse nested dictionary to preserve legacy test compatibility
            try:
                entry = payload.get("entry", [])
                if entry and isinstance(entry, list) and len(entry) > 0:
                    changes = entry[0].get("changes", [])
                    if changes and isinstance(changes, list) and len(changes) > 0:
                        value = changes[0].get("value", {})
                        if value and isinstance(value, dict):
                            # Extract message body and sender from the first message
                            messages = value.get("messages", [])
                            message_text = ""
                            sender_phone = ""
                            
                            if messages and isinstance(messages, list) and len(messages) > 0:
                                first_msg = messages[0]
                                if "text" in first_msg and isinstance(first_msg["text"], dict):
                                    message_text = first_msg["text"].get("body", "")
                                sender_phone = first_msg.get("from", "")
                            
                            # Fallback to contacts if message phone is missing
                            if not sender_phone:
                                contacts = value.get("contacts", [])
                                if contacts and isinstance(contacts, list) and len(contacts) > 0:
                                    sender_phone = contacts[0].get("wa_id", "")
                            
                            # Extract receiver display phone number
                            metadata = value.get("metadata", {})
                            receiver_phone = None
                            if metadata and isinstance(metadata, dict):
                                receiver_phone = metadata.get("display_phone_number")
                                
                            tenant_id_raw = payload.get("tenant_id")
                            tenant_id = None
                            if tenant_id_raw:
                                tenant_id = uuid.UUID(str(tenant_id_raw))
                            
                            return CanonicalWhatsAppMessage(
                                tenant_id=tenant_id,
                                sender_phone=str(sender_phone),
                                receiver_phone=str(receiver_phone) if receiver_phone else None,
                                message_text=str(message_text)
                            )
            except Exception as e:
                logger.error("Failed to adapt nested dictionary in webhook payload: %s", str(e))
        # LEGACY_META_CODE_END

        # Case B: Flat dictionary format
        tenant_id_raw = payload.get("tenant_id")
        tenant_id = uuid.UUID(str(tenant_id_raw)) if tenant_id_raw else None
        sender_phone = payload.get("sender_phone") or payload.get("phone_number") or payload.get("sender") or ""
        receiver_phone = payload.get("receiver")
        message_text = payload.get("message_text") or payload.get("message") or ""
        
        return CanonicalWhatsAppMessage(
            tenant_id=tenant_id,
            sender_phone=str(sender_phone),
            receiver_phone=str(receiver_phone) if receiver_phone else None,
            message_text=str(message_text)
        )

    raise ValueError("Unsupported webhook payload format")


# LEGACY_META_CODE_START
def send_whatsapp_message(
    db: Session,
    tenant_id: uuid.UUID,
    to_phone: str,
    message_text: str
) -> dict:
    """
    Sends a WhatsApp message using Meta Graph API with dynamic multi-tenant credentials.
    """
    logger.error("Meta Graph API message sending is disabled.")
    raise RuntimeError("Meta Graph API integration is legacy/disabled. Please use the new Evolution API Flow.")
# LEGACY_META_CODE_END

