from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, or_, text

from .config import settings as app_settings
from .core.security import hash_password
from .database import Base, SessionLocal, engine
from .models.inventory import Bodega, EgresoTipo, IngresoTipo, Linea, Marca, Producto, ProductoCombo, Proveedor, Segmento, UnidadMedida
from .models.notification import EmailConfig, NotificationRecipient
from .models.procurement import QuoteRequest, QuoteRequestLine, SupplierQuote, SupplyItem, SupplyMovement
from .models.sales import CashVoucher, Customer, SalesInvoice, SalesInvoiceItem, SalesPayment, SalesSequence
from .models.settings import BusinessSetting, CompanyEnvironment, ExchangeRate
from .models.user import Branch, Permission, Role, User, UserAccessProfile, Vendor
from .routers import access, auth, inventory, procurement, reports, sales, settings

# Archivo principal del backend.
# Aqui se crea la aplicacion FastAPI, se registran los routers y se preparan
# tablas/catalogos iniciales para que el sistema pueda arrancar completo.
app = FastAPI(title="Servidor del sistema de planificacion de recursos empresariales")
BACKEND_DIR = Path(__file__).resolve().parents[1]
UPLOADS_DIR = BACKEND_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


def ensure_cash_close_columns():
    inspector = inspect(engine)
    if "cash_closures" not in inspector.get_table_names():
        return
    existing_columns = {column["name"] for column in inspector.get_columns("cash_closures")}
    column_sql = {
        "detalle_cs": "TEXT",
        "detalle_usd": "TEXT",
        "total_efectivo_cs": "NUMERIC(14, 2) DEFAULT 0",
        "total_efectivo_usd": "NUMERIC(14, 2) DEFAULT 0",
        "tasa_cambio": "NUMERIC(12, 4)",
    }
    with engine.begin() as conn:
        for column_name, sql_type in column_sql.items():
            if column_name not in existing_columns:
                conn.execute(text(f"ALTER TABLE cash_closures ADD COLUMN {column_name} {sql_type}"))


ensure_cash_close_columns()


def ensure_cash_voucher_columns():
    inspector = inspect(engine)
    if "cash_vouchers" not in inspector.get_table_names():
        return
    existing_columns = {column["name"] for column in inspector.get_columns("cash_vouchers")}
    column_sql = {
        "status": "VARCHAR(20) DEFAULT 'EMITIDO'",
    }
    with engine.begin() as conn:
        for column_name, sql_type in column_sql.items():
            if column_name not in existing_columns:
                conn.execute(text(f"ALTER TABLE cash_vouchers ADD COLUMN {column_name} {sql_type}"))


ensure_cash_voucher_columns()


