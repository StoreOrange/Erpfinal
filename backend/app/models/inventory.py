"""Modelos de inventario.

Hecho por Carlos.
Colaboracion academica: Oded Garcia y Carlos Ramirez.

Recordatorio para el equipo:
estos modelos representan tablas de base de datos. No colocar aqui reglas
visuales ni codigo de interfaz; solo estructura de datos y relaciones.
"""

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class Linea(Base):
    __tablename__ = "lineas"

    id = Column(Integer, primary_key=True, index=True)
    cod_linea = Column(String(50), unique=True, nullable=False)
    linea = Column(String(120), nullable=False)
    activo = Column(Boolean, default=True)
    registro = Column(DateTime, server_default=func.now())

    productos = relationship("Producto", back_populates="linea")


class Segmento(Base):
    __tablename__ = "segmentos"

    id = Column(Integer, primary_key=True, index=True)
    segmento = Column(String(120), unique=True, nullable=False)
    activo = Column(Boolean, default=True)
    registro = Column(DateTime, server_default=func.now())

    productos = relationship("Producto", back_populates="segmento")


class UnidadMedida(Base):
    __tablename__ = "unidades_medida"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, nullable=False)
    nombre = Column(String(80), unique=True, nullable=False)
    abreviatura = Column(String(20), nullable=False)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    productos = relationship("Producto", back_populates="unidad_medida")


class Marca(Base):
    __tablename__ = "marcas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), unique=True, nullable=False)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    productos = relationship("Producto", back_populates="marca_ref")


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    cod_producto = Column(String(60), unique=True, nullable=False)
    usa_codigo_barra = Column(Boolean, default=False)
    codigo_barra = Column(String(120), unique=True, nullable=True)
    descripcion = Column(String(200), nullable=False)
    segmento_id = Column(Integer, ForeignKey("segmentos.id"), nullable=True)
    linea_id = Column(Integer, ForeignKey("lineas.id"), nullable=True)
    unidad_medida_id = Column(Integer, ForeignKey("unidades_medida.id"), nullable=True)
    marca_id = Column(Integer, ForeignKey("marcas.id"), nullable=True)
    marca = Column(String(80), nullable=True)
    presentacion = Column(String(100), nullable=True)
    precio_venta1 = Column(Numeric(12, 2), default=0)
    precio_venta2 = Column(Numeric(12, 2), default=0)
    precio_venta3 = Column(Numeric(12, 2), default=0)
    activo = Column(Boolean, default=True)
    servicio_producto = Column(Boolean, default=False)
    es_por_peso = Column(Boolean, default=False)
    costo_producto = Column(Numeric(12, 2), default=0)
    referencia_producto = Column(String(120), nullable=True)
    tipo_producto = Column(String(30), nullable=False, default="DIRECTO")
    usuario_registro = Column(String(80), nullable=True)
    maquina_registro = Column(String(80), nullable=True)
    registro = Column(DateTime, server_default=func.now())
    ultima_modificacion = Column(DateTime, server_default=func.now(), onupdate=func.now())

    linea = relationship("Linea", back_populates="productos")
    segmento = relationship("Segmento", back_populates="productos")
    unidad_medida = relationship("UnidadMedida", back_populates="productos")
    marca_ref = relationship("Marca", back_populates="productos")
    saldo = relationship("SaldoProducto", back_populates="producto", uselist=False, cascade="all, delete-orphan")
    receta = relationship(
        "ProductoReceta",
        back_populates="producto_final",
        uselist=False,
        cascade="all, delete-orphan",
        foreign_keys="ProductoReceta.producto_final_id",
    )
    receta_insumo = relationship(
        "ProductoRecetaLinea",
        back_populates="insumo",
        foreign_keys="ProductoRecetaLinea.insumo_producto_id",
    )
    combo_children = relationship(
        "ProductoCombo",
        back_populates="parent",
        cascade="all, delete-orphan",
        foreign_keys="ProductoCombo.parent_producto_id",
    )


