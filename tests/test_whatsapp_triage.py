import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.tenant import DistributorTenant
from app.models.customer import Customer, CustomerAlias
from app.models.product import Product
from app.models.order import Order
from app.database import tenant_context

@pytest.fixture(name="client")
def fixture_client():
    return TestClient(app)

def test_whatsapp_webhook_triage_flow(db_session, client):
    # 1. Setup Tenant
    tenant = DistributorTenant(name="Triage Test Tenant")
    db_session.add(tenant)
    db_session.commit()

    tenant_context.set(tenant.id)

    # 2. Setup Customer with WhatsApp Phone Alias
    customer = Customer(
        retailer_name="Kaveri Provision Store",
        customer_id="CUST-T-101",
        address_text="Bengaluru",
        gstin="29AAAAA1111A1Z1",
        tax_group="GST-18",
        payment_terms="0-15 Days"
    )
    db_session.add(customer)
    db_session.flush()

    cust_alias = CustomerAlias(customer_id=customer.id, alias_value="+919999888877")
    db_session.add(cust_alias)
    db_session.commit()

    # 3. Post to WhatsApp webhook with an unmapped token
    response = client.post("/api/v1/whatsapp/webhook", json={
        "tenant_id": str(tenant.id),
        "phone_number": "+919999888877",
        "message_text": "10 PatanjaliDantKanti"
    })
    
    # Assert HTTP 200 OK
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["failed_rows"] == 0
    assert "manual assignment" in data["message"]

    # 4. Verify Order was created in database and tracking status normalizes to "Needs Review"
    order = db_session.query(Order).filter(Order.internal_order_id == data["order_id"]).first()
    assert order is not None
    assert order.current_status == "Needs Review"
    
    # 5. Verify the unmatched item exists and brand field contains the raw token string
    from app.models.order import OrderLineItem
    line_items = db_session.query(OrderLineItem).filter(OrderLineItem.order_id == order.id).all()
    assert len(line_items) == 1
    
    unmatched_item = line_items[0]
    prod = db_session.get(Product, unmatched_item.product_id)
    assert prod is not None
    assert prod.sku_id == "UNMATCHED_TRIAGE_SKU"
    assert prod.brand == "System Triage"
