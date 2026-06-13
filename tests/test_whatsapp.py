import uuid
import pytest
from app.models.tenant import DistributorTenant
from app.models.customer import Customer, CustomerAlias
from app.models.product import Product, ProductAlias
from app.models.order import Order, OrderLineItem, OrderStateLedger
from app.models.ingestion import IngestionJob, IngestionStaging
from app.services.whatsapp_service import WhatsAppService
from app.database import tenant_context

def test_whatsapp_ingestion_success(db_session):
    # 1. Setup Tenant
    tenant = DistributorTenant(name="Tata Distributors Ltd")
    db_session.add(tenant)
    db_session.commit()

    # Bind active tenant context
    tenant_context.set(tenant.id)

    # 2. Setup Customer with WhatsApp Phone Alias
    customer = Customer(
        retailer_name="Aggarwal Kirana Store",
        customer_id="CUST-101",
        address_text="Shop 14, Sector 5, Rohini, Delhi",
        gstin="07AAAAA1111A1Z1",
        tax_group="GST-18",
        payment_terms="Net 15"
    )
    db_session.add(customer)
    db_session.flush()

    cust_alias = CustomerAlias(
        customer_id=customer.id,
        alias_value="+919999888877"
    )
    db_session.add(cust_alias)

    # 3. Setup Products and their Aliases
    p1 = Product(sku_id="PROD-HUL-SOAP", brand="HUL", category="Soap", pack_size="100g", base_price=45.00)
    p2 = Product(sku_id="PROD-ITC-AATA", brand="ITC", category="Flour", pack_size="5kg", base_price=260.00)
    db_session.add_all([p1, p2])
    db_session.flush()

    alias_soap = ProductAlias(product_id=p1.id, alias_name="HUL Soap")
    alias_aata = ProductAlias(product_id=p2.id, alias_name="ITC Aashirvaad Aata")
    db_session.add_all([alias_soap, alias_aata])
    db_session.commit()

    # 4. Trigger WhatsApp Ingestion
    service = WhatsAppService()
    message = "Bhaiya, please send 50 HUL Soap and 12 ITC Aashirvaad Aata immediately"
    
    job = service.process_whatsapp_message(
        db=db_session,
        tenant_id=tenant.id,
        phone_number="+919999888877",
        message_text=message
    )

    # 5. Assertions on Ingestion Job
    assert job.status == "Completed"
    assert job.successful_rows == 1
    assert job.failed_rows == 0

    # Assertions on Staging
    staging = db_session.query(IngestionStaging).filter_by(job_id=job.id).one()
    assert staging.status == "Validated"
    assert staging.error_message is None

    # Assertions on Canonical Tables (Order & Ledger)
    orders = db_session.query(Order).all()
    assert len(orders) == 1
    order = orders[0]
    assert order.source == "WhatsApp"
    assert order.customer_id == customer.id
    # Check current status dynamic property
    assert order.current_status == "Draft"

    # Verify line items
    items = db_session.query(OrderLineItem).filter_by(order_id=order.id).all()
    assert len(items) == 2
    
    soap_item = next(it for it in items if it.product_id == p1.id)
    assert soap_item.quantity == 50
    assert float(soap_item.unit_price) == 45.00

    aata_item = next(it for it in items if it.product_id == p2.id)
    assert aata_item.quantity == 12
    assert float(aata_item.unit_price) == 260.00

    # Verify state ledger entry
    ledger_entries = db_session.query(OrderStateLedger).filter_by(order_id=order.id).all()
    assert len(ledger_entries) == 1
    ledger = ledger_entries[0]
    assert ledger.from_status is None
    assert ledger.to_status == "Draft"
    assert ledger.updated_by == "system_whatsapp_agent"


def test_whatsapp_ingestion_unknown_customer(db_session):
    # Setup Tenant
    tenant = DistributorTenant(name="Tata Distributors Ltd")
    db_session.add(tenant)
    db_session.commit()

    tenant_context.set(tenant.id)

    # Setup Product only
    p1 = Product(sku_id="PROD-HUL-SOAP", brand="HUL", category="Soap", pack_size="100g", base_price=45.00)
    db_session.add(p1)
    db_session.flush()
    alias_soap = ProductAlias(product_id=p1.id, alias_name="HUL Soap")
    db_session.add(alias_soap)
    db_session.commit()

    # Call with unregistered phone number
    service = WhatsAppService()
    job = service.process_whatsapp_message(
        db=db_session,
        tenant_id=tenant.id,
        phone_number="+910000000000",  # Unknown
        message_text="Need 50 HUL Soap"
    )

    # Check status
    assert job.status == "Completed"
    assert job.successful_rows == 0
    assert job.failed_rows == 1

    # Check staging error
    staging = db_session.query(IngestionStaging).filter_by(job_id=job.id).one()
    assert staging.status == "Failed"
    assert "Unknown customer phone number" in staging.error_message

    # Ensure no Order was generated
    assert db_session.query(Order).count() == 0


def test_whatsapp_ingestion_unmapped_product(db_session):
    # Setup Tenant
    tenant = DistributorTenant(name="Tata Distributors Ltd")
    db_session.add(tenant)
    db_session.commit()

    tenant_context.set(tenant.id)

    # Setup Customer
    customer = Customer(
        retailer_name="Aggarwal Kirana Store",
        customer_id="CUST-101",
        address_text="Shop 14, Sector 5, Rohini, Delhi",
        gstin="07AAAAA1111A1Z1",
        tax_group="GST-18",
        payment_terms="Net 15"
    )
    db_session.add(customer)
    db_session.flush()
    cust_alias = CustomerAlias(customer_id=customer.id, alias_value="+919999888877")
    db_session.add(cust_alias)
    db_session.commit()

    # Call with message referencing unknown product SKU
    service = WhatsAppService()
    job = service.process_whatsapp_message(
        db=db_session,
        tenant_id=tenant.id,
        phone_number="+919999888877",
        message_text="Send 10 boxes of Nestle Maggi"  # "Nestle Maggi" is unmapped
    )

    assert job.status == "Completed"
    assert job.successful_rows == 0
    assert job.failed_rows == 1

    staging = db_session.query(IngestionStaging).filter_by(job_id=job.id).one()
    assert staging.status == "Failed"
    assert "Unmapped product aliases" in staging.error_message
    assert "maggi" in staging.error_message.lower()

    # Verify no order is created
    assert db_session.query(Order).count() == 0
