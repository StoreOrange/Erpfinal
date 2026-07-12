from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from ..core.security import hash_password
from ..database import get_db
from ..models.inventory import Bodega
from ..models.user import Branch, Permission, Role, User, UserAccessProfile, Vendor
from ..schemas.user import (
    BranchCreate,
    BranchResponse,
    BranchUpdate,
    PermissionGroupResponse,
    PermissionResponse,
    RoleCreate,
    RoleResponse,
    RoleUpdate,
    UserAccessProfileCreate,
    UserAccessProfileResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
    VendorCreate,
    VendorResponse,
    VendorUpdate,
)

router = APIRouter(prefix="/access", tags=["Access Management"])

# Regla de seguridad: cada modulo/ruta nueva debe registrar sus permisos aqui.
# El rol administrador siempre se sincroniza con el catalogo completo.
PERMISSION_GROUPS = [
    {
        "key": "inicio",
        "label": "Inicio",
        "permissions": [
            ("menu.dashboard", "Ver inicio"),
        ],
    },
    {
        "key": "ventas",
        "label": "Ventas y facturacion",
        "permissions": [
            ("menu.sales", "Ver modulo de ventas"),
            ("menu.sales.checkout", "Acceso a punto de venta"),
            ("menu.sales.cash_vouchers", "Vales de caja"),
            ("menu.sales.cash_close", "Cierre de caja"),
            ("menu.sales.utilities", "Utilidades de facturacion"),
            ("access.sales", "Operar ventas"),
            ("access.sales.create_invoice", "Crear facturas"),
            ("access.sales.cash_vouchers", "Crear y editar vales"),
            ("access.sales.cash_close", "Registrar cierres"),
            ("access.sales.utilities", "Usar utilidades de facturacion"),
            ("access.sales.invoice_reprint", "Reimprimir facturas"),
            ("access.sales.invoice_void", "Anular facturas"),
        ],
    },
    {
        "key": "inventario",
        "label": "Inventario",
        "permissions": [
            ("menu.inventory", "Ver modulo de inventario"),
            ("menu.inventory.products", "Productos"),
            ("menu.inventory.movements", "Ingresos y egresos"),
            ("menu.inventory.production", "Produccion"),
            ("menu.inventory.paca_opening", "Apertura de pacas"),
            ("access.inventory", "Operar inventario"),
            ("access.inventory.products", "Crear y editar productos"),
            ("access.inventory.movements", "Registrar movimientos"),
            ("access.inventory.production", "Registrar produccion"),
            ("access.inventory.paca_opening", "Abrir pacas"),
        ],
    },
    {
        "key": "administracion",
        "label": "Administracion",
        "permissions": [
            ("menu.admin", "Ver administracion"),
            ("menu.admin.users", "Usuarios y permisos"),
            ("menu.admin.settings", "Configuracion"),
            ("access.admin", "Operar administracion"),
            ("access.admin.users", "Crear y editar usuarios"),
            ("access.admin.roles", "Crear y editar roles"),
            ("access.admin.permissions", "Asignar permisos"),
            ("access.admin.settings", "Editar configuracion"),
        ],
    },
    {
        "key": "informes",
        "label": "Informes",
        "permissions": [
            ("menu.reports", "Ver modulo de informes"),
            ("menu.reports.sales", "Informes de ventas"),
            ("menu.reports.inventory", "Informes de inventario"),
            ("menu.reports.cash", "Informes de caja"),
            ("menu.reports.analysis", "Analisis especial"),
            ("access.reports", "Consultar informes"),
            ("access.reports.sales", "Consultar informes de ventas"),
            ("access.reports.inventory", "Consultar informes de inventario"),
            ("access.reports.cash", "Consultar informes de caja"),
            ("access.reports.analysis", "Consultar analisis especial"),
        ],
    },
    {
        "key": "compras",
        "label": "Compras operativas",
        "permissions": [
            ("menu.procurement", "Ver modulo de compras"),
            ("menu.procurement.supplies", "Inventario de insumos"),
            ("menu.procurement.quotes", "Solicitudes de cotizacion"),
            ("menu.procurement.notifications", "Notificaciones por correo"),
            ("access.procurement", "Operar compras"),
            ("access.procurement.supplies", "Crear y mover insumos"),
            ("access.procurement.quotes", "Crear y gestionar cotizaciones"),
            ("access.procurement.notifications", "Configurar correos de compras"),
        ],
    },
]

