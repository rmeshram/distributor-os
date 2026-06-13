import uuid
from sqlalchemy import String, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base, TenantMixin

class Invoice(Base, TenantMixin):
    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    gstin: Mapped[str] = mapped_column(String(15), nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    irn_status: Mapped[str] = mapped_column(String(50), default="Pending")
    qr_code_status: Mapped[str] = mapped_column(String(50), default="Pending")
