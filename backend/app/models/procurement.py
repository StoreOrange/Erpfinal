from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class SupplyItem(Base):
    __tablename__ = "supply_items"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(40), unique=True, nullable=False, index=True)
    name = Column(String(180), nullable=False, index=True)
    category = Column(String(100), nullable=True)
    unit = Column(String(40), nullable=False, default="Unidad")
    min_stock = Column(Numeric(14, 2), default=0)
    current_stock = Column(Numeric(14, 2), default=0)
    location = Column(String(140), nullable=True)
    notes = Column(Text, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    movements = relationship("SupplyMovement", back_populates="item", cascade="all, delete-orphan")


class SupplyMovement(Base):
    __tablename__ = "supply_movements"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("supply_items.id", ondelete="CASCADE"), nullable=False)
    fecha = Column(Date, nullable=False)
    tipo = Column(String(20), nullable=False)
    quantity = Column(Numeric(14, 2), nullable=False, default=0)
    unit_cost = Column(Numeric(14, 2), default=0)
    total_cost = Column(Numeric(14, 2), default=0)
    area = Column(String(120), nullable=True)
    requester = Column(String(120), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    item = relationship("SupplyItem", back_populates="movements")


class QuoteRequest(Base):
    __tablename__ = "quote_requests"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(40), unique=True, nullable=False, index=True)
    fecha = Column(Date, nullable=False)
    needed_by = Column(Date, nullable=True)
    requester = Column(String(120), nullable=False)
    department = Column(String(120), nullable=True)
    purpose = Column(String(220), nullable=False)
    status = Column(String(30), nullable=False, default="SOLICITADA")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    lines = relationship("QuoteRequestLine", back_populates="request", cascade="all, delete-orphan")
    quotes = relationship("SupplierQuote", back_populates="request", cascade="all, delete-orphan")


class QuoteRequestLine(Base):
    __tablename__ = "quote_request_lines"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("quote_requests.id", ondelete="CASCADE"), nullable=False)
    supply_item_id = Column(Integer, ForeignKey("supply_items.id"), nullable=True)
    description = Column(String(220), nullable=False)
    unit = Column(String(40), nullable=False, default="Unidad")
    quantity = Column(Numeric(14, 2), nullable=False, default=1)
    estimated_unit_cost = Column(Numeric(14, 2), default=0)
    preferred_supplier = Column(String(160), nullable=True)

    request = relationship("QuoteRequest", back_populates="lines")
    supply_item = relationship("SupplyItem")


class SupplierQuote(Base):
    __tablename__ = "supplier_quotes"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("quote_requests.id", ondelete="CASCADE"), nullable=False)
    supplier_name = Column(String(180), nullable=False)
    contact = Column(String(160), nullable=True)
    amount_cs = Column(Numeric(14, 2), default=0)
    delivery_days = Column(Integer, nullable=True)
    payment_terms = Column(String(160), nullable=True)
    status = Column(String(30), nullable=False, default="RECIBIDA")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    request = relationship("QuoteRequest", back_populates="quotes")
