import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, status, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.ingestion_service import IngestionService

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])

@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_bulk_file(
    tenant_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Uploads an Excel or CSV file containing SKU inventory data.
    Row-by-row mapping is validated and written to staging. Valid rows update inventory,
    and invalid rows remain in IngestionStaging with error messages.
    """
    filename = file.filename
    if not filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only CSV and Excel (.xlsx, .xls) files are supported."
        )

    try:
        content = await file.read()
        service = IngestionService()
        job = service.ingest_file(
            db=db,
            tenant_id=tenant_id,
            file_content=content,
            filename=filename
        )

        return {
            "job_id": str(job.id),
            "filename": job.filename,
            "status": job.status,
            "total_rows": job.total_rows,
            "successful_rows": job.successful_rows,
            "failed_rows": job.failed_rows,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during file upload: {str(e)}"
        )
