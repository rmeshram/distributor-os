import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.tenant import DistributorTenant
from app.models.customer import Customer
from app.database import tenant_context

@pytest.fixture(name="client")
def fixture_client():
    return TestClient(app)

def test_patch_customer_settings(db_session, client):
    # Setup Tenant
    tenant = DistributorTenant(name="Customer Edit Tenant")
    db_session.add(tenant)
    db_session.commit()

    tenant_context.set(tenant.id)

    # Setup Customer
    cust = Customer(
        retailer_name="Settings Test Shop", customer_id="C-SETTINGS-1", address_text="Settings Street, Delhi",
        gstin="07AAAAA1111A1Z1", tax_group="GST", payment_terms="0-15 Days",
        credit_limit=50000.0, outstanding_balance=1000.0
    )
    db_session.add(cust)
    db_session.commit()

    # Call PATCH endpoint
    response = client.patch(
        f"/api/v1/customers/{cust.id}",
        json={
            "credit_limit": 75000.0,
            "billing_terms": "16-30 Days"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["customer_id"] == str(cust.id)
    assert data["credit_limit"] == 75000.0
    assert data["billing_terms"] == "16-30 Days"

    # Verify DB update
    db_session.expire_all()
    cust_db = db_session.get(Customer, cust.id)
    assert float(cust_db.credit_limit) == 75000.0
    assert cust_db.payment_terms == "16-30 Days"


def test_patch_customer_settings_not_found(client):
    fake_id = uuid.uuid4()
    response = client.patch(
        f"/api/v1/customers/{fake_id}",
        json={
            "credit_limit": 75000.0,
            "billing_terms": "16-30 Days"
        }
    )
    assert response.status_code == 404
    assert "Customer not found" in response.json()["detail"]
