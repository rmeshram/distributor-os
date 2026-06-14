import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db, tenant_context
from app.models.customer import Customer

router = APIRouter(prefix="/customers", tags=["Customers"])

class CustomerUpdatePayload(BaseModel):
    credit_limit: float
    billing_terms: str

@router.patch("/{customer_id}", status_code=status.HTTP_200_OK)
def update_customer(
    customer_id: uuid.UUID,
    payload: CustomerUpdatePayload,
    db: Session = Depends(get_db)
):
    """
    Updates a customer's credit limit and billing terms dynamically.
    """
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )
    
    tenant_context.set(customer.tenant_id)
    
    customer.credit_limit = payload.credit_limit
    customer.payment_terms = payload.billing_terms
    
    db.commit()
    return {
        "status": "success",
        "customer_id": str(customer.id),
        "credit_limit": float(customer.credit_limit),
        "billing_terms": customer.payment_terms
    }
