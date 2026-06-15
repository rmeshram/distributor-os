import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.database import engine, Base

# CRITICAL: Force table lifecycle creation on server startup
# This scans all registered ORM models and creates the tables instantly if missing
Base.metadata.create_all(bind=engine)

from sqlalchemy import text
try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE products ADD COLUMN stock_quantity INTEGER DEFAULT 100"))
        conn.commit()
except Exception:
    pass

try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE customers ADD COLUMN credit_limit NUMERIC DEFAULT 100000.0"))
        conn.execute(text("ALTER TABLE customers ADD COLUMN outstanding_balance NUMERIC DEFAULT 0.0"))
        conn.commit()
except Exception:
    pass

try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE distributor_tenants ADD COLUMN category VARCHAR(100);"))
        conn.commit()
except Exception:
    pass

app = FastAPI(
    title="Distributor OS API",
    description="Multi-tenant backend platform for supply chain distributors",
    version="1.0.0"
)

# Robust CORS origin list — hardcode production frontend + local dev defaults
# Override at runtime via ALLOWED_ORIGINS env var (comma-separated)
allowed_origins = [
    "https://distributor-os-ui.onrender.com",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
env_origins = os.getenv("ALLOWED_ORIGINS")
if env_origins:
    # Split by comma, strip whitespace, filter empty strings safely
    allowed_origins = [orig.strip() for orig in env_origins.split(",") if orig.strip()]

# Enforce explicit CORS origins so credentials (HttpOnly cookies) transmit correctly
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "healthy", "service": "Distributor OS Backend Core"}
