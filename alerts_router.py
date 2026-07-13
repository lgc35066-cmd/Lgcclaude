"""إدارة التنبيهات."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models, schemas
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/api/alerts", tags=["التنبيهات"])


@router.get("/", response_model=List[schemas.AlertOut])
def list_alerts(resolved: bool = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    query = db.query(models.Alert)
    if resolved is not None:
        query = query.filter(models.Alert.is_resolved == resolved)
    return query.order_by(models.Alert.created_at.desc()).all()


@router.post("/", response_model=schemas.AlertOut)
def create_alert(payload: schemas.AlertCreate, db: Session = Depends(get_db)):
    """يمكن استدعاؤها من وحدة الذكاء الاصطناعي أو من الحساسات مباشرة عند اكتشاف حالة غير طبيعية."""
    alert = models.Alert(**payload.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.put("/{alert_id}/resolve", response_model=schemas.AlertOut)
def resolve_alert(alert_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    alert = db.query(models.Alert).get(alert_id)
    if not alert:
        raise HTTPException(404, "التنبيه غير موجود")
    alert.is_resolved = True
    db.commit()
    db.refresh(alert)
    return alert
