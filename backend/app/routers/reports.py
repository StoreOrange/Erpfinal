"""Router de informes.

Hecho por Carlos.
Colaboracion academica: Oded Garcia y Carlos Ramirez.

Los endpoints de este archivo son para consulta y analisis. Evitar modificar
datos desde reportes para que sean seguros y faciles de auditar.
"""

from datetime import date, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.inventory import (
    Bodega,
    EgresoInventario,
    EgresoItem,
    IngresoInventario,
    IngresoItem,
    Producto,
    SaldoProducto,
)
from ..models.sales import CashVoucher, SalesInvoice, SalesInvoiceItem
from ..routers.inventory import _balances_by_bodega

router = APIRouter(prefix="/reports", tags=["Reports"])


def _to_float(value) -> float:
    return float(Decimal(str(value or 0)))


def _default_start() -> date:
    today = date.today()
    return today.replace(day=1)


def _date_range(start_date: date | None, end_date: date | None) -> tuple[date, date]:
    start = start_date or _default_start()
    end = end_date or date.today()
    if end < start:
        return end, start
    return start, end


def _money_summary(query, usd_field, cs_field) -> dict:
    total_usd, total_cs = query.with_entities(func.coalesce(func.sum(usd_field), 0), func.coalesce(func.sum(cs_field), 0)).first()
    return {"usd": _to_float(total_usd), "cs": _to_float(total_cs)}


def _base_invoice_query(db: Session, start: date, end: date, bodega_id: int | None = None):
    query = db.query(SalesInvoice).filter(SalesInvoice.fecha.between(start, end))
    if bodega_id:
        query = query.filter(SalesInvoice.bodega_id == bodega_id)
    return query


def _base_voucher_query(db: Session, start: date, end: date, bodega_id: int | None = None):
    query = db.query(CashVoucher).filter(CashVoucher.fecha.between(start, end))
    if bodega_id:
        query = query.filter(CashVoucher.bodega_id == bodega_id)
    return query


@router.get("/catalogs")
def report_catalogs(db: Session = Depends(get_db)):
    products = (
        db.query(Producto.id, Producto.cod_producto, Producto.descripcion)
        .filter(Producto.activo.is_(True))
        .order_by(Producto.descripcion)
        .limit(500)
        .all()
    )
    bodegas = db.query(Bodega.id, Bodega.code, Bodega.name).filter(Bodega.activo.is_(True)).order_by(Bodega.name).all()
    return {
        "bodegas": [{"id": row.id, "code": row.code, "name": row.name} for row in bodegas],
        "products": [
            {"id": row.id, "cod_producto": row.cod_producto, "descripcion": row.descripcion}
            for row in products
        ],
    }


