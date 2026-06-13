from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(
    title="DistributorOS API Backend",
    description="AI-Native Distribution Operating System for India",
    version="2.0.0"
)

# Include the API router
app.include_router(api_router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to DistributorOS Backend Core API",
        "documentation": "/docs"
    }
