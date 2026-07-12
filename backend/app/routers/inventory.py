"""Router de inventario.

Hecho por Carlos.
Colaboracion academica: Oded Garcia y Carlos Ramirez.

Contiene operaciones de productos, ingresos, egresos, saldos, produccion y
apertura de pacas. Revisar con cuidado antes de tocar calculos de existencia.
"""

from datetime import date
from decimal import Decimal
import re
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models.inventory import (
    Bodega,
    EgresoInventario,
    EgresoItem,
    EgresoTipo,
    IngresoInventario,
    IngresoItem,
    IngresoTipo,
    Linea,
    Marca,
    PacaApertura,
    PacaAperturaOrigen,
    PacaAperturaLinea,
    Producto,
    ProductoCombo,
    ProductoReceta,
    ProductoRecetaLinea,
    ProduccionInventario,
    ProduccionInventarioLinea,
    Proveedor,
    SaldoProducto,
    Segmento,
    UnidadMedida,
)
from ..models.settings import BusinessSetting, ExchangeRate
from ..schemas.inventory import (
    BodegaCreate,
    BodegaResponse,
    EgresoCreate,
    EgresoResponse,
    EgresoTipoCreate,
    EgresoTipoResponse,
    IngresoCreate,
    IngresoResponse,
    IngresoTipoCreate,
    IngresoTipoResponse,
    InventoryCatalogsResponse,
    KardexMovimientoResponse,
    LineaCreate,
    LineaResponse,
    LineaUpdate,
    MarcaCreate,
    MarcaResponse,
    MarcaUpdate,
    ProductBodegaBalanceResponse,
    ProductSearchResponse,
    PacaAperturaCreate,
    PacaAperturaResponse,
    ProductoRecetaResponse,
    ProductoRecetaSaveRequest,
    ProductoComboCreate,
    ProductoComboResponse,
    ProductoCreate,
    ProductoResponse,
    ProductoUpdate,
    ProduccionInventarioCreate,
    ProduccionInventarioResponse,
    ProveedorCreate,
    ProveedorResponse,
    ProveedorUpdate,
    SegmentoCreate,
    SegmentoResponse,
    SegmentoUpdate,
    UnidadMedidaCreate,
    UnidadMedidaResponse,
    UnidadMedidaUpdate,
)

router = APIRouter(prefix="/inventory", tags=["Inventory"])


def _normalize_product_code(code: str) -> str:
    value = (code or "").strip().upper()
    if not value:
        raise HTTPException(status_code=400, detail="El codigo de producto es requerido")
    return value


def _normalize_barcode(code: str | None) -> str | None:
    value = (code or "").strip().upper()
    return value or None


def _next_product_code(db: Session) -> str:
    rows = db.query(Producto.id, Producto.cod_producto).all()
    max_value = 0

    for product_id, raw_code in rows:
        max_value = max(max_value, int(product_id or 0))
        value = (raw_code or "").strip()
        if re.fullmatch(r"\d+", value):
            max_value = max(max_value, int(value))

    return f"{max_value + 1:05d}"


def _normalize_text(value: str | None, field_name: str) -> str:
    text = (value or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail=f"{field_name} es requerido")
    return text


def _normalize_currency(moneda: str) -> str:
    value = (moneda or "").strip().upper()
    if value not in {"USD", "CS"}:
        raise HTTPException(status_code=400, detail="La moneda debe ser USD o CS")
    return value


def _require_exchange_rate(moneda: str, tasa_cambio: Decimal | None) -> Decimal:
    if moneda == "USD":
        if tasa_cambio is None or tasa_cambio <= 0:
            raise HTTPException(status_code=400, detail="La tasa de cambio es requerida para moneda USD")
        return tasa_cambio
    return tasa_cambio or Decimal("0")


def _current_exchange_rate_value(db: Session) -> Decimal:
    row = (
        db.query(ExchangeRate)
        .filter(ExchangeRate.is_active.is_(True), ExchangeRate.effective_date <= date.today())
        .order_by(ExchangeRate.effective_date.desc(), ExchangeRate.id.desc())
        .first()
    )
    if not row or Decimal(str(row.rate or 0)) <= 0:
        raise HTTPException(status_code=400, detail="Registra una tasa de cambio vigente antes de procesar apertura de pacas")
    return Decimal(str(row.rate)).quantize(Decimal("0.0001"))


def _get_or_create_saldo(db: Session, producto_id: int) -> SaldoProducto:
    saldo = db.query(SaldoProducto).filter(SaldoProducto.producto_id == producto_id).first()
    if saldo:
        return saldo
    saldo = SaldoProducto(producto_id=producto_id, existencia=Decimal("0"))
    db.add(saldo)
    db.flush()
    return saldo


def _normalize_price_tier(price_list: int | None, default: int = 1) -> int:
    if price_list is None:
        return default
    if price_list not in {1, 2, 3}:
        return default
    return price_list


def _balances_by_bodega(
    db: Session,
    bodega_ids: list[int],
    product_ids: list[int],
) -> dict[tuple[int, int], Decimal]:
    if not bodega_ids or not product_ids:
        return {}

    balances: dict[tuple[int, int], Decimal] = {}
    ingreso_rows = (
        db.query(IngresoItem.producto_id, IngresoInventario.bodega_id, func.sum(IngresoItem.cantidad))
        .join(IngresoInventario, IngresoInventario.id == IngresoItem.ingreso_id)
        .filter(
            IngresoInventario.bodega_id.in_(bodega_ids),
            IngresoItem.producto_id.in_(product_ids),
        )
        .group_by(IngresoItem.producto_id, IngresoInventario.bodega_id)
        .all()
    )
    egreso_rows = (
        db.query(EgresoItem.producto_id, EgresoInventario.bodega_id, func.sum(EgresoItem.cantidad))
        .join(EgresoInventario, EgresoInventario.id == EgresoItem.egreso_id)
        .filter(
            EgresoInventario.bodega_id.in_(bodega_ids),
            EgresoItem.producto_id.in_(product_ids),
        )
        .group_by(EgresoItem.producto_id, EgresoInventario.bodega_id)
        .all()
    )

    for producto_id, bodega_id, qty in ingreso_rows:
        balances[(int(producto_id), int(bodega_id))] = Decimal(str(qty or 0))
    for producto_id, bodega_id, qty in egreso_rows:
        key = (int(producto_id), int(bodega_id))
        balances[key] = balances.get(key, Decimal("0")) - Decimal(str(qty or 0))
    return balances


def _rebuild_global_saldo(db: Session, producto_id: int) -> Decimal:
    total_entradas = (
        db.query(func.coalesce(func.sum(IngresoItem.cantidad), 0))
        .filter(IngresoItem.producto_id == producto_id)
        .scalar()
    )
    total_salidas = (
        db.query(func.coalesce(func.sum(EgresoItem.cantidad), 0))
        .filter(EgresoItem.producto_id == producto_id)
        .scalar()
    )
    existencia = Decimal(str(total_entradas or 0)) - Decimal(str(total_salidas or 0))
    saldo = _get_or_create_saldo(db, producto_id)
    saldo.existencia = existencia
    return existencia


def _ensure_catalog_refs(
    db: Session,
    linea_id: int | None,
    segmento_id: int | None,
    unidad_medida_id: int | None,
    marca_id: int | None = None,
    bodega_id: int | None = None,
) -> None:
    if linea_id and not db.query(Linea).filter(Linea.id == linea_id).first():
        raise HTTPException(status_code=404, detail="Linea no encontrada")
    if segmento_id and not db.query(Segmento).filter(Segmento.id == segmento_id).first():
        raise HTTPException(status_code=404, detail="Segmento no encontrado")
    if unidad_medida_id and not db.query(UnidadMedida).filter(UnidadMedida.id == unidad_medida_id).first():
        raise HTTPException(status_code=404, detail="Unidad de medida no encontrada")
    if marca_id and not db.query(Marca).filter(Marca.id == marca_id).first():
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    if bodega_id and not db.query(Bodega).filter(Bodega.id == bodega_id).first():
        raise HTTPException(status_code=404, detail="Bodega inicial no encontrada")


def _recipe_explosion_on_ingreso_mode(db: Session) -> bool:
    row = db.query(BusinessSetting).first()
    return bool(getattr(row, "recipe_explosion_on_ingreso", False)) if row else False


def _get_business_settings(db: Session) -> BusinessSetting | None:
    return db.query(BusinessSetting).first()


def _inventory_cost_currency(settings: BusinessSetting | None) -> str:
    if settings and bool(getattr(settings, "inventory_cs_only", False)):
        return "CS"
    currency = (getattr(settings, "pricing_currency", "CS") or "CS").strip().upper() if settings else "CS"
    return "USD" if currency == "USD" else "CS"


def _cost_pair_from_amount(amount: Decimal, moneda: str, tasa: Decimal) -> tuple[Decimal, Decimal]:
    value = Decimal(str(amount or 0))
    if moneda == "USD":
        return value, value * tasa
    costo_cs = value
    costo_usd = costo_cs / tasa if tasa > 0 else Decimal("0")
    return costo_usd, costo_cs


def _product_cost_pair(
    producto: Producto,
    tasa: Decimal,
    settings: BusinessSetting | None,
) -> tuple[Decimal, Decimal]:
    stored_cost = Decimal(str(producto.costo_producto or 0))
    return _cost_pair_from_amount(stored_cost, _inventory_cost_currency(settings), tasa)


