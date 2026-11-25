"""
Database Depth Expansion, Enrichment & Verification Runner.
Ingests high-priority national depth schemes and enriches existing schemes with
complete eligibility conditions, required documents, application steps, and official URLs.
"""

import json
import os
import sys
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models.scheme import Scheme
from backend.models.condition import EligibilityCondition
from backend.models.document import RequiredDocument
from backend.models.step import ApplicationStep
from backend.models.source import OfficialSource
from backend.services.scheme_importer import SchemeImporterService
from backend.services.portal_health_monitor import PortalHealthMonitorService

ENRICHMENT_DATA = {
    "assam-arundhati-gold": {
        "conditions": [
            {
                "field_name": "age",
                "operator": "gte",
                "field_value": "18",
                "description_en": "Bride must be at least 18 years of age at marriage registration",
                "description_ta": "மணமகள் திருமணப் பதிவின் போது குறைந்தபட்சம் 18 வயது பூர்த்தியடைந்திருக்க வேண்டும்",
                "description_hi": "विवाह पंजीकरण के समय दुल्हन की न्यूनतम आयु 18 वर्ष होनी चाहिए",
                "description_ml": "വിവാഹ രജിസ്ട്രേഷൻ സമയത്ത് വധുവിന് കുറഞ്ഞത് 18 വയസ്സ് ഉണ്ടായിരിക്കണം"
            },
            {
                "field_name": "income",
                "operator": "lte",
                "field_value": "500000",
                "description_en": "Total annual family income must not exceed ₹5,00,000",
                "description_ta": "குடும்ப ஆண்டு வருமானம் ₹5 லட்சத்திற்குள் இருக்க வேண்டும்",
                "description_hi": "कुल वार्षिक पारिवारिक आय ₹5,00,000 से अधिक नहीं होनी चाहिए",
                "description_ml": "കുടുംബ വാർഷിക വരുമാനം ₹5 ലക്ഷത്തിൽ താഴെയായിരിക്കണം"
            }
        ],
        "documents": [
            {
                "document_name_en": "Marriage Registration Certificate under Special Marriage Act 1954",
                "document_name_ta": "சிறப்பு திருமண சட்டத்தின் கீழ் திருமணப் பதிவு சான்றிதழ்",
                "is_mandatory": True,
                "issuing_authority": "Senior Sub-Registrar / Marriage Officer Assam"
            },
            {
                "document_name_en": "Income Certificate",
                "document_name_ta": "வருமானச் சான்றிதழ்",
                "is_mandatory": True,
                "issuing_authority": "Circle Officer Assam"
            },
            {
                "document_name_en": "Educational Certificate (Minimum 10th Pass)",
                "document_name_ta": "10ஆம் வகுப்பு தேர்ச்சி சான்றிதழ்",
                "is_mandatory": False,
                "issuing_authority": "SEBA / Recognized Board"
            }
        ],
        "application_url": "https://revenueassam.nic.in/arundhati"
    },
    "punjab-ashirwad": {
        "conditions": [
            {
                "field_name": "state",
                "operator": "eq",
                "field_value": "Punjab",
                "description_en": "Must be a permanent resident of Punjab",
                "description_ta": "பஞ்சாபின் நிரந்தரக் குடியுரிமை கொண்டவராக இருக்க வேண்டும்",
                "description_hi": "पंजाब का स्थायी निवासी होना अनिवार्य है",
                "description_ml": "പഞ്ചാബിലെ സ്ഥിരതാമസക്കാരനായിരിക്കണം"
            },
            {
                "field_name": "income",
                "operator": "lte",
                "field_value": "32790",
                "description_en": "Annual family income must not exceed ₹32,790",
                "description_ta": "ஆண்டு குடும்ப வருமானம் ₹32,790க்கு மிகாமல் இருக்க வேண்டும்",
                "description_hi": "वार्षिक पारिवारिक आय ₹32,790 से कम होनी चाहिए",
                "description_ml": "കുടുംബ വാർഷിക വരുമാനം ₹32,790 ൽ താഴെയായിരിക്കണം"
            },
            {
                "field_name": "age",
                "operator": "gte",
                "field_value": "18",
                "description_en": "Girl must be at least 18 years of age at the time of marriage",
                "description_ta": "மணமகள் திருமணத்தின் போது 18 வயது பூர்த்தியடைந்திருக்க வேண்டும்",
                "description_hi": "विवाह के समय लड़की की आयु 18 वर्ष या अधिक होनी चाहिए",
                "description_ml": "പെൺകുട്ടിക്ക് 18 വയസ്സ് തികഞ്ഞിരിക്കണം"
            }
        ],
        "documents": [
            {
                "document_name_en": "Domicile / Residence Certificate of Punjab",
                "document_name_ta": "பஞ்சாப் இருப்பிடச் சான்றிதழ்",
                "is_mandatory": True,
                "issuing_authority": "Tehsildar Punjab"
            },
            {
                "document_name_en": "Caste / Minority Certificate (SC / BC / Christian / Muslim / Widow daughter)",
                "document_name_ta": "ஜாதி / சிறுபான்மையினர் சான்றிதழ்",
                "is_mandatory": True,
                "issuing_authority": "Tehsildar Punjab"
            },
            {
                "document_name_en": "Income Certificate",
                "document_name_ta": "வருமானச் சான்றிதழ்",
                "is_mandatory": True,
                "issuing_authority": "Tehsildar / SDO"
            }
        ],
        "application_url": "https://punjab.gov.in"
    },
    "meghalaya-mhis-health": {
        "conditions": [
            {
                "field_name": "state",
                "operator": "eq",
                "field_value": "Meghalaya",
                "description_en": "Must be a resident of Meghalaya not in state/central government service",
                "description_ta": "மேகாலயாவில் வசிப்பவராக இருக்க வேண்டும் (அரசு ஊழியர்கள் தவிர்த்து)",
                "description_hi": "मेघालय का निवासी होना चाहिए (सरकारी कर्मचारियों को छोड़कर)",
                "description_ml": "മേഘാലയയിലെ താമസക്കാരനായിരിക്കണം"
            }
        ],
        "documents": [
            {
                "document_name_en": "EPIC / Voter ID Card",
                "document_name_ta": "வாக்காளர் அடையாள அட்டை",
                "is_mandatory": True,
                "issuing_authority": "Election Commission of India"
            },
            {
                "document_name_en": "Ration Card (NFSA or Non-NFSA)",
                "document_name_ta": "குடும்ப அட்டை",
                "is_mandatory": True,
                "issuing_authority": "Food & Civil Supplies Meghalaya"
            }
        ],
        "application_url": "https://mhis.org.in"
    },
    "mizoram-mshcs-health": {
        "conditions": [
            {
                "field_name": "state",
                "operator": "eq",
                "field_value": "Mizoram",
                "description_en": "Must be a permanent resident of Mizoram holding valid voter card or indigenous certificate",
                "description_ta": "மிசோரமில் நிரந்தரமாக வசிப்பவராக இருக்க வேண்டும்",
                "description_hi": "मिजोरम का स्थायी निवासी होना आवश्यक है",
                "description_ml": "മിസോറാമിലെ സ്ഥിരതാമസക്കാരനായിരിക്കണം"
            }
        ],
        "documents": [
            {
                "document_name_en": "Tribal / Indigenous Certificate",
                "document_name_ta": "பழங்குடியின சான்றிதழ்",
                "is_mandatory": True,
                "issuing_authority": "Deputy Commissioner Mizoram"
            },
            {
                "document_name_en": "Ration Card / Voter ID",
                "document_name_ta": "ரேஷன் கார்டு",
                "is_mandatory": True,
                "issuing_authority": "Civil Supplies Mizoram"
            }
        ],
        "application_url": "https://mshcs.mizoram.gov.in"
    },
    "nagaland-cmhis-health": {
        "conditions": [
            {
                "field_name": "state",
                "operator": "eq",
                "field_value": "Nagaland",
                "description_en": "Must be an Indigenous Inhabitant or permanent resident of Nagaland",
                "description_ta": "நாகாலாந்தின் பூர்வீக குடிமகனாக இருக்க வேண்டும்",
                "description_hi": "नागालैंड का मूल निवासी होना आवश्यक है",
                "description_ml": "നാഗാലാൻഡിലെ തദ്ദേശീയനായിരിക്കണം"
            }
        ],
        "documents": [
            {
                "document_name_en": "Indigenous Inhabitant Certificate (IIC)",
                "document_name_ta": "பூர்வீக குடியுரிமை சான்றிதழ்",
                "is_mandatory": True,
                "issuing_authority": "Deputy Commissioner Nagaland"
            },
            {
                "document_name_en": "Ration Card / Aadhaar",
                "document_name_ta": "ஆதார் / குடும்ப அட்டை",
                "is_mandatory": True,
                "issuing_authority": "UIDAI / Civil Supplies"
            }
        ],
        "application_url": "https://cmhis.nagaland.gov.in"
    },
    "rajasthan-chiranjeevi-health": {
        "conditions": [
            {
                "field_name": "state",
                "operator": "eq",
                "field_value": "Rajasthan",
                "description_en": "Must be a resident of Rajasthan enrolled in Jan Aadhaar",
                "description_ta": "ராஜஸ்தானில் வசித்து ஜன் ஆதார் அட்டை கொண்டவராக இருக்க வேண்டும்",
                "description_hi": "राजस्थान का निवासी एवं जन आधार कार्ड धारक होना आवश्यक है",
                "description_ml": "രാജസ്ഥാനിലെ ജന ആധാർ കാർഡുള്ള താമസക്കാരനായിരിക്കണം"
            }
        ],
        "documents": [
            {
                "document_name_en": "Jan Aadhaar Card",
                "document_name_ta": "ஜன் ஆதார் அட்டை",
                "is_mandatory": True,
                "issuing_authority": "Planning Department Rajasthan"
            },
            {
                "document_name_en": "Aadhaar Card",
                "document_name_ta": "ஆதார் அட்டை",
                "is_mandatory": True,
                "issuing_authority": "UIDAI"
            }
        ],
        "application_url": "https://chiranjeevi.rajasthan.gov.in"
    },
    "an-health-anhis": {
        "conditions": [
            {
                "field_name": "state",
                "operator": "eq",
                "field_value": "Andaman and Nicobar Islands",
                "description_en": "Must be an Islander / permanent resident of Andaman and Nicobar Islands",
                "description_ta": "அந்தமான் நிக்கோபார் தீவுகளின் நிரந்தர குடிமகனாக இருக்க வேண்டும்",
                "description_hi": "अंडमान एवं निकोबार द्वीप समूह का स्थायी निवासी/आइसलैंडर होना चाहिए",
                "description_ml": "ആൻഡമാൻ നിക്കോബാർ ദ്വീപുകളിലെ സ്ഥിരതാമസക്കാരനായിരിക്കണം"
            }
        ],
        "documents": [
            {
                "document_name_en": "Islander Card / Local Certificate",
                "document_name_ta": "தீவுவாசி அடையாள அட்டை",
                "is_mandatory": True,
                "issuing_authority": "Deputy Commissioner Andaman"
            },
            {
                "document_name_en": "Aadhaar Card",
                "document_name_ta": "ஆதார் அட்டை",
                "is_mandatory": True,
                "issuing_authority": "UIDAI"
            }
        ],
        "application_url": "https://dhs.andaman.gov.in"
    }
}

