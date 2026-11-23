from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# PostgreSQL Connection URL (Defaults to localhost, configurable via env)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://nammasevai_user:password@localhost:5432/nammasevai_db"
)

# SQLite fallback for local development without active PostgreSQL server
if not DATABASE_URL.startswith("postgresql"):
    DATABASE_URL = "sqlite:///./nammasevai.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