def _assign_product_cost(
    producto: Producto,
    costo_usd: Decimal,
    costo_cs: Decimal,
    settings: BusinessSetting | None,
) -> None:
    producto.costo_producto = costo_usd if _inventory_cost_currency(settings) == "USD" else costo_cs


def _normalize_product_type(value: str | None) -> str:
    normalized = (value or "DIRECTO").strip().upper()
    return "RECETA" if normalized == "RECETA" else "DIRECTO"


def _build_recipe_requirements(
    db: Session,
    items: list[tuple[int, Decimal]],
) -> tuple[dict[int, dict[str, object]], str | None]:
    requirements: dict[int, dict[str, object]] = {}
    for product_id, qty in items:
        if qty <= 0:
            continue
        producto = (
            db.query(Producto)
            .options(
                joinedload(Producto.receta).joinedload(ProductoReceta.lineas).joinedload(ProductoRecetaLinea.insumo),
                joinedload(Producto.receta).joinedload(ProductoReceta.lineas).joinedload(ProductoRecetaLinea.unidad_medida),
            )
            .filter(Producto.id == int(product_id))
            .first()
        )
        if not producto:
            return {}, "Producto no encontrado en produccion"
        if _normalize_product_type(getattr(producto, "tipo_producto", "DIRECTO")) != "RECETA":
            continue
        receta = producto.receta
        if not receta or not (receta.lineas or []):
            return {}, f"El producto {producto.cod_producto} requiere receta configurada antes de ingresar produccion"
        qty_dec = Decimal(str(qty or 0))
        for line in receta.lineas or []:
            insumo = line.insumo
            if not insumo:
                return {}, f"La receta de {producto.cod_producto} tiene un insumo invalido"
            required = qty_dec * Decimal(str(line.cantidad or 0))
            if required <= 0:
                continue
            bucket = requirements.setdefault(
                int(insumo.id),
                {
                    "producto": insumo,
                    "cantidad": Decimal("0"),
                    "unidad": line.unidad_medida or insumo.unidad_medida,
                },
            )
            bucket["cantidad"] = Decimal(str(bucket["cantidad"])) + required
    return requirements, None


def _ensure_recipe_stock(
    db: Session,
    bodega_id: int,
    requirements: dict[int, dict[str, object]],
) -> str | None:
    ingredient_ids = list(requirements.keys())
    balances_req = _balances_by_bodega(db, [bodega_id], ingredient_ids) if ingredient_ids else {}
    for ingredient_id, payload in requirements.items():
        available = Decimal(str(balances_req.get((ingredient_id, bodega_id), Decimal("0")) or 0))
        required_qty = Decimal(str(payload["cantidad"] or 0))
        if available < required_qty:
            producto_req = payload["producto"]
            unidad_req = payload.get("unidad")
            unit_label = unidad_req.abreviatura if unidad_req else "und"
            return (
                f"Materia prima insuficiente para {producto_req.cod_producto}. "
                f"Disponible {available.quantize(Decimal('0.01'))} {unit_label}, "
                f"requerido {required_qty.quantize(Decimal('0.01'))} {unit_label}."
            )
    return None


def _resolve_or_create_egreso_tipo(db: Session, nombre: str) -> EgresoTipo:
    row = db.query(EgresoTipo).filter(func.lower(EgresoTipo.nombre) == nombre.lower()).first()
    if row:
        return row
    row = EgresoTipo(nombre=nombre)
    db.add(row)
    db.flush()
    return row


def _resolve_or_create_ingreso_tipo(db: Session, nombre: str, requiere_proveedor: bool = False) -> IngresoTipo:
    row = db.query(IngresoTipo).filter(func.lower(IngresoTipo.nombre) == nombre.lower()).first()
    if row:
        return row
    row = IngresoTipo(nombre=nombre, requiere_proveedor=requiere_proveedor)
    db.add(row)
    db.flush()
    return row


def _is_compra_local_ingreso(nombre: str | None) -> bool:
    normalized = (nombre or "").strip().lower()
    return "compra" in normalized and "local" in normalized


@router.get("/catalogs", response_model=InventoryCatalogsResponse)
def get_catalogs(db: Session = Depends(get_db)):
    return InventoryCatalogsResponse(
        lineas=db.query(Linea).order_by(Linea.linea).all(),
        segmentos=db.query(Segmento).order_by(Segmento.segmento).all(),
        unidades_medida=db.query(UnidadMedida).order_by(UnidadMedida.nombre).all(),
        marcas=db.query(Marca).order_by(Marca.nombre).all(),
        bodegas=db.query(Bodega).order_by(Bodega.name).all(),
        proveedores=db.query(Proveedor).order_by(Proveedor.nombre).all(),
        ingreso_tipos=db.query(IngresoTipo).order_by(IngresoTipo.nombre).all(),
        egreso_tipos=db.query(EgresoTipo).order_by(EgresoTipo.nombre).all(),
    )


@router.post("/lineas", response_model=LineaResponse, status_code=status.HTTP_201_CREATED)
def create_linea(payload: LineaCreate, db: Session = Depends(get_db)):
    exists = db.query(Linea).filter(Linea.cod_linea == payload.cod_linea).first()
    if exists:
        raise HTTPException(status_code=400, detail="Codigo de linea ya existe")
    linea = Linea(**payload.model_dump())
    db.add(linea)
    db.commit()
    db.refresh(linea)
    return linea


@router.put("/lineas/{linea_id}", response_model=LineaResponse)
def update_linea(linea_id: int, payload: LineaUpdate, db: Session = Depends(get_db)):
    linea = db.query(Linea).filter(Linea.id == linea_id).first()
    if not linea:
        raise HTTPException(status_code=404, detail="Linea no encontrada")

    data = payload.model_dump(exclude_unset=True)
    if "cod_linea" in data and data["cod_linea"] is not None:
        code = _normalize_text(data["cod_linea"], "El codigo de linea").upper()
        exists = db.query(Linea).filter(func.lower(Linea.cod_linea) == code.lower(), Linea.id != linea.id).first()
        if exists:
            raise HTTPException(status_code=400, detail="Codigo de linea ya existe")
        linea.cod_linea = code
    if "linea" in data and data["linea"] is not None:
        linea.linea = _normalize_text(data["linea"], "La linea")
    if "activo" in data:
        linea.activo = bool(data["activo"])

    db.add(linea)
    db.commit()
    db.refresh(linea)
    return linea


@router.post("/segmentos", response_model=SegmentoResponse, status_code=status.HTTP_201_CREATED)
def create_segmento(payload: SegmentoCreate, db: Session = Depends(get_db)):
    exists = db.query(Segmento).filter(Segmento.segmento == payload.segmento).first()
    if exists:
        raise HTTPException(status_code=400, detail="Segmento ya existe")
    segmento = Segmento(**payload.model_dump())
    db.add(segmento)
    db.commit()
    db.refresh(segmento)
    return segmento


@router.put("/segmentos/{segmento_id}", response_model=SegmentoResponse)
def update_segmento(segmento_id: int, payload: SegmentoUpdate, db: Session = Depends(get_db)):
    segmento = db.query(Segmento).filter(Segmento.id == segmento_id).first()
    if not segmento:
        raise HTTPException(status_code=404, detail="Segmento no encontrado")

    data = payload.model_dump(exclude_unset=True)
    if "segmento" in data and data["segmento"] is not None:
        nombre = _normalize_text(data["segmento"], "El segmento")
        exists = db.query(Segmento).filter(func.lower(Segmento.segmento) == nombre.lower(), Segmento.id != segmento.id).first()
        if exists:
            raise HTTPException(status_code=400, detail="Segmento ya existe")
        segmento.segmento = nombre
    if "activo" in data:
        segmento.activo = bool(data["activo"])

    db.add(segmento)
    db.commit()
    db.refresh(segmento)
    return segmento


@router.post("/unidades-medida", response_model=UnidadMedidaResponse, status_code=status.HTTP_201_CREATED)
def create_unidad_medida(payload: UnidadMedidaCreate, db: Session = Depends(get_db)):
    exists = db.query(UnidadMedida).filter(
        (UnidadMedida.codigo == payload.codigo) | (UnidadMedida.nombre == payload.nombre)
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="La unidad de medida ya existe")
    unidad = UnidadMedida(**payload.model_dump())
    db.add(unidad)
    db.commit()
    db.refresh(unidad)
    return unidad


@router.put("/unidades-medida/{unidad_id}", response_model=UnidadMedidaResponse)
def update_unidad_medida(unidad_id: int, payload: UnidadMedidaUpdate, db: Session = Depends(get_db)):
    unidad = db.query(UnidadMedida).filter(UnidadMedida.id == unidad_id).first()
    if not unidad:
        raise HTTPException(status_code=404, detail="Unidad de medida no encontrada")

    data = payload.model_dump(exclude_unset=True)
    codigo = _normalize_text(data["codigo"], "El codigo") if data.get("codigo") is not None else unidad.codigo
    nombre = _normalize_text(data["nombre"], "El nombre") if data.get("nombre") is not None else unidad.nombre
    abreviatura = _normalize_text(data["abreviatura"], "La abreviatura") if data.get("abreviatura") is not None else unidad.abreviatura

    exists = db.query(UnidadMedida).filter(
        ((func.lower(UnidadMedida.codigo) == codigo.lower()) | (func.lower(UnidadMedida.nombre) == nombre.lower())),
        UnidadMedida.id != unidad.id,
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="La unidad de medida ya existe")

    unidad.codigo = codigo.upper()
    unidad.nombre = nombre
    unidad.abreviatura = abreviatura
    if "activo" in data:
        unidad.activo = bool(data["activo"])

    db.add(unidad)
    db.commit()
    db.refresh(unidad)
    return unidad


