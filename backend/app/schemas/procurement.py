from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SupplyItemBase(BaseModel):
    code: Optional[str] = None
    name: str
    category: Optional[str] = None
    unit: str = "Unidad"
    min_stock: Decimal = Field(default=Decimal("0"))
    current_stock: Decimal = Field(default=Decimal("0"))
    location: Optional[str] = None
    notes: Optional[str] = None
    active: bool = True


class SupplyItemCreate(SupplyItemBase):
    pass


class SupplyItemUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    min_stock: Optional[Decimal] = None
    current_stock: Optional[Decimal] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    active: Optional[bool] = None


class SupplyItemResponse(SupplyItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None


class SupplyMovementBase(BaseModel):
    item_id: int
    fecha: date
    tipo: str
    quantity: Decimal = Field(default=Decimal("0"))
    unit_cost: Decimal = Field(default=Decimal("0"))
    area: Optional[str] = None
    requester: Optional[str] = None
    notes: Optional[str] = None


class SupplyMovementCreate(SupplyMovementBase):
    pass


class SupplyMovementResponse(SupplyMovementBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    total_cost: Decimal = Field(default=Decimal("0"))
    item_name: Optional[str] = None
    item_code: Optional[str] = None
    created_at: Optional[datetime] = None


class QuoteRequestLineBase(BaseModel):
    supply_item_id: Optional[int] = None
    description: str
    unit: str = "Unidad"
    quantity: Decimal = Field(default=Decimal("1"))
    estimated_unit_cost: Decimal = Field(default=Decimal("0"))
    preferred_supplier: Optional[str] = None


class QuoteRequestLineCreate(QuoteRequestLineBase):
    pass


class QuoteRequestLineResponse(QuoteRequestLineBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    supply_item_name: Optional[str] = None


class SupplierQuoteBase(BaseModel):
    supplier_name: str
    contact: Optional[str] = None
    amount_cs: Decimal = Field(default=Decimal("0"))
    delivery_days: Optional[int] = None
    payment_terms: Optional[str] = None
    status: str = "RECIBIDA"
    notes: Optional[str] = None


class SupplierQuoteCreate(SupplierQuoteBase):
    pass


class SupplierQuoteResponse(SupplierQuoteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    request_id: int
    created_at: Optional[datetime] = None


class QuoteRequestBase(BaseModel):
    fecha: date
    needed_by: Optional[date] = None
    requester: str
    department: Optional[str] = None
    purpose: str
    status: str = "SOLICITADA"
    notes: Optional[str] = None


class QuoteRequestCreate(QuoteRequestBase):
    lines: List[QuoteRequestLineCreate] = []


class QuoteRequestUpdate(BaseModel):
    fecha: Optional[date] = None
    needed_by: Optional[date] = None
    requester: Optional[str] = None
    department: Optional[str] = None
    purpose: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    lines: Optional[List[QuoteRequestLineCreate]] = None


class QuoteRequestResponse(QuoteRequestBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    number: str
    lines: List[QuoteRequestLineResponse] = []
    quotes: List[SupplierQuoteResponse] = []
    created_at: Optional[datetime] = None


class ProcurementSummaryResponse(BaseModel):
    supplies_count: int
    low_stock_count: int
    requests_count: int
    pending_requests_count: int
    quoted_requests_count: int
    total_quoted_cs: Decimal


class EmailConfigBase(BaseModel):
    sender_email: str
    sender_name: Optional[str] = None
    active: bool = False


class EmailConfigResponse(EmailConfigBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None


class NotificationRecipientBase(BaseModel):
    email: str
    name: Optional[str] = None
    active: bool = True
    procurement_quote_active: bool = True


class NotificationRecipientCreate(NotificationRecipientBase):
    pass


class NotificationRecipientUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    active: Optional[bool] = None
    procurement_quote_active: Optional[bool] = None


class NotificationRecipientResponse(NotificationRecipientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None


class EmailSendResponse(BaseModel):
    ok: bool
    message: str
    recipients: List[str] = []