PERMISSION_LABELS = {
    name: label
    for group in PERMISSION_GROUPS
    for name, label in group["permissions"]
}
PERMISSION_GROUP_BY_NAME = {
    name: group["key"]
    for group in PERMISSION_GROUPS
    for name, _label in group["permissions"]
}


def _catalog_permission_names() -> list[str]:
    return [name for group in PERMISSION_GROUPS for name, _label in group["permissions"]]


def _normalize(value: str | None, field: str) -> str:
    text = (value or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail=f"{field} es requerido")
    return text


def _role_names_for_scope(scope: str) -> list[str]:
    normalized = (scope or "VENDEDOR").strip().lower()
    if "admin" in normalized:
        return ["administrador"]
    if "inventario" in normalized:
        return ["inventario"]
    if "caja" in normalized:
        return ["caja"]
    return ["vendedor"]


def _get_or_create_roles(db: Session, names: list[str]) -> list[Role]:
    roles: list[Role] = []
    for name in names:
        clean = _normalize(name, "Rol").lower()
        role = db.query(Role).filter(func.lower(Role.name) == clean).first()
        if not role:
            role = Role(name=clean)
            db.add(role)
            db.flush()
        roles.append(role)
    return roles


def _get_or_create_permissions(db: Session, names: list[str]) -> list[Permission]:
    permissions: list[Permission] = []
    for name in names:
        clean = _normalize(name, "Permiso")
        permission = db.query(Permission).filter(Permission.name == clean).first()
        if not permission:
            permission = Permission(name=clean)
            db.add(permission)
            db.flush()
        permissions.append(permission)
    return permissions


def _sync_admin_full_access(db: Session) -> None:
    admin_role = db.query(Role).filter(func.lower(Role.name) == "administrador").first()
    if not admin_role:
        admin_role = Role(name="administrador")
        db.add(admin_role)
        db.flush()
    admin_role.permissions = _get_or_create_permissions(db, _catalog_permission_names())


def _permission_response(permission: Permission) -> PermissionResponse:
    return PermissionResponse(
        id=permission.id,
        name=permission.name,
        label=PERMISSION_LABELS.get(permission.name, permission.name),
        group=PERMISSION_GROUP_BY_NAME.get(permission.name, "otros"),
    )


def _role_response(role: Role) -> RoleResponse:
    return RoleResponse(
        id=role.id,
        name=role.name,
        permissions=[_permission_response(permission) for permission in sorted(role.permissions, key=lambda item: item.name)],
    )


def _ensure_branch(db: Session, branch_id: int | None) -> Branch | None:
    if not branch_id:
        return None
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    return branch


def _ensure_bodega(db: Session, bodega_id: int | None) -> Bodega | None:
    if not bodega_id:
        return None
    bodega = db.query(Bodega).filter(Bodega.id == bodega_id).first()
    if not bodega:
        raise HTTPException(status_code=404, detail="Bodega no encontrada")
    return bodega


def _user_response(user: User) -> UserResponse:
    access_profiles = [
        UserAccessProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            sucursal_id=profile.sucursal_id,
            bodega_id=profile.bodega_id,
            role_scope=profile.role_scope,
            can_sell=bool(profile.can_sell),
            can_move_inventory=bool(profile.can_move_inventory),
            can_manage_catalogs=bool(profile.can_manage_catalogs),
            is_default=bool(profile.is_default),
            activo=bool(profile.activo),
            sucursal_name=profile.sucursal.name if profile.sucursal else None,
            bodega_name=profile.bodega.name if profile.bodega else None,
            user_name=user.full_name,
            user_email=user.email,
        )
        for profile in user.access_profiles
    ]
    vendor = user.vendor_profile
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=bool(user.is_active),
        roles=[_role_response(role) for role in user.roles],
        permissions=[_permission_response(permission) for permission in sorted(user.permissions, key=lambda item: item.name)],
        access_profiles=access_profiles,
        vendor_profile=_vendor_response(vendor) if vendor else None,
    )


