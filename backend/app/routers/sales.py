import json
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import func, or_
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
    Producto,
)
from ..models.sales import CashClose, CashCloseMovement, CashVoucher, Customer, SalesInvoice, SalesInvoiceItem, SalesPayment, SalesSequence
from ..models.settings import BusinessSetting
from ..routers.inventory import (
    _balances_by_bodega,
    _cost_pair_from_amount,
    _current_exchange_rate_value,
    _get_business_settings,
    _get_or_create_saldo,
    _normalize_currency,
    _product_cost_pair,
    _rebuild_global_saldo,
    _require_exchange_rate,
)
from ..schemas.sales import (
    CustomerCreate,
    CustomerResponse,
    CustomerUpdate,
    CashCloseCreate,
    CashCloseResponse,
    CashCloseSummaryResponse,
    CashVoucherCreate,
    CashVoucherResponse,
    SalesInvoiceCreate,
    SalesInvoiceResponse,
    SalesNextInvoiceResponse,
)

router = APIRouter(prefix="/sales-api", tags=["Sales"])

MONEY = Decimal("0.01")


def _money(value: Decimal | int | float | str | None) -> Decimal:
    return Decimal(str(value or 0)).quantize(MONEY, rounding=ROUND_HALF_UP)


def _next_invoice_number(db: Session) -> str:
    sequence = db.query(SalesSequence).filter(SalesSequence.prefix == "POS").with_for_update().first()
    if not sequence:
        sequence = SalesSequence(prefix="POS", current_value=0, is_active=True)
        db.add(sequence)
        db.flush()
    sequence.current_value = int(sequence.current_value or 0) + 1
    return f"{sequence.prefix}-{sequence.current_value:06d}"


def _peek_invoice_number(db: Session) -> str:
    sequence = db.query(SalesSequence).filter(SalesSequence.prefix == "POS").first()
    next_value = int(sequence.current_value or 0) + 1 if sequence else 1
    return f"POS-{next_value:06d}"


def _next_cash_close_number(db: Session) -> str:
    next_value = (db.query(func.count(CashClose.id)).scalar() or 0) + 1
    return f"CC-{next_value:06d}"


def _next_cash_voucher_number(db: Session) -> str:
    next_value = (db.query(func.count(CashVoucher.id)).scalar() or 0) + 1
    return f"VC-{next_value:06d}"


def _payment_bucket(payment: SalesPayment) -> str:
    code = (payment.forma_codigo or "").strip().lower()
    name = (payment.forma_nombre or "").strip().lower()
    if code in {"cash", "efectivo"} or "efectivo" in name:
        return "cash"
    if code in {"card", "tarjeta"} or "tarjeta" in name:
        return "card"
    if code in {"transfer", "transferencia"} or "transfer" in name:
        return "transfer"
    return "other"


def _cash_close_summary(db: Session, fecha, bodega_id: int | None = None) -> dict:
    invoice_query = db.query(SalesInvoice).filter(SalesInvoice.fecha == fecha, SalesInvoice.status != "ANULADA")
    if bodega_id:
        invoice_query = invoice_query.filter(SalesInvoice.bodega_id == bodega_id)
    invoices = invoice_query.all()
    invoice_ids = [invoice.id for invoice in invoices]

    totals = {
        "invoice_count": len(invoices),
        "total_ventas_cs": _money(sum((invoice.total_cs or 0) for invoice in invoices)),
        "total_ventas_usd": _money(sum((invoice.total_usd or 0) for invoice in invoices)),
        "efectivo_ventas_cs": Decimal("0.00"),
        "tarjeta_ventas_cs": Decimal("0.00"),
        "transferencia_ventas_cs": Decimal("0.00"),
        "otros_pagos_cs": Decimal("0.00"),
    }
    if invoice_ids:
        for payment in db.query(SalesPayment).filter(SalesPayment.invoice_id.in_(invoice_ids)).all():
            amount = _money(payment.monto_cs)
            bucket = _payment_bucket(payment)
            if bucket == "cash":
                totals["efectivo_ventas_cs"] += amount
            elif bucket == "card":
                totals["tarjeta_ventas_cs"] += amount
            elif bucket == "transfer":
                totals["transferencia_ventas_cs"] += amount
            else:
                totals["otros_pagos_cs"] += amount

    voucher_query = db.query(CashVoucher).filter(
        CashVoucher.fecha == fecha,
        CashVoucher.afecta_caja.is_(True),
        CashVoucher.status == "EMITIDO",
    )
    if bodega_id:
        voucher_query = voucher_query.filter(CashVoucher.bodega_id == bodega_id)
    vouchers = voucher_query.all()
    totals["ingresos_caja_cs"] = _money(
        sum((voucher.monto_cs or 0) for voucher in vouchers if (voucher.tipo or "").upper() == "INGRESO")
    )
    totals["egresos_caja_cs"] = _money(
        sum((voucher.monto_cs or 0) for voucher in vouchers if (voucher.tipo or "").upper() == "EGRESO")
    )

    closed = db.query(CashClose).filter(CashClose.fecha == fecha, CashClose.bodega_id == bodega_id).first()
    bodega = db.query(Bodega).filter(Bodega.id == bodega_id).first() if bodega_id else None
    return {
        "fecha": fecha,
        "bodega_id": bodega_id,
        "bodega_name": bodega.name if bodega else None,
        "has_closed": bool(closed),
        "closed_id": closed.id if closed else None,
        **totals,
    }


