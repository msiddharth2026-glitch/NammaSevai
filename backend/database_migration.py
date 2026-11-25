import logging
from sqlalchemy import text
from .database import engine, SessionLocal
from .data.geography import INDIAN_STATES, INDIAN_UNION_TERRITORIES

logger = logging.getLogger("nammasevai.migration")

def run_database_migrations():
    """
    Applies backward-compatible schema migrations for National Scheme Expansion.
    Safely adds missing columns and indexes to SQLite / PostgreSQL without data loss.
    """
    logger.info("Checking database schema and applying migrations...")
    dialect = engine.dialect.name

    with engine.connect() as conn:
        # 1. Inspect existing columns in 'schemes' table
        existing_scheme_cols = set()
        if dialect == "sqlite":
            res = conn.execute(text("PRAGMA table_info(schemes)"))
            for row in res:
                existing_scheme_cols.add(row[1])
        else:
            res = conn.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'schemes'"
            ))
            for row in res:
                existing_scheme_cols.add(row[0])

        # New columns for 'schemes'
        new_scheme_columns = [
            ("level", "VARCHAR(32) DEFAULT 'State' NOT NULL"),
            ("state", "VARCHAR(64) DEFAULT 'Tamil Nadu'"),
            ("scheme_status", "VARCHAR(32) DEFAULT 'Active' NOT NULL"),
            ("keywords", "TEXT"),
            ("target_beneficiaries", "VARCHAR(255)"),
            ("target_beneficiaries_ta", "VARCHAR(255)"),
            ("name_hi", "VARCHAR(255)"),
            ("name_ml", "VARCHAR(255)"),
            ("department_hi", "VARCHAR(255)"),
            ("department_ml", "VARCHAR(255)"),
            ("benefit_summary_hi", "TEXT"),
            ("benefit_summary_ml", "TEXT"),
            ("description_hi", "TEXT"),
            ("description_ml", "TEXT"),
        ]

        for col_name, col_type in new_scheme_columns:
            if col_name not in existing_scheme_cols:
                logger.info(f"Adding column '{col_name}' to 'schemes' table...")
                try:
                    conn.execute(text(f"ALTER TABLE schemes ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
                except Exception as e:
                    logger.warning(f"Could not add column '{col_name}': {e}")

        # 2. Inspect existing columns in 'official_sources' table
        existing_source_cols = set()
        if dialect == "sqlite":
            res = conn.execute(text("PRAGMA table_info(official_sources)"))
            for row in res:
                existing_source_cols.add(row[1])
        else:
            res = conn.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'official_sources'"
            ))
            for row in res:
                existing_source_cols.add(row[0])

        new_source_columns = [
            ("source_publication_date", "VARCHAR(32)"),
            ("is_official", "BOOLEAN DEFAULT 1"),
            ("source_category", "VARCHAR(64) DEFAULT 'Official Portal'"),
            ("ministry_department", "VARCHAR(255)"),
            ("assigned_administrator", "VARCHAR(128) DEFAULT 'admin@nammasevai.gov.in'"),
            ("last_content_check", "VARCHAR(64)"),
            ("last_detected_modification", "VARCHAR(64)"),
            ("content_fingerprint", "VARCHAR(64)"),
            ("content_length", "INTEGER"),
            ("last_known_excerpt", "TEXT"),
            ("monitoring_status", "VARCHAR(32) DEFAULT 'active'"),
        ]

        for col_name, col_type in new_source_columns:
            if col_name not in existing_source_cols:
                logger.info(f"Adding column '{col_name}' to 'official_sources' table...")
                try:
                    conn.execute(text(f"ALTER TABLE official_sources ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
                except Exception as e:
                    logger.warning(f"Could not add column '{col_name}': {e}")

        # 3. Create helpful indexes if on SQLite/PostgreSQL
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_schemes_level ON schemes(level)",
            "CREATE INDEX IF NOT EXISTS idx_schemes_state ON schemes(state)",
            "CREATE INDEX IF NOT EXISTS idx_schemes_status ON schemes(scheme_status)",
            "CREATE INDEX IF NOT EXISTS idx_schemes_category ON schemes(category)",
            "CREATE INDEX IF NOT EXISTS idx_schemes_is_active ON schemes(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_schemes_active_cat ON schemes(is_active, category)",
        ]
        for q in index_queries:
            try:
                conn.execute(text(q))
                conn.commit()
            except Exception as e:
                pass

    # 4. Normalize and update existing schemes geographical metadata
    db = SessionLocal()
    try:
        from .models.scheme import Scheme
        existing_schemes = db.query(Scheme).all()
        updated_count = 0

        for s in existing_schemes:
            # Central schemes classification
            is_central = any(k in s.id.lower() for k in ["pm-", "pmegp", "nsp-", "ayushman", "pmay"])
            
            needs_update = False
            if not getattr(s, "level", None) or s.level not in ("Central", "State", "Union Territory"):
                s.level = "Central" if is_central else "State"
                needs_update = True
                
            if not getattr(s, "state", None):
                s.state = "All India" if s.level == "Central" else "Tamil Nadu"
                needs_update = True

            if not getattr(s, "scheme_status", None):
                s.scheme_status = "Active"
                needs_update = True

            if needs_update:
                updated_count += 1

        if updated_count > 0:
            db.commit()
            logger.info(f"Normalized geographical metadata for {updated_count} existing schemes.")
    except Exception as e:
        logger.error(f"Error updating existing scheme metadata: {e}")
        db.rollback()
    finally:
        db.close()

    logger.info("Database migration check completed successfully.")

if __name__ == "__main__":
    run_database_migrations()