class ProductoCombo(Base):
    __tablename__ = "producto_combos"
    __table_args__ = (
        UniqueConstraint("parent_producto_id", "child_producto_id", name="uq_producto_combo_child"),
    )

    id = Column(Integer, primary_key=True, index=True)
    parent_producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    child_producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Numeric(12, 2), default=1)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    parent = relationship("Producto", foreign_keys=[parent_producto_id], back_populates="combo_children")
    child = relationship("Producto", foreign_keys=[child_producto_id])


class ProductoReceta(Base):
    __tablename__ = "productos_recetas"

    id = Column(Integer, primary_key=True, index=True)
    producto_final_id = Column(Integer, ForeignKey("productos.id"), nullable=False, unique=True)
    nombre = Column(String(160), nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    producto_final = relationship("Producto", back_populates="receta", foreign_keys=[producto_final_id])
    lineas = relationship(
        "ProductoRecetaLinea",
        back_populates="receta",
        cascade="all, delete-orphan",
        order_by="ProductoRecetaLinea.id",
    )


class ProductoRecetaLinea(Base):
    __tablename__ = "productos_receta_lineas"
    __table_args__ = (
        UniqueConstraint("receta_id", "insumo_producto_id", name="uq_producto_receta_insumo"),
    )

    id = Column(Integer, primary_key=True, index=True)
    receta_id = Column(Integer, ForeignKey("productos_recetas.id"), nullable=False)
    insumo_producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    unidad_medida_id = Column(Integer, ForeignKey("unidades_medida.id"), nullable=True)
    cantidad = Column(Numeric(14, 4), nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    receta = relationship("ProductoReceta", back_populates="lineas")
    insumo = relationship("Producto", back_populates="receta_insumo", foreign_keys=[insumo_producto_id])
    unidad_medida = relationship("UnidadMedida")


class SaldoProducto(Base):
    __tablename__ = "saldos_productos"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), unique=True, nullable=False)
    existencia = Column(Numeric(14, 2), default=0)

    producto = relationship("Producto", back_populates="saldo")


class Bodega(Base):
    __tablename__ = "bodegas"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(40), unique=True, nullable=False)
    name = Column(String(120), nullable=False)
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    sucursal = relationship("Branch", back_populates="bodegas")
    access_profiles = relationship("UserAccessProfile", back_populates="bodega")
    vendors = relationship("Vendor", back_populates="bodega")


