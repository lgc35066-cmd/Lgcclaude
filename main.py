"""
LGC Smart Farm OS - Backend
نقطة تشغيل تطبيق FastAPI الرئيسية.

تشغيل محلي:
    pip install -r requirements.txt
    uvicorn main:app --reload

توثيق API تلقائي عبر Swagger على: http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from database import Base, engine
import models  # noqa: F401  (يضمن تسجيل جميع النماذج قبل create_all)

from routers import (
    auth_router,
    users_router,
    farms_router,
    crops_router,
    sensors_router,
    irrigation_router,
    energy_router,
    alerts_router,
    ai_router,
    dashboard_router,
    reports_router,
)

# إنشاء الجداول تلقائيًا في وضع التطوير (SQLite).
# في الإنتاج يُفضّل استخدام Alembic للترحيلات (migrations) بدلاً من create_all.
Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="LGC Smart Farm OS API",
    description="نظام تشغيل متكامل لإدارة المزارع الذكية - Libya Green Chain",
    version="0.1.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS: في الإنتاج يجب تقييد allow_origins للنطاقات الفعلية للواجهة الأمامية فقط
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(farms_router.router)
app.include_router(crops_router.router)
app.include_router(sensors_router.router)
app.include_router(irrigation_router.router)
app.include_router(energy_router.router)
app.include_router(alerts_router.router)
app.include_router(ai_router.router)
app.include_router(dashboard_router.router)
app.include_router(reports_router.router)


@app.get("/")
def root():
    return {"project": "LGC Smart Farm OS", "status": "running", "docs": "/docs"}


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
