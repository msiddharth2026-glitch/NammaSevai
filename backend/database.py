import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings

logger = logging.getLogger("nammasevai.database")

db_url = settings.DATABASE_URL

# Check if PostgreSQL connection can be established, otherwise fallback to SQLite
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
else:
    # Try testing PostgreSQL connection
    try:
        test_engine = create_engine(db_url, connect_args={"connect_timeout": 2})
        with test_engine.connect() as conn:
            pass
        logger.info(f"Connected to PostgreSQL database: {db_url}")
    except Exception as e:
        logger.warning(
            f"Could not connect to PostgreSQL ({e}). "
            f"Falling back to local SQLite database for development/testing."
        )
        db_url = "sqlite:///./nammasevai.db"
        connect_args["check_same_thread"] = False

engine = create_engine(db_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