def ensure_notification_tables():
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS email_config (
                    id SERIAL PRIMARY KEY,
                    sender_email VARCHAR(160) NOT NULL DEFAULT '',
                    sender_name VARCHAR(160),
                    active BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW()
                )
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS email_recipients (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(160) UNIQUE NOT NULL,
                    name VARCHAR(160),
                    active BOOLEAN DEFAULT TRUE,
                    procurement_quote_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT NOW()
                )
                """
            )
        )
        connection.execute(text("ALTER TABLE email_recipients ADD COLUMN IF NOT EXISTS procurement_quote_active BOOLEAN DEFAULT TRUE"))


ensure_notification_tables()

app.include_router(auth.router)
app.include_router(access.router)
app.include_router(inventory.router)
app.include_router(procurement.router)
app.include_router(reports.router)
app.include_router(sales.router)
app.include_router(settings.router)
app.mount("/media", StaticFiles(directory=UPLOADS_DIR), name="media")

# Regla de seguridad: cada modulo nuevo debe registrar sus permisos aqui.
# El rol administrador siempre recibe el catalogo completo.
ACCESS_PERMISSION_GROUPS = [
    ("menu.dashboard", "administrador", "supervisor", "vendedor", "caja", "inventario"),
    ("menu.sales", "administrador", "supervisor", "vendedor", "caja"),
    ("menu.sales.checkout", "administrador", "supervisor", "vendedor", "caja"),
    ("menu.sales.cash_vouchers", "administrador", "supervisor", "caja"),
    ("menu.sales.cash_close", "administrador", "supervisor", "caja"),
    ("menu.sales.utilities", "administrador", "supervisor", "caja"),
    ("access.sales", "administrador", "supervisor", "vendedor", "caja"),
    ("access.sales.create_invoice", "administrador", "supervisor", "vendedor", "caja"),
    ("access.sales.cash_vouchers", "administrador", "supervisor", "caja"),
    ("access.sales.cash_close", "administrador", "supervisor", "caja"),
    ("access.sales.utilities", "administrador", "supervisor", "caja"),
    ("access.sales.invoice_reprint", "administrador", "supervisor", "caja"),
    ("access.sales.invoice_void", "administrador", "supervisor"),
    ("menu.inventory", "administrador", "supervisor", "inventario"),
    ("menu.inventory.products", "administrador", "supervisor", "inventario"),
    ("menu.inventory.movements", "administrador", "supervisor", "inventario"),
    ("menu.inventory.production", "administrador", "supervisor", "inventario"),
    ("menu.inventory.paca_opening", "administrador", "supervisor", "inventario"),
    ("access.inventory", "administrador", "supervisor", "inventario"),
    ("access.inventory.products", "administrador", "supervisor", "inventario"),
    ("access.inventory.movements", "administrador", "supervisor", "inventario"),
    ("access.inventory.production", "administrador", "supervisor", "inventario"),
    ("access.inventory.paca_opening", "administrador", "supervisor", "inventario"),
    ("menu.admin", "administrador", "supervisor"),
    ("menu.admin.users", "administrador", "supervisor"),
    ("menu.admin.settings", "administrador"),
    ("access.admin", "administrador", "supervisor"),
    ("access.admin.users", "administrador", "supervisor"),
    ("access.admin.roles", "administrador"),
    ("access.admin.permissions", "administrador"),
    ("access.admin.settings", "administrador"),
    ("menu.reports", "administrador", "supervisor"),
    ("menu.reports.sales", "administrador", "supervisor"),
    ("menu.reports.inventory", "administrador", "supervisor", "inventario"),
    ("menu.reports.cash", "administrador", "supervisor", "caja"),
    ("menu.reports.analysis", "administrador", "supervisor", "inventario"),
    ("access.reports", "administrador", "supervisor"),
    ("access.reports.sales", "administrador", "supervisor"),
    ("access.reports.inventory", "administrador", "supervisor", "inventario"),
    ("access.reports.cash", "administrador", "supervisor", "caja"),
    ("access.reports.analysis", "administrador", "supervisor", "inventario"),
    ("menu.procurement", "administrador", "supervisor"),
    ("menu.procurement.supplies", "administrador", "supervisor"),
    ("menu.procurement.quotes", "administrador", "supervisor"),
    ("menu.procurement.notifications", "administrador", "supervisor"),
    ("access.procurement", "administrador", "supervisor"),
    ("access.procurement.supplies", "administrador", "supervisor"),
    ("access.procurement.quotes", "administrador", "supervisor"),
    ("access.procurement.notifications", "administrador", "supervisor"),
]


def catalog_permission_names() -> list[str]:
    return [permission_name for permission_name, *_role_names in ACCESS_PERMISSION_GROUPS]


@app.get("/")
def root():
    return {"message": "API del sistema empresarial lista"}


@app.get("/sales", include_in_schema=False)
def sales_entry():
    return RedirectResponse(url=f"{app_settings.FRONTEND_URL}/app/sales", status_code=307)


@app.get("/sales/", include_in_schema=False)
def sales_entry_slash():
    return RedirectResponse(url=f"{app_settings.FRONTEND_URL}/app/sales", status_code=307)


def create_initial_admin():
    db = SessionLocal()
    admin_email = "administrador"
    admin_password = "020416"
    admin_name = "Administrador"

    try:
        admin_role = db.query(Role).filter(Role.name == "administrador").first()
        if not admin_role:
            admin_role = Role(name="administrador")
            db.add(admin_role)
            db.flush()

        existing = (
            db.query(User)
            .filter(
                or_(
                    User.email == admin_email,
                    User.email == "admin@erp.com",
                    User.full_name == admin_name,
                )
            )
            .first()
        )

        if not existing:
            existing = User(
                full_name=admin_name,
                email=admin_email,
                hashed_password=hash_password(admin_password),
                is_active=True,
            )
            db.add(existing)
            db.flush()
        else:
            existing.full_name = admin_name
            existing.email = admin_email
            existing.hashed_password = hash_password(admin_password)
            existing.is_active = True

        if admin_role not in existing.roles:
            existing.roles.append(admin_role)

        db.commit()
        db.refresh(existing)
        print(">>> Usuario admin listo (administrador / 020416)")
    finally:
        db.close()


def seed_inventory_catalogs():
    db = SessionLocal()
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS sucursales (
                        id SERIAL PRIMARY KEY,
                        code VARCHAR(40) UNIQUE NOT NULL,
                        name VARCHAR(140) NOT NULL,
                        address VARCHAR(220),
                        phone VARCHAR(80),
                        activo BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                    """
                )
            )
            connection.execute(
                text(
                    """
                    ALTER TABLE bodegas
                    ADD COLUMN IF NOT EXISTS sucursal_id INTEGER REFERENCES sucursales(id)
                    """
                )
            )
            connection.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS user_access_profiles (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        sucursal_id INTEGER REFERENCES sucursales(id),
                        bodega_id INTEGER REFERENCES bodegas(id),
                        role_scope VARCHAR(50) NOT NULL DEFAULT 'VENDEDOR',
                        can_sell BOOLEAN DEFAULT TRUE,
                        can_move_inventory BOOLEAN DEFAULT FALSE,
                        can_manage_catalogs BOOLEAN DEFAULT FALSE,
                        is_default BOOLEAN DEFAULT FALSE,
                        activo BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                    """
                )
            )
            connection.execute(
                text(
                    """
                    CREATE UNIQUE INDEX IF NOT EXISTS uq_user_access_scope_idx
                    ON user_access_profiles (
                        user_id,
                        COALESCE(sucursal_id, 0),
                        COALESCE(bodega_id, 0)
                    )
                    """
                )
            )
            connection.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS vendedores (
                        id SERIAL PRIMARY KEY,
                        code VARCHAR(40) UNIQUE NOT NULL,
                        nombre VARCHAR(160) NOT NULL,
                        user_id INTEGER UNIQUE REFERENCES users(id),
                        sucursal_id INTEGER REFERENCES sucursales(id),
                        bodega_id INTEGER REFERENCES bodegas(id),
                        telefono VARCHAR(80),
                        email VARCHAR(140),
                        meta_ventas INTEGER,
                        activo BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                    """
                )
            )
            connection.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS marcas (
                        id SERIAL PRIMARY KEY,
                        nombre VARCHAR(120) UNIQUE NOT NULL,
                        activo BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                    """
                )
            )
            connection.execute(
                text(
                    """
                    ALTER TABLE productos
                    ADD COLUMN IF NOT EXISTS marca_id INTEGER REFERENCES marcas(id)
                    """
                )
            )
            connection.execute(
                text(
                    """
                    ALTER TABLE productos
                    ADD COLUMN IF NOT EXISTS usa_codigo_barra BOOLEAN DEFAULT FALSE
                    """
                )
            )
            connection.execute(
                text(
                    """
                    ALTER TABLE productos
                    ADD COLUMN IF NOT EXISTS codigo_barra VARCHAR(120)
                    """
                )
            )
            connection.execute(
                text(
                    """
                    ALTER TABLE productos
                    ADD COLUMN IF NOT EXISTS tipo_producto VARCHAR(30) DEFAULT 'DIRECTO'
                    """
                )
            )
            connection.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS producto_combos (
                        id SERIAL PRIMARY KEY,
                        parent_producto_id INTEGER NOT NULL REFERENCES productos(id),
                        child_producto_id INTEGER NOT NULL REFERENCES productos(id),
                        cantidad NUMERIC(12, 2) DEFAULT 1,
                        activo BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                    """
                )
            )
            connection.execute(
                text(
                    """
                    CREATE UNIQUE INDEX IF NOT EXISTS uq_producto_combo_child_idx
                    ON producto_combos (parent_producto_id, child_producto_id)
                    """
                )
            )
            connection.execute(
                text(
                    """
                    ALTER TABLE sales_invoice_items
                    ADD COLUMN IF NOT EXISTS combo_role VARCHAR(20)
                    """
                )
            )
            connection.execute(
                text(
                    """
                    ALTER TABLE sales_invoice_items
                    ADD COLUMN IF NOT EXISTS combo_group VARCHAR(60)
                    """
                )
            )
            connection.execute(
                text(
                    """
                    ALTER TABLE paca_aperturas
                    ADD COLUMN IF NOT EXISTS bodega_destino_id INTEGER REFERENCES bodegas(id)
                    """
                )
            )
            connection.execute(
                text(
                    """
                    CREATE UNIQUE INDEX IF NOT EXISTS ix_productos_codigo_barra
                    ON productos (codigo_barra)
                    WHERE codigo_barra IS NOT NULL
                    """
                )
            )

        default_branch = db.query(Branch).filter(Branch.code == "SUC-001").first()
        if not default_branch:
            default_branch = Branch(code="SUC-001", name="Sucursal Principal", activo=True)
            db.add(default_branch)
            db.flush()

        if not db.query(Bodega).first():
            db.add(Bodega(code="BOD-001", name="Bodega Principal", sucursal_id=default_branch.id, activo=True))
            db.flush()

        db.query(Bodega).filter(Bodega.sucursal_id.is_(None)).update({Bodega.sucursal_id: default_branch.id})

        default_lineas = [
            ("LIN-001", "General"),
        ]
        for cod_linea, linea in default_lineas:
            exists = db.query(Linea).filter(Linea.cod_linea == cod_linea).first()
            if not exists:
                db.add(Linea(cod_linea=cod_linea, linea=linea, activo=True))

        default_segmentos = ["General"]
        for nombre in default_segmentos:
            exists = db.query(Segmento).filter(Segmento.segmento == nombre).first()
            if not exists:
                db.add(Segmento(segmento=nombre, activo=True))

        default_units = [
            ("UND", "Unidad", "Und"),
            ("CJ", "Caja", "Cj"),
            ("LB", "Libra", "Lb"),
        ]
        for codigo, nombre, abreviatura in default_units:
            exists = (
                db.query(UnidadMedida)
                .filter(or_(UnidadMedida.codigo == codigo, UnidadMedida.nombre == nombre))
                .first()
            )
            if not exists:
                db.add(UnidadMedida(codigo=codigo, nombre=nombre, abreviatura=abreviatura, activo=True))
            else:
                exists.codigo = codigo
                exists.nombre = nombre
                exists.abreviatura = abreviatura
                exists.activo = True

        existing_product_brands = (
            db.query(Producto.marca)
            .filter(Producto.marca.isnot(None), Producto.marca != "")
            .distinct()
            .all()
        )
        for (brand_name,) in existing_product_brands:
            normalized = (brand_name or "").strip()
            if not normalized:
                continue
            brand = db.query(Marca).filter(Marca.nombre == normalized).first()
            if not brand:
                db.add(Marca(nombre=normalized, activo=True))

        db.flush()

        for product in db.query(Producto).filter(Producto.marca_id.is_(None), Producto.marca.isnot(None), Producto.marca != "").all():
            normalized = (product.marca or "").strip()
            if not normalized:
                continue
            brand = db.query(Marca).filter(Marca.nombre == normalized).first()
            if brand:
                product.marca_id = brand.id

        default_ingresos = [
            ("Inventario Inicial", False),
            ("Compras Locales", True),
            ("Importacion", True),
            ("Ajustes de Inventario", False),
            ("Produccion", False),
            ("Apertura de Pacas", False),
            ("Clasificacion de mermas", False),
            ("Perdidas", False),
        ]
        for nombre, requiere_proveedor in default_ingresos:
            exists = db.query(IngresoTipo).filter(IngresoTipo.nombre == nombre).first()
            if not exists:
                db.add(IngresoTipo(nombre=nombre, requiere_proveedor=requiere_proveedor))

        default_egresos = [
            "Venta",
            "Inventario Fisico",
            "Traslado entre bodegas",
            "Merma",
            "Perdida",
            "Reposicion a Cliente",
            "Produccion por receta",
            "Produccion de Abierta",
            "Produccion embalaje",
            "Produccion perdida",
            "Ajuste por Faltante",
        ]
        for nombre in default_egresos:
            exists = db.query(EgresoTipo).filter(EgresoTipo.nombre == nombre).first()
            if not exists:
                db.add(EgresoTipo(nombre=nombre))

        default_proveedores = [
            ("Proveedor Local", "LOCAL"),
            ("Proveedor Extranjero", "EXTRANJERO"),
        ]
        for nombre, tipo in default_proveedores:
            exists = db.query(Proveedor).filter(Proveedor.nombre == nombre).first()
            if not exists:
                db.add(Proveedor(nombre=nombre, tipo=tipo, activo=True))

        db.commit()
    finally:
        db.close()


