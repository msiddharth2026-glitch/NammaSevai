import os
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings

logger = logging.getLogger("nammasevai.database")

db_url = settings.DATABASE_URL

# Support Vercel serverless writable storage (/tmp) for zero-config deployments
if os.getenv("VERCEL") and db_url.startswith("sqlite"):
    db_url = "sqlite:////tmp/nammasevai.db"

# Check if PostgreSQL connection can be established, otherwise fallback to SQLite
connect_args = {}
engine_kwargs = {}

if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
else:
    # PostgreSQL production pooling settings
    engine_kwargs.update({
        "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
        "pool_pre_ping": True,
        "pool_recycle": 300
    })
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
        engine_kwargs.clear()

engine = create_engine(db_url, connect_args=connect_args, **engine_kwargs)

# Optimize SQLite performance under concurrent multi-user load
if db_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA journal_mode = WAL")
            cursor.execute("PRAGMA busy_timeout = 5000")
            cursor.execute("PRAGMA synchronous = NORMAL")
            cursor.execute("PRAGMA cache_size = -64000")
        except Exception:
            pass
        finally:
            cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
