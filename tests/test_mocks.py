import uuid
from datetime import datetime
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.tenant import DistributorTenant
from app.models.product import Product
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.shipment import Shipment
from app.models.order import Order, OrderStateLedger
from app.services.integration_service import IntegrationService
from app.database import tenant_context
import httpx

@pytest.fixture(name="api_client")
def fixture_api_client():
    return TestClient(app)

def test_tally_inventory_sync(db_session, api_client, monkeypatch):
    # Setup Tenant
    tenant = DistributorTenant(name="Karan & Co")
    db_session.add(tenant)
    db_session.commit()
    tenant_context.set(tenant.id)

    # Setup Products in catalog matching Tally XML SKUs
    p1 = Product(sku_id="PROD-HUL-SOAP", brand="HUL", category="Soap", pack_size="100g", base_price=45.00)
    p2 = Product(sku_id="PROD-ITC-AATA", brand="ITC", category="Aata", pack_size="10kg", base_price=250.00)
    db_session.add_all([p1, p2])
    db_session.commit()

    # Intercept outbound HTTP requests and route them to our mock server
    def mock_post(url, *args, **kwargs):
        path = url.replace("http://testserver", "")
        # Forward Content and headers
        content = kwargs.get("content")
        resp = api_client.post(path, content=content)
        return resp

    monkeypatch.setattr(httpx, "post", mock_post)

    service = IntegrationService()
    # Call Tally Sync
    res = service.sync_tally_inventory(db_session, tenant.id, base_url="http://testserver")

    assert res["status"] == "success"
    assert res["synced_records"] == 2

    # Check Inventory records updated/created
    inv1 = db_session.query(Inventory).filter_by(sku_id=p1.id).one()
    assert inv1.quantity_on_hand == 500
    assert inv1.quantity_committed == 50

    inv2 = db_session.query(Inventory).filter_by(sku_id=p2.id).one()
    assert inv2.quantity_on_hand == 150
    assert inv2.quantity_committed == 12


def test_delhivery_shipment_booking(db_session, api_client, monkeypatch):
    # Setup Tenant
    tenant = DistributorTenant(name="Karan & Co")
    db_session.add(tenant)
    db_session.commit()
    tenant_context.set(tenant.id)

    # Setup Customer
    cust = Customer(
        retailer_name="Aggarwal Kirana", customer_id="C-1", address_text="Gali 5, Noida",
        gstin="09AAAAA1111A1Z1", tax_group="GST", payment_terms="Net 15"
    )
    db_session.add(cust)
    db_session.flush()

    # Setup Order
    order = Order(internal_order_id="ORD-100", source="Portal", customer_id=cust.id)
    db_session.add(order)
    db_session.flush()

    # Transition order state to 'Confirmed'
    db_session.add(OrderStateLedger(order_id=order.id, from_status=None, to_status="Draft", updated_by="user"))
    db_session.add(OrderStateLedger(order_id=order.id, from_status="Draft", to_status="Confirmed", updated_by="user"))
    db_session.commit()

    # Intercept outbound HTTP post to route to TestClient
    def mock_post(url, *args, **kwargs):
        path = url.replace("http://testserver", "")
        json_data = kwargs.get("json")
        resp = api_client.post(path, json=json_data)
        return resp

    monkeypatch.setattr(httpx, "post", mock_post)

    service = IntegrationService()
    # Book shipment using Delhivery Mock API
    shipment = service.book_outbound_shipment(
        db=db_session,
        tenant_id=tenant.id,
        order_id=order.id,
        carrier="Delhivery",
        base_url="http://testserver"
    )

    # Check Shipment record
    assert shipment.carrier == "Delhivery"
    assert shipment.tracking_id.startswith("DELH")
    assert shipment.status == "In Transit"
    assert shipment.destination == "Gali 5, Noida"

    # Verify Order Ledger updated to 'Dispatched'
    assert order.current_status == "Dispatched"
    ledger_entries = db_session.query(OrderStateLedger).filter_by(order_id=order.id).all()
    # Initial Draft, Confirmed, then Dispatched
    assert len(ledger_entries) == 3
    latest_ledger = sorted(ledger_entries, key=lambda e: e.timestamp, reverse=True)[0]
    assert latest_ledger.from_status == "Confirmed"
    assert latest_ledger.to_status == "Dispatched"
    assert latest_ledger.updated_by == "system_logistics_agent"
