"""إدارة الطاقة الشمسية: الألواح، البطاريات، الإنتاج والاستهلاك."""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models, schemas
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/api/energy", tags=["الطاقة"])


@router.get("/", response_model=List[schemas.EnergyOut])
def list_energy_logs(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(models.Energy).order_by(models.Energy.recorded_at.desc()).limit(200).all()


@router.get("/latest", response_model=schemas.EnergyOut)
def latest_energy(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(models.Energy).order_by(models.Energy.recorded_at.desc()).first()


@router.get("/panels")
def list_panels(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(models.SolarPanel).all()


@router.get("/batteries")
def list_batteries(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(models.Battery).all()
