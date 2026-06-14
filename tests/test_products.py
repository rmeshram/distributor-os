import io
import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.tenant import DistributorTenant
from app.models.product import Product, ProductAlias
from app.database import tenant_context

@pytest.fixture(name="client")
def fixture_client():
    return TestClient(app)

def test_import_products_success(db_session, client):
    # 1. Setup Tenant
    tenant = DistributorTenant(name="Import Test Tenant")
    db_session.add(tenant)
    db_session.commit()

    tenant_context.set(tenant.id)

    # 2. Add an existing product to update
    existing_prod = Product(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        sku_id="PROD-TEST-UPDATE",
        brand="BrandOld",
        category="CatOld",
        pack_size="50g",
        base_price=100.00
    )
    db_session.add(existing_prod)
    db_session.commit()

    # 3. Create mock CSV data
    # Contains:
    # - Update for existing_prod
    # - Insert for new_prod
    csv_content = (
        "sku_id,brand,category,pack_size,base_price\n"
        "PROD-TEST-UPDATE,BrandNew,CatNew,100g,120.50\n"
        "PROD-TEST-INSERT,BrandInsert,CatInsert,250g,45.00\n"
    )

    csv_file = io.BytesIO(csv_content.encode("utf-8"))

    # 4. Trigger import endpoint
    response = client.post(
        "/api/v1/products/import",
        data={"tenant_id": str(tenant.id)},
        files={"file": ("products.csv", csv_file, "text/csv")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["successful_rows"] == 2
    assert data["failed_rows"] == 0

    # 5. Assert database state
    # Verify existing product got updated
    db_session.expire_all()
    updated_prod = db_session.query(Product).filter_by(sku_id="PROD-TEST-UPDATE").one()
    assert float(updated_prod.base_price) == 120.50
    assert updated_prod.brand == "BrandNew"
    assert updated_prod.category == "CatNew"
    assert updated_prod.pack_size == "100g"

    # Verify new product got inserted
    inserted_prod = db_session.query(Product).filter_by(sku_id="PROD-TEST-INSERT").one()
    assert float(inserted_prod.base_price) == 45.00
    assert inserted_prod.brand == "BrandInsert"
    assert inserted_prod.category == "CatInsert"
    assert inserted_prod.pack_size == "250g"

    # Verify default aliases got created for the inserted product
    aliases = db_session.query(ProductAlias).filter_by(product_id=inserted_prod.id).all()
    assert len(aliases) == 2
    alias_names = {a.alias_name for a in aliases}
    assert "PROD-TEST-INSERT" in alias_names
    assert "BrandInsert CatInsert" in alias_names


def test_import_products_missing_headers(db_session, client):
    tenant = DistributorTenant(name="Import Header Test Tenant")
    db_session.add(tenant)
    db_session.commit()

    # CSV missing base_price column
    csv_content = (
        "sku_id,brand,category,pack_size\n"
        "PROD-FAIL,BrandFail,CatFail,100g\n"
    )

    csv_file = io.BytesIO(csv_content.encode("utf-8"))

    response = client.post(
        "/api/v1/products/import",
        data={"tenant_id": str(tenant.id)},
        files={"file": ("products.csv", csv_file, "text/csv")}
    )

    assert response.status_code == 400
    assert "missing required headers" in response.json()["detail"].lower()


def test_import_products_validation_rollback(db_session, client):
    tenant = DistributorTenant(name="Import Rollback Tenant")
    db_session.add(tenant)
    db_session.commit()

    # Row 3 contains invalid float value for price, causing rollback of the whole file
    csv_content = (
        "sku_id,brand,category,pack_size,base_price\n"
        "PROD-VALID-1,Brand1,Cat1,100g,10.00\n"
        "PROD-INVALID-2,Brand2,Cat2,200g,NOT_A_FLOAT\n"
    )

    csv_file = io.BytesIO(csv_content.encode("utf-8"))

    response = client.post(
        "/api/v1/products/import",
        data={"tenant_id": str(tenant.id)},
        files={"file": ("products.csv", csv_file, "text/csv")}
    )

    assert response.status_code == 422
    data = response.json()
    assert "errors" in data["detail"]
    assert any("NOT_A_FLOAT" in err for err in data["detail"]["errors"])

    # Verify transactional integrity: PROD-VALID-1 was NOT committed since the whole import failed
    db_session.expire_all()
    product_count = db_session.query(Product).filter(Product.tenant_id == tenant.id).count()
    assert product_count == 0
