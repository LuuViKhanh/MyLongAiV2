from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os

DATABASE_URL = settings.DATABASE_URL or os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Please configure it in environment variables.")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
