from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class LineaBase(BaseModel):
    cod_linea: str
    linea: str
    activo: bool = True


class LineaCreate(LineaBase):
    pass


class LineaUpdate(BaseModel):
    cod_linea: Optional[str] = None
    linea: Optional[str] = None
    activo: Optional[bool] = None


class LineaResponse(LineaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    registro: Optional[datetime] = None


class SegmentoBase(BaseModel):
    segmento: str
    activo: bool = True


class SegmentoCreate(SegmentoBase):
    pass


class SegmentoUpdate(BaseModel):
    segmento: Optional[str] = None
    activo: Optional[bool] = None


class SegmentoResponse(SegmentoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    registro: Optional[datetime] = None


class UnidadMedidaBase(BaseModel):
    codigo: str
    nombre: str
    abreviatura: str
    activo: bool = True


class UnidadMedidaCreate(UnidadMedidaBase):
    pass


class UnidadMedidaUpdate(BaseModel):
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    abreviatura: Optional[str] = None
    activo: Optional[bool] = None


class UnidadMedidaResponse(UnidadMedidaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None


class MarcaBase(BaseModel):
    nombre: str
    activo: bool = True


class MarcaCreate(MarcaBase):
    pass


class MarcaUpdate(BaseModel):
    nombre: Optional[str] = None
    activo: Optional[bool] = None


class MarcaResponse(MarcaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None


class BodegaBase(BaseModel):
    code: str
    name: str
    sucursal_id: Optional[int] = None
    can_invoice: bool = True
    manages_inventory: bool = True
    supplies_only: bool = False
    invoice_series: Optional[str] = None
    invoice_sequence: int = 0
    activo: bool = True


class BodegaCreate(BodegaBase):
    pass


class BodegaUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    sucursal_id: Optional[int] = None
    can_invoice: Optional[bool] = None
    manages_inventory: Optional[bool] = None
    supplies_only: Optional[bool] = None
    invoice_series: Optional[str] = None
    invoice_sequence: Optional[int] = None
    activo: Optional[bool] = None


class BodegaResponse(BodegaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None


class ProveedorBase(BaseModel):
    nombre: str
    tipo: Optional[str] = None
    activo: bool = True


class ProveedorCreate(ProveedorBase):
    pass


class ProveedorUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    activo: Optional[bool] = None


class ProveedorResponse(ProveedorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None


class IngresoTipoBase(BaseModel):
    nombre: str
    requiere_proveedor: bool = False


class IngresoTipoCreate(IngresoTipoBase):
    pass


class IngresoTipoResponse(IngresoTipoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class EgresoTipoBase(BaseModel):
    nombre: str


class EgresoTipoCreate(EgresoTipoBase):
    pass


class EgresoTipoResponse(EgresoTipoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class SaldoProductoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    existencia: Decimal


class ProductoBase(BaseModel):
    cod_producto: str
    usa_codigo_barra: bool = False
    codigo_barra: Optional[str] = None
    descripcion: str
    segmento_id: Optional[int] = None
    linea_id: Optional[int] = None
    unidad_medida_id: Optional[int] = None
    marca_id: Optional[int] = None
    marca: Optional[str] = None
    presentacion: Optional[str] = None
    precio_venta1: Decimal = Field(default=Decimal("0"))
    precio_venta2: Decimal = Field(default=Decimal("0"))
    precio_venta3: Decimal = Field(default=Decimal("0"))
    activo: bool = True
    servicio_producto: bool = False
    es_por_peso: bool = False
    tipo_producto: str = "DIRECTO"
    costo_producto: Decimal = Field(default=Decimal("0"))
    referencia_producto: Optional[str] = None
    usuario_registro: Optional[str] = None
    maquina_registro: Optional[str] = None


class ProductoCreate(ProductoBase):
    cod_producto: Optional[str] = None
    existencia: Decimal = Field(default=Decimal("0"))
    bodega_inicial_id: Optional[int] = None


class ProductoUpdate(BaseModel):
    cod_producto: Optional[str] = None
    usa_codigo_barra: Optional[bool] = None
    codigo_barra: Optional[str] = None
    descripcion: Optional[str] = None
    segmento_id: Optional[int] = None
    linea_id: Optional[int] = None
    unidad_medida_id: Optional[int] = None
    marca_id: Optional[int] = None
    marca: Optional[str] = None
    presentacion: Optional[str] = None
    precio_venta1: Optional[Decimal] = None
    precio_venta2: Optional[Decimal] = None
    precio_venta3: Optional[Decimal] = None
    activo: Optional[bool] = None
    servicio_producto: Optional[bool] = None
    es_por_peso: Optional[bool] = None
    costo_producto: Optional[Decimal] = None
    referencia_producto: Optional[str] = None
    usuario_registro: Optional[str] = None
    maquina_registro: Optional[str] = None
    existencia: Optional[Decimal] = None


class ProductoResponse(ProductoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    registro: Optional[datetime] = None
    ultima_modificacion: Optional[datetime] = None
    saldo: Optional[SaldoProductoResponse] = None
    linea: Optional[LineaResponse] = None
    segmento: Optional[SegmentoResponse] = None
    unidad_medida: Optional[UnidadMedidaResponse] = None
    marca_ref: Optional[MarcaResponse] = None


class ProductoRecetaLineaPayload(BaseModel):
    insumo_producto_id: int
    unidad_medida_id: Optional[int] = None
    cantidad: Decimal


class ProductoRecetaSaveRequest(BaseModel):
    nombre: Optional[str] = None
    activo: bool = True
    lineas: List[ProductoRecetaLineaPayload]


class ProductoRecetaLineaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    insumo_producto_id: int
    unidad_medida_id: Optional[int] = None
    cantidad: Decimal
    insumo: Optional[ProductoResponse] = None
    unidad_medida: Optional[UnidadMedidaResponse] = None


class ProductoRecetaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    producto_final_id: int
    nombre: Optional[str] = None
    activo: bool = True
    lineas: List[ProductoRecetaLineaResponse]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProductoComboCreate(BaseModel):
    child_producto_id: int
    cantidad: Decimal = Field(default=Decimal("1"))
    activo: bool = True


class ProductoComboResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    parent_producto_id: int
    child_producto_id: int
    cantidad: Decimal
    activo: bool = True
    created_at: Optional[datetime] = None
    child: Optional[ProductoResponse] = None


class InventoryCatalogsResponse(BaseModel):
    lineas: List[LineaResponse]
    segmentos: List[SegmentoResponse]
    unidades_medida: List[UnidadMedidaResponse]
    marcas: List[MarcaResponse]
    bodegas: List[BodegaResponse]
    proveedores: List[ProveedorResponse]
    ingreso_tipos: List[IngresoTipoResponse]
    egreso_tipos: List[EgresoTipoResponse]


class IngresoItemCreate(BaseModel):
    producto_id: int
    cantidad: Decimal
    costo_unitario: Decimal = Field(default=Decimal("0"))


class IngresoCreate(BaseModel):
    tipo_id: int
    bodega_id: int
    proveedor_id: Optional[int] = None
    usuario_id: Optional[int] = None
    fecha: date
    moneda: str
    tasa_cambio: Optional[Decimal] = None
    observacion: Optional[str] = None
    usuario_registro: Optional[str] = None
    items: List[IngresoItemCreate]


class IngresoItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    producto_id: int
    cantidad: Decimal
    costo_unitario_usd: Decimal
    costo_unitario_cs: Decimal
    subtotal_usd: Decimal
    subtotal_cs: Decimal


class IngresoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo_id: int
    bodega_id: int
    proveedor_id: Optional[int] = None
    usuario_id: Optional[int] = None
    fecha: date
    moneda: str
    tasa_cambio: Optional[Decimal] = None
    total_usd: Decimal
    total_cs: Decimal
    observacion: Optional[str] = None
    usuario_registro: Optional[str] = None
    created_at: Optional[datetime] = None
    items: List[IngresoItemResponse]


class EgresoItemCreate(BaseModel):
    producto_id: int
    cantidad: Decimal
    costo_unitario: Optional[Decimal] = None


class EgresoCreate(BaseModel):
    tipo_id: int
    bodega_id: int
    bodega_destino_id: Optional[int] = None
    usuario_id: Optional[int] = None
    fecha: date
    moneda: str
    tasa_cambio: Optional[Decimal] = None
    observacion: Optional[str] = None
    usuario_registro: Optional[str] = None
    items: List[EgresoItemCreate]


class EgresoItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    producto_id: int
    cantidad: Decimal
    costo_unitario_usd: Decimal
    costo_unitario_cs: Decimal
    subtotal_usd: Decimal
    subtotal_cs: Decimal


class EgresoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo_id: int
    bodega_id: int
    bodega_destino_id: Optional[int] = None
    usuario_id: Optional[int] = None
    fecha: date
    moneda: str
    tasa_cambio: Optional[Decimal] = None
    total_usd: Decimal
    total_cs: Decimal
    observacion: Optional[str] = None
    usuario_registro: Optional[str] = None
    created_at: Optional[datetime] = None
    items: List[EgresoItemResponse]


class ProduccionInventarioCreate(BaseModel):
    producto_final_id: int
    bodega_id: int
    fecha: date
    cantidad_producida: Decimal
    moneda: str = "CS"
    tasa_cambio: Optional[Decimal] = None
    observacion: Optional[str] = None
    usuario_registro: Optional[str] = None


class ProduccionInventarioLineaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo_linea: str
    producto_id: int
    cantidad: Decimal
    costo_unitario_usd: Decimal
    costo_unitario_cs: Decimal
    subtotal_usd: Decimal
    subtotal_cs: Decimal
    producto: Optional[ProductoResponse] = None


class ProduccionInventarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    producto_final_id: int
    bodega_id: int
    fecha: date
    estado: str
    moneda: str
    tasa_cambio: Optional[Decimal] = None
    cantidad_producida: Decimal
    total_insumos_usd: Decimal
    total_insumos_cs: Decimal
    total_produccion_usd: Decimal
    total_produccion_cs: Decimal
    observacion: Optional[str] = None
    usuario_registro: Optional[str] = None
    ingreso_id: Optional[int] = None
    egreso_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    producto_final: Optional[ProductoResponse] = None
    bodega: Optional[BodegaResponse] = None
    lineas: List[ProduccionInventarioLineaResponse]


class PacaAperturaOrigenCreate(BaseModel):
    producto_id: int
    cantidad: Decimal


class PacaAperturaLineaCreate(BaseModel):
    producto_id: int
    cantidad: Decimal
    precio_estimado_unitario: Decimal = Field(default=Decimal("0"))


class PacaAperturaCreate(BaseModel):
    paca_producto_id: int
    bodega_id: int
    bodega_destino_id: Optional[int] = None
    fecha: date
    cantidad_pacas: Decimal = Field(default=Decimal("1"))
    moneda: str = "CS"
    tasa_cambio: Optional[Decimal] = None
    observacion: Optional[str] = None
    usuario_registro: Optional[str] = None
    pacas_origen: List[PacaAperturaOrigenCreate] = Field(default_factory=list)
    lineas: List[PacaAperturaLineaCreate]


class PacaAperturaOrigenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    producto_id: int
    cantidad: Decimal
    costo_unitario_usd: Decimal
    costo_unitario_cs: Decimal
    subtotal_usd: Decimal
    subtotal_cs: Decimal
    producto: Optional[ProductoResponse] = None


class PacaAperturaLineaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    producto_id: int
    cantidad: Decimal
    precio_estimado_unitario_usd: Decimal
    precio_estimado_unitario_cs: Decimal
    valor_estimado_usd: Decimal
    valor_estimado_cs: Decimal
    costo_asignado_unitario_usd: Decimal
    costo_asignado_unitario_cs: Decimal
    costo_asignado_usd: Decimal
    costo_asignado_cs: Decimal
    producto: Optional[ProductoResponse] = None


class PacaAperturaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    paca_producto_id: int
    bodega_id: int
    bodega_destino_id: Optional[int] = None
    fecha: date
    cantidad_pacas: Decimal
    moneda: str
    tasa_cambio: Optional[Decimal] = None
    costo_origen_usd: Decimal
    costo_origen_cs: Decimal
    valor_estimado_usd: Decimal
    valor_estimado_cs: Decimal
    diferencia_usd: Decimal
    diferencia_cs: Decimal
    estado: str
    observacion: Optional[str] = None
    usuario_registro: Optional[str] = None
    ingreso_id: Optional[int] = None
    egreso_id: Optional[int] = None
    created_at: Optional[datetime] = None
    paca_producto: Optional[ProductoResponse] = None
    bodega: Optional[BodegaResponse] = None
    bodega_destino: Optional[BodegaResponse] = None
    origenes: List[PacaAperturaOrigenResponse] = Field(default_factory=list)
    lineas: List[PacaAperturaLineaResponse]


class KardexMovimientoResponse(BaseModel):
    fecha: date
    tipo: str
    documento: str
    producto_id: int
    cod_producto: str
    descripcion: str
    cantidad_entrada: Decimal = Field(default=Decimal("0"))
    cantidad_salida: Decimal = Field(default=Decimal("0"))
    costo_unitario_cs: Decimal = Field(default=Decimal("0"))
    subtotal_cs: Decimal = Field(default=Decimal("0"))


class ProductSearchItemResponse(BaseModel):
    id: int
    cod_producto: str
    codigo_barra: str = ""
    descripcion: str
    precio_venta1: float
    precio_venta2: float
    precio_venta3: float
    selected_price_tier: int
    selected_price_cs: float
    selected_price_usd: float = 0
    existencia: float
    free_qty: float
    combo_count: int = 0
    es_por_peso: bool
    unidad_medida_id: Optional[int] = None
    unidad_medida_nombre: str = ""
    unidad_medida_abreviatura: str = ""


class ProductSearchResponse(BaseModel):
    ok: bool = True
    items: List[ProductSearchItemResponse]


class ProductBodegaBalanceResponse(BaseModel):
    bodega_id: int
    bodega_code: str
    bodega_name: str
    existencia: float
