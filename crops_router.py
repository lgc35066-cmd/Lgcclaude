"""إدارة المحاصيل."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models, schemas
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/api/crops", tags=["المحاصيل"])


@router.get("/", response_model=List[schemas.CropOut])
def list_crops(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(models.Crop).all()


@router.post("/", response_model=schemas.CropOut)
def create_crop(payload: schemas.CropCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    crop = models.Crop(**payload.model_dump())
    db.add(crop)
    db.commit()
    db.refresh(crop)
    return crop


@router.put("/{crop_id}", response_model=schemas.CropOut)
def update_crop(crop_id: int, payload: schemas.CropCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    crop = db.query(models.Crop).get(crop_id)
    if not crop:
        raise HTTPException(404, "المحصول غير موجود")
    for key, value in payload.model_dump().items():
        setattr(crop, key, value)
    db.commit()
    db.refresh(crop)
    return crop


@router.delete("/{crop_id}")
def delete_crop(crop_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    crop = db.query(models.Crop).get(crop_id)
    if not crop:
        raise HTTPException(404, "المحصول غير موجود")
    db.delete(crop)
    db.commit()
    return {"deleted": True}
