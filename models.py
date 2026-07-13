"""
نماذج قاعدة البيانات (SQLAlchemy ORM)
تغطي جميع الجداول المطلوبة في مشروع LGC Smart Farm OS.
كل جدول موثّق بتعليق مختصر يوضّح غرضه.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
)
from sqlalchemy.orm import relationship
import enum

from database import Base


# ---------------------------------------------------------------------------
# المستخدمون والصلاحيات
# ---------------------------------------------------------------------------
class RoleEnum(str, enum.Enum):
    system_admin = "مدير النظام"
    farm_manager = "مدير المزرعة"
    irrigation_officer = "مسؤول الري"
    energy_officer = "مسؤول الطاقة"
    maintenance_tech = "فني الصيانة"
    worker = "عامل"


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(Enum(RoleEnum), unique=True, nullable=False)
    description = Column(String(255))
    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String(150), nullable=False)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(150), unique=True)
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    role = relationship("Role", back_populates="users")


# ---------------------------------------------------------------------------
# المزرعة والقطاعات
# ---------------------------------------------------------------------------
class Farm(Base):
    __tablename__ = "farms"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    location = Column(String(255))
    area_hectares = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    zones = relationship("Zone", back_populates="farm")
    employees = relationship("Employee", back_populates="farm")


class Zone(Base):
    __tablename__ = "zones"
    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    name = Column(String(120), nullable=False)
    area_hectares = Column(Float)
    soil_type = Column(String(80))
    geo_coordinates = Column(String(255))  # GeoJSON / lat,lng مبسّط

    farm = relationship("Farm", back_populates="zones")
    crops = relationship("Crop", back_populates="zone")
    trees = relationship("Tree", back_populates="zone")
    valves = relationship("Valve", back_populates="zone")


# ---------------------------------------------------------------------------
# المحاصيل والأشجار
# ---------------------------------------------------------------------------
class Crop(Base):
    __tablename__ = "crops"
    id = Column(Integer, primary_key=True)
    zone_id = Column(Integer, ForeignKey("zones.id"))
    name = Column(String(120), nullable=False)
    growth_stage = Column(String(80))
    planting_date = Column(DateTime)
    expected_yield_kg = Column(Float)
    water_requirement_liters_per_day = Column(Float)
    disease_status = Column(String(120), default="سليم")

    zone = relationship("Zone", back_populates="crops")


class Tree(Base):
    __tablename__ = "trees"
    id = Column(Integer, primary_key=True)
    zone_id = Column(Integer, ForeignKey("zones.id"))
    species = Column(String(120))
    planting_date = Column(DateTime)
    health_status = Column(String(80), default="جيدة")

    zone = relationship("Zone", back_populates="trees")


# ---------------------------------------------------------------------------
# الحساسات
# ---------------------------------------------------------------------------
class SoilSensor(Base):
    __tablename__ = "soil_sensors"
    id = Column(Integer, primary_key=True)
    zone_id = Column(Integer, ForeignKey("zones.id"))
    device_code = Column(String(80), unique=True)
    is_online = Column(Boolean, default=True)
    last_seen = Column(DateTime, default=datetime.utcnow)


class WeatherSensor(Base):
    __tablename__ = "weather_sensors"
    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    device_code = Column(String(80), unique=True)
    is_online = Column(Boolean, default=True)
    last_seen = Column(DateTime, default=datetime.utcnow)


class SensorReading(Base):
    """قراءات موحّدة لجميع أنواع الحساسات (تربة، جو، مياه، طاقة)."""
    __tablename__ = "sensor_readings"
    id = Column(Integer, primary_key=True)
    sensor_type = Column(String(50))  # soil_moisture, soil_temp, air_temp, air_humidity, tank_level, battery_voltage, solar_production
    sensor_ref_id = Column(Integer)   # معرف الحساس المصدر (soil_sensors / weather_sensors ...)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=True)
    value = Column(Float, nullable=False)
    unit = Column(String(20))
    recorded_at = Column(DateTime, default=datetime.utcnow)


# ---------------------------------------------------------------------------
# الطاقة
# ---------------------------------------------------------------------------
class Energy(Base):
    """سجل إجمالي لحالة الطاقة في المزرعة (لقطة زمنية)."""
    __tablename__ = "energy"
    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    production_kwh = Column(Float, default=0)
    consumption_kwh = Column(Float, default=0)
    battery_charge_percent = Column(Float, default=0)
    recorded_at = Column(DateTime, default=datetime.utcnow)


class SolarPanel(Base):
    __tablename__ = "solar_panels"
    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    code = Column(String(80))
    capacity_watt = Column(Float)
    status = Column(String(50), default="يعمل")


class Battery(Base):
    __tablename__ = "batteries"
    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    code = Column(String(80))
    capacity_ah = Column(Float)
    current_charge_percent = Column(Float, default=100)
    health_percent = Column(Float, default=100)


# ---------------------------------------------------------------------------
# المياه والري
# ---------------------------------------------------------------------------
class WaterTank(Base):
    __tablename__ = "water_tanks"
    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    name = Column(String(120))
    capacity_liters = Column(Float)
    current_level_percent = Column(Float, default=0)


class Pump(Base):
    __tablename__ = "pumps"
    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    code = Column(String(80))
    status = Column(String(50), default="متوقفة")  # تعمل / متوقفة / عطل
    flow_rate_lph = Column(Float)


class Valve(Base):
    __tablename__ = "valves"
    id = Column(Integer, primary_key=True)
    zone_id = Column(Integer, ForeignKey("zones.id"))
    code = Column(String(80))
    is_open = Column(Boolean, default=False)

    zone = relationship("Zone", back_populates="valves")


class IrrigationLog(Base):
    __tablename__ = "irrigation_logs"
    id = Column(Integer, primary_key=True)
    zone_id = Column(Integer, ForeignKey("zones.id"))
    pump_id = Column(Integer, ForeignKey("pumps.id"), nullable=True)
    mode = Column(String(20), default="آلي")  # آلي / يدوي
    liters_used = Column(Float)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    triggered_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)


# ---------------------------------------------------------------------------
# التنبيهات والتقارير
# ---------------------------------------------------------------------------
class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=True)
    category = Column(String(50))  # ري / طاقة / حساس / أمان / صيانة
    severity = Column(String(20), default="متوسط")  # منخفض / متوسط / عالي / حرج
    message = Column(Text)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    report_type = Column(String(20))  # يومي / أسبوعي / شهري
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    file_path = Column(String(255), nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)


# ---------------------------------------------------------------------------
# الصيانة والمخزون والموظفون
# ---------------------------------------------------------------------------
class MaintenanceTask(Base):
    __tablename__ = "maintenance_tasks"
    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    asset_type = Column(String(50))  # pump / valve / panel / battery / sensor
    asset_ref_id = Column(Integer)
    description = Column(Text)
    status = Column(String(20), default="مفتوحة")  # مفتوحة / قيد التنفيذ / مكتملة
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)


class InventoryItem(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    name = Column(String(150))
    category = Column(String(80))
    quantity = Column(Float, default=0)
    unit = Column(String(20))
    reorder_threshold = Column(Float, default=0)


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    full_name = Column(String(150))
    position = Column(String(120))
    phone = Column(String(30))

    farm = relationship("Farm", back_populates="employees")