@router.post("/bodegas", response_model=BodegaResponse, status_code=status.HTTP_201_CREATED)
def create_bodega(payload: BodegaCreate, db: Session = Depends(get_db)):
    exists = db.query(Bodega).filter(Bodega.code == payload.code).first()
    if exists:
        raise HTTPException(status_code=400, detail="Codigo de bodega ya existe")
    bodega = Bodega(**payload.model_dump())
    db.add(bodega)
    db.commit()
    db.refresh(bodega)
    return bodega


@router.post("/marcas", response_model=MarcaResponse, status_code=status.HTTP_201_CREATED)
def create_marca(payload: MarcaCreate, db: Session = Depends(get_db)):
    nombre = _normalize_text(payload.nombre, "La marca")
    exists = db.query(Marca).filter(func.lower(Marca.nombre) == nombre.lower()).first()
    if exists:
        raise HTTPException(status_code=400, detail="La marca ya existe")
    marca = Marca(nombre=nombre, activo=payload.activo)
    db.add(marca)
    db.commit()
    db.refresh(marca)
    return marca


@router.put("/marcas/{marca_id}", response_model=MarcaResponse)
def update_marca(marca_id: int, payload: MarcaUpdate, db: Session = Depends(get_db)):
    marca = db.query(Marca).filter(Marca.id == marca_id).first()
    if not marca:
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    if payload.nombre is not None:
        nombre = _normalize_text(payload.nombre, "La marca")
        exists = db.query(Marca).filter(func.lower(Marca.nombre) == nombre.lower(), Marca.id != marca.id).first()
        if exists:
            raise HTTPException(status_code=400, detail="La marca ya existe")
        marca.nombre = nombre
    if payload.activo is not None:
        marca.activo = bool(payload.activo)
    db.add(marca)
    db.commit()
    db.refresh(marca)
    return marca


@router.post("/proveedores", response_model=ProveedorResponse, status_code=status.HTTP_201_CREATED)
def create_proveedor(payload: ProveedorCreate, db: Session = Depends(get_db)):
    exists = db.query(Proveedor).filter(Proveedor.nombre == payload.nombre).first()
    if exists:
        raise HTTPException(status_code=400, detail="Proveedor ya existe")
    proveedor = Proveedor(**payload.model_dump())
    db.add(proveedor)
    db.commit()
    db.refresh(proveedor)
    return proveedor


@router.put("/proveedores/{proveedor_id}", response_model=ProveedorResponse)
def update_proveedor(proveedor_id: int, payload: ProveedorUpdate, db: Session = Depends(get_db)):
    proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    data = payload.model_dump(exclude_unset=True)
    if "nombre" in data:
        nombre = (data.get("nombre") or "").strip()
        if not nombre:
            raise HTTPException(status_code=400, detail="Nombre de proveedor requerido")
        exists = (
            db.query(Proveedor)
            .filter(func.lower(Proveedor.nombre) == nombre.lower(), Proveedor.id != proveedor.id)
            .first()
        )
        if exists:
            raise HTTPException(status_code=400, detail="Proveedor ya existe")
        proveedor.nombre = nombre
    if "tipo" in data:
        proveedor.tipo = (data.get("tipo") or "").strip() or None
    if "activo" in data:
        proveedor.activo = bool(data["activo"])

    db.add(proveedor)
    db.commit()
    db.refresh(proveedor)
    return proveedor


