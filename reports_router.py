"""إدارة التقارير الدورية (يومي / أسبوعي / شهري)."""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models, schemas
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/api/reports", tags=["التقارير"])


@router.get("/", response_model=List[schemas.ReportOut])
def list_reports(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(models.Report).order_by(models.Report.generated_at.desc()).all()

# ملاحظة تنفيذية: توليد ملفات PDF/Excel الفعلية يمكن تنفيذه لاحقًا بمكتبات
# مثل reportlab أو WeasyPrint لملفات PDF، وopenpyxl لملفات Excel،
# مع حفظ الملف الناتج في مجلد storage/reports وربط file_path بسجل التقرير.
