import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, tenant_context, get_db
import app.models  # Registers all models

from sqlalchemy.pool import StaticPool

@pytest.fixture(name="db_engine")
def fixture_db_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="db_session")
def fixture_db_session(db_engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()
    yield session
    session.close()
    # Reset tenant context
    tenant_context.set(None)

@pytest.fixture(autouse=True)
def override_get_db(db_session):
    from app.main import app
    def _override():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.clear()