@router.post("/ingreso-tipos", response_model=IngresoTipoResponse, status_code=status.HTTP_201_CREATED)
def create_ingreso_tipo(payload: IngresoTipoCreate, db: Session = Depends(get_db)):
    exists = db.query(IngresoTipo).filter(IngresoTipo.nombre == payload.nombre).first()
    if exists:
        raise HTTPException(status_code=400, detail="Tipo de ingreso ya existe")
    row = IngresoTipo(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.post("/egreso-tipos", response_model=EgresoTipoResponse, status_code=status.HTTP_201_CREATED)
def create_egreso_tipo(payload: EgresoTipoCreate, db: Session = Depends(get_db)):
    exists = db.query(EgresoTipo).filter(EgresoTipo.nombre == payload.nombre).first()
    if exists:
        raise HTTPException(status_code=400, detail="Tipo de egreso ya existe")
    row = EgresoTipo(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/products", response_model=List[ProductoResponse])
def list_products(
    include_inactive: bool = Query(False),
    q: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Producto).options(
        joinedload(Producto.saldo),
        joinedload(Producto.linea),
        joinedload(Producto.segmento),
        joinedload(Producto.unidad_medida),
        joinedload(Producto.marca_ref),
    )
    if not include_inactive:
        query = query.filter(Producto.activo.is_(True))
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            (Producto.cod_producto.ilike(like))
            | (Producto.codigo_barra.ilike(like))
            | (Producto.descripcion.ilike(like))
        )
    return query.order_by(Producto.descripcion).all()


@router.get("/products/next-code")
def get_next_product_code(db: Session = Depends(get_db)):
    return {"code": _next_product_code(db)}


@router.get("/products/search", response_model=ProductSearchResponse)
def search_products_for_sales(
    q: str = Query(""),
    bodega_id: int | None = Query(None),
    price_list: int | None = Query(1),
    db: Session = Depends(get_db),
):
    query = q.strip()
    if len(query) < 2:
        return ProductSearchResponse(items=[])

    price_tier = _normalize_price_tier(price_list, default=1)
    like = f"%{query.lower()}%"
    productos = (
        db.query(Producto)
        .options(joinedload(Producto.unidad_medida))
        .filter(
            Producto.activo.is_(True),
            (func.lower(Producto.cod_producto).like(like))
            | (func.lower(func.coalesce(Producto.codigo_barra, "")).like(like))
            | (func.lower(Producto.descripcion).like(like)),
        )
        .order_by(Producto.descripcion)
        .limit(100)
        .all()
    )

    balances: dict[tuple[int, int], Decimal] = {}
    if bodega_id and productos:
        balances = _balances_by_bodega(db, [bodega_id], [p.id for p in productos])

    items = []
    for producto in productos:
        selected_price = {
            1: producto.precio_venta1,
            2: producto.precio_venta2,
            3: producto.precio_venta3,
        }[price_tier]
        combo_count = len([combo for combo in (producto.combo_children or []) if combo.activo])
        existencia = float(balances.get((producto.id, bodega_id), Decimal("0")) or 0) if bodega_id else float(producto.saldo.existencia if producto.saldo else 0)
        selected_price_cs = float(selected_price or 0)
        items.append(
            {
                "id": producto.id,
                "cod_producto": producto.cod_producto,
                "codigo_barra": producto.codigo_barra or "",
                "descripcion": producto.descripcion,
                "precio_venta1": float(producto.precio_venta1 or 0),
                "precio_venta2": float(producto.precio_venta2 or 0),
                "precio_venta3": float(producto.precio_venta3 or 0),
                "selected_price_tier": price_tier,
                "selected_price_cs": selected_price_cs,
                "selected_price_usd": 0,
                "existencia": existencia,
                "free_qty": existencia,
                "combo_count": combo_count,
                "es_por_peso": bool(producto.es_por_peso),
                "unidad_medida_id": producto.unidad_medida_id,
                "unidad_medida_nombre": producto.unidad_medida.nombre if producto.unidad_medida else "",
                "unidad_medida_abreviatura": producto.unidad_medida.abreviatura if producto.unidad_medida else "",
            }
        )
    return ProductSearchResponse(items=items)


@router.get("/products/{product_id}", response_model=ProductoResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).options(
        joinedload(Producto.saldo),
        joinedload(Producto.linea),
        joinedload(Producto.segmento),
        joinedload(Producto.unidad_medida),
        joinedload(Producto.marca_ref),
    ).filter(Producto.id == product_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.get("/products/{product_id}/balances", response_model=List[ProductBodegaBalanceResponse])
def get_product_balances(product_id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == product_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    bodegas = db.query(Bodega).filter(Bodega.activo.is_(True)).order_by(Bodega.name).all()
    balances = _balances_by_bodega(db, [b.id for b in bodegas], [product_id])
    return [
        ProductBodegaBalanceResponse(
            bodega_id=bodega.id,
            bodega_code=bodega.code,
            bodega_name=bodega.name,
            existencia=float(balances.get((product_id, bodega.id), Decimal("0")) or 0),
        )
        for bodega in bodegas
    ]


@router.post("/products", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductoCreate, db: Session = Depends(get_db)):
    settings = _get_business_settings(db)
    code = _next_product_code(db)
    _ensure_catalog_refs(
        db,
        payload.linea_id,
        payload.segmento_id,
        payload.unidad_medida_id,
        payload.marca_id,
        payload.bodega_inicial_id,
    )

    existencia_inicial = Decimal(payload.existencia or 0)
    if existencia_inicial < 0:
        raise HTTPException(status_code=400, detail="La existencia inicial no puede ser negativa")
    if existencia_inicial > 0 and not payload.bodega_inicial_id:
        raise HTTPException(status_code=400, detail="Debes indicar la bodega inicial para registrar existencia")

    producto_data = payload.model_dump(exclude={"existencia", "bodega_inicial_id"})
    producto_data["cod_producto"] = code
    producto_data["usa_codigo_barra"] = bool(payload.usa_codigo_barra)
    producto_data["codigo_barra"] = (
        _normalize_barcode(payload.codigo_barra) if producto_data["usa_codigo_barra"] else None
    )
    producto_data["descripcion"] = _normalize_text(payload.descripcion, "La descripcion")
    producto_data["tipo_producto"] = _normalize_product_type(payload.tipo_producto)
    if producto_data["codigo_barra"]:
        exists_barcode = db.query(Producto).filter(Producto.codigo_barra == producto_data["codigo_barra"]).first()
        if exists_barcode:
            raise HTTPException(status_code=400, detail="El codigo de barra ya existe")
    if payload.marca_id:
        marca = db.query(Marca).filter(Marca.id == payload.marca_id).first()
        producto_data["marca"] = marca.nombre if marca else payload.marca
    producto = Producto(**producto_data)
    db.add(producto)
    db.flush()

    saldo = SaldoProducto(producto_id=producto.id, existencia=Decimal("0"))
    db.add(saldo)

    if existencia_inicial > 0:
        ingreso_tipo = db.query(IngresoTipo).filter(IngresoTipo.nombre == "Inventario Inicial").first()
        if not ingreso_tipo:
            ingreso_tipo = IngresoTipo(nombre="Inventario Inicial", requiere_proveedor=False)
            db.add(ingreso_tipo)
            db.flush()

        costo_unitario_usd, costo_unitario_cs = _product_cost_pair(producto, Decimal("0"), settings)
        total_usd = existencia_inicial * costo_unitario_usd
        total_cs = existencia_inicial * costo_unitario_cs
        ingreso = IngresoInventario(
            tipo_id=ingreso_tipo.id,
            bodega_id=payload.bodega_inicial_id,
            proveedor_id=None,
            usuario_id=None,
            fecha=date.today(),
            moneda="CS",
            tasa_cambio=None,
            observacion=f"Inventario inicial de producto {producto.cod_producto}",
            usuario_registro=payload.usuario_registro,
            total_usd=total_usd,
            total_cs=total_cs,
        )
        db.add(ingreso)
        db.flush()
        db.add(
            IngresoItem(
                ingreso_id=ingreso.id,
                producto_id=producto.id,
                cantidad=existencia_inicial,
                costo_unitario_usd=costo_unitario_usd,
                costo_unitario_cs=costo_unitario_cs,
                subtotal_usd=total_usd,
                subtotal_cs=total_cs,
            )
        )
        _rebuild_global_saldo(db, producto.id)

    db.commit()
    db.refresh(producto)
    return get_product(producto.id, db)


@router.put("/products/{product_id}", response_model=ProductoResponse)
def update_product(product_id: int, payload: ProductoUpdate, db: Session = Depends(get_db)):
    producto = db.query(Producto).options(joinedload(Producto.saldo)).filter(Producto.id == product_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    data = payload.model_dump(exclude_unset=True)
    if "cod_producto" in data and data["cod_producto"] is not None:
        code = _normalize_product_code(data["cod_producto"])
        exists = (
            db.query(Producto)
            .filter(func.lower(Producto.cod_producto) == code.lower(), Producto.id != producto.id)
            .first()
        )
        if exists:
            raise HTTPException(status_code=400, detail="Codigo de producto ya existe")
        data["cod_producto"] = code
    if "codigo_barra" in data:
        barcode_enabled = bool(data.get("usa_codigo_barra", producto.usa_codigo_barra))
        barcode = _normalize_barcode(data["codigo_barra"]) if barcode_enabled else None
        if barcode is not None:
            exists_barcode = (
                db.query(Producto)
                .filter(Producto.codigo_barra == barcode, Producto.id != producto.id)
                .first()
            )
            if exists_barcode:
                raise HTTPException(status_code=400, detail="El codigo de barra ya existe")
        data["codigo_barra"] = barcode
    elif "usa_codigo_barra" in data and not bool(data["usa_codigo_barra"]):
        data["codigo_barra"] = None
    if "descripcion" in data and data["descripcion"] is not None:
        data["descripcion"] = _normalize_text(data["descripcion"], "La descripcion")
    if "tipo_producto" in data and data["tipo_producto"] is not None:
        data["tipo_producto"] = _normalize_product_type(data["tipo_producto"])

    _ensure_catalog_refs(
        db,
        data.get("linea_id"),
        data.get("segmento_id"),
        data.get("unidad_medida_id"),
        data.get("marca_id"),
    )
    if "marca_id" in data:
        marca = db.query(Marca).filter(Marca.id == data["marca_id"]).first() if data["marca_id"] else None
        data["marca"] = marca.nombre if marca else None

    existencia = data.pop("existencia", None)
    for key, value in data.items():
        setattr(producto, key, value)

    if existencia is not None:
        movimientos = (
            db.query(IngresoItem.id).filter(IngresoItem.producto_id == producto.id).first()
            or db.query(EgresoItem.id).filter(EgresoItem.producto_id == producto.id).first()
        )
        if movimientos:
            raise HTTPException(
                status_code=400,
                detail="La existencia ya no se edita desde productos; usa ingresos o egresos de inventario",
            )
        if Decimal(existencia) < 0:
            raise HTTPException(status_code=400, detail="La existencia no puede ser negativa")
        saldo = _get_or_create_saldo(db, producto.id)
        saldo.existencia = existencia

    db.commit()
    db.refresh(producto)
    return get_product(producto.id, db)


@router.patch("/products/{product_id}/toggle-active", response_model=ProductoResponse)
def toggle_product_active(product_id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == product_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    producto.activo = not producto.activo
    db.commit()
    db.refresh(producto)
    return get_product(producto.id, db)


@router.get("/products/{product_id}/recipe", response_model=ProductoRecetaResponse)
def get_product_recipe(product_id: int, db: Session = Depends(get_db)):
    producto = (
        db.query(Producto)
        .options(
            joinedload(Producto.receta).joinedload(ProductoReceta.lineas).joinedload(ProductoRecetaLinea.insumo).joinedload(Producto.unidad_medida),
            joinedload(Producto.receta).joinedload(ProductoReceta.lineas).joinedload(ProductoRecetaLinea.unidad_medida),
        )
        .filter(Producto.id == product_id)
        .first()
    )
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if not producto.receta:
        raise HTTPException(status_code=404, detail="El producto no tiene receta configurada")
    return producto.receta


@router.put("/products/{product_id}/recipe", response_model=ProductoRecetaResponse)
def save_product_recipe(product_id: int, payload: ProductoRecetaSaveRequest, db: Session = Depends(get_db)):
    producto = (
        db.query(Producto)
        .options(joinedload(Producto.receta).joinedload(ProductoReceta.lineas))
        .filter(Producto.id == product_id)
        .first()
    )
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    producto.tipo_producto = "RECETA"
    receta = producto.receta
    if not payload.lineas:
        if receta:
            db.delete(receta)
            db.commit()
        raise HTTPException(status_code=400, detail="Debes registrar al menos un insumo en la receta")

    seen: set[int] = set()
    for line in payload.lineas:
        if line.insumo_producto_id == product_id:
            raise HTTPException(status_code=400, detail="El producto final no puede ser insumo de su propia receta")
        if line.insumo_producto_id in seen:
            raise HTTPException(status_code=400, detail="No repitas el mismo insumo en la receta")
        seen.add(line.insumo_producto_id)
        if Decimal(line.cantidad) <= 0:
            raise HTTPException(status_code=400, detail="La cantidad del insumo debe ser mayor que cero")
        insumo = db.query(Producto).filter(Producto.id == line.insumo_producto_id).first()
        if not insumo:
            raise HTTPException(status_code=404, detail=f"Insumo {line.insumo_producto_id} no encontrado")
        if line.unidad_medida_id and not db.query(UnidadMedida).filter(UnidadMedida.id == line.unidad_medida_id).first():
            raise HTTPException(status_code=404, detail="Unidad de medida no encontrada")

    if not receta:
        receta = ProductoReceta(
            producto_final_id=product_id,
            nombre=(payload.nombre or f"Receta {producto.descripcion}").strip() or f"Receta {producto.descripcion}",
            activo=bool(payload.activo),
        )
        db.add(receta)
        db.flush()
    else:
        receta.nombre = (payload.nombre or f"Receta {producto.descripcion}").strip() or f"Receta {producto.descripcion}"
        receta.activo = bool(payload.activo)
        for line in list(receta.lineas or []):
            db.delete(line)
        db.flush()

    for line in payload.lineas:
        db.add(
            ProductoRecetaLinea(
                receta_id=receta.id,
                insumo_producto_id=line.insumo_producto_id,
                unidad_medida_id=line.unidad_medida_id,
                cantidad=Decimal(line.cantidad),
            )
        )

    db.commit()
    return (
        db.query(ProductoReceta)
        .options(
            joinedload(ProductoReceta.lineas).joinedload(ProductoRecetaLinea.insumo),
            joinedload(ProductoReceta.lineas).joinedload(ProductoRecetaLinea.unidad_medida),
        )
        .filter(ProductoReceta.producto_final_id == product_id)
        .first()
    )


@router.get("/products/{product_id}/combo", response_model=List[ProductoComboResponse])
def get_product_combo(product_id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == product_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return (
        db.query(ProductoCombo)
        .options(joinedload(ProductoCombo.child).joinedload(Producto.unidad_medida))
        .filter(ProductoCombo.parent_producto_id == product_id, ProductoCombo.activo.is_(True))
        .order_by(ProductoCombo.id)
        .all()
    )


@router.post("/products/{product_id}/combo", response_model=ProductoComboResponse, status_code=status.HTTP_201_CREATED)
def save_product_combo_item(product_id: int, payload: ProductoComboCreate, db: Session = Depends(get_db)):
    parent = db.query(Producto).filter(Producto.id == product_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Producto combo no encontrado")
    child = db.query(Producto).filter(Producto.id == payload.child_producto_id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Producto de regalia no encontrado")
    if child.id == parent.id:
        raise HTTPException(status_code=400, detail="El producto combo no puede ser su propia regalia")
    if Decimal(payload.cantidad or 0) <= 0:
        raise HTTPException(status_code=400, detail="La cantidad de regalia debe ser mayor que cero")

    combo = (
        db.query(ProductoCombo)
        .filter(
            ProductoCombo.parent_producto_id == product_id,
            ProductoCombo.child_producto_id == payload.child_producto_id,
        )
        .first()
    )
    if combo:
        combo.cantidad = Decimal(payload.cantidad)
        combo.activo = bool(payload.activo)
    else:
        combo = ProductoCombo(
            parent_producto_id=product_id,
            child_producto_id=payload.child_producto_id,
            cantidad=Decimal(payload.cantidad),
            activo=bool(payload.activo),
        )
        db.add(combo)
    db.commit()
    return (
        db.query(ProductoCombo)
        .options(joinedload(ProductoCombo.child).joinedload(Producto.unidad_medida))
        .filter(ProductoCombo.id == combo.id)
        .first()
    )


@router.delete("/products/{product_id}/combo/{combo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_combo_item(product_id: int, combo_id: int, db: Session = Depends(get_db)):
    combo = (
        db.query(ProductoCombo)
        .filter(ProductoCombo.id == combo_id, ProductoCombo.parent_producto_id == product_id)
        .first()
    )
    if not combo:
        raise HTTPException(status_code=404, detail="Regalia de combo no encontrada")
    db.delete(combo)
    db.commit()
    return None


@router.post("/producciones/open", response_model=ProduccionInventarioResponse, status_code=status.HTTP_201_CREATED)
def open_production(payload: ProduccionInventarioCreate, db: Session = Depends(get_db)):
    settings = _get_business_settings(db)
    producto = (
        db.query(Producto)
        .options(
            joinedload(Producto.receta).joinedload(ProductoReceta.lineas).joinedload(ProductoRecetaLinea.insumo),
            joinedload(Producto.receta).joinedload(ProductoReceta.lineas).joinedload(ProductoRecetaLinea.unidad_medida),
        )
        .filter(Producto.id == payload.producto_final_id)
        .first()
    )
    if not producto:
        raise HTTPException(status_code=404, detail="Producto final no encontrado")
    if _normalize_product_type(producto.tipo_producto) != "RECETA":
        raise HTTPException(status_code=400, detail="El producto debe estar configurado como producto final por receta")
    if not db.query(Bodega).filter(Bodega.id == payload.bodega_id).first():
        raise HTTPException(status_code=404, detail="Bodega no encontrada")
    if Decimal(payload.cantidad_producida) <= 0:
        raise HTTPException(status_code=400, detail="La cantidad a producir debe ser mayor que cero")

    requirements, error = _build_recipe_requirements(db, [(payload.producto_final_id, Decimal(payload.cantidad_producida))])
    if error:
        raise HTTPException(status_code=400, detail=error)
    stock_error = _ensure_recipe_stock(db, payload.bodega_id, requirements)
    if stock_error:
        raise HTTPException(status_code=400, detail=stock_error)

    moneda = _normalize_currency(payload.moneda)
    tasa = _require_exchange_rate(moneda, payload.tasa_cambio)
    produccion = ProduccionInventario(
        producto_final_id=payload.producto_final_id,
        bodega_id=payload.bodega_id,
        fecha=payload.fecha,
        estado="ABIERTA",
        moneda=moneda,
        tasa_cambio=payload.tasa_cambio,
        cantidad_producida=Decimal(payload.cantidad_producida),
        observacion=payload.observacion,
        usuario_registro=payload.usuario_registro,
    )
    db.add(produccion)
    db.flush()

    total_insumos_cs = Decimal("0")
    total_insumos_usd = Decimal("0")
    for ingredient_id, requirement in requirements.items():
        producto_req = requirement["producto"]
        cantidad = Decimal(str(requirement["cantidad"] or 0))
        costo_usd, costo_cs = _product_cost_pair(producto_req, tasa, settings)
        subtotal_cs = cantidad * costo_cs
        subtotal_usd = cantidad * costo_usd
        total_insumos_cs += subtotal_cs
        total_insumos_usd += subtotal_usd
        db.add(
            ProduccionInventarioLinea(
                produccion_id=produccion.id,
                tipo_linea="INSUMO",
                producto_id=ingredient_id,
                cantidad=cantidad,
                costo_unitario_usd=costo_usd,
                costo_unitario_cs=costo_cs,
                subtotal_usd=subtotal_usd,
                subtotal_cs=subtotal_cs,
            )
        )

    costo_final_cs = total_insumos_cs / Decimal(payload.cantidad_producida)
    costo_final_usd = total_insumos_usd / Decimal(payload.cantidad_producida) if Decimal(payload.cantidad_producida) > 0 else Decimal("0")
    db.add(
        ProduccionInventarioLinea(
            produccion_id=produccion.id,
            tipo_linea="PRODUCTO_FINAL",
            producto_id=payload.producto_final_id,
            cantidad=Decimal(payload.cantidad_producida),
            costo_unitario_usd=costo_final_usd,
            costo_unitario_cs=costo_final_cs,
            subtotal_usd=total_insumos_usd,
            subtotal_cs=total_insumos_cs,
        )
    )
    produccion.total_insumos_cs = total_insumos_cs
    produccion.total_insumos_usd = total_insumos_usd
    produccion.total_produccion_cs = total_insumos_cs
    produccion.total_produccion_usd = total_insumos_usd
    db.commit()
    return (
        db.query(ProduccionInventario)
        .options(
            joinedload(ProduccionInventario.lineas).joinedload(ProduccionInventarioLinea.producto),
            joinedload(ProduccionInventario.producto_final),
            joinedload(ProduccionInventario.bodega),
        )
        .filter(ProduccionInventario.id == produccion.id)
        .first()
    )


@router.post("/producciones/{production_id}/execute", response_model=ProduccionInventarioResponse)
def execute_production(production_id: int, db: Session = Depends(get_db)):
    settings = _get_business_settings(db)
    produccion = (
        db.query(ProduccionInventario)
        .options(
            joinedload(ProduccionInventario.lineas).joinedload(ProduccionInventarioLinea.producto),
            joinedload(ProduccionInventario.producto_final),
        )
        .filter(ProduccionInventario.id == production_id)
        .first()
    )
    if not produccion:
        raise HTTPException(status_code=404, detail="Produccion no encontrada")
    if (produccion.estado or "").upper() != "ABIERTA":
        raise HTTPException(status_code=400, detail="La produccion ya fue ejecutada")

    requirements = {
        int(line.producto_id): {
            "producto": line.producto,
            "cantidad": Decimal(str(line.cantidad or 0)),
            "unidad": getattr(line.producto, "unidad_medida", None),
        }
        for line in produccion.lineas
        if (line.tipo_linea or "").upper() == "INSUMO"
    }
    stock_error = _ensure_recipe_stock(db, int(produccion.bodega_id), requirements)
    if stock_error:
        raise HTTPException(status_code=400, detail=stock_error)

    egreso_tipo = _resolve_or_create_egreso_tipo(db, "Produccion de Abierta")
    ingreso_tipo = _resolve_or_create_ingreso_tipo(db, "Produccion", False)

    egreso = EgresoInventario(
        tipo_id=egreso_tipo.id,
        bodega_id=produccion.bodega_id,
        bodega_destino_id=None,
        usuario_id=None,
        fecha=produccion.fecha,
        moneda=produccion.moneda,
        tasa_cambio=produccion.tasa_cambio,
        observacion=f"Produccion abierta #{produccion.id}. {produccion.observacion or ''}".strip()[:300],
        usuario_registro=produccion.usuario_registro,
        total_usd=produccion.total_insumos_usd,
        total_cs=produccion.total_insumos_cs,
    )
    db.add(egreso)
    db.flush()

    for line in [row for row in produccion.lineas if (row.tipo_linea or "").upper() == "INSUMO"]:
        db.add(
            EgresoItem(
                egreso_id=egreso.id,
                producto_id=line.producto_id,
                cantidad=line.cantidad,
                costo_unitario_usd=line.costo_unitario_usd,
                costo_unitario_cs=line.costo_unitario_cs,
                subtotal_usd=line.subtotal_usd,
                subtotal_cs=line.subtotal_cs,
            )
        )

    final_line = next((row for row in produccion.lineas if (row.tipo_linea or "").upper() == "PRODUCTO_FINAL"), None)
    if not final_line:
        raise HTTPException(status_code=400, detail="La produccion no tiene linea de producto final")

    ingreso = IngresoInventario(
        tipo_id=ingreso_tipo.id,
        bodega_id=produccion.bodega_id,
        proveedor_id=None,
        usuario_id=None,
        fecha=produccion.fecha,
        moneda=produccion.moneda,
        tasa_cambio=produccion.tasa_cambio,
        observacion=f"Produccion abierta #{produccion.id}. {produccion.observacion or ''}".strip()[:300],
        usuario_registro=produccion.usuario_registro,
        total_usd=produccion.total_produccion_usd,
        total_cs=produccion.total_produccion_cs,
    )
    db.add(ingreso)
    db.flush()
    db.add(
        IngresoItem(
            ingreso_id=ingreso.id,
            producto_id=final_line.producto_id,
            cantidad=final_line.cantidad,
            costo_unitario_usd=final_line.costo_unitario_usd,
            costo_unitario_cs=final_line.costo_unitario_cs,
            subtotal_usd=final_line.subtotal_usd,
            subtotal_cs=final_line.subtotal_cs,
        )
    )

    producto_final = db.query(Producto).filter(Producto.id == produccion.producto_final_id).first()
    if producto_final:
        _assign_product_cost(
            producto_final,
            Decimal(str(final_line.costo_unitario_usd or 0)),
            Decimal(str(final_line.costo_unitario_cs or 0)),
            settings,
        )

    produccion.egreso_id = egreso.id
    produccion.ingreso_id = ingreso.id
    produccion.estado = "FINALIZADA"

    for line in produccion.lineas:
        _rebuild_global_saldo(db, line.producto_id)
    db.commit()
    return (
        db.query(ProduccionInventario)
        .options(
            joinedload(ProduccionInventario.lineas).joinedload(ProduccionInventarioLinea.producto),
            joinedload(ProduccionInventario.producto_final),
            joinedload(ProduccionInventario.bodega),
        )
        .filter(ProduccionInventario.id == produccion.id)
        .first()
    )


@router.get("/producciones", response_model=List[ProduccionInventarioResponse])
def list_productions(db: Session = Depends(get_db)):
    return (
        db.query(ProduccionInventario)
        .options(
            joinedload(ProduccionInventario.lineas).joinedload(ProduccionInventarioLinea.producto),
            joinedload(ProduccionInventario.producto_final),
            joinedload(ProduccionInventario.bodega),
        )
        .order_by(ProduccionInventario.id.desc())
        .all()
    )


@router.get("/producciones/{production_id}/report", response_model=ProduccionInventarioResponse)
def get_production_report(production_id: int, db: Session = Depends(get_db)):
    row = (
        db.query(ProduccionInventario)
        .options(
            joinedload(ProduccionInventario.lineas).joinedload(ProduccionInventarioLinea.producto),
            joinedload(ProduccionInventario.producto_final),
            joinedload(ProduccionInventario.bodega),
            joinedload(ProduccionInventario.ingreso).joinedload(IngresoInventario.items),
            joinedload(ProduccionInventario.egreso).joinedload(EgresoInventario.items),
        )
        .filter(ProduccionInventario.id == production_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Produccion no encontrada")
    return row


def _load_paca_apertura(db: Session, apertura_id: int) -> PacaApertura | None:
    return (
        db.query(PacaApertura)
        .options(
            joinedload(PacaApertura.paca_producto),
            joinedload(PacaApertura.bodega),
            joinedload(PacaApertura.bodega_destino),
            joinedload(PacaApertura.origenes).joinedload(PacaAperturaOrigen.producto),
            joinedload(PacaApertura.lineas).joinedload(PacaAperturaLinea.producto),
        )
        .filter(PacaApertura.id == apertura_id)
        .first()
    )


@router.post("/paca-aperturas", response_model=PacaAperturaResponse, status_code=status.HTTP_201_CREATED)
def create_paca_apertura(payload: PacaAperturaCreate, db: Session = Depends(get_db)):
    settings = _get_business_settings(db)
    if not payload.lineas:
        raise HTTPException(status_code=400, detail="Debes registrar al menos un producto clasificado")
    bodega = db.query(Bodega).filter(Bodega.id == payload.bodega_id).first()
    if not bodega:
        raise HTTPException(status_code=404, detail="Bodega origen no encontrada")

    bodega_destino_id = payload.bodega_destino_id or payload.bodega_id
    bodega_destino = db.query(Bodega).filter(Bodega.id == bodega_destino_id).first()
    if not bodega_destino:
        raise HTTPException(status_code=404, detail="Bodega destino no encontrada")

    moneda = _normalize_currency(payload.moneda)
    tasa = _current_exchange_rate_value(db)

    source_payload = payload.pacas_origen or [
        {"producto_id": payload.paca_producto_id, "cantidad": payload.cantidad_pacas}
    ]
    source_qty_by_product: dict[int, Decimal] = {}
    for source in source_payload:
        product_id = int(source.producto_id if hasattr(source, "producto_id") else source["producto_id"])
        quantity = Decimal(source.cantidad if hasattr(source, "cantidad") else source["cantidad"])
        if quantity <= 0:
            raise HTTPException(status_code=400, detail="Las cantidades de pacas origen deben ser mayores que cero")
        source_qty_by_product[product_id] = source_qty_by_product.get(product_id, Decimal("0")) + quantity

    if not source_qty_by_product:
        raise HTTPException(status_code=400, detail="Debes registrar al menos una paca origen")

    source_products = {
        product.id: product
        for product in db.query(Producto).filter(Producto.id.in_(list(source_qty_by_product.keys()))).all()
    }
    missing_sources = [product_id for product_id in source_qty_by_product if product_id not in source_products]
    if missing_sources:
        raise HTTPException(status_code=404, detail=f"Producto paca no encontrado: {missing_sources[0]}")

    source_balances = _balances_by_bodega(db, [payload.bodega_id], list(source_qty_by_product.keys()))
    source_rows: list[dict[str, object]] = []
    costo_origen_usd = Decimal("0")
    costo_origen_cs = Decimal("0")
    cantidad_pacas = Decimal("0")
    for product_id, quantity in source_qty_by_product.items():
        product = source_products[product_id]
        available = source_balances.get((product_id, payload.bodega_id), Decimal("0"))
        if available < quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para abrir {product.cod_producto}. Disponible: {available}",
            )
        unit_usd, unit_cs = _product_cost_pair(product, tasa, settings)
        subtotal_usd = unit_usd * quantity
        subtotal_cs = unit_cs * quantity
        costo_origen_usd += subtotal_usd
        costo_origen_cs += subtotal_cs
        cantidad_pacas += quantity
        source_rows.append(
            {
                "producto": product,
                "cantidad": quantity,
                "unit_usd": unit_usd,
                "unit_cs": unit_cs,
                "subtotal_usd": subtotal_usd,
                "subtotal_cs": subtotal_cs,
            }
        )

    paca_producto = source_rows[0]["producto"]

    result_rows: list[dict[str, object]] = []
    valor_estimado_usd = Decimal("0")
    valor_estimado_cs = Decimal("0")
    total_qty = Decimal("0")
    for line in payload.lineas:
        producto = db.query(Producto).filter(Producto.id == line.producto_id).first()
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto resultante {line.producto_id} no encontrado")
        cantidad = Decimal(line.cantidad)
        if cantidad <= 0:
            raise HTTPException(status_code=400, detail="Las cantidades resultantes deben ser mayores que cero")
        precio_usd, precio_cs = _product_cost_pair(producto, tasa, settings)
        subtotal_usd = precio_usd * cantidad
        subtotal_cs = precio_cs * cantidad
        valor_estimado_usd += subtotal_usd
        valor_estimado_cs += subtotal_cs
        total_qty += cantidad
        result_rows.append(
            {
                "producto": producto,
                "cantidad": cantidad,
                "precio_usd": precio_usd,
                "precio_cs": precio_cs,
                "valor_usd": subtotal_usd,
                "valor_cs": subtotal_cs,
            }
        )

    egreso_tipo = _resolve_or_create_egreso_tipo(db, "Produccion de Abierta")
    ingreso_tipo = _resolve_or_create_ingreso_tipo(db, "Produccion", False)

    egreso = EgresoInventario(
        tipo_id=egreso_tipo.id,
        bodega_id=payload.bodega_id,
        bodega_destino_id=bodega_destino.id,
        fecha=payload.fecha,
        moneda=moneda,
        tasa_cambio=tasa,
        observacion=f"Produccion de Abierta de {len(source_rows)} referencia(s) de paca. {payload.observacion or ''}".strip()[:300],
        usuario_registro=payload.usuario_registro,
        total_usd=costo_origen_usd,
        total_cs=costo_origen_cs,
    )
    db.add(egreso)
    db.flush()

    for source in source_rows:
        db.add(
            EgresoItem(
                egreso_id=egreso.id,
                producto_id=source["producto"].id,
                cantidad=source["cantidad"],
                costo_unitario_usd=source["unit_usd"],
                costo_unitario_cs=source["unit_cs"],
                subtotal_usd=source["subtotal_usd"],
                subtotal_cs=source["subtotal_cs"],
            )
        )

    ingreso = IngresoInventario(
        tipo_id=ingreso_tipo.id,
        bodega_id=bodega_destino.id,
        proveedor_id=None,
        fecha=payload.fecha,
        moneda=moneda,
        tasa_cambio=tasa,
        observacion=(
            f"Resultado de Produccion de Abierta desde {bodega.name} hacia {bodega_destino.name}. "
            f"Egreso #{egreso.id}. {len(source_rows)} referencia(s) de paca. {payload.observacion or ''}"
        ).strip()[:300],
        usuario_registro=payload.usuario_registro,
        total_usd=valor_estimado_usd,
        total_cs=valor_estimado_cs,
    )
    db.add(ingreso)
    db.flush()

    apertura = PacaApertura(
        paca_producto_id=paca_producto.id,
        bodega_id=payload.bodega_id,
        bodega_destino_id=bodega_destino.id,
        fecha=payload.fecha,
        cantidad_pacas=cantidad_pacas,
        moneda=moneda,
        tasa_cambio=tasa,
        costo_origen_usd=costo_origen_usd,
        costo_origen_cs=costo_origen_cs,
        valor_estimado_usd=valor_estimado_usd,
        valor_estimado_cs=valor_estimado_cs,
        diferencia_usd=valor_estimado_usd - costo_origen_usd,
        diferencia_cs=valor_estimado_cs - costo_origen_cs,
        estado="FINALIZADA",
        observacion=payload.observacion,
        usuario_registro=payload.usuario_registro,
        ingreso_id=ingreso.id,
        egreso_id=egreso.id,
    )
    db.add(apertura)
    db.flush()

    for source in source_rows:
        db.add(
            PacaAperturaOrigen(
                apertura_id=apertura.id,
                producto_id=source["producto"].id,
                cantidad=source["cantidad"],
                costo_unitario_usd=source["unit_usd"],
                costo_unitario_cs=source["unit_cs"],
                subtotal_usd=source["subtotal_usd"],
                subtotal_cs=source["subtotal_cs"],
            )
        )

    for row in result_rows:
        cantidad = Decimal(row["cantidad"])
        if valor_estimado_cs > 0:
            ratio = Decimal(row["valor_cs"]) / valor_estimado_cs
        else:
            ratio = cantidad / total_qty if total_qty > 0 else Decimal("0")
        costo_linea_cs = costo_origen_cs * ratio
        costo_linea_usd = costo_origen_usd * ratio
        costo_unit_cs = costo_linea_cs / cantidad if cantidad > 0 else Decimal("0")
        costo_unit_usd = costo_linea_usd / cantidad if cantidad > 0 else Decimal("0")
        producto = row["producto"]
        db.add(
            PacaAperturaLinea(
                apertura_id=apertura.id,
                producto_id=producto.id,
                cantidad=cantidad,
                precio_estimado_unitario_usd=row["precio_usd"],
                precio_estimado_unitario_cs=row["precio_cs"],
                valor_estimado_usd=row["valor_usd"],
                valor_estimado_cs=row["valor_cs"],
                costo_asignado_unitario_usd=costo_unit_usd,
                costo_asignado_unitario_cs=costo_unit_cs,
                costo_asignado_usd=costo_linea_usd,
                costo_asignado_cs=costo_linea_cs,
            )
        )
        db.add(
            IngresoItem(
                ingreso_id=ingreso.id,
                producto_id=producto.id,
                cantidad=cantidad,
                costo_unitario_usd=row["precio_usd"],
                costo_unitario_cs=row["precio_cs"],
                subtotal_usd=row["valor_usd"],
                subtotal_cs=row["valor_cs"],
            )
        )
        _assign_product_cost(producto, row["precio_usd"], row["precio_cs"], settings)

    for source in source_rows:
        _rebuild_global_saldo(db, source["producto"].id)
    for row in result_rows:
        _rebuild_global_saldo(db, row["producto"].id)

    db.commit()
    return _load_paca_apertura(db, apertura.id)


@router.get("/paca-aperturas", response_model=List[PacaAperturaResponse])
def list_paca_aperturas(db: Session = Depends(get_db)):
    return (
        db.query(PacaApertura)
        .options(
            joinedload(PacaApertura.paca_producto),
            joinedload(PacaApertura.bodega),
            joinedload(PacaApertura.bodega_destino),
            joinedload(PacaApertura.origenes).joinedload(PacaAperturaOrigen.producto),
            joinedload(PacaApertura.lineas).joinedload(PacaAperturaLinea.producto),
        )
        .order_by(PacaApertura.id.desc())
        .all()
    )


@router.get("/paca-aperturas/{apertura_id}/report", response_model=PacaAperturaResponse)
def get_paca_apertura_report(apertura_id: int, db: Session = Depends(get_db)):
    row = _load_paca_apertura(db, apertura_id)
    if not row:
        raise HTTPException(status_code=404, detail="Apertura de paca no encontrada")
    return row


@router.post("/ingresos", response_model=IngresoResponse, status_code=status.HTTP_201_CREATED)
def create_ingreso(payload: IngresoCreate, db: Session = Depends(get_db)):
    settings = _get_business_settings(db)
    if not payload.items:
        raise HTTPException(status_code=400, detail="Debes registrar al menos un item")

    ingreso_tipo = db.query(IngresoTipo).filter(IngresoTipo.id == payload.tipo_id).first()
    if not ingreso_tipo:
        raise HTTPException(status_code=404, detail="Tipo de ingreso no encontrado")
    if not db.query(Bodega).filter(Bodega.id == payload.bodega_id).first():
        raise HTTPException(status_code=404, detail="Bodega no encontrada")
    if payload.proveedor_id and not db.query(Proveedor).filter(Proveedor.id == payload.proveedor_id).first():
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    if ingreso_tipo.requiere_proveedor and not payload.proveedor_id:
        raise HTTPException(status_code=400, detail="Este tipo de ingreso requiere proveedor")

    moneda = _normalize_currency(payload.moneda)
    tasa = _require_exchange_rate(moneda, payload.tasa_cambio)

    ingreso = IngresoInventario(
        tipo_id=payload.tipo_id,
        bodega_id=payload.bodega_id,
        proveedor_id=payload.proveedor_id,
        usuario_id=payload.usuario_id,
        fecha=payload.fecha,
        moneda=moneda,
        tasa_cambio=payload.tasa_cambio,
        observacion=payload.observacion,
        usuario_registro=payload.usuario_registro,
    )
    db.add(ingreso)
    db.flush()

    total_usd = Decimal("0")
    total_cs = Decimal("0")
    allow_manual_cost = _is_compra_local_ingreso(ingreso_tipo.nombre)

    for item in payload.items:
        producto = db.query(Producto).filter(Producto.id == item.producto_id).first()
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto {item.producto_id} no encontrado")

        cantidad = Decimal(item.cantidad)
        if cantidad <= 0:
            raise HTTPException(status_code=400, detail="La cantidad debe ser mayor que cero")

        if allow_manual_cost:
            costo_unitario = Decimal(item.costo_unitario)
            if costo_unitario < 0:
                raise HTTPException(status_code=400, detail="El costo unitario debe ser valido")
            if moneda == "USD":
                costo_usd = costo_unitario
                costo_cs = costo_unitario * tasa
            else:
                costo_cs = costo_unitario
                costo_usd = costo_unitario / tasa if tasa > 0 else Decimal("0")
        else:
            costo_usd, costo_cs = _product_cost_pair(producto, tasa, settings)

        subtotal_usd = cantidad * costo_usd
        subtotal_cs = cantidad * costo_cs
        total_usd += subtotal_usd
        total_cs += subtotal_cs

        db.add(
            IngresoItem(
                ingreso_id=ingreso.id,
                producto_id=producto.id,
                cantidad=cantidad,
                costo_unitario_usd=costo_usd,
                costo_unitario_cs=costo_cs,
                subtotal_usd=subtotal_usd,
                subtotal_cs=subtotal_cs,
            )
        )

        _get_or_create_saldo(db, producto.id)
        _assign_product_cost(producto, costo_usd, costo_cs, settings)

    ingreso.total_usd = total_usd
    ingreso.total_cs = total_cs

    if _recipe_explosion_on_ingreso_mode(db):
        recipe_requirements, recipe_error = _build_recipe_requirements(
            db,
            [(int(item.producto_id), Decimal(item.cantidad)) for item in payload.items],
        )
        if recipe_error:
            raise HTTPException(status_code=400, detail=recipe_error)
        if recipe_requirements:
            stock_error = _ensure_recipe_stock(db, payload.bodega_id, recipe_requirements)
            if stock_error:
                raise HTTPException(status_code=400, detail=stock_error)

            egreso_tipo = _resolve_or_create_egreso_tipo(db, "Produccion por receta")
            egreso = EgresoInventario(
                tipo_id=egreso_tipo.id,
                bodega_id=payload.bodega_id,
                bodega_destino_id=None,
                usuario_id=payload.usuario_id,
                fecha=payload.fecha,
                moneda="CS",
                tasa_cambio=None,
                observacion=f"Explosion automatica de receta por ingreso #{ingreso.id}"[:300],
                usuario_registro=payload.usuario_registro,
                total_usd=Decimal("0"),
                total_cs=Decimal("0"),
            )
            db.add(egreso)
            db.flush()

            egreso_total_cs = Decimal("0")
            egreso_total_usd = Decimal("0")
            for ingredient_id, requirement in recipe_requirements.items():
                producto_req = requirement["producto"]
                required_qty = Decimal(str(requirement["cantidad"] or 0))
                cost_usd, cost_cs = _product_cost_pair(producto_req, tasa, settings)
                subtotal_cs = cost_cs * required_qty
                subtotal_usd = cost_usd * required_qty
                db.add(
                    EgresoItem(
                        egreso_id=egreso.id,
                        producto_id=ingredient_id,
                        cantidad=required_qty,
                        costo_unitario_usd=cost_usd,
                        costo_unitario_cs=cost_cs,
                        subtotal_usd=subtotal_usd,
                        subtotal_cs=subtotal_cs,
                    )
                )
                egreso_total_cs += subtotal_cs
                egreso_total_usd += subtotal_usd
            egreso.total_cs = egreso_total_cs
            egreso.total_usd = egreso_total_usd

    for item in payload.items:
        _rebuild_global_saldo(db, item.producto_id)
    if _recipe_explosion_on_ingreso_mode(db):
        recipe_requirements, _ = _build_recipe_requirements(
            db,
            [(int(item.producto_id), Decimal(item.cantidad)) for item in payload.items],
        )
        for ingredient_id in recipe_requirements.keys():
            _rebuild_global_saldo(db, ingredient_id)
    db.commit()
    return db.query(IngresoInventario).options(joinedload(IngresoInventario.items)).filter(IngresoInventario.id == ingreso.id).first()


@router.get("/ingresos", response_model=List[IngresoResponse])
def list_ingresos(db: Session = Depends(get_db)):
    return db.query(IngresoInventario).options(joinedload(IngresoInventario.items)).order_by(IngresoInventario.id.desc()).all()


@router.post("/egresos", response_model=EgresoResponse, status_code=status.HTTP_201_CREATED)
def create_egreso(payload: EgresoCreate, db: Session = Depends(get_db)):
    settings = _get_business_settings(db)
    if not payload.items:
        raise HTTPException(status_code=400, detail="Debes registrar al menos un item")

    if not db.query(EgresoTipo).filter(EgresoTipo.id == payload.tipo_id).first():
        raise HTTPException(status_code=404, detail="Tipo de egreso no encontrado")
    if not db.query(Bodega).filter(Bodega.id == payload.bodega_id).first():
        raise HTTPException(status_code=404, detail="Bodega no encontrada")
    if payload.bodega_destino_id and not db.query(Bodega).filter(Bodega.id == payload.bodega_destino_id).first():
        raise HTTPException(status_code=404, detail="Bodega destino no encontrada")
    if payload.bodega_destino_id and payload.bodega_destino_id == payload.bodega_id:
        raise HTTPException(status_code=400, detail="La bodega destino debe ser distinta de la bodega origen")

    moneda = _normalize_currency(payload.moneda)
    tasa = _require_exchange_rate(moneda, payload.tasa_cambio)

    egreso = EgresoInventario(
        tipo_id=payload.tipo_id,
        bodega_id=payload.bodega_id,
        bodega_destino_id=payload.bodega_destino_id,
        usuario_id=payload.usuario_id,
        fecha=payload.fecha,
        moneda=moneda,
        tasa_cambio=payload.tasa_cambio,
        observacion=payload.observacion,
        usuario_registro=payload.usuario_registro,
    )
    db.add(egreso)
    db.flush()

    total_usd = Decimal("0")
    total_cs = Decimal("0")
    resolved_items: list[dict[str, Decimal | int]] = []

    for item in payload.items:
        producto = db.query(Producto).options(joinedload(Producto.saldo)).filter(Producto.id == item.producto_id).first()
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto {item.producto_id} no encontrado")

        cantidad = Decimal(item.cantidad)
        if cantidad <= 0:
            raise HTTPException(status_code=400, detail="La cantidad debe ser mayor que cero")

        _get_or_create_saldo(db, producto.id)
        if payload.bodega_id:
            existencia_actual = _balances_by_bodega(db, [payload.bodega_id], [producto.id]).get((producto.id, payload.bodega_id), Decimal("0"))
        else:
            existencia_actual = Decimal(producto.saldo.existencia or 0) if producto.saldo else Decimal("0")
        if existencia_actual < cantidad:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para {producto.cod_producto}. Disponible: {existencia_actual}",
            )

        costo_usd, costo_cs = _product_cost_pair(producto, tasa, settings)

        subtotal_usd = cantidad * costo_usd
        subtotal_cs = cantidad * costo_cs
        total_usd += subtotal_usd
        total_cs += subtotal_cs
        resolved_items.append(
            {
                "producto_id": int(producto.id),
                "cantidad": cantidad,
                "costo_unitario_usd": costo_usd,
                "costo_unitario_cs": costo_cs,
                "subtotal_usd": subtotal_usd,
                "subtotal_cs": subtotal_cs,
            }
        )

        db.add(
            EgresoItem(
                egreso_id=egreso.id,
                producto_id=producto.id,
                cantidad=cantidad,
                costo_unitario_usd=costo_usd,
                costo_unitario_cs=costo_cs,
                subtotal_usd=subtotal_usd,
                subtotal_cs=subtotal_cs,
            )
        )
    egreso.total_usd = total_usd
    egreso.total_cs = total_cs
    if payload.bodega_destino_id:
        traslado_tipo = db.query(IngresoTipo).filter(IngresoTipo.nombre == "Ajustes de Inventario").first()
        if not traslado_tipo:
            traslado_tipo = IngresoTipo(nombre="Ajustes de Inventario", requiere_proveedor=False)
            db.add(traslado_tipo)
            db.flush()
        ingreso_destino = IngresoInventario(
            tipo_id=traslado_tipo.id,
            bodega_id=payload.bodega_destino_id,
            proveedor_id=None,
            usuario_id=payload.usuario_id,
            fecha=payload.fecha,
            moneda=moneda,
            tasa_cambio=payload.tasa_cambio,
            observacion=f"Traslado desde bodega {payload.bodega_id}. {payload.observacion or ''}".strip(),
            usuario_registro=payload.usuario_registro,
            total_usd=total_usd,
            total_cs=total_cs,
        )
        db.add(ingreso_destino)
        db.flush()
        for item_data in resolved_items:
            db.add(
                IngresoItem(
                    ingreso_id=ingreso_destino.id,
                    producto_id=int(item_data["producto_id"]),
                    cantidad=item_data["cantidad"],
                    costo_unitario_usd=item_data["costo_unitario_usd"],
                    costo_unitario_cs=item_data["costo_unitario_cs"],
                    subtotal_usd=item_data["subtotal_usd"],
                    subtotal_cs=item_data["subtotal_cs"],
                )
            )
    for item in payload.items:
        _rebuild_global_saldo(db, item.producto_id)
    db.commit()
    return db.query(EgresoInventario).options(joinedload(EgresoInventario.items)).filter(EgresoInventario.id == egreso.id).first()


@router.get("/egresos", response_model=List[EgresoResponse])
def list_egresos(db: Session = Depends(get_db)):
    return db.query(EgresoInventario).options(joinedload(EgresoInventario.items)).order_by(EgresoInventario.id.desc()).all()


@router.get("/kardex/{product_id}", response_model=List[KardexMovimientoResponse])
def get_kardex(product_id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == product_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    movimientos: list[KardexMovimientoResponse] = []

    ingresos = (
        db.query(IngresoItem, IngresoInventario)
        .join(IngresoInventario, IngresoInventario.id == IngresoItem.ingreso_id)
        .filter(IngresoItem.producto_id == product_id)
        .all()
    )
    for item, ingreso in ingresos:
        movimientos.append(
            KardexMovimientoResponse(
                fecha=ingreso.fecha,
                tipo="INGRESO",
                documento=f"ING-{ingreso.id}",
                producto_id=producto.id,
                cod_producto=producto.cod_producto,
                descripcion=producto.descripcion,
                cantidad_entrada=item.cantidad,
                cantidad_salida=Decimal("0"),
                costo_unitario_cs=item.costo_unitario_cs,
                subtotal_cs=item.subtotal_cs,
            )
        )

    egresos = (
        db.query(EgresoItem, EgresoInventario)
        .join(EgresoInventario, EgresoInventario.id == EgresoItem.egreso_id)
        .filter(EgresoItem.producto_id == product_id)
        .all()
    )
    for item, egreso in egresos:
        movimientos.append(
            KardexMovimientoResponse(
                fecha=egreso.fecha,
                tipo="EGRESO",
                documento=f"EGR-{egreso.id}",
                producto_id=producto.id,
                cod_producto=producto.cod_producto,
                descripcion=producto.descripcion,
                cantidad_entrada=Decimal("0"),
                cantidad_salida=item.cantidad,
                costo_unitario_cs=item.costo_unitario_cs,
                subtotal_cs=item.subtotal_cs,
            )
        )

    return sorted(movimientos, key=lambda row: (row.fecha, row.documento))