def _vendor_response(vendor: Vendor) -> VendorResponse:
    return VendorResponse(
        id=vendor.id,
        code=vendor.code,
        nombre=vendor.nombre,
        user_id=vendor.user_id,
        sucursal_id=vendor.sucursal_id,
        bodega_id=vendor.bodega_id,
        telefono=vendor.telefono,
        email=vendor.email,
        meta_ventas=vendor.meta_ventas,
        activo=bool(vendor.activo),
        user_name=vendor.user.full_name if vendor.user else None,
        user_email=vendor.user.email if vendor.user else None,
        sucursal_name=vendor.sucursal.name if vendor.sucursal else None,
        bodega_name=vendor.bodega.name if vendor.bodega else None,
    )


def _access_response(profile: UserAccessProfile) -> UserAccessProfileResponse:
    return UserAccessProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        sucursal_id=profile.sucursal_id,
        bodega_id=profile.bodega_id,
        role_scope=profile.role_scope,
        can_sell=bool(profile.can_sell),
        can_move_inventory=bool(profile.can_move_inventory),
        can_manage_catalogs=bool(profile.can_manage_catalogs),
        is_default=bool(profile.is_default),
        activo=bool(profile.activo),
        sucursal_name=profile.sucursal.name if profile.sucursal else None,
        bodega_name=profile.bodega.name if profile.bodega else None,
        user_name=profile.user.full_name if profile.user else None,
        user_email=profile.user.email if profile.user else None,
    )


def _apply_default_scope(db: Session, profile: UserAccessProfile) -> None:
    if not profile.is_default:
        return
    (
        db.query(UserAccessProfile)
        .filter(UserAccessProfile.user_id == profile.user_id, UserAccessProfile.id != profile.id)
        .update({UserAccessProfile.is_default: False})
    )


@router.get("/roles", response_model=list[RoleResponse])
def list_roles(db: Session = Depends(get_db)):
    roles = db.query(Role).options(joinedload(Role.permissions)).order_by(Role.name).all()
    return [_role_response(role) for role in roles]


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(payload: RoleCreate, db: Session = Depends(get_db)):
    name = _normalize(payload.name, "Rol").lower()
    if db.query(Role).filter(func.lower(Role.name) == name).first():
        raise HTTPException(status_code=400, detail="Rol ya registrado")
    role = Role(name=name)
    role.permissions = _get_or_create_permissions(db, payload.permission_names or [])
    if name == "administrador":
        role.permissions = _get_or_create_permissions(db, _catalog_permission_names())
    db.add(role)
    db.commit()
    db.refresh(role)
    return _role_response(role)


@router.put("/roles/{role_id}", response_model=RoleResponse)
def update_role(role_id: int, payload: RoleUpdate, db: Session = Depends(get_db)):
    role = db.query(Role).options(joinedload(Role.permissions)).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    data = payload.model_dump(exclude_unset=True)
    original_name = (role.name or "").strip().lower()
    if data.get("name") is not None:
        name = _normalize(data["name"], "Rol").lower()
        if original_name == "administrador" and name != "administrador":
            raise HTTPException(status_code=400, detail="El rol administrador no se puede renombrar")
        exists = db.query(Role).filter(func.lower(Role.name) == name, Role.id != role.id).first()
        if exists:
            raise HTTPException(status_code=400, detail="Rol ya registrado")
        role.name = name
    effective_name = (role.name or "").strip().lower()
    if data.get("permission_names") is not None and effective_name != "administrador":
        role.permissions = _get_or_create_permissions(db, data["permission_names"] or [])
    if effective_name == "administrador":
        role.permissions = _get_or_create_permissions(db, _catalog_permission_names())
    db.add(role)
    db.commit()
    db.refresh(role)
    return _role_response(role)


