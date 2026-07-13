"""
وحدة الذكاء الاصطناعي (AI Assistant).
هذه نسخة أولية بقواعد استدلال بسيطة (Rule-Based) قابلة للاستبدال لاحقًا
بنموذج تعلّم آلي فعلي أو باستدعاء Claude API لتحليل أعمق للبيانات.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/api/ai", tags=["الذكاء الاصطناعي"])


@router.get("/recommendations")
def get_recommendations(db: Session = Depends(get_db), _=Depends(get_current_user)):
    recommendations = []

    # قاعدة: رطوبة تربة منخفضة تعني حاجة للري
    low_moisture = (
        db.query(models.SensorReading)
        .filter(models.SensorReading.sensor_type == "soil_moisture", models.SensorReading.value < 30)
        .order_by(models.SensorReading.recorded_at.desc())
        .limit(20)
        .all()
    )
    for reading in low_moisture:
        recommendations.append({
            "type": "ري",
            "zone_id": reading.zone_id,
            "message": f"رطوبة التربة منخفضة ({reading.value}%) — يُنصح بتشغيل الري.",
        })

    # قاعدة: شحن بطارية منخفض
    low_battery = (
        db.query(models.Battery)
        .filter(models.Battery.current_charge_percent < 25)
        .all()
    )
    for battery in low_battery:
        recommendations.append({
            "type": "طاقة",
            "message": f"شحن البطارية {battery.code} منخفض ({battery.current_charge_percent}%).",
        })

    if not recommendations:
        recommendations.append({"type": "عام", "message": "لا توجد توصيات حرجة حاليًا. جميع المؤشرات ضمن النطاق الطبيعي."})

    return {"recommendations": recommendations}
