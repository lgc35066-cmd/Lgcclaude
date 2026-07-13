"""إدارة المستخدمين والصلاحيات."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models, schemas
from database import get_db
from auth import hash_password, require_roles

router = APIRouter(prefix="/api/users", tags=["المستخدمون"])


@router.get("/", response_model=List[schemas.UserOut])
def list_users(db: Session = Depends(get_db), _=Depends(require_roles("مدير النظام", "مدير المزرعة"))):
    return db.query(models.User).all()


@router.post("/", response_model=schemas.UserOut)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db), _=Depends(require_roles("مدير النظام"))):
    if db.query(models.User).filter(models.User.username == payload.username).first():
        raise HTTPException(400, "اسم المستخدم مستخدم بالفعل")
    user = models.User(
        full_name=payload.full_name,
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role_id=payload.role_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, payload: schemas.UserCreate, db: Session = Depends(get_db), _=Depends(require_roles("مدير النظام"))):
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(404, "المستخدم غير موجود")
    user.full_name = payload.full_name
    user.email = payload.email
    user.role_id = payload.role_id
    if payload.password:
        user.hashed_password = hash_password(payload.password)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), _=Depends(require_roles("مدير النظام"))):
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(404, "المستخدم غير موجود")
    db.delete(user)
    db.commit()
    return {"deleted": True}
