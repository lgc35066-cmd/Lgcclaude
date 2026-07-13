"""إدارة المزارع والقطاعات الزراعية."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models, schemas
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/api/farms", tags=["المزارع والقطاعات"])


@router.get("/", response_model=List[schemas.FarmOut])
def list_farms(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(models.Farm).all()


@router.post("/", response_model=schemas.FarmOut)
def create_farm(payload: schemas.FarmCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    farm = models.Farm(**payload.model_dump())
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm


@router.get("/{farm_id}/zones", response_model=List[schemas.ZoneOut])
def list_zones(farm_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(models.Zone).filter(models.Zone.farm_id == farm_id).all()


@router.post("/zones", response_model=schemas.ZoneOut)
def create_zone(payload: schemas.ZoneCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    zone = models.Zone(**payload.model_dump())
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


@router.put("/zones/{zone_id}", response_model=schemas.ZoneOut)
def update_zone(zone_id: int, payload: schemas.ZoneCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    zone = db.query(models.Zone).get(zone_id)
    if not zone:
        raise HTTPException(404, "القطاع غير موجود")
    for key, value in payload.model_dump().items():
        setattr(zone, key, value)
    db.commit()
    db.refresh(zone)
    return zone


@router.delete("/zones/{zone_id}")
def delete_zone(zone_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    zone = db.query(models.Zone).get(zone_id)
    if not zone:
        raise HTTPException(404, "القطاع غير موجود")
    db.delete(zone)
    db.commit()
    return {"deleted": True}
