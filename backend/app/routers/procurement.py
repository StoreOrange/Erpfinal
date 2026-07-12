from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..core.email import send_html_email
from ..models.notification import EmailConfig, NotificationRecipient
from ..models.procurement import QuoteRequest, QuoteRequestLine, SupplierQuote, SupplyItem, SupplyMovement
from ..schemas.procurement import (
    EmailConfigBase,
    EmailConfigResponse,
    EmailSendResponse,
    NotificationRecipientCreate,
    NotificationRecipientResponse,
    NotificationRecipientUpdate,
    ProcurementSummaryResponse,
    QuoteRequestCreate,
    QuoteRequestLineResponse,
    QuoteRequestResponse,
    QuoteRequestUpdate,
    SupplierQuoteCreate,
    SupplierQuoteResponse,
    SupplyItemCreate,
    SupplyItemResponse,
    SupplyItemUpdate,
    SupplyMovementCreate,
    SupplyMovementResponse,
)

router = APIRouter(prefix="/procurement", tags=["Procurement"])


def _normalize(value: str | None, field: str) -> str:
    text = (value or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail=f"{field} es requerido")
    return text


def _next_supply_code(db: Session) -> str:
    count = db.query(func.count(SupplyItem.id)).scalar() or 0
    return f"INS-{count + 1:05d}"


def _next_request_number(db: Session) -> str:
    count = db.query(func.count(QuoteRequest.id)).scalar() or 0
    return f"COT-{count + 1:06d}"


def _movement_type(value: str) -> str:
    text = _normalize(value, "Tipo de movimiento").upper()
    if text not in {"INGRESO", "CONSUMO", "AJUSTE"}:
        raise HTTPException(status_code=400, detail="Tipo debe ser INGRESO, CONSUMO o AJUSTE")
    return text


def _supply_response(item: SupplyItem) -> SupplyItemResponse:
    return SupplyItemResponse.model_validate(item)


def _movement_response(movement: SupplyMovement) -> SupplyMovementResponse:
    return SupplyMovementResponse(
        id=movement.id,
        item_id=movement.item_id,
        fecha=movement.fecha,
        tipo=movement.tipo,
        quantity=movement.quantity,
        unit_cost=movement.unit_cost,
        total_cost=movement.total_cost,
        area=movement.area,
        requester=movement.requester,
        notes=movement.notes,
        item_name=movement.item.name if movement.item else None,
        item_code=movement.item.code if movement.item else None,
        created_at=movement.created_at,
    )


def _line_response(line: QuoteRequestLine) -> QuoteRequestLineResponse:
    return QuoteRequestLineResponse(
        id=line.id,
        supply_item_id=line.supply_item_id,
        description=line.description,
        unit=line.unit,
        quantity=line.quantity,
        estimated_unit_cost=line.estimated_unit_cost,
        preferred_supplier=line.preferred_supplier,
        supply_item_name=line.supply_item.name if line.supply_item else None,
    )


def _quote_response(quote: SupplierQuote) -> SupplierQuoteResponse:
    return SupplierQuoteResponse.model_validate(quote)


def _request_response(request: QuoteRequest) -> QuoteRequestResponse:
    return QuoteRequestResponse(
        id=request.id,
        number=request.number,
        fecha=request.fecha,
        needed_by=request.needed_by,
        requester=request.requester,
        department=request.department,
        purpose=request.purpose,
        status=request.status,
        notes=request.notes,
        lines=[_line_response(line) for line in request.lines],
        quotes=[_quote_response(quote) for quote in request.quotes],
        created_at=request.created_at,
    )


def _email_config_response(config: EmailConfig) -> EmailConfigResponse:
    return EmailConfigResponse.model_validate(config)


def _recipient_response(recipient: NotificationRecipient) -> NotificationRecipientResponse:
    return NotificationRecipientResponse.model_validate(recipient)


