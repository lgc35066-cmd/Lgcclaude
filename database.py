"""
طبقة الاتصال بقاعدة البيانات.
- أثناء التطوير: SQLite (ملف محلي lgc_farm.db)
- عند الانتقال للإنتاج: غيّر DATABASE_URL إلى رابط PostgreSQL
  مثال: postgresql+psycopg2://user:password@localhost:5432/lgc_farm
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lgc_farm.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