@router.get("/permissions", response_model=list[PermissionGroupResponse])
def list_permissions(db: Session = Depends(get_db)):
    _get_or_create_permissions(db, _catalog_permission_names())
    _sync_admin_full_access(db)
    db.commit()
    permissions = {permission.name: permission for permission in db.query(Permission).order_by(Permission.name).all()}
    groups: list[PermissionGroupResponse] = []
    for group in PERMISSION_GROUPS:
        groups.append(
            PermissionGroupResponse(
                key=group["key"],
                label=group["label"],
                permissions=[
                    _permission_response(permissions[name])
                    for name, _label in group["permissions"]
                    if name in permissions
                ],
            )
        )
    extras = [
        _permission_response(permission)
        for permission in permissions.values()
        if permission.name not in PERMISSION_LABELS
    ]
    if extras:
        groups.append(PermissionGroupResponse(key="otros", label="Otros permisos", permissions=extras))
    return groups


@router.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    users = (
        db.query(User)
        .options(
            joinedload(User.roles).joinedload(Role.permissions),
            joinedload(User.access_profiles).joinedload(UserAccessProfile.sucursal),
            joinedload(User.access_profiles).joinedload(UserAccessProfile.bodega),
            joinedload(User.vendor_profile).joinedload(Vendor.sucursal),
            joinedload(User.vendor_profile).joinedload(Vendor.bodega),
        )
        .order_by(User.full_name)
        .all()
    )
    return [_user_response(user) for user in users]


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    email = _normalize(payload.email, "Email").lower()
    if db.query(User).filter(func.lower(User.email) == email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    user = User(
        email=email,
        full_name=(payload.full_name or "").strip() or email,
        hashed_password=hash_password(payload.password),
        is_active=True,
    )
    user.roles = _get_or_create_roles(db, ["vendedor"])
    db.add(user)
    db.commit()
    db.refresh(user)
    return _user_response(user)


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    data = payload.model_dump(exclude_unset=True)
    if data.get("email") is not None:
        email = _normalize(data["email"], "Email").lower()
        exists = db.query(User).filter(func.lower(User.email) == email, User.id != user.id).first()
        if exists:
            raise HTTPException(status_code=400, detail="Email ya registrado")
        user.email = email
    if data.get("full_name") is not None:
        user.full_name = _normalize(data["full_name"], "Nombre")
    if data.get("password"):
        user.hashed_password = hash_password(data["password"])
    if "is_active" in data:
        user.is_active = bool(data["is_active"])
    if data.get("role_names") is not None:
        user.roles = _get_or_create_roles(db, data["role_names"] or ["vendedor"])
    db.add(user)
    db.commit()
    db.refresh(user)
    return _user_response(user)


@router.get("/branches", response_model=list[BranchResponse])
def list_branches(db: Session = Depends(get_db)):
    return db.query(Branch).order_by(Branch.name).all()


@router.post("/branches", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
def create_branch(payload: BranchCreate, db: Session = Depends(get_db)):
    code = _normalize(payload.code, "Codigo").upper()
    name = _normalize(payload.name, "Sucursal")
    exists = db.query(Branch).filter(func.lower(Branch.code) == code.lower()).first()
    if exists:
        raise HTTPException(status_code=400, detail="Codigo de sucursal ya existe")
    branch = Branch(
        code=code,
        name=name,
        address=(payload.address or "").strip() or None,
        phone=(payload.phone or "").strip() or None,
        activo=payload.activo,
    )
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return branch


@router.put("/branches/{branch_id}", response_model=BranchResponse)
def update_branch(branch_id: int, payload: BranchUpdate, db: Session = Depends(get_db)):
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    data = payload.model_dump(exclude_unset=True)
    if data.get("code") is not None:
        code = _normalize(data["code"], "Codigo").upper()
        exists = db.query(Branch).filter(func.lower(Branch.code) == code.lower(), Branch.id != branch.id).first()
        if exists:
            raise HTTPException(status_code=400, detail="Codigo de sucursal ya existe")
        branch.code = code
    if data.get("name") is not None:
        branch.name = _normalize(data["name"], "Sucursal")
    if "address" in data:
        branch.address = (data.get("address") or "").strip() or None
    if "phone" in data:
        branch.phone = (data.get("phone") or "").strip() or None
    if "activo" in data:
        branch.activo = bool(data["activo"])
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return branch


@router.get("/vendors", response_model=list[VendorResponse])
def list_vendors(include_inactive: bool = False, db: Session = Depends(get_db)):
    query = (
        db.query(Vendor)
        .options(joinedload(Vendor.user), joinedload(Vendor.sucursal), joinedload(Vendor.bodega))
        .order_by(Vendor.nombre)
    )
    if not include_inactive:
        query = query.filter(Vendor.activo.is_(True))
    return [_vendor_response(vendor) for vendor in query.all()]


@router.post("/vendors", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
def create_vendor(payload: VendorCreate, db: Session = Depends(get_db)):
    code = _normalize(payload.code, "Codigo").upper()
    nombre = _normalize(payload.nombre, "Vendedor")
    if db.query(Vendor).filter(func.lower(Vendor.code) == code.lower()).first():
        raise HTTPException(status_code=400, detail="Codigo de vendedor ya existe")
    user = db.query(User).filter(User.id == payload.user_id).first() if payload.user_id else None
    if payload.user_id and not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    _ensure_branch(db, payload.sucursal_id)
    _ensure_bodega(db, payload.bodega_id)
    vendor = Vendor(**payload.model_dump(exclude={"code", "nombre"}), code=code, nombre=nombre)
    db.add(vendor)
    if user and not any(role.name == "vendedor" for role in user.roles):
        user.roles.extend(_get_or_create_roles(db, ["vendedor"]))
    db.commit()
    db.refresh(vendor)
    return _vendor_response(vendor)


@router.put("/vendors/{vendor_id}", response_model=VendorResponse)
def update_vendor(vendor_id: int, payload: VendorUpdate, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    data = payload.model_dump(exclude_unset=True)
    if data.get("code") is not None:
        code = _normalize(data["code"], "Codigo").upper()
        exists = db.query(Vendor).filter(func.lower(Vendor.code) == code.lower(), Vendor.id != vendor.id).first()
        if exists:
            raise HTTPException(status_code=400, detail="Codigo de vendedor ya existe")
        vendor.code = code
    if data.get("nombre") is not None:
        vendor.nombre = _normalize(data["nombre"], "Vendedor")
    if "user_id" in data:
        if data["user_id"] and not db.query(User).filter(User.id == data["user_id"]).first():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        vendor.user_id = data["user_id"]
    if "sucursal_id" in data:
        _ensure_branch(db, data["sucursal_id"])
        vendor.sucursal_id = data["sucursal_id"]
    if "bodega_id" in data:
        _ensure_bodega(db, data["bodega_id"])
        vendor.bodega_id = data["bodega_id"]
    for field in ["telefono", "email"]:
        if field in data:
            setattr(vendor, field, (data.get(field) or "").strip() or None)
    if "meta_ventas" in data:
        vendor.meta_ventas = data["meta_ventas"]
    if "activo" in data:
        vendor.activo = bool(data["activo"])
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return _vendor_response(vendor)


@router.post("/profiles", response_model=UserAccessProfileResponse, status_code=status.HTTP_201_CREATED)
def create_access_profile(payload: UserAccessProfileCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    _ensure_branch(db, payload.sucursal_id)
    _ensure_bodega(db, payload.bodega_id)
    profile = UserAccessProfile(**payload.model_dump())
    db.add(profile)
    user.roles = list({role.name: role for role in [*user.roles, *_get_or_create_roles(db, _role_names_for_scope(profile.role_scope))]}.values())
    db.flush()
    _apply_default_scope(db, profile)
    db.commit()
    db.refresh(profile)
    return _access_response(profile)


@router.put("/profiles/{profile_id}", response_model=UserAccessProfileResponse)
def update_access_profile(profile_id: int, payload: UserAccessProfileCreate, db: Session = Depends(get_db)):
    profile = db.query(UserAccessProfile).filter(UserAccessProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil de acceso no encontrado")
    _ensure_branch(db, payload.sucursal_id)
    _ensure_bodega(db, payload.bodega_id)
    data = payload.model_dump(exclude={"user_id"})
    for key, value in data.items():
        setattr(profile, key, value)
    db.add(profile)
    db.flush()
    _apply_default_scope(db, profile)
    db.commit()
    db.refresh(profile)
    return _access_response(profile)
