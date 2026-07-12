"""Modelos de ventas y caja.

Hecho por Carlos.
Colaboracion academica: Oded Garcia y Carlos Ramirez.

Recordatorio:
las clases de este archivo son tablas. Las acciones como facturar, anular o
calcular totales deben vivir en routers o servicios, no dentro del modelo.
"""

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class Customer(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(180), nullable=False, index=True)
    telefono = Column(String(80), nullable=True)
    identificacion = Column(String(80), nullable=True, index=True)
    direccion = Column(String(250), nullable=True)
    email = Column(String(140), nullable=True)
    tipo = Column(String(40), nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class SalesInvoice(Base):
    __tablename__ = "sales_invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(40), unique=True, nullable=False, index=True)
    customer_name = Column(String(180), nullable=False, default="Consumidor final")
    customer_phone = Column(String(80), nullable=True)
    customer_document = Column(String(80), nullable=True)
    customer_address = Column(String(250), nullable=True)
    vendor_name = Column(String(160), nullable=True)
    bodega_id = Column(Integer, ForeignKey("bodegas.id"), nullable=False)
    egreso_id = Column(Integer, ForeignKey("egresos_inventario.id"), nullable=True)
    fecha = Column(Date, nullable=False)
    condicion = Column(String(20), nullable=False, default="CONTADO")
    moneda = Column(String(10), nullable=False, default="CS")
    tasa_cambio = Column(Numeric(12, 4), nullable=True)
    subtotal_usd = Column(Numeric(14, 2), default=0)
    subtotal_cs = Column(Numeric(14, 2), default=0)
    total_usd = Column(Numeric(14, 2), default=0)
    total_cs = Column(Numeric(14, 2), default=0)
    paid_usd = Column(Numeric(14, 2), default=0)
    paid_cs = Column(Numeric(14, 2), default=0)
    balance_usd = Column(Numeric(14, 2), default=0)
    balance_cs = Column(Numeric(14, 2), default=0)
    change_usd = Column(Numeric(14, 2), default=0)
    change_cs = Column(Numeric(14, 2), default=0)
    status = Column(String(20), nullable=False, default="EMITIDA")
    observacion = Column(Text, nullable=True)
    usuario_registro = Column(String(120), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    bodega = relationship("Bodega")
    egreso = relationship("EgresoInventario")
    items = relationship("SalesInvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("SalesPayment", back_populates="invoice", cascade="all, delete-orphan")


class SalesInvoiceItem(Base):
    __tablename__ = "sales_invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("sales_invoices.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cod_producto = Column(String(60), nullable=False)
    descripcion = Column(String(220), nullable=False)
    unidad = Column(String(30), nullable=True)
    cantidad = Column(Numeric(14, 4), nullable=False, default=0)
    precio_unitario_usd = Column(Numeric(14, 2), default=0)
    precio_unitario_cs = Column(Numeric(14, 2), default=0)
    subtotal_usd = Column(Numeric(14, 2), default=0)
    subtotal_cs = Column(Numeric(14, 2), default=0)
    combo_role = Column(String(20), nullable=True)
    combo_group = Column(String(60), nullable=True)

    invoice = relationship("SalesInvoice", back_populates="items")
    producto = relationship("Producto")


class SalesPayment(Base):
    __tablename__ = "sales_payments"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("sales_invoices.id"), nullable=False)
    forma_codigo = Column(String(40), nullable=False)
    forma_nombre = Column(String(100), nullable=False)
    moneda = Column(String(10), nullable=False)
    monto = Column(Numeric(14, 2), nullable=False, default=0)
    monto_usd = Column(Numeric(14, 2), default=0)
    monto_cs = Column(Numeric(14, 2), default=0)
    banco = Column(String(120), nullable=True)
    cuenta = Column(String(120), nullable=True)
    referencia = Column(String(120), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    invoice = relationship("SalesInvoice", back_populates="payments")


class SalesSequence(Base):
    __tablename__ = "sales_sequences"
    __table_args__ = (UniqueConstraint("prefix", name="uq_sales_sequences_prefix"),)

    id = Column(Integer, primary_key=True, index=True)
    prefix = Column(String(20), nullable=False, default="POS")
    current_value = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class CashClose(Base):
    __tablename__ = "cash_closures"
    __table_args__ = (UniqueConstraint("fecha", "bodega_id", name="uq_cash_closure_fecha_bodega"),)

    id = Column(Integer, primary_key=True, index=True)
    cierre_numero = Column(String(40), unique=True, nullable=False, index=True)
    fecha = Column(Date, nullable=False, index=True)
    bodega_id = Column(Integer, ForeignKey("bodegas.id"), nullable=True)
    usuario_registro = Column(String(120), nullable=True)
    total_ventas_cs = Column(Numeric(14, 2), default=0)
    total_ventas_usd = Column(Numeric(14, 2), default=0)
    efectivo_ventas_cs = Column(Numeric(14, 2), default=0)
    tarjeta_ventas_cs = Column(Numeric(14, 2), default=0)
    transferencia_ventas_cs = Column(Numeric(14, 2), default=0)
    otros_pagos_cs = Column(Numeric(14, 2), default=0)
    ingresos_caja_cs = Column(Numeric(14, 2), default=0)
    egresos_caja_cs = Column(Numeric(14, 2), default=0)
    detalle_cs = Column(Text, nullable=True)
    detalle_usd = Column(Text, nullable=True)
    total_efectivo_cs = Column(Numeric(14, 2), default=0)
    total_efectivo_usd = Column(Numeric(14, 2), default=0)
    tasa_cambio = Column(Numeric(12, 4), nullable=True)
    efectivo_esperado_cs = Column(Numeric(14, 2), default=0)
    efectivo_fisico_cs = Column(Numeric(14, 2), default=0)
    diferencia_cs = Column(Numeric(14, 2), default=0)
    resultado = Column(String(20), nullable=False, default="CUADRADO")
    observacion = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="CERRADO")
    created_at = Column(DateTime, server_default=func.now())

    bodega = relationship("Bodega")
    movements = relationship("CashCloseMovement", back_populates="closure", cascade="all, delete-orphan")


class CashVoucher(Base):
    __tablename__ = "cash_vouchers"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(40), unique=True, nullable=False, index=True)
    fecha = Column(Date, nullable=False, index=True)
    bodega_id = Column(Integer, ForeignKey("bodegas.id"), nullable=True)
    tipo = Column(String(20), nullable=False)
    rubro = Column(String(120), nullable=False)
    motivo = Column(String(160), nullable=False)
    descripcion = Column(Text, nullable=True)
    moneda = Column(String(10), nullable=False, default="CS")
    tasa_cambio = Column(Numeric(12, 4), nullable=True)
    monto_usd = Column(Numeric(14, 2), default=0)
    monto_cs = Column(Numeric(14, 2), default=0)
    afecta_caja = Column(Boolean, default=True)
    status = Column(String(20), nullable=False, default="EMITIDO")
    usuario_registro = Column(String(120), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    bodega = relationship("Bodega")


class CashCloseMovement(Base):
    __tablename__ = "cash_close_movements"

    id = Column(Integer, primary_key=True, index=True)
    closure_id = Column(Integer, ForeignKey("cash_closures.id"), nullable=False)
    tipo = Column(String(20), nullable=False)
    concepto = Column(String(160), nullable=False)
    monto_cs = Column(Numeric(14, 2), default=0)
    referencia = Column(String(120), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    closure = relationship("CashClose", back_populates="movements")
