import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, Integer, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, TenantMixin

class IngestionJob(Base, TenantMixin):
    __tablename__ = "ingestion_jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source: Mapped[str] = mapped_column(String(50), nullable=False) # "WhatsApp", "Excel", "CSV"
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Pending") # "Pending", "Processing", "Completed"
    filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    total_rows: Mapped[int] = mapped_column(Integer, default=0)
    successful_rows: Mapped[int] = mapped_column(Integer, default=0)
    failed_rows: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    staging_rows: Mapped[list["IngestionStaging"]] = relationship(back_populates="job", cascade="all, delete-orphan")

class IngestionStaging(Base, TenantMixin):
    __tablename__ = "ingestion_staging"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ingestion_jobs.id", ondelete="CASCADE"), nullable=False)
    raw_data: Mapped[dict] = mapped_column(JSON, nullable=False) # Contains the raw row data as a key-value dictionary
    status: Mapped[str] = mapped_column(String(50), default="Staged") # "Staged", "Validated", "Failed"
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    job: Mapped[IngestionJob] = relationship(back_populates="staging_rows")