@router.get("/summary")
def reports_summary(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    bodega_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    start, end = _date_range(start_date, end_date)
    invoice_query = _base_invoice_query(db, start, end, bodega_id)
    voucher_query = _base_voucher_query(db, start, end, bodega_id)

    sales_totals = _money_summary(invoice_query, SalesInvoice.total_usd, SalesInvoice.total_cs)
    invoice_count = invoice_query.count()
    ingresos_caja = _money_summary(voucher_query.filter(CashVoucher.tipo == "INGRESO"), CashVoucher.monto_usd, CashVoucher.monto_cs)
    egresos_caja = _money_summary(voucher_query.filter(CashVoucher.tipo == "EGRESO"), CashVoucher.monto_usd, CashVoucher.monto_cs)

    inventory_rows = (
        db.query(
            func.count(Producto.id),
            func.coalesce(func.sum(SaldoProducto.existencia), 0),
            func.coalesce(func.sum(SaldoProducto.existencia * Producto.costo_producto), 0),
            func.coalesce(func.sum(SaldoProducto.existencia * Producto.precio_venta1), 0),
        )
        .outerjoin(SaldoProducto, SaldoProducto.producto_id == Producto.id)
        .filter(Producto.activo.is_(True))
        .first()
    )

    return {
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "sales": {
            "invoice_count": invoice_count,
            "total_usd": sales_totals["usd"],
            "total_cs": sales_totals["cs"],
            "average_ticket_cs": sales_totals["cs"] / invoice_count if invoice_count else 0,
        },
        "cash_vouchers": {
            "ingresos_cs": ingresos_caja["cs"],
            "egresos_cs": egresos_caja["cs"],
            "balance_cs": ingresos_caja["cs"] - egresos_caja["cs"],
        },
        "inventory": {
            "product_count": int(inventory_rows[0] or 0),
            "existencia_total": _to_float(inventory_rows[1]),
            "valor_costo_cs": _to_float(inventory_rows[2]),
            "valor_venta_cs": _to_float(inventory_rows[3]),
        },
    }


@router.get("/sales-detailed")
def sales_detailed_report(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    bodega_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    start, end = _date_range(start_date, end_date)
    invoices = _base_invoice_query(db, start, end, bodega_id).order_by(SalesInvoice.fecha.desc(), SalesInvoice.id.desc()).all()
    return [
        {
            "id": invoice.id,
            "fecha": invoice.fecha.isoformat(),
            "invoice_number": invoice.invoice_number,
            "customer_name": invoice.customer_name,
            "vendor_name": invoice.vendor_name,
            "bodega": invoice.bodega.name if invoice.bodega else "",
            "condicion": invoice.condicion,
            "status": invoice.status,
            "total_usd": _to_float(invoice.total_usd),
            "total_cs": _to_float(invoice.total_cs),
            "paid_cs": _to_float(invoice.paid_cs),
            "balance_cs": _to_float(invoice.balance_cs),
        }
        for invoice in invoices
    ]


@router.get("/sales-products")
def sales_products_report(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    bodega_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    start, end = _date_range(start_date, end_date)
    query = (
        db.query(
            SalesInvoiceItem.producto_id,
            SalesInvoiceItem.cod_producto,
            SalesInvoiceItem.descripcion,
            func.coalesce(func.sum(SalesInvoiceItem.cantidad), 0).label("cantidad"),
            func.coalesce(func.sum(SalesInvoiceItem.subtotal_usd), 0).label("subtotal_usd"),
            func.coalesce(func.sum(SalesInvoiceItem.subtotal_cs), 0).label("subtotal_cs"),
        )
        .join(SalesInvoice, SalesInvoice.id == SalesInvoiceItem.invoice_id)
        .filter(SalesInvoice.fecha.between(start, end))
    )
    if bodega_id:
        query = query.filter(SalesInvoice.bodega_id == bodega_id)
    rows = query.group_by(SalesInvoiceItem.producto_id, SalesInvoiceItem.cod_producto, SalesInvoiceItem.descripcion).order_by(func.sum(SalesInvoiceItem.subtotal_cs).desc()).all()
    return [
        {
            "producto_id": row.producto_id,
            "cod_producto": row.cod_producto,
            "descripcion": row.descripcion,
            "cantidad": _to_float(row.cantidad),
            "subtotal_usd": _to_float(row.subtotal_usd),
            "subtotal_cs": _to_float(row.subtotal_cs),
        }
        for row in rows
    ]


@router.get("/profit")
def profit_report(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    bodega_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    start, end = _date_range(start_date, end_date)
    query = (
        db.query(
            SalesInvoiceItem.cod_producto,
            SalesInvoiceItem.descripcion,
            func.coalesce(func.sum(SalesInvoiceItem.cantidad), 0).label("cantidad"),
            func.coalesce(func.sum(SalesInvoiceItem.subtotal_cs), 0).label("venta_cs"),
            func.coalesce(func.sum(SalesInvoiceItem.cantidad * Producto.costo_producto), 0).label("costo_cs"),
        )
        .join(SalesInvoice, SalesInvoice.id == SalesInvoiceItem.invoice_id)
        .join(Producto, Producto.id == SalesInvoiceItem.producto_id)
        .filter(SalesInvoice.fecha.between(start, end))
    )
    if bodega_id:
        query = query.filter(SalesInvoice.bodega_id == bodega_id)
    rows = query.group_by(SalesInvoiceItem.cod_producto, SalesInvoiceItem.descripcion).order_by(func.sum(SalesInvoiceItem.subtotal_cs).desc()).all()
    return [
        {
            "cod_producto": row.cod_producto,
            "descripcion": row.descripcion,
            "cantidad": _to_float(row.cantidad),
            "venta_cs": _to_float(row.venta_cs),
            "costo_cs": _to_float(row.costo_cs),
            "utilidad_cs": _to_float(row.venta_cs) - _to_float(row.costo_cs),
        }
        for row in rows
    ]


@router.get("/inventory-consolidated")
def inventory_consolidated_report(db: Session = Depends(get_db)):
    rows = (
        db.query(Producto, SaldoProducto.existencia)
        .outerjoin(SaldoProducto, SaldoProducto.producto_id == Producto.id)
        .filter(Producto.activo.is_(True))
        .order_by(Producto.descripcion)
        .all()
    )
    return [
        {
            "id": product.id,
            "cod_producto": product.cod_producto,
            "descripcion": product.descripcion,
            "linea": product.linea.linea if product.linea else "",
            "segmento": product.segmento.segmento if product.segmento else "",
            "existencia": _to_float(existencia),
            "costo_producto": _to_float(product.costo_producto),
            "precio_venta1": _to_float(product.precio_venta1),
            "valor_costo_cs": _to_float(existencia) * _to_float(product.costo_producto),
            "valor_venta_cs": _to_float(existencia) * _to_float(product.precio_venta1),
        }
        for product, existencia in rows
    ]


@router.get("/saldos-bodega")
def warehouse_balances_report(bodega_id: int | None = Query(None), db: Session = Depends(get_db)):
    bodegas_query = db.query(Bodega).filter(Bodega.activo.is_(True))
    if bodega_id:
        bodegas_query = bodegas_query.filter(Bodega.id == bodega_id)
    bodegas = bodegas_query.order_by(Bodega.name).all()
    products = db.query(Producto).filter(Producto.activo.is_(True)).order_by(Producto.descripcion).all()
    balances = _balances_by_bodega(db, [bodega.id for bodega in bodegas], [product.id for product in products])
    rows = []
    for bodega in bodegas:
        for product in products:
            existencia = balances.get((product.id, bodega.id), Decimal("0"))
            if existencia == 0:
                continue
            rows.append(
                {
                    "bodega_id": bodega.id,
                    "bodega": bodega.name,
                    "cod_producto": product.cod_producto,
                    "descripcion": product.descripcion,
                    "existencia": _to_float(existencia),
                    "costo_producto": _to_float(product.costo_producto),
                    "valor_costo_cs": _to_float(existencia) * _to_float(product.costo_producto),
                }
            )
    return rows


@router.get("/kardex")
def kardex_report(
    product_id: int | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    bodega_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    start, end = _date_range(start_date, end_date)
    entries = []

    ingreso_query = (
        db.query(IngresoInventario, IngresoItem, Producto)
        .join(IngresoItem, IngresoItem.ingreso_id == IngresoInventario.id)
        .join(Producto, Producto.id == IngresoItem.producto_id)
        .filter(IngresoInventario.fecha.between(start, end))
    )
    egreso_query = (
        db.query(EgresoInventario, EgresoItem, Producto)
        .join(EgresoItem, EgresoItem.egreso_id == EgresoInventario.id)
        .join(Producto, Producto.id == EgresoItem.producto_id)
        .filter(EgresoInventario.fecha.between(start, end))
    )
    if product_id:
        ingreso_query = ingreso_query.filter(IngresoItem.producto_id == product_id)
        egreso_query = egreso_query.filter(EgresoItem.producto_id == product_id)
    if bodega_id:
        ingreso_query = ingreso_query.filter(IngresoInventario.bodega_id == bodega_id)
        egreso_query = egreso_query.filter(EgresoInventario.bodega_id == bodega_id)

    for ingreso, item, product in ingreso_query.all():
        entries.append(
            {
                "fecha": ingreso.fecha.isoformat(),
                "tipo": "INGRESO",
                "documento": f"ING-{ingreso.id:06d}",
                "bodega": ingreso.bodega.name if ingreso.bodega else "",
                "cod_producto": product.cod_producto,
                "descripcion": product.descripcion,
                "entrada": _to_float(item.cantidad),
                "salida": 0,
                "costo_unitario_cs": _to_float(item.costo_unitario_cs),
                "subtotal_cs": _to_float(item.subtotal_cs),
            }
        )
    for egreso, item, product in egreso_query.all():
        entries.append(
            {
                "fecha": egreso.fecha.isoformat(),
                "tipo": "EGRESO",
                "documento": f"EGR-{egreso.id:06d}",
                "bodega": egreso.bodega.name if egreso.bodega else "",
                "cod_producto": product.cod_producto,
                "descripcion": product.descripcion,
                "entrada": 0,
                "salida": _to_float(item.cantidad),
                "costo_unitario_cs": _to_float(item.costo_unitario_cs),
                "subtotal_cs": _to_float(item.subtotal_cs),
            }
        )
    return sorted(entries, key=lambda row: (row["fecha"], row["cod_producto"], row["tipo"]))


@router.get("/cash-vouchers")
def cash_vouchers_report(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    bodega_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    start, end = _date_range(start_date, end_date)
    vouchers = _base_voucher_query(db, start, end, bodega_id).order_by(CashVoucher.fecha.desc(), CashVoucher.id.desc()).all()
    return [
        {
            "id": voucher.id,
            "fecha": voucher.fecha.isoformat(),
            "numero": voucher.numero,
            "tipo": voucher.tipo,
            "rubro": voucher.rubro,
            "motivo": voucher.motivo,
            "bodega": voucher.bodega.name if voucher.bodega else "",
            "monto_usd": _to_float(voucher.monto_usd),
            "monto_cs": _to_float(voucher.monto_cs),
            "status": voucher.status,
        }
        for voucher in vouchers
    ]


@router.get("/stagnant-products")
def stagnant_products_report(
    days_without_movement: int = Query(60, ge=1, le=730),
    bodega_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    cutoff = date.today() - timedelta(days=days_without_movement)
    products = db.query(Producto).filter(Producto.activo.is_(True)).order_by(Producto.descripcion).all()
    balances = {}
    if bodega_id:
        balances = _balances_by_bodega(db, [bodega_id], [product.id for product in products])

    rows = []
    for product in products:
        last_ingreso = (
            db.query(func.max(IngresoInventario.fecha))
            .join(IngresoItem, IngresoItem.ingreso_id == IngresoInventario.id)
            .filter(IngresoItem.producto_id == product.id)
        )
        last_egreso = (
            db.query(func.max(EgresoInventario.fecha))
            .join(EgresoItem, EgresoItem.egreso_id == EgresoInventario.id)
            .filter(EgresoItem.producto_id == product.id)
        )
        if bodega_id:
            last_ingreso = last_ingreso.filter(IngresoInventario.bodega_id == bodega_id)
            last_egreso = last_egreso.filter(EgresoInventario.bodega_id == bodega_id)
            existencia = balances.get((product.id, bodega_id), Decimal("0"))
        else:
            existencia = Decimal(str(product.saldo.existencia if product.saldo else 0))

        last_dates = [value for value in [last_ingreso.scalar(), last_egreso.scalar()] if value]
        last_movement = max(last_dates) if last_dates else None
        if last_movement and last_movement > cutoff:
            continue
        if existencia <= 0:
            continue
        days_stagnant = (date.today() - last_movement).days if last_movement else None
        rows.append(
            {
                "cod_producto": product.cod_producto,
                "descripcion": product.descripcion,
                "linea": product.linea.linea if product.linea else "",
                "segmento": product.segmento.segmento if product.segmento else "",
                "existencia": _to_float(existencia),
                "ultimo_movimiento": last_movement.isoformat() if last_movement else "Sin movimiento",
                "dias_sin_movimiento": days_stagnant if days_stagnant is not None else days_without_movement,
                "valor_costo_cs": _to_float(existencia) * _to_float(product.costo_producto),
            }
        )
    return sorted(rows, key=lambda row: row["dias_sin_movimiento"], reverse=True)


@router.get("/top-movement")
def top_movement_report(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    bodega_id: int | None = Query(None),
    limit: int = Query(50, ge=1, le=300),
    db: Session = Depends(get_db),
):
    start, end = _date_range(start_date, end_date)
    ingreso_query = (
        db.query(IngresoItem.producto_id, func.coalesce(func.sum(IngresoItem.cantidad), 0))
        .join(IngresoInventario, IngresoInventario.id == IngresoItem.ingreso_id)
        .filter(IngresoInventario.fecha.between(start, end))
        .group_by(IngresoItem.producto_id)
    )
    egreso_query = (
        db.query(EgresoItem.producto_id, func.coalesce(func.sum(EgresoItem.cantidad), 0))
        .join(EgresoInventario, EgresoInventario.id == EgresoItem.egreso_id)
        .filter(EgresoInventario.fecha.between(start, end))
        .group_by(EgresoItem.producto_id)
    )
    if bodega_id:
        ingreso_query = ingreso_query.filter(IngresoInventario.bodega_id == bodega_id)
        egreso_query = egreso_query.filter(EgresoInventario.bodega_id == bodega_id)

    ingreso_map = {int(product_id): Decimal(str(qty or 0)) for product_id, qty in ingreso_query.all()}
    egreso_map = {int(product_id): Decimal(str(qty or 0)) for product_id, qty in egreso_query.all()}
    product_ids = set(ingreso_map) | set(egreso_map)
    products = {product.id: product for product in db.query(Producto).filter(Producto.id.in_(product_ids)).all()} if product_ids else {}
    rows = []
    for product_id in product_ids:
        product = products.get(product_id)
        if not product:
            continue
        entradas = ingreso_map.get(product_id, Decimal("0"))
        salidas = egreso_map.get(product_id, Decimal("0"))
        rows.append(
            {
                "cod_producto": product.cod_producto,
                "descripcion": product.descripcion,
                "entradas": _to_float(entradas),
                "salidas": _to_float(salidas),
                "movimiento_total": _to_float(entradas + salidas),
                "rotacion_neta": _to_float(salidas - entradas),
                "valor_salidas_cs": _to_float(salidas) * _to_float(product.costo_producto),
            }
        )
    return sorted(rows, key=lambda row: row["movimiento_total"], reverse=True)[:limit]


@router.get("/low-stock")
def low_stock_report(
    max_stock: float = Query(5, ge=0),
    bodega_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    products = db.query(Producto).filter(Producto.activo.is_(True)).order_by(Producto.descripcion).all()
    if bodega_id:
        balances = _balances_by_bodega(db, [bodega_id], [product.id for product in products])
    rows = []
    for product in products:
        existencia = balances.get((product.id, bodega_id), Decimal("0")) if bodega_id else Decimal(str(product.saldo.existencia if product.saldo else 0))
        if existencia < 0 or existencia > Decimal(str(max_stock)):
            continue
        rows.append(
            {
                "cod_producto": product.cod_producto,
                "descripcion": product.descripcion,
                "linea": product.linea.linea if product.linea else "",
                "existencia": _to_float(existencia),
                "costo_producto": _to_float(product.costo_producto),
                "valor_costo_cs": _to_float(existencia) * _to_float(product.costo_producto),
            }
        )
    return rows


@router.get("/no-stock")
def no_stock_report(db: Session = Depends(get_db)):
    rows = (
        db.query(Producto, SaldoProducto.existencia)
        .outerjoin(SaldoProducto, SaldoProducto.producto_id == Producto.id)
        .filter(Producto.activo.is_(True))
        .order_by(Producto.descripcion)
        .all()
    )
    return [
        {
            "cod_producto": product.cod_producto,
            "descripcion": product.descripcion,
            "linea": product.linea.linea if product.linea else "",
            "segmento": product.segmento.segmento if product.segmento else "",
            "existencia": _to_float(existencia),
            "precio_venta1": _to_float(product.precio_venta1),
        }
        for product, existencia in rows
        if Decimal(str(existencia or 0)) <= 0
    ]