def _cash_detail_total(detail: dict[str, Decimal] | None) -> tuple[dict[str, float], Decimal]:
    normalized = {}
    total = Decimal("0.00")
    for denom_key, quantity_value in (detail or {}).items():
        denom = Decimal(str(denom_key or 0))
        quantity = Decimal(str(quantity_value or 0))
        if denom <= 0:
            continue
        if quantity < 0:
            raise HTTPException(status_code=400, detail="Las cantidades de denominaciones no pueden ser negativas")
        normalized[str(denom)] = float(quantity)
        total += denom * quantity
    return normalized, _money(total)


def _resolve_venta_tipo(db: Session) -> EgresoTipo:
    tipo = db.query(EgresoTipo).filter(func.lower(func.trim(EgresoTipo.nombre)) == "venta").first()
    if tipo:
        return tipo
    tipo = EgresoTipo(nombre="Venta")
    db.add(tipo)
    db.flush()
    return tipo


def _to_currency_pair(amount: Decimal, moneda: str, tasa: Decimal) -> tuple[Decimal, Decimal]:
    if moneda == "USD":
        return _money(amount), _money(amount * tasa)
    return _money(amount / tasa) if tasa > 0 else Decimal("0.00"), _money(amount)


def _settings_rate(settings: BusinessSetting | None, payload_rate: Decimal | None, moneda: str) -> Decimal:
    if moneda == "USD":
        return _require_exchange_rate(moneda, payload_rate)
    return payload_rate or Decimal("0")


@router.get("/invoices/next", response_model=SalesNextInvoiceResponse)
def get_next_invoice(db: Session = Depends(get_db)):
    return SalesNextInvoiceResponse(invoice_number=_peek_invoice_number(db))


@router.get("/customers", response_model=List[CustomerResponse])
def list_customers(q: str | None = None, include_inactive: bool = False, db: Session = Depends(get_db)):
    query = db.query(Customer)
    if not include_inactive:
        query = query.filter(Customer.activo.is_(True))
    if q:
        term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Customer.nombre.ilike(term),
                Customer.identificacion.ilike(term),
                Customer.telefono.ilike(term),
                Customer.email.ilike(term),
            )
        )
    return query.order_by(Customer.nombre.asc()).limit(300).all()


