import typing
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.customer import Customer
from app.models.product import Product
from app.models.order import Order, OrderLineItem, OrderStateLedger

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

# Static Tenant ID fallback
DEMO_TENANT_ID = uuid.UUID("d3b07384-d113-4956-a5d2-64be7357c11d")

class WebhookPayload(BaseModel):
    tenant_id: typing.Optional[uuid.UUID] = None
    phone_number: typing.Optional[str] = None
    sender_phone: typing.Optional[str] = None
    message_text: str

@router.post("/webhook")
def handle_whatsapp_webhook(
    payload: WebhookPayload,
    db: Session = Depends(get_db)
):
    try:
        # 1. Resolve phone and tenant contexts
        resolved_tenant_id = payload.tenant_id or DEMO_TENANT_ID
        phone = payload.sender_phone or payload.phone_number or ""

        # 2. Map incoming numbers to mock customer nodes for visibility
        customer_name = "Kaveri Provision Store" if "98765" in phone or "9999888" in phone else "Maruthi Stores"
        
        # Resolve customer from database or fallback to seeder structure
        customer = db.query(Customer).filter_by(retailer_name=customer_name).first()
        if not customer:
            cust_id = "CUST-101" if customer_name == "Kaveri Provision Store" else "CUST-102"
            customer = db.query(Customer).filter_by(customer_id=cust_id).first()
            if not customer:
                customer = Customer(
                    id=uuid.uuid4(),
                    tenant_id=resolved_tenant_id,
                    customer_id=cust_id,
                    retailer_name=customer_name,
                    address_text="Bengaluru",
                    gstin="29AAAAA1111A1Z1",
                    tax_group="GST-18",
                    payment_terms="0-15 Days"
                )
                db.add(customer)
                db.flush()

        # 3. Extract a random/mock amount for testing or default values
        mock_amount = 45000 if "Maggi" in payload.message_text else 25000
        
        # 4. Create a unique Order ID string
        generated_order_id = f"ORD-2506-{uuid.uuid4().hex[:4].upper()}"
        
        # 5. Construct the physical ORM database model instance
        # Ensure the field parameters perfectly match your Order table definition schema
        new_order = Order(
            id=uuid.uuid4(),
            tenant_id=resolved_tenant_id,
            internal_order_id=generated_order_id,
            source="WhatsApp",
            customer_id=customer.id
        )
        db.add(new_order)
        db.flush()

        # Resolve first product to associate with order line item
        product = db.query(Product).first()
        if not product:
            product = Product(
                id=uuid.uuid4(),
                tenant_id=resolved_tenant_id,
                sku_id="PROD-HUL-SOAP",
                brand="HUL",
                category="Soap",
                pack_size="100g",
                base_price=45.00
            )
            db.add(product)
            db.flush()

        # Persist line item mapping to capture order amount
        db.add(OrderLineItem(
            tenant_id=resolved_tenant_id,
            order_id=new_order.id,
            product_id=product.id,
            quantity=1,
            unit_price=mock_amount
        ))

        # Register state transition in state ledger
        db.add(OrderStateLedger(
            tenant_id=resolved_tenant_id,
            order_id=new_order.id,
            from_status=None,
            to_status="Draft", # Draft status maps to Pending in the dashboard UI
            updated_by="system_whatsapp_agent"
        ))
        
        # 6. COMMIT STRATEGY: Explicitly save to distributor_os.db database file
        db.commit()
        db.refresh(new_order)
        
        print(f"Successfully persisted incoming WhatsApp order {generated_order_id} to SQLite store!")
        return {
            "status": "success",
            "order_id": generated_order_id,
            "job_id": str(uuid.uuid4()),
            "successful_rows": 1,
            "failed_rows": 0,
            "error_message": None
        }
        
    except Exception as e:
        db.rollback()
        print(f"Database Ingestion Failure: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database write crash: {str(e)}")
