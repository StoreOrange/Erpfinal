from pydantic import BaseModel
from typing import List, Optional

class RoleBase(BaseModel):
    name: str

class PermissionResponse(BaseModel):
    id: int
    name: str
    label: Optional[str] = None
    group: Optional[str] = None

    class Config:
        orm_mode = True


class PermissionGroupResponse(BaseModel):
    key: str
    label: str
    permissions: List[PermissionResponse]


class RoleResponse(RoleBase):
    id: int
    permissions: List[PermissionResponse] = []
    class Config:
        orm_mode = True


class RoleCreate(RoleBase):
    permission_names: List[str] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    permission_names: Optional[List[str]] = None


class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str


class BranchBase(BaseModel):
    code: str
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    activo: bool = True


class BranchCreate(BranchBase):
    pass


class BranchUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    activo: Optional[bool] = None


class BranchResponse(BranchBase):
    id: int

    class Config:
        orm_mode = True


class UserAccessProfileBase(BaseModel):
    user_id: int
    sucursal_id: Optional[int] = None
    bodega_id: Optional[int] = None
    role_scope: str = "VENDEDOR"
    can_sell: bool = True
    can_move_inventory: bool = False
    can_manage_catalogs: bool = False
    is_default: bool = False
    activo: bool = True


class UserAccessProfileCreate(UserAccessProfileBase):
    pass


class UserAccessProfileUpdate(BaseModel):
    sucursal_id: Optional[int] = None
    bodega_id: Optional[int] = None
    role_scope: Optional[str] = None
    can_sell: Optional[bool] = None
    can_move_inventory: Optional[bool] = None
    can_manage_catalogs: Optional[bool] = None
    is_default: Optional[bool] = None
    activo: Optional[bool] = None


class UserAccessProfileResponse(UserAccessProfileBase):
    id: int
    sucursal_name: Optional[str] = None
    bodega_name: Optional[str] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None

    class Config:
        orm_mode = True


class VendorBase(BaseModel):
    code: str
    nombre: str
    user_id: Optional[int] = None
    sucursal_id: Optional[int] = None
    bodega_id: Optional[int] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    meta_ventas: Optional[int] = None
    activo: bool = True


class VendorCreate(VendorBase):
    pass


class VendorUpdate(BaseModel):
    code: Optional[str] = None
    nombre: Optional[str] = None
    user_id: Optional[int] = None
    sucursal_id: Optional[int] = None
    bodega_id: Optional[int] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    meta_ventas: Optional[int] = None
    activo: Optional[bool] = None


class VendorResponse(VendorBase):
    id: int
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    sucursal_name: Optional[str] = None
    bodega_name: Optional[str] = None

    class Config:
        orm_mode = True


class UserResponse(UserBase):
    id: int
    is_active: bool
    roles: List[RoleResponse] = []
    permissions: List[PermissionResponse] = []
    access_profiles: List[UserAccessProfileResponse] = []
    vendor_profile: Optional[VendorResponse] = None

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role_names: Optional[List[str]] = None