def _quote_request_email_html(request: QuoteRequest) -> str:
    line_rows = "".join(
        f"""
        <tr>
          <td style="padding:10px;border-bottom:1px solid #e5e7eb;">{line.description}</td>
          <td style="padding:10px;border-bottom:1px solid #e5e7eb;text-align:center;">{line.quantity}</td>
          <td style="padding:10px;border-bottom:1px solid #e5e7eb;text-align:center;">{line.unit}</td>
          <td style="padding:10px;border-bottom:1px solid #e5e7eb;">{line.preferred_supplier or ""}</td>
        </tr>
        """
        for line in request.lines
    )
    return f"""
    <!doctype html>
    <html lang="es">
    <body style="margin:0;background:#f6f7fb;font-family:Arial,Helvetica,sans-serif;color:#0f172a;">
      <div style="padding:28px 16px;">
        <div style="max-width:760px;margin:0 auto;background:#fff;border-radius:18px;overflow:hidden;border:1px solid #e5e7eb;">
          <div style="background:#0f172a;color:#fff;padding:24px 28px;">
            <div style="font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#bae6fd;">Solicitud de cotizacion</div>
            <h1 style="margin:10px 0 4px;font-size:26px;">{request.number}</h1>
            <div style="color:#cbd5e1;">{request.purpose}</div>
          </div>
          <div style="padding:24px 28px;">
            <p style="line-height:1.65;color:#475569;margin-top:0;">
              Se solicita cotizacion para los insumos indicados. Favor responder con precio, disponibilidad,
              tiempo de entrega y condiciones de pago.
            </p>
            <table width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;margin:18px 0;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;">
              <tr style="background:#f8fafc;">
                <th style="padding:10px;text-align:left;">Insumo / descripcion</th>
                <th style="padding:10px;text-align:center;">Cantidad</th>
                <th style="padding:10px;text-align:center;">Unidad</th>
                <th style="padding:10px;text-align:left;">Proveedor sugerido</th>
              </tr>
              {line_rows or '<tr><td colspan="4" style="padding:14px;">Sin lineas registradas.</td></tr>'}
            </table>
            <div style="display:grid;gap:8px;color:#475569;font-size:14px;">
              <div><strong>Solicitante:</strong> {request.requester}</div>
              <div><strong>Area:</strong> {request.department or "No indicada"}</div>
              <div><strong>Fecha:</strong> {request.fecha.strftime("%d/%m/%Y")}</div>
              <div><strong>Necesario para:</strong> {request.needed_by.strftime("%d/%m/%Y") if request.needed_by else "No indicado"}</div>
            </div>
          </div>
          <div style="padding:16px 28px;background:#f8fafc;color:#64748b;font-size:12px;">
            Este correo fue generado automaticamente por el modulo de compras operativas.
          </div>
        </div>
      </div>
    </body>
    </html>
    """


@router.get("/summary", response_model=ProcurementSummaryResponse)
def procurement_summary(db: Session = Depends(get_db)):
    supplies_count = db.query(func.count(SupplyItem.id)).filter(SupplyItem.active.is_(True)).scalar() or 0
    low_stock_count = (
        db.query(func.count(SupplyItem.id))
        .filter(SupplyItem.active.is_(True), SupplyItem.current_stock <= SupplyItem.min_stock)
        .scalar()
        or 0
    )
    requests_count = db.query(func.count(QuoteRequest.id)).scalar() or 0
    pending_requests_count = (
        db.query(func.count(QuoteRequest.id))
        .filter(QuoteRequest.status.in_(["BORRADOR", "SOLICITADA"]))
        .scalar()
        or 0
    )
    quoted_requests_count = (
        db.query(func.count(QuoteRequest.id))
        .filter(QuoteRequest.status.in_(["COTIZADA", "APROBADA"]))
        .scalar()
        or 0
    )
    total_quoted_cs = db.query(func.coalesce(func.sum(SupplierQuote.amount_cs), 0)).scalar() or Decimal("0")
    return ProcurementSummaryResponse(
        supplies_count=supplies_count,
        low_stock_count=low_stock_count,
        requests_count=requests_count,
        pending_requests_count=pending_requests_count,
        quoted_requests_count=quoted_requests_count,
        total_quoted_cs=total_quoted_cs,
    )


@router.get("/notifications/config", response_model=EmailConfigResponse | None)
def get_email_config(db: Session = Depends(get_db)):
    config = db.query(EmailConfig).first()
    return _email_config_response(config) if config else None


@router.put("/notifications/config", response_model=EmailConfigResponse)
def save_email_config(payload: EmailConfigBase, db: Session = Depends(get_db)):
    sender_email = _normalize(payload.sender_email, "Correo emisor").lower()
    config = db.query(EmailConfig).first()
    if not config:
        config = EmailConfig(sender_email=sender_email)
        db.add(config)
    config.sender_email = sender_email
    config.sender_name = (payload.sender_name or "").strip() or None
    config.active = bool(payload.active)
    db.commit()
    db.refresh(config)
    return _email_config_response(config)


@router.get("/notifications/recipients", response_model=list[NotificationRecipientResponse])
def list_notification_recipients(db: Session = Depends(get_db)):
    recipients = db.query(NotificationRecipient).order_by(NotificationRecipient.email).all()
    return [_recipient_response(recipient) for recipient in recipients]


