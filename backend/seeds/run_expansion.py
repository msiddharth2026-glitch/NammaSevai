"""
National Scheme Data Expansion Script
Curates and ingests verified government welfare schemes covering:
1. Central Government of India (all 12 welfare sectors)
2. All 28 Indian States
3. All 8 Union Territories

Uses official government sources: MyScheme, India.gov.in, and official Ministry/State portals.
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models.scheme import Scheme
from backend.models.source import OfficialSource
from backend.services.scheme_importer import SchemeImporterService

def run_expansion():
    db = SessionLocal()
    print("Starting National Government Scheme Data Expansion...")

    # 1. Reclassify historical misclassified schemes
    pmegp = db.query(Scheme).filter(Scheme.id == "pmegp-msme-business").first()
    if pmegp:
        pmegp.level = "Central"
        pmegp.state = "All India"
        pmegp.coverage_type = "Central Government / Centrally Sponsored"
        print("Reclassified pmegp-msme-business to Central / All India")

    nsp = db.query(Scheme).filter(Scheme.id == "nsp-post-matric-scholarship").first()
    if nsp:
        nsp.level = "Central"
        nsp.state = "All India"
        nsp.coverage_type = "Central Government / Centrally Sponsored"
        print("Reclassified nsp-post-matric-scholarship to Central / All India")

    db.commit()

    # Load authentic expansion schemes
    expansion_file = os.path.join(os.path.dirname(__file__), "national_expansion_records.json")
    with open(expansion_file, "r", encoding="utf-8") as f:
        records = json.load(f)

    print(f"Loaded {len(records)} verified expansion schemes from {expansion_file}")

    report = SchemeImporterService.import_records(db=db, records=records, allow_overwrite=True)

    print("\n--- IMPORT AUDIT REPORT ---")
    print(f"Total Processed: {report['total_processed']}")
    print(f"Imported / Inserted: {report['imported']}")
    print(f"Existing Skipped (Duplicates): {report['duplicates']}")
    print(f"Invalid Records: {report['invalid']}")
    print(f"Failed Records: {report['failed']}")

    # Verification of database state
    all_schemes = db.query(Scheme).all()
    central_count = sum(1 for s in all_schemes if s.level == "Central")
    state_count = sum(1 for s in all_schemes if s.level == "State")
    ut_count = sum(1 for s in all_schemes if s.level == "Union Territory")

    states_represented = sorted(list(set(s.state for s in all_schemes if s.level == "State" and s.state)))
    uts_represented = sorted(list(set(s.state for s in all_schemes if s.level == "Union Territory" and s.state)))

    print("\n--- POST-EXPANSION JURISDICTION COVERAGE ---")
    print(f"Total Database Schemes: {len(all_schemes)}")
    print(f"Central Schemes: {central_count}")
    print(f"State Schemes: {state_count} (across {len(states_represented)} States)")
    print(f"Union Territory Schemes: {ut_count} (across {len(uts_represented)} UTs)")
    print(f"States Represented ({len(states_represented)}/28): {', '.join(states_represented)}")
    print(f"UTs Represented ({len(uts_represented)}/8): {', '.join(uts_represented)}")

    db.close()

if __name__ == "__main__":
    run_expansion()
