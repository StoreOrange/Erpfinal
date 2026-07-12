"""Modelos de configuracion del sistema.

Hecho por Carlos.
Colaboracion academica: Oded Garcia y Carlos Ramirez.

Aqui se guardan datos generales de empresa, entornos y tasa de cambio. Son
datos base que afectan varias pantallas del ERP.
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, Integer, Numeric, String, Text

from ..database import Base


class BusinessSetting(Base):
    __tablename__ = "business_settings"

    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String(160), nullable=False, default="Orange Tec")
    legal_name = Column(String(180), nullable=True)
    trade_name = Column(String(180), nullable=True)
    app_title = Column(String(180), nullable=True)
    sidebar_subtitle = Column(String(200), nullable=True)
    address = Column(Text, nullable=True)
    ruc = Column(String(80), nullable=True)
    phone = Column(String(80), nullable=True)
    phones = Column(String(200), nullable=True)
    email = Column(String(180), nullable=True)
    website = Column(String(200), nullable=True)
    theme_code = Column(String(60), nullable=True, default="default")
    sales_interface_code = Column(String(60), nullable=True, default="ropa")
    pricing_currency = Column(String(10), nullable=False, default="CS")
    logo_login = Column(String(255), nullable=True)
    logo_sidebar = Column(String(255), nullable=True)
    logo_invoice = Column(String(255), nullable=True)
    logo_favicon = Column(String(255), nullable=True)
    inventory_cs_only = Column(Boolean, nullable=False, default=False)
    weighted_inventory_enabled = Column(Boolean, nullable=False, default=False)
    weighted_sales_enabled = Column(Boolean, nullable=False, default=False)
    recipe_explosion_on_ingreso = Column(Boolean, nullable=False, default=False)
    multi_branch_enabled = Column(Boolean, nullable=False, default=False)
    price_auto_from_cost_enabled = Column(Boolean, nullable=False, default=False)
    price_margin_percent = Column(Integer, nullable=False, default=0)


class CompanyEnvironment(Base):
    __tablename__ = "company_environments"

    id = Column(Integer, primary_key=True, index=True)
    company_key = Column(String(80), unique=True, nullable=False)
    company_name = Column(String(180), nullable=False)
    database_url = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, index=True)
    effective_date = Column(Date, nullable=False, index=True)
    period_type = Column(String(20), nullable=False, default="daily")
    rate = Column(Numeric(12, 4), nullable=False)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
