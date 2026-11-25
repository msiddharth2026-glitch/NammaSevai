import logging
from sqlalchemy import text
from ..database import engine, Base
from ..models.source import OfficialSource, DetectedSchemeChange, SchemeVersionHistory

logger = logging.getLogger("nammasevai.migrations")

def run_database_migrations():
    """
    Safely executes backward-compatible schema migrations on startup.
    Creates new tables and adds missing columns without altering or deleting existing scheme records.
    """
    try:
        # 1. Create all missing tables (detected_scheme_changes, scheme_version_history, etc.)
        Base.metadata.create_all(bind=engine)
        
        # 2. Check and add new columns to official_sources
        with engine.connect() as conn:
            res = conn.execute(text("PRAGMA table_info(official_sources)")).fetchall()
            existing_cols = {row[1] for row in res}

            new_cols = [
                ("source_category", "VARCHAR(64) DEFAULT 'Official Portal'"),
                ("ministry_department", "VARCHAR(255)"),
                ("assigned_administrator", "VARCHAR(128) DEFAULT 'admin@nammasevai.gov.in'"),
                ("last_content_check", "VARCHAR(64)"),
                ("last_detected_modification", "VARCHAR(64)"),
                ("content_fingerprint", "VARCHAR(64)"),
                ("content_length", "INTEGER"),
                ("last_known_excerpt", "TEXT"),
                ("monitoring_status", "VARCHAR(32) DEFAULT 'active'")
            ]

            for col_name, col_type in new_cols:
                if col_name not in existing_cols:
                    logger.info(f"Adding column '{col_name}' to official_sources table.")
                    conn.execute(text(f"ALTER TABLE official_sources ADD COLUMN {col_name} {col_type}"))
                    conn.commit()

        logger.info("Database migrations completed successfully.")
    except Exception as e:
        logger.error(f"Database migration error: {e}")

if __name__ == "__main__":
    run_database_migrations()