class Proveedor(Base):
    __tablename__ = "proveedores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(160), unique=True, nullable=False)
    tipo = Column(String(40), nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class IngresoTipo(Base):
    __tablename__ = "ingreso_tipos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), unique=True, nullable=False)
    requiere_proveedor = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


class IngresoInventario(Base):
    __tablename__ = "ingresos_inventario"

    id = Column(Integer, primary_key=True, index=True)
    tipo_id = Column(Integer, ForeignKey("ingreso_tipos.id"), nullable=False)
    bodega_id = Column(Integer, ForeignKey("bodegas.id"), nullable=False)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=True)
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    fecha = Column(Date, nullable=False)
    moneda = Column(String(10), nullable=False)
    tasa_cambio = Column(Numeric(12, 4), nullable=True)
    total_usd = Column(Numeric(14, 2), default=0)
    total_cs = Column(Numeric(14, 2), default=0)
    observacion = Column(String(300), nullable=True)
    usuario_registro = Column(String(120), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    tipo = relationship("IngresoTipo")
    bodega = relationship("Bodega")
    proveedor = relationship("Proveedor")
    usuario = relationship("User")
    items = relationship("IngresoItem", back_populates="ingreso", cascade="all, delete-orphan")


class IngresoItem(Base):
    __tablename__ = "ingreso_items"

    id = Column(Integer, primary_key=True, index=True)
    ingreso_id = Column(Integer, ForeignKey("ingresos_inventario.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Numeric(14, 2), default=0)
    costo_unitario_usd = Column(Numeric(14, 2), default=0)
    costo_unitario_cs = Column(Numeric(14, 2), default=0)
    subtotal_usd = Column(Numeric(14, 2), default=0)
    subtotal_cs = Column(Numeric(14, 2), default=0)

    ingreso = relationship("IngresoInventario", back_populates="items")
    producto = relationship("Producto")


class EgresoTipo(Base):
    __tablename__ = "egreso_tipos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class EgresoInventario(Base):
    __tablename__ = "egresos_inventario"

    id = Column(Integer, primary_key=True, index=True)
    tipo_id = Column(Integer, ForeignKey("egreso_tipos.id"), nullable=False)
    bodega_id = Column(Integer, ForeignKey("bodegas.id"), nullable=False)
    bodega_destino_id = Column(Integer, ForeignKey("bodegas.id"), nullable=True)
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    fecha = Column(Date, nullable=False)
    moneda = Column(String(10), nullable=False)
    tasa_cambio = Column(Numeric(12, 4), nullable=True)
    total_usd = Column(Numeric(14, 2), default=0)
    total_cs = Column(Numeric(14, 2), default=0)
    observacion = Column(String(300), nullable=True)
    usuario_registro = Column(String(120), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    tipo = relationship("EgresoTipo")
    bodega = relationship("Bodega", foreign_keys=[bodega_id])
    bodega_destino = relationship("Bodega", foreign_keys=[bodega_destino_id])
    usuario = relationship("User")
    items = relationship("EgresoItem", back_populates="egreso", cascade="all, delete-orphan")


class EgresoItem(Base):
    __tablename__ = "egreso_items"

    id = Column(Integer, primary_key=True, index=True)
    egreso_id = Column(Integer, ForeignKey("egresos_inventario.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Numeric(14, 2), default=0)
    costo_unitario_usd = Column(Numeric(14, 2), default=0)
    costo_unitario_cs = Column(Numeric(14, 2), default=0)
    subtotal_usd = Column(Numeric(14, 2), default=0)
    subtotal_cs = Column(Numeric(14, 2), default=0)

    egreso = relationship("EgresoInventario", back_populates="items")
    producto = relationship("Producto")


class ProduccionInventario(Base):
    __tablename__ = "producciones_inventario"

    id = Column(Integer, primary_key=True, index=True)
    producto_final_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    bodega_id = Column(Integer, ForeignKey("bodegas.id"), nullable=False)
    fecha = Column(Date, nullable=False)
    estado = Column(String(20), nullable=False, default="ABIERTA")
    moneda = Column(String(10), nullable=False, default="CS")
    tasa_cambio = Column(Numeric(12, 4), nullable=True)
    cantidad_producida = Column(Numeric(14, 4), nullable=False, default=0)
    total_insumos_usd = Column(Numeric(14, 2), default=0)
    total_insumos_cs = Column(Numeric(14, 2), default=0)
    total_produccion_usd = Column(Numeric(14, 2), default=0)
    total_produccion_cs = Column(Numeric(14, 2), default=0)
    observacion = Column(String(300), nullable=True)
    usuario_registro = Column(String(120), nullable=True)
    ingreso_id = Column(Integer, ForeignKey("ingresos_inventario.id"), nullable=True)
    egreso_id = Column(Integer, ForeignKey("egresos_inventario.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    producto_final = relationship("Producto")
    bodega = relationship("Bodega")
    ingreso = relationship("IngresoInventario", foreign_keys=[ingreso_id])
    egreso = relationship("EgresoInventario", foreign_keys=[egreso_id])
    lineas = relationship("ProduccionInventarioLinea", back_populates="produccion", cascade="all, delete-orphan")


class ProduccionInventarioLinea(Base):
    __tablename__ = "producciones_inventario_lineas"

    id = Column(Integer, primary_key=True, index=True)
    produccion_id = Column(Integer, ForeignKey("producciones_inventario.id"), nullable=False)
    tipo_linea = Column(String(20), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Numeric(14, 4), nullable=False, default=0)
    costo_unitario_usd = Column(Numeric(14, 2), default=0)
    costo_unitario_cs = Column(Numeric(14, 2), default=0)
    subtotal_usd = Column(Numeric(14, 2), default=0)
    subtotal_cs = Column(Numeric(14, 2), default=0)

    produccion = relationship("ProduccionInventario", back_populates="lineas")
    producto = relationship("Producto")


class PacaApertura(Base):
    __tablename__ = "paca_aperturas"

    id = Column(Integer, primary_key=True, index=True)
    paca_producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    bodega_id = Column(Integer, ForeignKey("bodegas.id"), nullable=False)
    bodega_destino_id = Column(Integer, ForeignKey("bodegas.id"), nullable=True)
    fecha = Column(Date, nullable=False)
    cantidad_pacas = Column(Numeric(14, 4), nullable=False, default=1)
    moneda = Column(String(10), nullable=False, default="CS")
    tasa_cambio = Column(Numeric(12, 4), nullable=True)
    costo_origen_usd = Column(Numeric(14, 2), default=0)
    costo_origen_cs = Column(Numeric(14, 2), default=0)
    valor_estimado_usd = Column(Numeric(14, 2), default=0)
    valor_estimado_cs = Column(Numeric(14, 2), default=0)
    diferencia_usd = Column(Numeric(14, 2), default=0)
    diferencia_cs = Column(Numeric(14, 2), default=0)
    estado = Column(String(20), nullable=False, default="FINALIZADA")
    observacion = Column(String(300), nullable=True)
    usuario_registro = Column(String(120), nullable=True)
    ingreso_id = Column(Integer, ForeignKey("ingresos_inventario.id"), nullable=True)
    egreso_id = Column(Integer, ForeignKey("egresos_inventario.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    paca_producto = relationship("Producto", foreign_keys=[paca_producto_id])
    bodega = relationship("Bodega", foreign_keys=[bodega_id])
    bodega_destino = relationship("Bodega", foreign_keys=[bodega_destino_id])
    ingreso = relationship("IngresoInventario", foreign_keys=[ingreso_id])
    egreso = relationship("EgresoInventario", foreign_keys=[egreso_id])
    origenes = relationship("PacaAperturaOrigen", back_populates="apertura", cascade="all, delete-orphan")
    lineas = relationship("PacaAperturaLinea", back_populates="apertura", cascade="all, delete-orphan")


class PacaAperturaOrigen(Base):
    __tablename__ = "paca_apertura_origenes"

    id = Column(Integer, primary_key=True, index=True)
    apertura_id = Column(Integer, ForeignKey("paca_aperturas.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Numeric(14, 4), nullable=False, default=0)
    costo_unitario_usd = Column(Numeric(14, 2), default=0)
    costo_unitario_cs = Column(Numeric(14, 2), default=0)
    subtotal_usd = Column(Numeric(14, 2), default=0)
    subtotal_cs = Column(Numeric(14, 2), default=0)

    apertura = relationship("PacaApertura", back_populates="origenes")
    producto = relationship("Producto")


class PacaAperturaLinea(Base):
    __tablename__ = "paca_apertura_lineas"

    id = Column(Integer, primary_key=True, index=True)
    apertura_id = Column(Integer, ForeignKey("paca_aperturas.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Numeric(14, 4), nullable=False, default=0)
    precio_estimado_unitario_usd = Column(Numeric(14, 2), default=0)
    precio_estimado_unitario_cs = Column(Numeric(14, 2), default=0)
    valor_estimado_usd = Column(Numeric(14, 2), default=0)
    valor_estimado_cs = Column(Numeric(14, 2), default=0)
    costo_asignado_unitario_usd = Column(Numeric(14, 2), default=0)
    costo_asignado_unitario_cs = Column(Numeric(14, 2), default=0)
    costo_asignado_usd = Column(Numeric(14, 2), default=0)
    costo_asignado_cs = Column(Numeric(14, 2), default=0)

    apertura = relationship("PacaApertura", back_populates="lineas")
    producto = relationship("Producto")
