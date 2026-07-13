"""مسارات المصادقة: تسجيل الدخول وإصدار التوكن."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import models
from database import get_db
from auth import verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["المصادقة"])


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="اسم المستخدم أو كلمة المرور غير صحيحة")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
