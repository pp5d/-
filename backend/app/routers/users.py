from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.core.deps import require_roles
from app.core.security import hash_password
from app.db import get_db
from app.models.user import ROLES, User
from app.schemas.user import UserCreate, UserOut, UserUpdate

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    dependencies=[Depends(require_roles("admin"))],
)


@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.scalars(select(User).order_by(User.id)).all()


@router.post("", response_model=UserOut)
def create_user(body: UserCreate, role: str = Query(default="support"), db: Session = Depends(get_db)):
    if settings.APP_MODE != "full":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "公网实例禁止创建用户")
    if role not in ROLES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"角色必须是 {ROLES}")
    exists = db.scalar(select(User).where(User.username == body.username))
    if exists:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "用户名已存在")
    user = User(
        username=body.username,
        phone=body.phone,
        group_name=body.group_name,
        role=role,
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, body: UserUpdate, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "用户不存在")
    if body.role is not None:
        if body.role not in ROLES:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"角色必须是 {ROLES}")
        user.role = body.role
    if body.group_name is not None:
        user.group_name = body.group_name
    if body.is_active is not None:
        user.is_active = body.is_active
    db.commit()
    db.refresh(user)
    return user
