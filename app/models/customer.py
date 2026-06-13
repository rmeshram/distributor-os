import uuid
from sqlalchemy import String, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, TenantMixin

class Customer(Base, TenantMixin):
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[str] = mapped_column(String(100), nullable=False)
    retailer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    address_text: Mapped[str] = mapped_column(String(512), nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    gstin: Mapped[str] = mapped_column(String(15), nullable=False)
    tax_group: Mapped[str] = mapped_column(String(100), nullable=False)
    payment_terms: Mapped[str] = mapped_column(String(255), nullable=False)

    aliases: Mapped[list["CustomerAlias"]] = relationship(back_populates="customer", cascade="all, delete-orphan")

class CustomerAlias(Base, TenantMixin):
    __tablename__ = "customer_aliases"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    alias_value: Mapped[str] = mapped_column(String(255), nullable=False) # WhatsApp phone number or alternative name

    customer: Mapped[Customer] = relationship(back_populates="aliases")
