"""
سكربت تهيئة بيانات أولية: الأدوار الوظيفية، مستخدم مدير افتراضي، ومزرعة تجريبية.
التشغيل: python seed_data.py
"""
from database import Base, engine, SessionLocal
import models
from auth import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

if not db.query(models.Role).first():
    roles = [models.Role(name=r, description=r.value) for r in models.RoleEnum]
    db.add_all(roles)
    db.commit()

admin_role = db.query(models.Role).filter(models.Role.name == models.RoleEnum.system_admin).first()

if not db.query(models.User).filter(models.User.username == "admin").first():
    admin = models.User(
        full_name="مدير النظام",
        username="admin",
        email="admin@lgc-farm.ly",
        hashed_password=hash_password("ChangeMe123!"),
        role_id=admin_role.id,
    )
    db.add(admin)
    db.commit()
    print("تم إنشاء مستخدم افتراضي: admin / ChangeMe123! (يرجى تغييرها فورًا)")

if not db.query(models.Farm).first():
    farm = models.Farm(name="مزرعة LGC التجريبية", location="طرابلس، ليبيا", area_hectares=25)
    db.add(farm)
    db.commit()
    db.refresh(farm)

    zone1 = models.Zone(farm_id=farm.id, name="القطاع 1", area_hectares=5, soil_type="طينية رملية")
    zone2 = models.Zone(farm_id=farm.id, name="القطاع 2", area_hectares=6, soil_type="رملية")
    db.add_all([zone1, zone2])
    db.commit()

    tank = models.WaterTank(farm_id=farm.id, name="الخزان الرئيسي", capacity_liters=50000, current_level_percent=68)
    energy = models.Energy(farm_id=farm.id, production_kwh=42.5, consumption_kwh=30.1, battery_charge_percent=81)
    db.add_all([tank, energy])
    db.commit()
    print("تم إنشاء بيانات تجريبية للمزرعة والقطاعات.")

db.close()
print("اكتملت عملية التهيئة.")
