from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..core.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    hash_password,
    verify_password,
)
from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])
bearer_scheme = HTTPBearer(auto_error=False)


class LoginData(BaseModel):
    email: str
    password: str


def _serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "roles": [
            {
                "id": role.id,
                "name": role.name,
                "permissions": [{"id": permission.id, "name": permission.name} for permission in role.permissions],
            }
            for role in user.roles
        ],
        "permissions": [{"id": permission.id, "name": permission.name} for permission in user.permissions],
        "access_profiles": [
            {
                "id": profile.id,
                "user_id": profile.user_id,
                "sucursal_id": profile.sucursal_id,
                "sucursal_name": profile.sucursal.name if profile.sucursal else None,
                "bodega_id": profile.bodega_id,
                "bodega_name": profile.bodega.name if profile.bodega else None,
                "role_scope": profile.role_scope,
                "can_sell": bool(profile.can_sell),
                "can_move_inventory": bool(profile.can_move_inventory),
                "can_manage_catalogs": bool(profile.can_manage_catalogs),
                "is_default": bool(profile.is_default),
                "activo": bool(profile.activo),
            }
            for profile in user.access_profiles
        ],
        "vendor_profile": {
            "id": user.vendor_profile.id,
            "code": user.vendor_profile.code,
            "nombre": user.vendor_profile.nombre,
            "user_id": user.vendor_profile.user_id,
            "sucursal_id": user.vendor_profile.sucursal_id,
            "sucursal_name": user.vendor_profile.sucursal.name if user.vendor_profile.sucursal else None,
            "bodega_id": user.vendor_profile.bodega_id,
            "bodega_name": user.vendor_profile.bodega.name if user.vendor_profile.bodega else None,
            "telefono": user.vendor_profile.telefono,
            "email": user.vendor_profile.email,
            "meta_ventas": user.vendor_profile.meta_ventas,
            "activo": bool(user.vendor_profile.activo),
        }
        if user.vendor_profile
        else None,
    }


def _get_user_from_token(
    credentials: HTTPAuthorizationCredentials | None,
    db: Session,
) -> User:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
        )

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        subject = str(payload.get("sub") or "").strip().lower()
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido",
        ) from exc

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido",
        )

    user = db.query(User).filter(func.lower(User.email) == subject).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )
    return user


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(func.lower(User.email) == user.email.strip().lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")

    new_user = User(
        email=user.email.strip().lower(),
        full_name=(user.full_name or "").strip() or user.email.strip().lower(),
        hashed_password=hash_password(user.password),
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    identifier = (data.email or "").strip().lower()
    password = data.password or ""

    user = db.query(User).filter(
        (func.lower(User.email) == identifier)
        | (func.lower(User.full_name) == identifier)
    ).first()

    if not user:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Contrasena incorrecta")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuario inactivo")

    token = create_access_token({"sub": user.email, "uid": user.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": _serialize_user(user),
    }


@router.get("/me", response_model=UserResponse)
def me(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    return _serialize_user(_get_user_from_token(credentials, db))
