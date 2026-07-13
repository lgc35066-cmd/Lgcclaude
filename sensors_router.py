"""استقبال وعرض قراءات الحساسات (طبقة IoT)."""
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models, schemas
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/api/sensors", tags=["الحساسات"])


@router.post("/readings", response_model=schemas.SensorReadingOut)
def ingest_reading(payload: schemas.SensorReadingCreate, db: Session = Depends(get_db)):
    """
    نقطة استقبال بيانات من أجهزة ESP32 / ESP8266 / Raspberry Pi عبر REST.
    يمكن لاحقًا إضافة مصادقة بمفتاح جهاز (Device API Key) بدلاً من JWT للأجهزة الميدانية.
    """
    reading = models.SensorReading(**payload.model_dump())
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


@router.get("/readings", response_model=List[schemas.SensorReadingOut])
def list_readings(
    sensor_type: Optional[str] = None,
    zone_id: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    query = db.query(models.SensorReading)
    if sensor_type:
        query = query.filter(models.SensorReading.sensor_type == sensor_type)
    if zone_id:
        query = query.filter(models.SensorReading.zone_id == zone_id)
    return query.order_by(models.SensorReading.recorded_at.desc()).limit(limit).all()


@router.get("/status")
def sensors_status(db: Session = Depends(get_db), _=Depends(get_current_user)):
    soil = db.query(models.SoilSensor).all()
    weather = db.query(models.WeatherSensor).all()
    return {
        "soil_sensors": [{"id": s.id, "device_code": s.device_code, "is_online": s.is_online} for s in soil],
        "weather_sensors": [{"id": s.id, "device_code": s.device_code, "is_online": s.is_online} for s in weather],
    }
