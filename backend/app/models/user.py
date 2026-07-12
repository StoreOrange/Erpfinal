from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

# Tabla intermedia para relacion N:N
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"))
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80), unique=True, nullable=False)

    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100))
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    roles = relationship("Role", secondary=user_roles, back_populates="users")
    access_profiles = relationship("UserAccessProfile", back_populates="user", cascade="all, delete-orphan")
    vendor_profile = relationship("Vendor", back_populates="user", uselist=False)

    @property
    def permissions(self):
        permission_map = {}
        for role in self.roles:
            for permission in role.permissions:
                permission_map[permission.id] = permission
        return list(permission_map.values())


class Branch(Base):
    __tablename__ = "sucursales"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(40), unique=True, nullable=False)
    name = Column(String(140), nullable=False)
    address = Column(String(220), nullable=True)
    phone = Column(String(80), nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    bodegas = relationship("Bodega", back_populates="sucursal")
    access_profiles = relationship("UserAccessProfile", back_populates="sucursal")
    vendors = relationship("Vendor", back_populates="sucursal")


class UserAccessProfile(Base):
    __tablename__ = "user_access_profiles"
    __table_args__ = (
        UniqueConstraint("user_id", "sucursal_id", "bodega_id", name="uq_user_access_scope"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=True)
    bodega_id = Column(Integer, ForeignKey("bodegas.id"), nullable=True)
    role_scope = Column(String(50), nullable=False, default="VENDEDOR")
    can_sell = Column(Boolean, default=True)
    can_move_inventory = Column(Boolean, default=False)
    can_manage_catalogs = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="access_profiles")
    sucursal = relationship("Branch", back_populates="access_profiles")
    bodega = relationship("Bodega", back_populates="access_profiles")


class Vendor(Base):
    __tablename__ = "vendedores"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(40), unique=True, nullable=False)
    nombre = Column(String(160), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, unique=True)
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=True)
    bodega_id = Column(Integer, ForeignKey("bodegas.id"), nullable=True)
    telefono = Column(String(80), nullable=True)
    email = Column(String(140), nullable=True)
    meta_ventas = Column(Integer, nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="vendor_profile")
    sucursal = relationship("Branch", back_populates="vendors")
    bodega = relationship("Bodega", back_populates="vendors")