@router.post("/notifications/recipients", response_model=NotificationRecipientResponse, status_code=status.HTTP_201_CREATED)
def create_notification_recipient(payload: NotificationRecipientCreate, db: Session = Depends(get_db)):
    email = _normalize(payload.email, "Correo").lower()
    if db.query(NotificationRecipient).filter(NotificationRecipient.email == email).first():
        raise HTTPException(status_code=400, detail="Correo ya registrado")
    recipient = NotificationRecipient(
        email=email,
        name=(payload.name or "").strip() or None,
        active=payload.active,
        procurement_quote_active=payload.procurement_quote_active,
    )
    db.add(recipient)
    db.commit()
    db.refresh(recipient)
    return _recipient_response(recipient)


@router.put("/notifications/recipients/{recipient_id}", response_model=NotificationRecipientResponse)
def update_notification_recipient(recipient_id: int, payload: NotificationRecipientUpdate, db: Session = Depends(get_db)):
    recipient = db.query(NotificationRecipient).filter(NotificationRecipient.id == recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Destinatario no encontrado")
    data = payload.model_dump(exclude_unset=True)
    if data.get("email") is not None:
        email = _normalize(data["email"], "Correo").lower()
        exists = db.query(NotificationRecipient).filter(NotificationRecipient.email == email, NotificationRecipient.id != recipient.id).first()
        if exists:
            raise HTTPException(status_code=400, detail="Correo ya registrado")
        recipient.email = email
    for field in ["name", "active", "procurement_quote_active"]:
        if field in data:
            setattr(recipient, field, data[field])
    db.add(recipient)
    db.commit()
    db.refresh(recipient)
    return _recipient_response(recipient)


@router.post("/quote-requests/{request_id}/send-email", response_model=EmailSendResponse)
def send_quote_request_email(request_id: int, db: Session = Depends(get_db)):
    request = (
        db.query(QuoteRequest)
        .options(joinedload(QuoteRequest.lines).joinedload(QuoteRequestLine.supply_item))
        .filter(QuoteRequest.id == request_id)
        .first()
    )
    if not request:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    config = db.query(EmailConfig).first()
    if not config or not config.active:
        raise HTTPException(status_code=400, detail="Configura y activa el correo emisor")
    recipients = [
        row.email
        for row in db.query(NotificationRecipient)
        .filter(NotificationRecipient.active.is_(True), NotificationRecipient.procurement_quote_active.is_(True))
        .order_by(NotificationRecipient.email)
        .all()
    ]
    error = send_html_email(
        recipients=recipients,
        subject=f"Solicitud de cotizacion {request.number}",
        html_body=_quote_request_email_html(request),
        sender_email=config.sender_email,
        sender_name=config.sender_name,
    )
    if error:
        raise HTTPException(status_code=400, detail=error)
    request.status = "ENVIADA"
    db.add(request)
    db.commit()
    return EmailSendResponse(ok=True, message="Correo enviado correctamente", recipients=recipients)


@router.get("/supplies", response_model=list[SupplyItemResponse])
def list_supplies(q: str = "", include_inactive: bool = False, db: Session = Depends(get_db)):
    query = db.query(SupplyItem).order_by(SupplyItem.name)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(or_(SupplyItem.code.ilike(like), SupplyItem.name.ilike(like), SupplyItem.category.ilike(like)))
    if not include_inactive:
        query = query.filter(SupplyItem.active.is_(True))
    return [_supply_response(item) for item in query.all()]


@router.post("/supplies", response_model=SupplyItemResponse, status_code=status.HTTP_201_CREATED)
def create_supply(payload: SupplyItemCreate, db: Session = Depends(get_db)):
    code = (payload.code or _next_supply_code(db)).strip().upper()
    if db.query(SupplyItem).filter(func.lower(SupplyItem.code) == code.lower()).first():
        raise HTTPException(status_code=400, detail="Codigo de insumo ya existe")
    item = SupplyItem(**payload.model_dump(exclude={"code"}), code=code, name=_normalize(payload.name, "Insumo"))
    db.add(item)
    db.commit()
    db.refresh(item)
    return _supply_response(item)


@router.put("/supplies/{item_id}", response_model=SupplyItemResponse)
def update_supply(item_id: int, payload: SupplyItemUpdate, db: Session = Depends(get_db)):
    item = db.query(SupplyItem).filter(SupplyItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    data = payload.model_dump(exclude_unset=True)
    if data.get("code") is not None:
        code = _normalize(data["code"], "Codigo").upper()
        exists = db.query(SupplyItem).filter(func.lower(SupplyItem.code) == code.lower(), SupplyItem.id != item.id).first()
        if exists:
            raise HTTPException(status_code=400, detail="Codigo de insumo ya existe")
        item.code = code
    for field in ["name", "category", "unit", "min_stock", "current_stock", "location", "notes", "active"]:
        if field in data:
            setattr(item, field, data[field])
    db.add(item)
    db.commit()
    db.refresh(item)
    return _supply_response(item)


@router.get("/movements", response_model=list[SupplyMovementResponse])
def list_movements(item_id: int | None = Query(None), db: Session = Depends(get_db)):
    query = db.query(SupplyMovement).options(joinedload(SupplyMovement.item)).order_by(SupplyMovement.fecha.desc(), SupplyMovement.id.desc())
    if item_id:
        query = query.filter(SupplyMovement.item_id == item_id)
    return [_movement_response(movement) for movement in query.limit(300).all()]


@router.post("/movements", response_model=SupplyMovementResponse, status_code=status.HTTP_201_CREATED)
def create_movement(payload: SupplyMovementCreate, db: Session = Depends(get_db)):
    item = db.query(SupplyItem).filter(SupplyItem.id == payload.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    tipo = _movement_type(payload.tipo)
    quantity = Decimal(str(payload.quantity or 0))
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a cero")
    unit_cost = Decimal(str(payload.unit_cost or 0))
    total_cost = quantity * unit_cost
    if tipo == "INGRESO":
        item.current_stock = Decimal(str(item.current_stock or 0)) + quantity
    elif tipo == "CONSUMO":
        current = Decimal(str(item.current_stock or 0))
        if current < quantity:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente. Disponible: {current}")
        item.current_stock = current - quantity
    else:
        item.current_stock = quantity
    movement = SupplyMovement(**payload.model_dump(exclude={"tipo", "unit_cost"}), tipo=tipo, unit_cost=unit_cost, total_cost=total_cost)
    db.add(item)
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return _movement_response(movement)


@router.get("/quote-requests", response_model=list[QuoteRequestResponse])
def list_quote_requests(status_filter: str = "", db: Session = Depends(get_db)):
    query = (
        db.query(QuoteRequest)
        .options(
            joinedload(QuoteRequest.lines).joinedload(QuoteRequestLine.supply_item),
            joinedload(QuoteRequest.quotes),
        )
        .order_by(QuoteRequest.fecha.desc(), QuoteRequest.id.desc())
    )
    if status_filter:
        query = query.filter(QuoteRequest.status == status_filter.strip().upper())
    return [_request_response(request) for request in query.all()]


@router.post("/quote-requests", response_model=QuoteRequestResponse, status_code=status.HTTP_201_CREATED)
def create_quote_request(payload: QuoteRequestCreate, db: Session = Depends(get_db)):
    request = QuoteRequest(
        number=_next_request_number(db),
        fecha=payload.fecha,
        needed_by=payload.needed_by,
        requester=_normalize(payload.requester, "Solicitante"),
        department=(payload.department or "").strip() or None,
        purpose=_normalize(payload.purpose, "Proposito"),
        status=(payload.status or "SOLICITADA").strip().upper(),
        notes=(payload.notes or "").strip() or None,
    )
    for line in payload.lines:
        request.lines.append(QuoteRequestLine(**line.model_dump(), description=_normalize(line.description, "Descripcion")))
    db.add(request)
    db.commit()
    db.refresh(request)
    return _request_response(request)


@router.put("/quote-requests/{request_id}", response_model=QuoteRequestResponse)
def update_quote_request(request_id: int, payload: QuoteRequestUpdate, db: Session = Depends(get_db)):
    request = (
        db.query(QuoteRequest)
        .options(joinedload(QuoteRequest.lines), joinedload(QuoteRequest.quotes))
        .filter(QuoteRequest.id == request_id)
        .first()
    )
    if not request:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    data = payload.model_dump(exclude_unset=True, exclude={"lines"})
    for field, value in data.items():
        setattr(request, field, value.strip().upper() if field == "status" and isinstance(value, str) else value)
    if payload.lines is not None:
        request.lines.clear()
        db.flush()
        for line in payload.lines:
            request.lines.append(QuoteRequestLine(**line.model_dump(), description=_normalize(line.description, "Descripcion")))
    db.add(request)
    db.commit()
    db.refresh(request)
    return _request_response(request)


@router.post("/quote-requests/{request_id}/quotes", response_model=SupplierQuoteResponse, status_code=status.HTTP_201_CREATED)
def add_supplier_quote(request_id: int, payload: SupplierQuoteCreate, db: Session = Depends(get_db)):
    request = db.query(QuoteRequest).filter(QuoteRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    quote_data = payload.model_dump()
    quote_data["supplier_name"] = _normalize(payload.supplier_name, "Proveedor")
    quote = SupplierQuote(request_id=request.id, **quote_data)
    if request.status in {"BORRADOR", "SOLICITADA"}:
        request.status = "COTIZADA"
    db.add(request)
    db.add(quote)
    db.commit()
    db.refresh(quote)
    return _quote_response(quote)
