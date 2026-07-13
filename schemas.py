"""
مخططات Pydantic للتحقق من صحة بيانات الطلبات والاستجابات.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---- المصادقة والمستخدمون ----
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    full_name: str
    username: str
    email: Optional[str] = None
    password: str
    role_id: Optional[int] = None


class UserOut(ORMBase):
    id: int
    full_name: str
    username: str
    email: Optional[str] = None
    role_id: Optional[int] = None
    is_active: bool


# ---- المزارع والقطاعات ----
class FarmCreate(BaseModel):
    name: str
    location: Optional[str] = None
    area_hectares: Optional[float] = None


class FarmOut(ORMBase):
    id: int
    name: str
    location: Optional[str] = None
    area_hectares: Optional[float] = None
    created_at: datetime


class ZoneCreate(BaseModel):
    farm_id: int
    name: str
    area_hectares: Optional[float] = None
    soil_type: Optional[str] = None
    geo_coordinates: Optional[str] = None


class ZoneOut(ORMBase):
    id: int
    farm_id: int
    name: str
    area_hectares: Optional[float] = None
    soil_type: Optional[str] = None
    geo_coordinates: Optional[str] = None


# ---- المحاصيل ----
class CropCreate(BaseModel):
    zone_id: int
    name: str
    growth_stage: Optional[str] = None
    planting_date: Optional[datetime] = None
    expected_yield_kg: Optional[float] = None
    water_requirement_liters_per_day: Optional[float] = None


class CropOut(ORMBase):
    id: int
    zone_id: int
    name: str
    growth_stage: Optional[str] = None
    expected_yield_kg: Optional[float] = None
    disease_status: Optional[str] = None


# ---- الحساسات والقراءات ----
class SensorReadingCreate(BaseModel):
    sensor_type: str
    sensor_ref_id: int
    zone_id: Optional[int] = None
    value: float
    unit: Optional[str] = None


class SensorReadingOut(ORMBase):
    id: int
    sensor_type: str
    zone_id: Optional[int] = None
    value: float
    unit: Optional[str] = None
    recorded_at: datetime


# ---- الري ----
class IrrigationLogCreate(BaseModel):
    zone_id: int
    pump_id: Optional[int] = None
    mode: str = "آلي"
    liters_used: Optional[float] = None


class IrrigationLogOut(ORMBase):
    id: int
    zone_id: int
    pump_id: Optional[int] = None
    mode: str
    liters_used: Optional[float] = None
    started_at: datetime
    ended_at: Optional[datetime] = None


class ValveToggle(BaseModel):
    is_open: bool


# ---- الطاقة ----
class EnergyOut(ORMBase):
    id: int
    farm_id: int
    production_kwh: float
    consumption_kwh: float
    battery_charge_percent: float
    recorded_at: datetime


# ---- التنبيهات ----
class AlertCreate(BaseModel):
    farm_id: int
    zone_id: Optional[int] = None
    category: str
    severity: str = "متوسط"
    message: str


class AlertOut(ORMBase):
    id: int
    farm_id: int
    zone_id: Optional[int] = None
    category: str
    severity: str
    message: str
    is_resolved: bool
    created_at: datetime


# ---- التقارير ----
class ReportOut(ORMBase):
    id: int
    farm_id: int
    report_type: str
    period_start: datetime
    period_end: datetime
    file_path: Optional[str] = None
    generated_at: datetime


# ---- لوحة التحكم ----
class DashboardSummary(BaseModel):
    active_sensors: int
    online_sensors: int
    water_level_percent: float
    energy_production_kwh: float
    battery_charge_percent: float
    open_alerts: int
    zones_count: int
    crops_count: int
