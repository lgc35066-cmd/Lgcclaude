"""إدارة الري: المضخات، الصمامات، سجل الري، التشغيل اليدوي والآلي."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

import models, schemas
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/api/irrigation", tags=["الري"])


@router.get("/logs", response_model=List[schemas.IrrigationLogOut])
def list_logs(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(models.IrrigationLog).order_by(models.IrrigationLog.started_at.desc()).all()


@router.post("/logs/start", response_model=schemas.IrrigationLogOut)
def start_irrigation(payload: schemas.IrrigationLogCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    log = models.IrrigationLog(
        zone_id=payload.zone_id,
        pump_id=payload.pump_id,
        mode=payload.mode,
        liters_used=payload.liters_used,
        triggered_by_user_id=current_user.id,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.post("/logs/{log_id}/stop", response_model=schemas.IrrigationLogOut)
def stop_irrigation(log_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    log = db.query(models.IrrigationLog).get(log_id)
    if not log:
        raise HTTPException(404, "سجل الري غير موجود")
    log.ended_at = datetime.utcnow()
    db.commit()
    db.refresh(log)
    return log


@router.put("/valves/{valve_id}")
def toggle_valve(valve_id: int, payload: schemas.ValveToggle, db: Session = Depends(get_db), _=Depends(get_current_user)):
    valve = db.query(models.Valve).get(valve_id)
    if not valve:
        raise HTTPException(404, "الصمام غير موجود")
    valve.is_open = payload.is_open
    db.commit()
    return {"id": valve.id, "is_open": valve.is_open}