def seed_business_settings():
    db = SessionLocal()
    try:
        with engine.begin() as connection:
            for statement in [
                "ALTER TABLE business_settings ADD COLUMN IF NOT EXISTS legal_name VARCHAR(180)",
                "ALTER TABLE business_settings ADD COLUMN IF NOT EXISTS trade_name VARCHAR(180)",
                "ALTER TABLE business_settings ADD COLUMN IF NOT EXISTS app_title VARCHAR(180)",
                "ALTER TABLE business_settings ADD COLUMN IF NOT EXISTS sidebar_subtitle VARCHAR(200)",
                "ALTER TABLE business_settings ADD COLUMN IF NOT EXISTS phone VARCHAR(80)",
                "ALTER TABLE business_settings ADD COLUMN IF NOT EXISTS email VARCHAR(180)",
                "ALTER TABLE business_settings ADD COLUMN IF NOT EXISTS theme_code VARCHAR(60) DEFAULT 'default'",
                "ALTER TABLE business_settings ADD COLUMN IF NOT EXISTS sales_interface_code VARCHAR(60) DEFAULT 'ecommerce'",
                "ALTER TABLE business_settings ADD COLUMN IF NOT EXISTS pricing_currency VARCHAR(10) DEFAULT 'CS'",
                "ALTER TABLE business_settings ADD COLUMN IF NOT EXISTS inventory_cs_only BOOLEAN DEFAULT FALSE",
                "ALTER TABLE business_settings ADD COLUMN IF NOT EXISTS weighted_inventory_enabled BOOLEAN DEFAULT FALSE",
                "ALTER TABLE business_settings ADD COLUMN IF NOT EXISTS weighted_sales_enabled BOOLEAN DEFAULT FALSE",
                "ALTER TABLE business_settings ADD COLUMN IF NOT EXISTS recipe_explosion_on_ingreso BOOLEAN DEFAULT FALSE",
                "ALTER TABLE business_settings ADD COLUMN IF NOT EXISTS multi_branch_enabled BOOLEAN DEFAULT FALSE",
                "ALTER TABLE business_settings ADD COLUMN IF NOT EXISTS price_auto_from_cost_enabled BOOLEAN DEFAULT FALSE",
                "ALTER TABLE business_settings ADD COLUMN IF NOT EXISTS price_margin_percent INTEGER DEFAULT 0",
            ]:
                connection.execute(text(statement))

        settings = db.query(BusinessSetting).first()
        if not settings:
            db.add(
                BusinessSetting(
                    business_name="Orange Tec",
                    legal_name="Orange Tec",
                    trade_name="Orange Tec",
                    app_title="Orange Tec Sistema empresarial",
                    sidebar_subtitle="Sistema empresarial",
                    address="",
                    ruc="",
                    phone="",
                    phones="",
                    email="",
                    website="",
                    theme_code="default",
                    sales_interface_code="ecommerce",
                    pricing_currency="CS",
                )
            )
            db.commit()
            settings = db.query(BusinessSetting).first()
        if settings:
            legacy_interface_map = {
                "sales_ropa": "ecommerce",
                "sales_zapatos": "ecommerce",
                "sales_restaurante": "supermarket",
                "sales_comestibles": "supermarket",
                "sales_utilitario": "ecommerce",
                "sales_roc": "ecommerce",
                "ropa": "ecommerce",
                "zapatos": "ecommerce",
                "restaurante": "supermarket",
                "comestibles": "supermarket",
                "ferreteria": "hardware",
            }
            settings.trade_name = settings.trade_name or settings.business_name or "Orange Tec"
            settings.legal_name = settings.legal_name or settings.trade_name
            settings.app_title = settings.app_title or f"{settings.trade_name} Sistema empresarial"
            settings.sidebar_subtitle = settings.sidebar_subtitle or "Sistema empresarial"
            settings.theme_code = settings.theme_code or "default"
            normalized_sales_interface = (settings.sales_interface_code or "ecommerce").strip().lower() or "ecommerce"
            normalized_sales_interface = legacy_interface_map.get(normalized_sales_interface, normalized_sales_interface)
            if normalized_sales_interface not in {"ecommerce", "supermarket", "hardware"}:
                normalized_sales_interface = "ecommerce"
            settings.sales_interface_code = normalized_sales_interface
            settings.pricing_currency = (settings.pricing_currency or "CS").upper()
            if settings.pricing_currency not in {"CS", "USD"}:
                settings.pricing_currency = "CS"
            settings.phone = settings.phone or ""
            settings.email = settings.email or ""
            db.add(settings)
            db.commit()

        if not db.query(CompanyEnvironment).first():
            db.add(
                CompanyEnvironment(
                    company_key="principal",
                    company_name=(settings.trade_name if settings else "Orange Tec"),
                    database_url=str(engine.url),
                    is_active=True,
                )
            )
            db.commit()
    finally:
        db.close()