@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    nombre = (payload.nombre or "").strip()
    if not nombre:
        raise HTTPException(status_code=400, detail="Nombre de cliente requerido")

    identificacion = (payload.identificacion or "").strip()
    if identificacion:
        exists = db.query(Customer).filter(func.lower(Customer.identificacion) == identificacion.lower()).first()
        if exists:
            raise HTTPException(status_code=400, detail="Ya existe un cliente con esa identificacion")

    customer = Customer(
        nombre=nombre,
        telefono=(payload.telefono or "").strip() or None,
        identificacion=identificacion or None,
        direccion=(payload.direccion or "").strip() or None,
        email=(payload.email or "").strip() or None,
        tipo=(payload.tipo or "").strip() or None,
        activo=bool(payload.activo),
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.put("/customers/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: int, payload: CustomerUpdate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    data = payload.model_dump(exclude_unset=True)
    if "nombre" in data:
        nombre = (data["nombre"] or "").strip()
        if not nombre:
            raise HTTPException(status_code=400, detail="Nombre de cliente requerido")
        customer.nombre = nombre
    if "identificacion" in data:
        identificacion = (data.get("identificacion") or "").strip()
        if identificacion:
            exists = (
                db.query(Customer)
                .filter(func.lower(Customer.identificacion) == identificacion.lower(), Customer.id != customer.id)
                .first()
            )
            if exists:
                raise HTTPException(status_code=400, detail="Ya existe un cliente con esa identificacion")
        customer.identificacion = identificacion or None
    for field in ("telefono", "direccion", "email", "tipo"):
        if field in data:
            setattr(customer, field, (data.get(field) or "").strip() or None)
    if "activo" in data:
        customer.activo = bool(data["activo"])

    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/invoices", response_model=List[SalesInvoiceResponse])
def list_invoices(
    q: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    status_filter: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(SalesInvoice).options(joinedload(SalesInvoice.items), joinedload(SalesInvoice.payments))
    search = (q or "").strip().lower()
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                func.lower(SalesInvoice.invoice_number).like(like),
                func.lower(SalesInvoice.customer_name).like(like),
                func.lower(SalesInvoice.customer_document).like(like),
                func.lower(SalesInvoice.vendor_name).like(like),
                SalesInvoice.items.any(func.lower(SalesInvoiceItem.cod_producto).like(like)),
                SalesInvoice.items.any(func.lower(SalesInvoiceItem.descripcion).like(like)),
            )
        )
    if start_date:
        query = query.filter(SalesInvoice.fecha >= start_date)
    if end_date:
        query = query.filter(SalesInvoice.fecha <= end_date)
    normalized_status = (status_filter or "").strip().upper()
    if normalized_status and normalized_status != "TODAS":
        query = query.filter(SalesInvoice.status == normalized_status)
    return query.order_by(SalesInvoice.fecha.desc(), SalesInvoice.id.desc()).limit(200).all()


def _invoice_print_payload(invoice: SalesInvoice, db: Session) -> dict:
    settings = _get_business_settings(db)
    currency = (invoice.moneda or "CS").upper()
    return {
        "invoice": {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "fecha": invoice.fecha.isoformat() if invoice.fecha else None,
            "created_at": invoice.created_at.isoformat() if invoice.created_at else None,
            "customer_name": invoice.customer_name,
            "customer_phone": invoice.customer_phone,
            "customer_document": invoice.customer_document,
            "customer_address": invoice.customer_address,
            "vendor_name": invoice.vendor_name,
            "bodega_name": invoice.bodega.name if invoice.bodega else None,
            "condicion": invoice.condicion,
            "moneda": currency,
            "tasa_cambio": invoice.tasa_cambio,
            "subtotal_usd": invoice.subtotal_usd,
            "subtotal_cs": invoice.subtotal_cs,
            "total_usd": invoice.total_usd,
            "total_cs": invoice.total_cs,
            "paid_usd": invoice.paid_usd,
            "paid_cs": invoice.paid_cs,
            "balance_usd": invoice.balance_usd,
            "balance_cs": invoice.balance_cs,
            "change_usd": invoice.change_usd,
            "change_cs": invoice.change_cs,
            "status": invoice.status,
            "observacion": invoice.observacion,
        },
        "items": [
            {
                "id": item.id,
                "producto_id": item.producto_id,
                "cod_producto": item.cod_producto,
                "descripcion": item.descripcion,
                "unidad": item.unidad,
                "cantidad": item.cantidad,
                "precio_unitario_usd": item.precio_unitario_usd,
                "precio_unitario_cs": item.precio_unitario_cs,
                "subtotal_usd": item.subtotal_usd,
                "subtotal_cs": item.subtotal_cs,
            }
            for item in invoice.items
        ],
        "payments": [
            {
                "forma_codigo": payment.forma_codigo,
                "forma_nombre": payment.forma_nombre,
                "moneda": payment.moneda,
                "monto": payment.monto,
                "monto_usd": payment.monto_usd,
                "monto_cs": payment.monto_cs,
                "referencia": payment.referencia,
            }
            for payment in invoice.payments
        ],
        "business": {
            "business_name": settings.business_name,
            "legal_name": settings.legal_name,
            "trade_name": settings.trade_name,
            "address": settings.address,
            "ruc": settings.ruc,
            "phone": settings.phone or settings.phones,
            "email": settings.email,
            "logo_invoice": settings.logo_invoice,
        },
    }


@router.get("/invoices/{invoice_id}/print")
def get_invoice_print(invoice_id: int, db: Session = Depends(get_db)):
    invoice = (
        db.query(SalesInvoice)
        .options(
            joinedload(SalesInvoice.items),
            joinedload(SalesInvoice.payments),
            joinedload(SalesInvoice.bodega),
        )
        .filter(SalesInvoice.id == invoice_id)
        .first()
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return _invoice_print_payload(invoice, db)


@router.post("/invoices/{invoice_id}/void", response_model=SalesInvoiceResponse)
def void_invoice(invoice_id: int, payload: dict | None = Body(default=None), db: Session = Depends(get_db)):
    invoice = (
        db.query(SalesInvoice)
        .options(
            joinedload(SalesInvoice.items),
            joinedload(SalesInvoice.payments),
            joinedload(SalesInvoice.egreso).joinedload(EgresoInventario.items),
        )
        .filter(SalesInvoice.id == invoice_id)
        .first()
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    if (invoice.status or "").upper() == "ANULADA":
        raise HTTPException(status_code=400, detail="La factura ya esta anulada")

    payload = payload or {}
    motivo = (payload.get("motivo") or "").strip()
    usuario = (payload.get("usuario_registro") or "").strip() or "Sistema"
    if len(motivo) < 8:
        raise HTTPException(status_code=400, detail="Indica un motivo de anulacion mas descriptivo")

    ingreso_tipo = db.query(IngresoTipo).filter(func.lower(IngresoTipo.nombre) == "anulacion de venta").first()
    if not ingreso_tipo:
        ingreso_tipo = IngresoTipo(nombre="Anulacion de Venta", requiere_proveedor=False)
        db.add(ingreso_tipo)
        db.flush()

    tasa = Decimal(str(invoice.tasa_cambio or 0))
    ingreso = IngresoInventario(
        tipo_id=ingreso_tipo.id,
        bodega_id=invoice.bodega_id,
        proveedor_id=None,
        usuario_id=None,
        fecha=invoice.fecha,
        moneda=invoice.moneda,
        tasa_cambio=invoice.tasa_cambio,
        observacion=f"Anulacion de factura {invoice.invoice_number}: {motivo}"[:300],
        usuario_registro=usuario,
    )
    db.add(ingreso)
    db.flush()

    egreso_items_by_product = {}
    if invoice.egreso:
        for egreso_item in invoice.egreso.items:
            egreso_items_by_product.setdefault(egreso_item.producto_id, egreso_item)

    total_usd = Decimal("0")
    total_cs = Decimal("0")
    touched_products: set[int] = set()
    for item in invoice.items:
        cantidad = Decimal(str(item.cantidad or 0))
        egreso_item = egreso_items_by_product.get(item.producto_id)
        producto = db.query(Producto).filter(Producto.id == item.producto_id).first()
        if egreso_item:
            cost_usd = _money(egreso_item.costo_unitario_usd)
            cost_cs = _money(egreso_item.costo_unitario_cs)
        elif producto:
            settings = _get_business_settings(db)
            cost_usd, cost_cs = _product_cost_pair(producto, tasa, settings)
        else:
            cost_usd = Decimal("0.00")
            cost_cs = Decimal("0.00")
        subtotal_usd = _money(cost_usd * cantidad)
        subtotal_cs = _money(cost_cs * cantidad)
        total_usd += subtotal_usd
        total_cs += subtotal_cs
        touched_products.add(item.producto_id)
        db.add(
            IngresoItem(
                ingreso_id=ingreso.id,
                producto_id=item.producto_id,
                cantidad=cantidad,
                costo_unitario_usd=cost_usd,
                costo_unitario_cs=cost_cs,
                subtotal_usd=subtotal_usd,
                subtotal_cs=subtotal_cs,
            )
        )

    ingreso.total_usd = _money(total_usd)
    ingreso.total_cs = _money(total_cs)
    previous_note = (invoice.observacion or "").strip()
    invoice.status = "ANULADA"
    invoice.observacion = f"{previous_note}\nANULADA por {usuario}: {motivo}".strip()
    db.add(invoice)

    for product_id in touched_products:
        _rebuild_global_saldo(db, product_id)

    db.commit()
    return (
        db.query(SalesInvoice)
        .options(joinedload(SalesInvoice.items), joinedload(SalesInvoice.payments))
        .filter(SalesInvoice.id == invoice.id)
        .first()
    )


@router.get("/cash-close/summary", response_model=CashCloseSummaryResponse)
def get_cash_close_summary(fecha: date, bodega_id: int | None = None, db: Session = Depends(get_db)):
    return _cash_close_summary(db, fecha, bodega_id)


@router.get("/cash-close", response_model=List[CashCloseResponse])
def list_cash_closures(db: Session = Depends(get_db)):
    return (
        db.query(CashClose)
        .options(joinedload(CashClose.movements))
        .order_by(CashClose.fecha.desc(), CashClose.id.desc())
        .limit(60)
        .all()
    )


@router.get("/cash-vouchers", response_model=List[CashVoucherResponse])
def list_cash_vouchers(
    start_date: date | None = None,
    end_date: date | None = None,
    bodega_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(CashVoucher)
    if start_date:
        query = query.filter(CashVoucher.fecha >= start_date)
    if end_date:
        query = query.filter(CashVoucher.fecha <= end_date)
    if bodega_id:
        query = query.filter(CashVoucher.bodega_id == bodega_id)
    return query.order_by(CashVoucher.fecha.desc(), CashVoucher.id.desc()).limit(200).all()


@router.post("/cash-vouchers", response_model=CashVoucherResponse, status_code=status.HTTP_201_CREATED)
def create_cash_voucher(payload: CashVoucherCreate, db: Session = Depends(get_db)):
    if payload.bodega_id and not db.query(Bodega).filter(Bodega.id == payload.bodega_id).first():
        raise HTTPException(status_code=404, detail="Bodega no encontrada")
    tipo = (payload.tipo or "").strip().upper()
    if tipo not in {"INGRESO", "EGRESO"}:
        raise HTTPException(status_code=400, detail="Tipo de vale invalido")
    rubro = (payload.rubro or "").strip()
    motivo = (payload.motivo or "").strip()
    if not rubro or not motivo:
        raise HTTPException(status_code=400, detail="Rubro y motivo son requeridos")
    moneda = _normalize_currency(payload.moneda)
    monto = _money(payload.monto)
    if monto <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser mayor que cero")
    tasa = Decimal(str(payload.tasa_cambio or 0))
    if moneda == "USD" and tasa <= 0:
        try:
            tasa = _current_exchange_rate_value(db)
        except HTTPException as exc:
            raise HTTPException(status_code=400, detail="Registra una tasa de cambio vigente para vales en dolares.") from exc
    monto_usd, monto_cs = _to_currency_pair(monto, moneda, tasa)
    voucher = CashVoucher(
        numero=_next_cash_voucher_number(db),
        fecha=payload.fecha,
        bodega_id=payload.bodega_id,
        tipo=tipo,
        rubro=rubro,
        motivo=motivo,
        descripcion=(payload.descripcion or "").strip() or None,
        moneda=moneda,
        tasa_cambio=tasa if tasa > 0 else None,
        monto_usd=monto_usd,
        monto_cs=monto_cs,
        afecta_caja=bool(payload.afecta_caja),
        status="EMITIDO",
        usuario_registro=(payload.usuario_registro or "").strip() or None,
    )
    db.add(voucher)
    db.commit()
    db.refresh(voucher)
    return voucher


@router.post("/cash-close", response_model=CashCloseResponse, status_code=status.HTTP_201_CREATED)
def create_cash_close(payload: CashCloseCreate, db: Session = Depends(get_db)):
    if payload.bodega_id and not db.query(Bodega).filter(Bodega.id == payload.bodega_id).first():
        raise HTTPException(status_code=404, detail="Bodega no encontrada")
    exists = db.query(CashClose).filter(CashClose.fecha == payload.fecha, CashClose.bodega_id == payload.bodega_id).first()
    if exists:
        raise HTTPException(status_code=400, detail="Ya existe un cierre de caja para esa fecha y bodega")

    summary = _cash_close_summary(db, payload.fecha, payload.bodega_id)
    ingresos = _money(summary["ingresos_caja_cs"])
    egresos = _money(summary["egresos_caja_cs"])
    normalized_movements = []
    for movement in payload.movements:
        tipo = (movement.tipo or "").strip().upper()
        if tipo not in {"INGRESO", "EGRESO"}:
            raise HTTPException(status_code=400, detail="Tipo de movimiento invalido")
        monto = _money(movement.monto_cs)
        if monto <= 0:
            raise HTTPException(status_code=400, detail="El monto de ingresos y egresos debe ser mayor que cero")
        concepto = (movement.concepto or "").strip()
        if not concepto:
            raise HTTPException(status_code=400, detail="El concepto del movimiento es requerido")
        if tipo == "INGRESO":
            ingresos += monto
        else:
            egresos += monto
        normalized_movements.append((tipo, concepto, monto, (movement.referencia or "").strip() or None))

    detalle_cs, total_efectivo_cs = _cash_detail_total(payload.detalle_cs)
    detalle_usd, total_efectivo_usd = _cash_detail_total(payload.detalle_usd)
    tasa_cambio = Decimal(str(payload.tasa_cambio or 0))
    if total_efectivo_usd > 0 and tasa_cambio <= 0:
        try:
            tasa_cambio = _current_exchange_rate_value(db)
        except HTTPException as exc:
            raise HTTPException(
                status_code=400,
                detail="Registra una tasa de cambio vigente antes de cerrar caja con dolares.",
            ) from exc
    efectivo_denominado_cs = _money(total_efectivo_cs + (total_efectivo_usd * tasa_cambio))
    efectivo_esperado = _money(summary["efectivo_ventas_cs"] + ingresos - egresos)
    efectivo_fisico = efectivo_denominado_cs if detalle_cs or detalle_usd else _money(payload.efectivo_fisico_cs)
    diferencia = _money(efectivo_fisico - efectivo_esperado)
    if diferencia > 0:
        resultado = "SOBRANTE"
    elif diferencia < 0:
        resultado = "FALTANTE"
    else:
        resultado = "CUADRADO"

    closure = CashClose(
        cierre_numero=_next_cash_close_number(db),
        fecha=payload.fecha,
        bodega_id=payload.bodega_id,
        usuario_registro=(payload.usuario_registro or "").strip() or None,
        total_ventas_cs=summary["total_ventas_cs"],
        total_ventas_usd=summary["total_ventas_usd"],
        efectivo_ventas_cs=summary["efectivo_ventas_cs"],
        tarjeta_ventas_cs=summary["tarjeta_ventas_cs"],
        transferencia_ventas_cs=summary["transferencia_ventas_cs"],
        otros_pagos_cs=summary["otros_pagos_cs"],
        ingresos_caja_cs=ingresos,
        egresos_caja_cs=egresos,
        detalle_cs=json.dumps(detalle_cs, sort_keys=True),
        detalle_usd=json.dumps(detalle_usd, sort_keys=True),
        total_efectivo_cs=total_efectivo_cs,
        total_efectivo_usd=total_efectivo_usd,
        tasa_cambio=tasa_cambio if tasa_cambio > 0 else None,
        efectivo_esperado_cs=efectivo_esperado,
        efectivo_fisico_cs=efectivo_fisico,
        diferencia_cs=diferencia,
        resultado=resultado,
        observacion=(payload.observacion or "").strip() or None,
        status="CERRADO",
    )
    db.add(closure)
    db.flush()
    for tipo, concepto, monto, referencia in normalized_movements:
        db.add(
            CashCloseMovement(
                closure_id=closure.id,
                tipo=tipo,
                concepto=concepto,
                monto_cs=monto,
                referencia=referencia,
            )
        )
    db.commit()
    return (
        db.query(CashClose)
        .options(joinedload(CashClose.movements))
        .filter(CashClose.id == closure.id)
        .first()
    )


@router.post("/invoices", response_model=SalesInvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(payload: SalesInvoiceCreate, db: Session = Depends(get_db)):
    settings = _get_business_settings(db)
    if not payload.items:
        raise HTTPException(status_code=400, detail="Debes registrar al menos un item")

    condicion = (payload.condicion or "CONTADO").strip().upper()
    if condicion not in {"CONTADO", "CREDITO"}:
        raise HTTPException(status_code=400, detail="Condicion de venta invalida")

    moneda = _normalize_currency(payload.moneda)
    tasa = _settings_rate(settings, payload.tasa_cambio, moneda)
    if moneda == "CS" and any((payment.moneda or "").strip().upper() == "USD" for payment in payload.payments) and tasa <= 0:
        raise HTTPException(status_code=400, detail="La tasa de cambio es requerida para pagos en USD")

    bodega = db.query(Bodega).filter(Bodega.id == payload.bodega_id).first()
    if not bodega:
        raise HTTPException(status_code=404, detail="Bodega no encontrada")

    product_ids = [int(item.producto_id) for item in payload.items]
    balances = _balances_by_bodega(db, [payload.bodega_id], product_ids)
    venta_tipo = _resolve_venta_tipo(db)

    invoice_number = _next_invoice_number(db)
    egreso = EgresoInventario(
        tipo_id=venta_tipo.id,
        bodega_id=payload.bodega_id,
        bodega_destino_id=None,
        usuario_id=None,
        fecha=payload.fecha,
        moneda=moneda,
        tasa_cambio=payload.tasa_cambio,
        observacion=f"Factura {invoice_number}. {payload.observacion or ''}".strip()[:300],
        usuario_registro=payload.usuario_registro,
    )
    db.add(egreso)
    db.flush()

    invoice = SalesInvoice(
        invoice_number=invoice_number,
        customer_name=(payload.customer_name or "Consumidor final").strip() or "Consumidor final",
        customer_phone=payload.customer_phone,
        customer_document=payload.customer_document,
        customer_address=payload.customer_address,
        vendor_name=payload.vendor_name,
        bodega_id=payload.bodega_id,
        egreso_id=egreso.id,
        fecha=payload.fecha,
        condicion=condicion,
        moneda=moneda,
        tasa_cambio=payload.tasa_cambio,
        observacion=payload.observacion,
        usuario_registro=payload.usuario_registro,
        status="EMITIDA" if condicion == "CONTADO" else "CREDITO",
    )
    db.add(invoice)
    db.flush()

    totals_usd = Decimal("0")
    totals_cs = Decimal("0")
    egreso_total_usd = Decimal("0")
    egreso_total_cs = Decimal("0")
    requested_by_product: dict[int, Decimal] = {}

    for item in payload.items:
        product_id = int(item.producto_id)
        cantidad = Decimal(str(item.cantidad or 0))
        precio_unitario = Decimal(str(item.precio_unitario or 0))
        if cantidad <= 0 or precio_unitario < 0:
            raise HTTPException(status_code=400, detail="Cantidad y precio deben ser validos")
        combo_role = (item.combo_role or "").strip().lower() or None
        if combo_role and combo_role not in {"parent", "gift"}:
            raise HTTPException(status_code=400, detail="Rol de combo invalido")
        combo_group = (item.combo_group or "").strip() or None

        requested_by_product[product_id] = requested_by_product.get(product_id, Decimal("0")) + cantidad
        available = Decimal(str(balances.get((product_id, payload.bodega_id), Decimal("0")) or 0))
        if requested_by_product[product_id] > available:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para producto {product_id}. Disponible: {available}")

        producto = db.query(Producto).options(joinedload(Producto.unidad_medida)).filter(Producto.id == product_id).first()
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto {product_id} no encontrado")

        _get_or_create_saldo(db, producto.id)
        price_usd, price_cs = _to_currency_pair(precio_unitario, moneda, tasa)
        subtotal_usd = _money(price_usd * cantidad)
        subtotal_cs = _money(price_cs * cantidad)
        totals_usd += subtotal_usd
        totals_cs += subtotal_cs

        cost_usd, cost_cs = _product_cost_pair(producto, tasa, settings)
        egreso_subtotal_usd = _money(cost_usd * cantidad)
        egreso_subtotal_cs = _money(cost_cs * cantidad)
        egreso_total_usd += egreso_subtotal_usd
        egreso_total_cs += egreso_subtotal_cs

        db.add(
            SalesInvoiceItem(
                invoice_id=invoice.id,
                producto_id=producto.id,
                cod_producto=item.cod_producto or producto.cod_producto,
                descripcion=item.descripcion or producto.descripcion,
                unidad=item.unidad or getattr(producto.unidad_medida, "abreviatura", None) or "UND",
                cantidad=cantidad,
                precio_unitario_usd=price_usd,
                precio_unitario_cs=price_cs,
                subtotal_usd=subtotal_usd,
                subtotal_cs=subtotal_cs,
                combo_role=combo_role,
                combo_group=combo_group,
            )
        )
        db.add(
            EgresoItem(
                egreso_id=egreso.id,
                producto_id=producto.id,
                cantidad=cantidad,
                costo_unitario_usd=cost_usd,
                costo_unitario_cs=cost_cs,
                subtotal_usd=egreso_subtotal_usd,
                subtotal_cs=egreso_subtotal_cs,
            )
        )

    paid_usd = Decimal("0")
    paid_cs = Decimal("0")
    if condicion == "CONTADO" and not payload.payments:
        raise HTTPException(status_code=400, detail="La venta de contado requiere al menos una forma de pago")

    for payment in payload.payments:
        payment_currency = _normalize_currency(payment.moneda)
        amount = Decimal(str(payment.monto or 0))
        if amount <= 0:
            raise HTTPException(status_code=400, detail="El monto del pago debe ser mayor que cero")
        amount_usd, amount_cs = _to_currency_pair(amount, payment_currency, tasa)
        paid_usd += amount_usd
        paid_cs += amount_cs
        db.add(
            SalesPayment(
                invoice_id=invoice.id,
                forma_codigo=(payment.forma_codigo or "").strip() or "cash",
                forma_nombre=(payment.forma_nombre or "").strip() or "Efectivo",
                moneda=payment_currency,
                monto=_money(amount),
                monto_usd=amount_usd,
                monto_cs=amount_cs,
                banco=payment.banco,
                cuenta=payment.cuenta,
                referencia=payment.referencia,
            )
        )

    if condicion == "CONTADO" and paid_cs < _money(totals_cs):
        raise HTTPException(status_code=400, detail="El pago no cubre el total de la factura")

    balance_cs = max(_money(totals_cs - paid_cs), Decimal("0.00"))
    change_cs = max(_money(paid_cs - totals_cs), Decimal("0.00"))
    balance_usd = _money(balance_cs / tasa) if tasa > 0 else Decimal("0.00")
    change_usd = _money(change_cs / tasa) if tasa > 0 else Decimal("0.00")

    invoice.subtotal_usd = _money(totals_usd)
    invoice.subtotal_cs = _money(totals_cs)
    invoice.total_usd = _money(totals_usd)
    invoice.total_cs = _money(totals_cs)
    invoice.paid_usd = _money(paid_usd)
    invoice.paid_cs = _money(paid_cs)
    invoice.balance_usd = balance_usd
    invoice.balance_cs = balance_cs
    invoice.change_usd = change_usd
    invoice.change_cs = change_cs

    egreso.total_usd = egreso_total_usd
    egreso.total_cs = egreso_total_cs

    for product_id in product_ids:
        _rebuild_global_saldo(db, product_id)

    db.commit()
    return (
        db.query(SalesInvoice)
        .options(joinedload(SalesInvoice.items), joinedload(SalesInvoice.payments))
        .filter(SalesInvoice.id == invoice.id)
        .first()
    )
