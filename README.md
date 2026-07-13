# Libya Green Chain (LGC) — Smart Farm OS

نظام تشغيل متكامل لإدارة المزارع الذكية، مصمَّم ليكون لاحقًا جزءًا من منصة وطنية أوسع للتنمية الزراعية في ليبيا.

---

## 1. هيكل المشروع

```
LGC-Smart-Farm-OS/
├── backend/                # FastAPI — REST API
│   ├── main.py              # نقطة تشغيل التطبيق
│   ├── database.py          # اتصال قاعدة البيانات (SQLite → PostgreSQL)
│   ├── models.py            # نماذج SQLAlchemy (20+ جدول)
│   ├── schemas.py           # مخططات Pydantic
│   ├── auth.py              # JWT + RBAC
│   ├── seed_data.py         # بيانات أولية للتجربة
│   ├── requirements.txt
│   └── routers/              # مسارات API لكل وحدة
│       ├── auth_router.py
│       ├── users_router.py
│       ├── farms_router.py
│       ├── crops_router.py
│       ├── sensors_router.py
│       ├── irrigation_router.py
│       ├── energy_router.py
│       ├── alerts_router.py
│       ├── ai_router.py
│       ├── dashboard_router.py
│       └── reports_router.py
├── frontend/                # واجهة الويب (HTML/CSS/JS — RTL + Dark Mode)
│   ├── index.html            # Dashboard
│   ├── login.html
│   ├── irrigation.html
│   ├── energy.html
│   ├── crops.html
│   ├── farm-map.html
│   ├── sensors.html
│   ├── ai.html
│   ├── reports.html
│   ├── users.html
│   └── assets/{css,js}
├── database/                 # ملاحظات ومخطط قاعدة البيانات
├── docs/                     # وثائق إضافية
└── README.md
```

---

## 2. القرارات الهندسية الرئيسية

**Backend: FastAPI بدل Flask/Django** — أداء أعلى للـ I/O غير المتزامن (مناسب لتدفقات بيانات IoT المستمرة)، وتوثيق Swagger تلقائي، وتكامل ممتاز مع Pydantic للتحقق من صحة البيانات القادمة من الحساسات.

**قاعدة البيانات: SQLite أثناء التطوير → PostgreSQL في الإنتاج** — نفس الكود يعمل مع الاثنين لأن SQLAlchemy يجرّد طبقة الاتصال؛ التبديل يتم فقط عبر متغير البيئة `DATABASE_URL`. اخترنا PostgreSQL للإنتاج لدعمه الأفضل للتزامن العالي (كتابة مستمرة من عشرات الحساسات) وأنواع بيانات جغرافية (PostGIS لاحقًا لخريطة المزرعة).

**نموذج بيانات موحّد للقراءات (`sensor_readings`)** بدل جدول منفصل لكل نوع حساس — يسمح بإضافة أنواع حساسات جديدة مستقبلاً دون تعديل مخطط قاعدة البيانات، وهو نمط شائع في أنظمة IoT (Time-series-friendly).

**RBAC عبر Dependency Injection في FastAPI** (`require_roles(...)`) بدل منطق صلاحيات متناثر — كل مسار يُصرّح بوضوح من يُسمح له بالوصول إليه، وهذا يسهّل المراجعة الأمنية لاحقًا.

**الواجهة الأمامية: HTML/CSS/JS خفيف بدل React في هذه المرحلة** — لضمان تحميل سريع جدًا وسهولة التشغيل حتى على أجهزة ضعيفة في مواقع ميدانية بإنترنت محدود (Offline-first). عند الحاجة لتفاعلية أعقد (مثل محرر خرائط متقدم)، يمكن تحويل وحدة محددة إلى React + Vite دون إعادة كتابة النظام بالكامل.

**وضع العرض التجريبي (Demo Mode)** — كل صفحة تحاول الاتصال بالـ API أولًا، وإن فشل (مثلاً أثناء العرض قبل تشغيل الخادم) تعرض بيانات تجريبية واقعية، بحيث تكون الواجهة قابلة للعرض فورًا لأصحاب القرار دون الحاجة لتشغيل الخادم.

---

## 3. التشغيل المحلي

### Backend
```bash
cd backend
pip install -r requirements.txt
python seed_data.py        # إنشاء الجداول + مستخدم admin/ChangeMe123!
uvicorn main:app --reload  # يعمل على http://localhost:8000
```
توثيق Swagger التفاعلي: `http://localhost:8000/docs`

### Frontend
افتح `frontend/login.html` مباشرة في المتصفح، أو قدّمه عبر خادم بسيط:
```bash
cd frontend
python -m http.server 5500
```

> **مهم أمنيًا:** غيّر `LGC_SECRET_KEY` وكلمة مرور `admin` الافتراضية فورًا قبل أي استخدام حقيقي.

---

## 4. طبقة IoT

المسار `POST /api/sensors/readings` جاهز لاستقبال بيانات من:
- **ESP32 / ESP8266**: عبر HTTP POST مباشر (WiFi) بصيغة JSON.
- **Raspberry Pi**: كوسيط (Gateway) يجمع من عدة حساسات محلية عبر MQTT/Modbus ثم يرسلها دفعة واحدة إلى الـ API.
- **MQTT / LoRa**: يُنصح بإضافة خدمة وسيطة (Bridge Service) صغيرة تشترك في موضوعات MQTT وتحوّل الرسائل إلى استدعاءات REST — هذا يفصل بروتوكول الحقل عن واجهة الـ API ويسهّل دعم بروتوكولات جديدة لاحقًا دون تعديل الـ backend الأساسي.

---

## 5. خارطة الطريق (المراحل القادمة)

| المرحلة | المحتوى |
|---|---|
| ✅ المرحلة 1 (الحالية) | الهيكل الكامل، قاعدة البيانات، REST API أساسي، لوحة تحكم وواجهات الوحدات العشر، مصادقة JWT + RBAC |
| المرحلة 2 | ربط فعلي بأجهزة ESP32/Raspberry Pi تجريبية، خدمة MQTT Bridge، تفعيل التخزين المتزامن (Offline Sync) |
| المرحلة 3 | تصدير تقارير PDF/Excel فعليًا (reportlab / openpyxl)، خريطة GPS تفاعلية حقيقية (Leaflet) |
| المرحلة 4 | نموذج تعلّم آلي فعلي لوحدة AI (تنبؤ الإنتاج، اكتشاف الأعطال) بدل القواعد المبسطة الحالية |
| المرحلة 5 | ترحيل الإنتاج إلى PostgreSQL، إعداد HTTPS/النشر، اختبارات أمان شاملة (Penetration Testing) |

---

## 6. الأمان (ملخص التنفيذ الحالي)

- **JWT Authentication** عبر `python-jose`، صلاحية التوكن 8 ساعات.
- **RBAC** على مستوى كل مسار API عبر `require_roles(...)`.
- **تشفير كلمات المرور** عبر bcrypt (`passlib`).
- **Rate Limiting** جاهز عبر `slowapi` (يُفعَّل تدريجيًا على المسارات الحساسة).
- **CORS** مضبوط للسماح بكل النطاقات في التطوير فقط — **يجب تقييده في الإنتاج**.
- **Audit Logs**: يُنصح بإضافة جدول `audit_logs` في المرحلة القادمة لتسجيل كل عملية حساسة (تغيير صلاحيات، حذف بيانات، تشغيل ري يدوي) مع من نفّذها ومتى.
