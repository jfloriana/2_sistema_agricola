from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

URL_BASE_DATOS = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.aephgcnbsomypsedvtyk:nosetudime0302@aws-1-us-east-2.pooler.supabase.com:5432/postgres"
)

engine = create_engine(URL_BASE_DATOS)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()