def main():
    print("=== Starting National Scheme Depth, Enrichment & Verification ===")
    db: Session = SessionLocal()

    # 1. Ingest newly researched depth schemes from JSON
    json_path = os.path.join(os.path.dirname(__file__), "national_depth_and_monitoring.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            depth_records = json.load(f)
        print(f"Loaded {len(depth_records)} new depth schemes from {json_path}")
        report = SchemeImporterService.import_records(db=db, records=depth_records)
        print(f"Depth Ingestion: Processed {report['total_processed']}, Inserted {report['imported']}, Skipped {report['duplicates']}")

    # 2. Enrich existing schemes that had 0 conditions
    print("\n--- Enriching Schemes with missing criteria ---")
    enriched_count = 0
    for s_id, data in ENRICHMENT_DATA.items():
        scheme = db.query(Scheme).filter(Scheme.id == s_id).first()
        if not scheme:
            continue

        # Add conditions if none exist
        if len(scheme.conditions) == 0:
            for c_idx, c_info in enumerate(data.get("conditions", [])):
                cond = EligibilityCondition(
                    scheme_id=s_id,
                    field_name=c_info["field_name"],
                    operator=c_info["operator"],
                    expected_value=c_info["field_value"],
                    description_en=c_info["description_en"],
                    description_ta=c_info["description_ta"]
                )
                db.add(cond)
            print(f"Enriched {s_id} with {len(data.get('conditions', []))} conditions")
            enriched_count += 1

        # Add documents if none exist
        if len(scheme.documents) == 0:
            for d_info in data.get("documents", []):
                doc = RequiredDocument(
                    scheme_id=s_id,
                    name_en=d_info["document_name_en"],
                    name_ta=d_info["document_name_ta"],
                    is_mandatory=d_info.get("is_mandatory", True),
                    issuing_authority_en=d_info.get("issuing_authority", "")
                )
                db.add(doc)

        # Update official source application_url and verification status
        if scheme.source:
            if data.get("application_url"):
                scheme.source.application_url = data["application_url"]
            scheme.source.verification_status = "Verified"

    db.commit()
    print(f"Successfully enriched {enriched_count} schemes with structured criteria.")

    # 3. Audit all schemes and verify status
    print("\n--- Auditing All Scheme Records and Updating Verification Statuses ---")
    all_schemes = db.query(Scheme).all()
    verified_count = 0
    partially_verified_count = 0
    needs_review_count = 0

    for s in all_schemes:
        # Evaluate criteria completeness
        has_conditions = len(s.conditions) > 0
        has_documents = len(s.documents) > 0
        has_source = s.source is not None and bool(s.source.portal_url)

        if has_conditions and has_documents and has_source:
            status = "Verified"
            verified_count += 1
        elif has_source and (has_conditions or has_documents):
            status = "Partially Verified"
            partially_verified_count += 1
        else:
            status = "Needs Review"
            needs_review_count += 1

        if s.source:
            s.source.verification_status = status
            if not s.source.application_url and s.steps:
                online_step = next((st for st in s.steps if st.portal_url), None)
                if online_step:
                    s.source.application_url = online_step.portal_url

    db.commit()

    print(f"\nTotal Schemes in Database: {len(all_schemes)}")
    print(f"Verified Records: {verified_count}")
    print(f"Partially Verified Records: {partially_verified_count}")
    print(f"Needs Review Records: {needs_review_count}")

    # 4. Run baseline portal health check
    print("\n--- Running Baseline Official Portal Health Monitor Check ---")
    summary = PortalHealthMonitorService.run_health_checks(db=db, max_workers=5)
    print(f"Health Check Summary: {summary.total_checked} Portals Checked, {summary.available_count} Available, {summary.unavailable_count} Unavailable, {summary.redirects_detected} Redirects, {summary.domain_migrations_detected} Migrations Detected.")

    db.close()
    print("\n=== Expansion, Enrichment & Verification Completed Successfully ===")

if __name__ == "__main__":
    main()