def seed_access_catalogs():
    db = SessionLocal()
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS permissions (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(80) UNIQUE NOT NULL
                    )
                    """
                )
            )
            connection.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS role_permissions (
                        role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
                        permission_id INTEGER REFERENCES permissions(id) ON DELETE CASCADE,
                        PRIMARY KEY (role_id, permission_id)
                    )
                    """
                )
            )
            connection.execute(
                text(
                    """
                    CREATE UNIQUE INDEX IF NOT EXISTS uq_role_permissions_idx
                    ON role_permissions (role_id, permission_id)
                    """
                )
            )

        role_names = ["administrador", "vendedor", "caja", "inventario", "supervisor"]
        roles = {}
        for role_name in role_names:
            role = db.query(Role).filter(Role.name == role_name).first()
            if not role:
                role = Role(name=role_name)
                db.add(role)
                db.flush()
            roles[role_name] = role

        permissions = {}
        for permission_name in catalog_permission_names():
            permission = db.query(Permission).filter(Permission.name == permission_name).first()
            if not permission:
                permission = Permission(name=permission_name)
                db.add(permission)
                db.flush()
            permissions[permission_name] = permission

        for permission_name, *allowed_roles in ACCESS_PERMISSION_GROUPS:
            permission = permissions[permission_name]
            for role_name in allowed_roles:
                role = roles.get(role_name)
                if role and permission not in role.permissions:
                    role.permissions.append(permission)

        roles["administrador"].permissions = [permissions[name] for name in catalog_permission_names()]

        admin = db.query(User).filter(User.email == "administrador").first()
        branch = db.query(Branch).filter(Branch.code == "SUC-001").first()
        bodega = db.query(Bodega).order_by(Bodega.id).first()
        if admin:
            if roles["administrador"] not in admin.roles:
                admin.roles.append(roles["administrador"])
            if branch and bodega:
                access_profile = (
                    db.query(UserAccessProfile)
                    .filter(
                        UserAccessProfile.user_id == admin.id,
                        UserAccessProfile.sucursal_id == branch.id,
                        UserAccessProfile.bodega_id == bodega.id,
                    )
                    .first()
                )
                if not access_profile:
                    db.add(
                        UserAccessProfile(
                            user_id=admin.id,
                            sucursal_id=branch.id,
                            bodega_id=bodega.id,
                            role_scope="ADMINISTRADOR",
                            can_sell=True,
                            can_move_inventory=True,
                            can_manage_catalogs=True,
                            is_default=True,
                            activo=True,
                        )
                    )
            vendor = db.query(Vendor).filter(Vendor.code == "VEN-001").first()
            if not vendor:
                db.add(
                    Vendor(
                        code="VEN-001",
                        nombre=admin.full_name or "Administrador",
                        user_id=admin.id,
                        sucursal_id=branch.id if branch else None,
                        bodega_id=bodega.id if bodega else None,
                        email=admin.email,
                        activo=True,
                    )
                )
            floor_vendor = db.query(Vendor).filter(Vendor.code == "VEN-PISO").first()
            if not floor_vendor:
                db.add(
                    Vendor(
                        code="VEN-PISO",
                        nombre="Vendedor de piso",
                        user_id=None,
                        sucursal_id=branch.id if branch else None,
                        bodega_id=bodega.id if bodega else None,
                        email=None,
                        activo=True,
                    )
                )
        db.commit()
    finally:
        db.close()


create_initial_admin()
seed_inventory_catalogs()
seed_business_settings()
seed_access_catalogs()
