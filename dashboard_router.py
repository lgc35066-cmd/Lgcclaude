"""تجميع مؤشرات لوحة التحكم الرئيسية من مختلف الوحدات."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models, schemas
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["لوحة التحكم"])


@router.get("/summary", response_model=schemas.DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db), _=Depends(get_current_user)):
    soil_sensors = db.query(models.SoilSensor).all()
    weather_sensors = db.query(models.WeatherSensor).all()
    online = sum(1 for s in soil_sensors + weather_sensors if s.is_online)

    latest_tank = db.query(models.WaterTank).first()
    latest_energy = db.query(models.Energy).order_by(models.Energy.recorded_at.desc()).first()
    open_alerts = db.query(models.Alert).filter(models.Alert.is_resolved == False).count()  # noqa: E712
    zones_count = db.query(models.Zone).count()
    crops_count = db.query(models.Crop).count()

    return schemas.DashboardSummary(
        active_sensors=len(soil_sensors) + len(weather_sensors),
        online_sensors=online,
        water_level_percent=latest_tank.current_level_percent if latest_tank else 0,
        energy_production_kwh=latest_energy.production_kwh if latest_energy else 0,
        battery_charge_percent=latest_energy.battery_charge_percent if latest_energy else 0,
        open_alerts=open_alerts,
        zones_count=zones_count,
        crops_count=crops_count,
    )
