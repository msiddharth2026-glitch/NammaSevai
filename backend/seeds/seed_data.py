import logging
from sqlalchemy.orm import Session
from ..database import SessionLocal, engine, Base
from ..models.scheme import Scheme
from ..models.condition import EligibilityCondition
from ..models.document import RequiredDocument
from ..models.step import ApplicationStep
from ..models.source import OfficialSource

logger = logging.getLogger("nammasevai.seed")

SCHEMES_SEED = [
    {
        "id": "pudhumai-penn",
        "name": "Moovalur Ramamirtham Ammaiyar Higher Education Assurance Scheme (Pudhumai Penn)",
        "name_ta": "மூவலூர் ராமாமிர்தம் அம்மையார் புதுமைப் பெண் திட்டம்",
        "department": "Social Welfare and Women Empowerment Department",
        "department_ta": "சமூக நலன் மற்றும் மகளிர் உரிமைத் துறை",
        "category": "education",
        "beneficiary_type": "Girl students joining undergraduate/diploma courses",
        "beneficiary_type_ta": "அரசுப் பள்ளியில் படித்து கல்லூரி சேரும் மாணவிகள்",
        "benefit_summary": "₹1,000 per month deposited directly into bank account until graduation",
        "benefit_summary_ta": "கல்லூரி படிப்பு முடியும் வரை மாதம் ₹1,000 நேரடி வங்கி வரவு",
        "benefit_amount": "₹1,000 / month",
        "description": "Financial assistance to encourage female students who studied from 6th to 12th standard in Tamil Nadu government schools to pursue higher education without financial constraints.",
        "description_ta": "தமிழ்நாடு அரசுப் பள்ளிகளில் 6 முதல் 12-ம் வகுப்பு வரை பயின்று உயர்கல்வியில் (டிகிரி, பாலிடெக்னிக், தொழிற்கல்வி) சேரும் மாணவிகளுக்கு மாதம் ₹1,000 உதவித்தொகை வழங்கும் திட்டம்.",
        "conditions": [
            {
                "field_name": "gender",
                "operator": "eq",
                "expected_value": "female",
                "is_mandatory": True,
                "description_en": "Applicant must be a female student",
                "description_ta": "விண்ணப்பதாரர் மாணவியாக (பெண்) இருக்க வேண்டும்",
                "prompt_question_en": "Are you a female student?",
                "prompt_question_ta": "நீங்கள் மாணவியா?"
            },
            {
                "field_name": "school_type",
                "operator": "eq",
                "expected_value": "government",
                "is_mandatory": True,
                "description_en": "Must have studied Classes 6 to 12 in Tamil Nadu Government schools",
                "description_ta": "6 முதல் 12-ம் வகுப்பு வரை தமிழ்நாடு அரசுப் பள்ளிகளில் படித்திருக்க வேண்டும்",
                "prompt_question_en": "Did you study in a Tamil Nadu Government school from 6th to 12th standard?",
                "prompt_question_ta": "நீங்கள் 6 முதல் 12-ம் வகுப்பு வரை தமிழ்நாடு அரசுப் பள்ளியில் படித்தீர்களா?"
            },
            {
                "field_name": "occupation",
                "operator": "eq",
                "expected_value": "student",
                "is_mandatory": True,
                "description_en": "Enrolled in recognized higher education college / university",
                "description_ta": "அங்கீகரிக்கப்பட்ட கல்லூரியில் பட்டப்படிப்பு அல்லது பட்டயப்படிப்பு பயில வேண்டும்",
                "prompt_question_en": "Are you currently enrolled in a college degree or diploma course?",
                "prompt_question_ta": "நீங்கள் தற்போது கல்லூரியில் பட்டப்படிப்பு அல்லது டிப்ளமோ பயில்கிறீர்களா?"
            }
        ],
        "documents": [
            {
                "name_en": "Aadhaar Card",
                "name_ta": "ஆதார் அட்டை",
                "is_mandatory": True,
                "issuing_authority_en": "UIDAI",
                "issuing_authority_ta": "இந்திய தனித்துவ அடையாள ஆணையம்",
                "description_en": "Must be linked to student's bank account",
                "description_ta": "மாணவியின் சொந்த வங்கிக் கணக்குடன் இணைக்கப்பட்டிருக்க வேண்டும்"
            },
            {
                "name_en": "10th & 12th Marksheet",
                "name_ta": "10 மற்றும் 12-ம் வகுப்பு மதிப்பெண் சான்றிதழ்",
                "is_mandatory": True,
                "issuing_authority_en": "Directorate of Government Examinations, TN",
                "issuing_authority_ta": "அரசுத் தேர்வுகள் இயக்ககம், தமிழ்நாடு"
            },
            {
                "name_en": "Govt School Study Bonafide Certificate",
                "name_ta": "அரசுப் பள்ளி பயின்றதற்கான சான்றிதழ் (Bonafide)",
                "is_mandatory": True,
                "issuing_authority_en": "Headmaster of respective Government School",
                "issuing_authority_ta": "படித்த அரசுப் பள்ளியின் தலைமை ஆசிரியர்"
            },
            {
                "name_en": "College Admission ID / Bonafide",
                "name_ta": "கல்லூரி சேர்க்கை அட்டை / பயிலும் சான்றிதழ்",
                "is_mandatory": True,
                "issuing_authority_en": "College Principal / Registrar",
                "issuing_authority_ta": "கல்லூரி முதல்வர் / பதிவாளர்"
            },
            {
                "name_en": "Bank Passbook with IFSC",
                "name_ta": "வங்கி சேமிப்புக் கணக்கு புத்தகம்",
                "is_mandatory": True,
                "issuing_authority_en": "Scheduled Commercial Bank",
                "issuing_authority_ta": "அங்கீகரிக்கப்பட்ட வங்கி"
            }
        ],
        "steps": [
            {
                "step_number": 1,
                "mode": "online",
                "title_en": "College Nodal Officer Enrollment",
                "title_ta": "கல்லூரி ஒருங்கிணைப்பாளர் மூலம் பதிவு",
                "description_en": "During college admission cycle, submit bonafide certificates to your college nodal officer who registers you on penkalvi.tn.gov.in.",
                "description_ta": "கல்லூரி சேர்க்கையின் போது penkalvi.tn.gov.in தளத்தில் கல்லூரி ஒருங்கிணைப்பாளர் மூலம் விண்ணப்பம் பதிவு செய்யப்படும்.",
                "portal_url": "https://www.penkalvi.tn.gov.in"
            },
            {
                "step_number": 2,
                "mode": "online",
                "title_en": "Social Welfare Department Verification",
                "title_ta": "சமூக நலத்துறை சரிபார்ப்பு",
                "description_en": "The Social Welfare Department verifies student school records via EMIS portal integration.",
                "description_ta": "பள்ளி கல்வித்துறையின் EMIS தகவல் மூலம் மாணவி அரசுப் பள்ளியில் படித்த விவரம் சரிபார்க்கப்படும்."
            },
            {
                "step_number": 3,
                "mode": "both",
                "title_en": "Direct Benefit Transfer (DBT)",
                "title_ta": "நேரடி வங்கிப் பரிமாற்றம்",
                "description_en": "₹1,000 monthly aid is credited directly into the student's individual bank account until degree completion.",
                "description_ta": "கல்லூரி படிப்பு முடியும் வரை மாதம் ₹1,000 மாணவியின் வங்கிக் கணக்கில் நேரடியாக வரவு வைக்கப்படும்."
            }
        ],
        "source": {
            "source_name": "Tamil Nadu Social Welfare and Women Empowerment Department",
            "portal_url": "https://www.penkalvi.tn.gov.in",
            "verified_date": "2026-10-20",
            "verification_status": "verified",
            "helpline_number": "044-24351885 / CM Helpline 1100",
            "government_order_ref": "G.O. (Ms) No. 46, Social Welfare Dept"
        }
    },
    {
        "id": "kmut-magalir",
        "name": "Kalaignar Magalir Urimai Thittam (KMUT)",
        "name_ta": "கலைஞர் மகளிர் உரிமைத் திட்டம்",
        "department": "Special Programme Implementation & Revenue Department",
        "department_ta": "சிறப்புத் திட்டச் செயலாக்கம் மற்றும் வருவாய்த் துறை",
        "category": "women",
        "beneficiary_type": "Eligible female heads of family in Tamil Nadu",
        "beneficiary_type_ta": "குடும்பத் தலைவிகள் (பெண்கள்)",
        "benefit_summary": "₹1,000 monthly basic income guarantee directly credited to bank account",
        "benefit_summary_ta": "குடும்பத் தலைவிகளுக்கு மாதம் ₹1,000 உரிமைத் தொகை வங்கி வரவு",
        "benefit_amount": "₹1,000 / month",
        "description": "A flagship universal basic income program recognizing unpaid care work and providing economic independence to women heads of family across Tamil Nadu.",
        "description_ta": "குடும்பத் தலைவிகளின் உழைப்பை அங்கீகரித்து, அவர்களின் பொருளாதார சுதந்திரத்திற்காக மாதம் ₹1,000 வழங்கும் வரலாற்றுச் சிறப்புமிக்க திட்டம்.",
        "conditions": [
            {
                "field_name": "gender",
                "operator": "eq",
                "expected_value": "female",
                "is_mandatory": True,
                "description_en": "Female head of family named in the Smart Ration Card",
                "description_ta": "ஸ்மார்ட் ரேஷன் கார்டில் குடும்பத் தலைவியாக பெயர் இருக்க வேண்டும்",
                "prompt_question_en": "Are you registered as the female head of family on your smart ration card?",
                "prompt_question_ta": "உங்கள் குடும்ப அட்டையில் நீங்கள் குடும்பத் தலைவியாக உள்ளீர்களா?"
            },
            {
                "field_name": "age_min",
                "operator": "gte",
                "expected_value": "21",
                "is_mandatory": True,
                "description_en": "Applicant age must be 21 years or older",
                "description_ta": "விண்ணப்பதாரருக்கு 21 வயது பூர்த்தியாகியிருக்க வேண்டும்",
                "prompt_question_en": "Is your age 21 years or older?",
                "prompt_question_ta": "உங்கள் வயது 21 அல்லது அதற்கு மேற்பட்டதா?"
            },
            {
                "field_name": "income_max",
                "operator": "lte",
                "expected_value": "250000",
                "is_mandatory": True,
                "description_en": "Family annual income should be less than ₹2.5 Lakhs",
                "description_ta": "குடும்ப ஆண்டு வருமானம் ₹2.5 லட்சத்திற்கு மிகாமல் இருக்க வேண்டும்",
                "prompt_question_en": "Is your family's annual income below ₹2.5 Lakhs?",
                "prompt_question_ta": "உங்கள் குடும்ப ஆண்டு வருமானம் ₹2.5 லட்சத்திற்குள் உள்ளதா?"
            },
            {
                "field_name": "land_max_acres",
                "operator": "lte",
                "expected_value": "10",
                "is_mandatory": True,
                "description_en": "Owns less than 5 acres of wetland or 10 acres of dryland",
                "description_ta": "5 ஏக்கருக்கு குறைவான நன்செய் அல்லது 10 ஏக்கருக்கு குறைவான புன்செய் நிலம் இருக்க வேண்டும்"
            }
        ],
        "documents": [
            {
                "name_en": "Smart Family Ration Card",
                "name_ta": "ஸ்மார்ட் குடும்ப அட்டை",
                "is_mandatory": True,
                "issuing_authority_en": "Civil Supplies & Consumer Protection Dept, TN",
                "issuing_authority_ta": "உணவுப் பொருள் வழங்கல் மற்றும் நுகர்வோர் பாதுகாப்புத்துறை"
            },
            {
                "name_en": "Aadhaar Card",
                "name_ta": "ஆதார் அட்டை",
                "is_mandatory": True,
                "issuing_authority_en": "UIDAI"
            },
            {
                "name_en": "Electricity Consumer Number / Bill",
                "name_ta": "மின் நுகர்வோர் எண் / மின் இணைப்பு அட்டை",
                "is_mandatory": True,
                "issuing_authority_en": "TANGEDCO",
                "issuing_authority_ta": "தமிழ்நாடு மின் உற்பத்தி மற்றும் பகிர்மானக் கழகம்"
            },
            {
                "name_en": "Bank Passbook with Aadhaar linkage",
                "name_ta": "ஆதார் இணைக்கப்பட்ட வங்கி புத்தகம்",
                "is_mandatory": True,
                "issuing_authority_en": "Scheduled Bank / Post Office IPPB"
            }
        ],
        "steps": [
            {
                "step_number": 1,
                "mode": "both",
                "title_en": "Application Submission via e-Sevai / Camp",
                "title_ta": "இ-சேவை மையம் அல்லது சிறப்பு முகாமில் விண்ணப்பம்",
                "description_en": "Submit biometric application with Ration Card and Aadhaar at your designated fair price shop camp or e-Sevai center.",
                "description_ta": "நியாய விலைக் கடை முகாம்கள் அல்லது இ-சேவை மையத்தில் கைரேகை பதிவு செய்து விண்ணப்பிக்கவும்.",
                "portal_url": "https://kmut.tn.gov.in"
            },
            {
                "step_number": 2,
                "mode": "offline",
                "title_en": "Field Verification by Revenue Officials",
                "title_ta": "வருவாய்த் துறை கள ஆய்வு",
                "description_en": "Village Administrative Officer (VAO) and Revenue Inspector (RI) cross-verify land and electricity consumption guidelines.",
                "description_ta": "கிராம நிர்வாக அலுவலர் (VAO) மற்றும் வருவாய் ஆய்வாளர் தகுதி வரம்புகளை சரிபார்ப்பார்கள்."
            },
            {
                "step_number": 3,
                "mode": "online",
                "title_en": "Monthly ₹1,000 Disbursement",
                "title_ta": "மாதாந்திர ₹1,000 வரவு",
                "description_en": "Beneficiaries receive ₹1,000 on the 15th of every month directly to their Aadhaar-seeded bank account.",
                "description_ta": "ஒவ்வொரு மாதமும் 15-ம் தேதி வங்கி கணக்கில் ₹1,000 நேரடியாக வரவு வைக்கப்படும்."
            }
        ],
        "source": {
            "source_name": "Special Programme Implementation & Revenue Department, TN",
            "portal_url": "https://kmut.tn.gov.in",
            "verified_date": "2026-11-01",
            "verification_status": "verified",
            "helpline_number": "044-25619224 / CM Helpline 1100"
        }
    },
    {
        "id": "cmchis-health",
        "name": "Chief Minister's Comprehensive Health Insurance Scheme (CMCHIS)",
        "name_ta": "முதலமைச்சரின் விரிவான மருத்துவக் காப்பீட்டுத் திட்டம்",
        "department": "Health and Family Welfare Department",
        "department_ta": "மக்கள் நல்வாழ்வு மற்றும் குடும்ப நலத்துறை",
        "category": "health",
        "beneficiary_type": "Low-income families, daily wage earners, rural citizens",
        "beneficiary_type_ta": "ஏழை மற்றும் நடுத்தர குடும்பங்கள், அமைப்புசாரா தொழிலாளர்கள்",
        "benefit_summary": "Cashless medical treatment up to ₹5,00,000 per family per year",
        "benefit_summary_ta": "ஆண்டுக்கு ₹5 லட்சம் வரை கட்டணமில்லா சிகிச்சை காப்பீடு",
        "benefit_amount": "Up to ₹5,00,000 / family / year",
        "description": "Comprehensive cashless hospitalization and surgical treatment across empanelled government and top private hospitals for 1,500+ listed medical procedures.",
        "description_ta": "அரசு மற்றும் தனியார் மருத்துவமனைகளில் 1,500-க்கும் மேற்பட்ட அறுவை சிகிச்சைகள் மற்றும் தீவிர சிகிச்சைகளுக்கு குடும்பத்திற்கு ₹5 லட்சம் வரை கட்டணமில்லா மருத்துவ உதவி.",
        "conditions": [
            {
                "field_name": "income_max",
                "operator": "lte",
                "expected_value": "120000",
                "is_mandatory": True,
                "description_en": "Family annual income should be less than ₹1,20,000 (or registered unorganized worker)",
                "description_ta": "குடும்ப ஆண்டு வருமானம் ₹1,20,000-க்கு மிகாமல் இருக்க வேண்டும் (வருமானச் சான்றிதழ் தேவை)",
                "prompt_question_en": "Is your family's annual income below ₹1,20,000?",
                "prompt_question_ta": "உங்கள் குடும்ப ஆண்டு வருமானம் ₹1,20,000-க்குள் உள்ளதா?"
            }
        ],
        "documents": [
            {
                "name_en": "Smart Ration Card",
                "name_ta": "ஸ்மார்ட் குடும்ப அட்டை",
                "is_mandatory": True,
                "issuing_authority_en": "Civil Supplies Dept"
            },
            {
                "name_en": "Aadhaar Card for all family members",
                "name_ta": "குடும்ப உறுப்பினர்களின் ஆதார் அட்டைகள்",
                "is_mandatory": True,
                "issuing_authority_en": "UIDAI"
            },
            {
                "name_en": "Income Certificate",
                "name_ta": "வருமானச் சான்றிதழ்",
                "is_mandatory": True,
                "issuing_authority_en": "Tahsildar / Revenue Department",
                "issuing_authority_ta": "வட்டாட்சியர் / வருவாய்த் துறை"
            }
        ],
        "steps": [
            {
                "step_number": 1,
                "mode": "offline",
                "title_en": "Biometric Enrollment at District Collectorate",
                "title_ta": "மாவட்ட ஆட்சியர் அலுவலகத்தில் பதிவு",
                "description_en": "Visit CMCHIS center at the District Collectorate with family members, Ration card and Income certificate for biometric capture.",
                "description_ta": "குடும்ப உறுப்பினர்களுடன் மாவட்ட ஆட்சியர் அலுவலகத்தில் உள்ள CMCHIS மையத்தில் கைரேகை பதிவு செய்யவும்.",
                "portal_url": "https://www.cmchistn.com"
            },
            {
                "step_number": 2,
                "mode": "both",
                "title_en": "Smart Health Card Issuance",
                "title_ta": "மருத்துவ அட்டை பெறுதல்",
                "description_en": "Instant smart card with unique URN number is issued and activated immediately.",
                "description_ta": "தனித்துவ URN எண்ணுடன் கூடிய ஸ்மார்ட் மருத்துவ அட்டை உடனடியாக வழங்கப்படும்."
            },
            {
                "step_number": 3,
                "mode": "offline",
                "title_en": "Cashless Hospital Treatment",
                "title_ta": "கட்டணமில்லா சிகிச்சை பெறுதல்",
                "description_en": "Show card at the CMCHIS insurance desk at any empanelled hospital for cashless hospitalization up to ₹5,00,000.",
                "description_ta": "அங்கீகரிக்கப்பட்ட மருத்துவமனைகளில் உள்ள காப்பீட்டு பிரிவில் அட்டையைக் காட்டி ₹5 லட்சம் வரை கட்டணமின்றி சிகிச்சை பெறலாம்."
            }
        ],
        "source": {
            "source_name": "Tamil Nadu Health Systems Project (TNHSP)",
            "portal_url": "https://www.cmchistn.com",
            "verified_date": "2026-10-18",
            "verification_status": "verified",
            "helpline_number": "Toll Free: 1800 425 3993"
        }
    },
    {
        "id": "sewing-machine-welfare",
        "name": "Sathiyavani Muthu Ammaiyar Free Sewing Machine Scheme",
        "name_ta": "சத்தியவாணி முத்து அம்மையார் நினைவு இலவச தையல் இயந்திரம் திட்டம்",
        "department": "Social Welfare and Women Empowerment Department",
        "department_ta": "சமூக நலன் மற்றும் மகளிர் உரிமைத் துறை",
        "category": "women",
        "beneficiary_type": "Widows, destitute women, deserted wives, physically challenged women",
        "beneficiary_type_ta": "விதவைகள், ஆதரவற்ற பெண்கள், கணவரால் கைவிடப்பட்ட பெண்கள், மாற்றுத்திறனாளிகள்",
        "benefit_summary": "Free motorized / manual sewing machine for home-based self-employment",
        "benefit_summary_ta": "சுயதொழில் தொடங்க இலவச நவீன தையல் இயந்திரம் வழங்கப்படுகிறது",
        "benefit_amount": "Free Sewing Machine",
        "description": "Empowers destitute women, widows, and economically disadvantaged women by providing free sewing machines to earn a sustainable livelihood from home.",
        "description_ta": "பொருளாதாரத்தில் பின்தங்கிய பெண்கள், விதவைகள் மற்றும் கணவரால் கைவிடப்பட்ட பெண்களுக்கு தையல் மூலம் வாழ்வாதாரம் பெற இலவச தையல் இயந்திரம் வழங்கும் திட்டம்.",
        "conditions": [
            {
                "field_name": "gender",
                "operator": "eq",
                "expected_value": "female",
                "is_mandatory": True,
                "description_en": "Applicant must be female",
                "description_ta": "பெண்ணாக இருக்க வேண்டும்"
            },
            {
                "field_name": "age_min",
                "operator": "gte",
                "expected_value": "20",
                "is_mandatory": True,
                "description_en": "Age must be at least 20 years",
                "description_ta": "குறைந்தபட்சம் 20 வயது பூர்த்தியாகியிருக்க வேண்டும்"
            },
            {
                "field_name": "age_max",
                "operator": "lte",
                "expected_value": "40",
                "is_mandatory": True,
                "description_en": "Age must not exceed 40 years",
                "description_ta": "அதிகபட்சம் 40 வயதுக்குள் இருக்க வேண்டும்"
            },
            {
                "field_name": "income_max",
                "operator": "lte",
                "expected_value": "72000",
                "is_mandatory": True,
                "description_en": "Family annual income should not exceed ₹72,000",
                "description_ta": "குடும்ப ஆண்டு வருமானம் ₹72,000-க்கு மிகாமல் இருக்க வேண்டும்",
                "prompt_question_en": "Is your family's annual income below ₹72,000?",
                "prompt_question_ta": "உங்கள் குடும்ப ஆண்டு வருமானம் ₹72,000-க்குள் உள்ளதா?"
            },
            {
                "field_name": "has_tailoring_training",
                "operator": "eq",
                "expected_value": "true",
                "is_mandatory": True,
                "description_en": "Must possess Tailoring Training Certificate (minimum 6 months)",
                "description_ta": "குறைந்தபட்சம் 6 மாத தையல் பயிற்சி முடித்த சான்றிதழ் பெற்றிருக்க வேண்டும்",
                "prompt_question_en": "Do you hold a certificate showing at least 6 months of tailoring training?",
                "prompt_question_ta": "குறைந்தபட்சம் 6 மாத தையல் பயிற்சி முடித்த சான்றிதழ் உங்களிடம் உள்ளதா?"
            }
        ],
        "documents": [
            {
                "name_en": "Tailoring Course Certificate (6 months)",
                "name_ta": "தையல் பயிற்சி முடித்த சான்றிதழ்",
                "is_mandatory": True,
                "issuing_authority_en": "Recognized Training Institute / Govt Organization"
            },
            {
                "name_en": "Income Certificate (Below ₹72k)",
                "name_ta": "வருமானச் சான்றிதழ் (ஆண்டுக்கு ₹72,000-க்குள்)",
                "is_mandatory": True,
                "issuing_authority_en": "Revenue Department / Tahsildar"
            },
            {
                "name_en": "Community Certificate",
                "name_ta": "சாதிச் சான்றிதழ்",
                "is_mandatory": True,
                "issuing_authority_en": "Revenue Department"
            },
            {
                "name_en": "Aadhaar Card & Smart Ration Card",
                "name_ta": "ஆதார் மற்றும் ரேஷன் அட்டை",
                "is_mandatory": True,
                "issuing_authority_en": "UIDAI / Civil Supplies Dept"
            }
        ],
        "steps": [
            {
                "step_number": 1,
                "mode": "both",
                "title_en": "Application via e-Sevai or DSWO",
                "title_ta": "இ-சேவை அல்லது சமூக நல அலுவலகத்தில் விண்ணப்பம்",
                "description_en": "Submit application online via tnesevai.tn.gov.in or in person at the District Social Welfare Office (DSWO).",
                "description_ta": "tnesevai.tn.gov.in மூலம் அல்லது மாவட்ட சமூக நல அலுவலகத்தில் விண்ணப்பிக்கலாம்.",
                "portal_url": "https://www.tnesevai.tn.gov.in"
            },
            {
                "step_number": 2,
                "mode": "offline",
                "title_en": "Skill & Document Verification",
                "title_ta": "சான்றிதழ் மற்றும் தகுதி சரிபார்ப்பு",
                "description_en": "Officials verify tailoring proficiency certificate, age proof, and income ceiling.",
                "description_ta": "தையல் சான்றிதழ், வயது மற்றும் வருமான வரம்பு அதிகாரிகள் மூலம் சரிபார்க்கப்படும்."
            },
            {
                "step_number": 3,
                "mode": "offline",
                "title_en": "Machine Distribution",
                "title_ta": "தையல் இயந்திரம் வழங்குதல்",
                "description_en": "Free sewing machine is handed over at annual district welfare distribution ceremonies.",
                "description_ta": "மாவட்ட அளவிலான நலத்திட்ட முகாம்களில் இலவச தையல் இயந்திரம் வழங்கப்படும்."
            }
        ],
        "source": {
            "source_name": "Social Welfare and Women Empowerment Department, TN",
            "portal_url": "https://www.tnesevai.tn.gov.in",
            "verified_date": "2026-10-05",
            "verification_status": "verified",
            "helpline_number": "044-24351885 / 181 Women Helpline"
        }
    },
    {
        "id": "pm-kisan-tn",
        "name": "PM-Kisan Samman Nidhi & Tamil Nadu Uzhavar Pathukappu Thittam",
        "name_ta": "பிரதமர் கிசான் & தமிழ்நாடு உழவர் பாதுகாப்புத் திட்டம்",
        "department": "Agriculture and Farmers Welfare Department",
        "department_ta": "வேளாண்மை மற்றும் உழவர் நலத்துறை",
        "category": "agriculture",
        "beneficiary_type": "Small, marginal, and landholding farmer families",
        "beneficiary_type_ta": "சிறு மற்றும் குறு விவசாயிகள், நில உரிமையாளர்கள்",
        "benefit_summary": "₹6,000 / year direct income support + subsidized seeds, fertilizers & crop insurance",
        "benefit_summary_ta": "ஆண்டுக்கு ₹6,000 நேரடி உதவித்தொகை + பயிர்க் காப்பீடு மற்றும் மானியங்கள்",
        "benefit_amount": "₹6,000 / year + Subsidies",
        "description": "Financial assistance given in 3 installments of ₹2,000 every four months to small and marginal farming families to purchase agricultural inputs, alongside Tamil Nadu state crop relief.",
        "description_ta": "சிறு, குறு விவசாய குடும்பங்களுக்கு விவசாய இடுபொருட்கள் வாங்க 4 மாதங்களுக்கு ஒருமுறை ₹2,000 வீதம் ஆண்டுக்கு ₹6,000 வழங்கும் திட்டம்.",
        "conditions": [
            {
                "field_name": "occupation",
                "operator": "eq",
                "expected_value": "farmer",
                "is_mandatory": True,
                "description_en": "Farmer family holding cultivable agricultural land registered in their name",
                "description_ta": "விவசாய நிலம் சொந்தமாக பட்டா வைத்துள்ள சிறு மற்றும் குறு விவசாயிகள்",
                "prompt_question_en": "Do you own cultivable agricultural land registered in your name?",
                "prompt_question_ta": "உங்கள் சொந்த பெயரில் சாகுபடி செய்யக்கூடிய விவசாய நிலம் உள்ளதா?"
            },
            {
                "field_name": "land_max_acres",
                "operator": "lte",
                "expected_value": "10",
                "is_mandatory": True,
                "description_en": "Land ownership verified via Tamil Nadu Patta / Chitta records",
                "description_ta": "தமிழ்நாடு பட்டா / சிட்டா ஆவணம் பதிவு செய்திருக்க வேண்டும்"
            }
        ],
        "documents": [
            {
                "name_en": "Land Patta / Chitta Copy",
                "name_ta": "நில பட்டா / சிட்டா நகல்",
                "is_mandatory": True,
                "issuing_authority_en": "Revenue Administration / eservices.tn.gov.in"
            },
            {
                "name_en": "Aadhaar Card",
                "name_ta": "ஆதார் அட்டை",
                "is_mandatory": True,
                "issuing_authority_en": "UIDAI"
            },
            {
                "name_en": "Bank Passbook with NPCI Aadhaar Seed",
                "name_ta": "ஆதார் இணைக்கப்பட்ட வங்கி கணக்கு புத்தகம்",
                "is_mandatory": True,
                "issuing_authority_en": "Bank / NPCI"
            }
        ],
        "steps": [
            {
                "step_number": 1,
                "mode": "online",
                "title_en": "Self Registration on PM-Kisan / Uzhavan App",
                "title_ta": "இணையதள பதிவு / உழவன் செயலி",
                "description_en": "Register online via pmkisan.gov.in or through Uzhavan App using land patta details and Aadhaar.",
                "description_ta": "pmkisan.gov.in அல்லது உழவன் செயலி மூலம் பட்டா எண் மற்றும் ஆதார் கொண்டு சுயமாக பதிவு செய்யலாம்.",
                "portal_url": "https://pmkisan.gov.in"
            },
            {
                "step_number": 2,
                "mode": "online",
                "title_en": "Mandatory e-KYC Verification",
                "title_ta": "e-KYC சரிபார்ப்பு",
                "description_en": "Complete biometric or OTP-based Aadhaar e-KYC on the portal.",
                "description_ta": "ஆதார் OTP அல்லது கைரேகை மூலம் e-KYC நிறைவு செய்ய வேண்டும்."
            },
            {
                "step_number": 3,
                "mode": "both",
                "title_en": "4-Monthly Direct Installments",
                "title_ta": "4 மாத தவணை வரவு",
                "description_en": "₹2,000 installment is transferred directly every 4 months, totaling ₹6,000 per year.",
                "description_ta": "ஆண்டுக்கு 3 தவணைகளில் தலா ₹2,000 வீதம் மொத்தம் ₹6,000 வங்கி கணக்கில் வரவு வைக்கப்படும்."
            }
        ],
        "source": {
            "source_name": "Ministry of Agriculture & TN Agriculture Department",
            "portal_url": "https://pmkisan.gov.in",
            "verified_date": "2026-11-10",
            "verification_status": "verified",
            "helpline_number": "Kisan Call Centre: 1800-180-1551"
        }
    },
    {
        "id": "naan-mudhalvan",
        "name": "Naan Mudhalvan Youth Skill & Competitive Exam Assistance",
        "name_ta": "நான் முதல்வன் இளைஞர் திறன் மேம்பாடு & போட்டித் தேர்வு திட்டம்",
        "department": "Tamil Nadu Skill Development Corporation (TNSDC)",
        "department_ta": "தமிழ்நாடு திறன் மேம்பாட்டுக் கழகம்",
        "category": "employment",
        "beneficiary_type": "College students, engineering/arts graduates, job seekers, civil service aspirants",
        "beneficiary_type_ta": "கல்லூரி மாணவர்கள், பட்டதாரிகள், வேலை தேடுவோர், போட்டித் தேர்வு எழுதுவோர்",
        "benefit_summary": "Free industry-recognized tech/vocational skills + ₹7,500/mo incentive for prelims clears",
        "benefit_summary_ta": "இலவச தொழில்நுட்ப திறன் பயிற்சி மற்றும் சிவில் சர்வீஸ் தேர்வர்களுக்கு மாதம் ₹7,500",
        "benefit_amount": "Free Training + ₹7,500 / month incentive",
        "description": "Transformative upskilling platform equipping Tamil Nadu youth with cutting-edge industry training (AI, Data, Coding, Core engineering, Banking) and financial incentives for UPSC/TNPSC aspirants.",
        "description_ta": "தமிழ்நாடு இளைஞர்களுக்கு செயற்கை நுண்ணறிவு, மென்பொருள், வங்கிப் பணி போன்ற தொழில்முறை திறன்களை இலவசமாக வழங்கி வேலைவாய்ப்பை உறுதி செய்யும் அரசு திட்டம்.",
        "conditions": [
            {
                "field_name": "occupation",
                "operator": "in",
                "expected_value": "student,graduate,unemployed",
                "is_mandatory": True,
                "description_en": "Students pursuing higher education or graduates seeking employment in Tamil Nadu",
                "description_ta": "தமிழ்நாட்டில் கல்லூரி பயிலும் மாணவர்கள் அல்லது வேலை தேடும் பட்டதாரிகள்"
            }
        ],
        "documents": [
            {
                "name_en": "College ID / Degree Certificate",
                "name_ta": "கல்லூரி அடையாள அட்டை / பட்டச் சான்றிதழ்",
                "is_mandatory": True,
                "issuing_authority_en": "University / College"
            },
            {
                "name_en": "Aadhaar Card",
                "name_ta": "ஆதார் அட்டை",
                "is_mandatory": True,
                "issuing_authority_en": "UIDAI"
            }
        ],
        "steps": [
            {
                "step_number": 1,
                "mode": "online",
                "title_en": "Student Portal Registration",
                "title_ta": "மாணவர் போர்ட்டல் பதிவு",
                "description_en": "Log into naanmudhalvan.tn.gov.in using your university / college roll number.",
                "description_ta": "கல்லூரி பதிவு எண் கொண்டு naanmudhalvan.tn.gov.in தளத்தில் இணையவும்.",
                "portal_url": "https://www.naanmudhalvan.tn.gov.in"
            },
            {
                "step_number": 2,
                "mode": "online",
                "title_en": "Course Selection & Placement Drive",
                "title_ta": "பயிற்சி தேர்வு மற்றும் வேலைவாய்ப்பு முகாம்",
                "description_en": "Enroll in free specialized tech courses and access campus mega job fairs.",
                "description_ta": "இலவச திறன் பயிற்சிகளை முடித்து வேலைவாய்ப்பு முகாம்களில் பங்கேற்கலாம்."
            }
        ],
        "source": {
            "source_name": "Tamil Nadu Skill Development Corporation (TNSDC)",
            "portal_url": "https://www.naanmudhalvan.tn.gov.in",
            "verified_date": "2026-10-25",
            "verification_status": "verified",
            "helpline_number": "044-22501070"
        }
    },
    {
        "id": "oap-senior-pension",
        "name": "Tamil Nadu Destitute Old Age Pension Scheme (OAP)",
        "name_ta": "முதியோர் உதவித்தொகை திட்டம் (OAP)",
        "department": "Revenue and Disaster Management Department",
        "department_ta": "வருவாய் மற்றும் பேரிடர் மேலாண்மைத் துறை",
        "category": "seniors",
        "beneficiary_type": "Destitute senior citizens with no means of regular subsistence",
        "beneficiary_type_ta": "ஆதரவற்ற 60 வயதுக்கு மேற்பட்ட முதியவர்கள்",
        "benefit_summary": "₹1,200 monthly pension deposited directly to bank account + free rice & dhotis",
        "benefit_summary_ta": "மாதம் ₹1,200 ஓய்வூதியம் + இலவச அரிசி மற்றும் வேட்டி/சேலை",
        "benefit_amount": "₹1,200 / month",
        "description": "Monthly financial pension provided to impoverished senior citizens who have no surviving adult earning members or sufficient source of livelihood.",
        "description_ta": "வாழ்க்கை நடத்த எவ்வித வருமானமும் அல்லது ஆதரவும் இல்லாத ஏழை முதியவர்களுக்கு மாதம் ₹1,200 ஓய்வூதியம் வழங்கும் திட்டம்.",
        "conditions": [
            {
                "field_name": "age_min",
                "operator": "gte",
                "expected_value": "60",
                "is_mandatory": True,
                "description_en": "Age of applicant must be 60 years or above",
                "description_ta": "விண்ணப்பதாரரின் வயது 60 அல்லது அதற்கு மேல் இருக்க வேண்டும்",
                "prompt_question_en": "Is the applicant aged 60 years or older?",
                "prompt_question_ta": "விண்ணப்பதாரரின் வயது 60 அல்லது அதற்கு மேற்பட்டதா?"
            }
        ],
        "documents": [
            {
                "name_en": "Age Proof (Aadhaar / Voter ID)",
                "name_ta": "வயது சான்று (ஆதார் / வாக்காளர் அட்டை)",
                "is_mandatory": True,
                "issuing_authority_en": "UIDAI / Election Commission"
            },
            {
                "name_en": "Smart Ration Card",
                "name_ta": "ஸ்மார்ட் குடும்ப அட்டை",
                "is_mandatory": True,
                "issuing_authority_en": "Civil Supplies Dept"
            },
            {
                "name_en": "Destitute Certificate from VAO",
                "name_ta": "ஆதரவற்றோர் சான்றிதழ்",
                "is_mandatory": True,
                "issuing_authority_en": "Village Administrative Officer (VAO)",
                "issuing_authority_ta": "கிராம நிர்வாக அலுவலர்"
            }
        ],
        "steps": [
            {
                "step_number": 1,
                "mode": "both",
                "title_en": "Application via e-Sevai / Taluk Office",
                "title_ta": "இ-சேவை அல்லது தாலுகா அலுவலகத்தில் மனு",
                "description_en": "Apply through your local e-Sevai center or submit physical form to Special Tahsildar (SSS) at the Taluk Office.",
                "description_ta": "இ-சேவை மையம் மூலமாகவோ அல்லது வட்டாட்சியர் அலுவலக சமூகப் பாதுகாப்பு பிரிவிலோ விண்ணப்பிக்கவும்.",
                "portal_url": "https://www.tnesevai.tn.gov.in"
            },
            {
                "step_number": 2,
                "mode": "offline",
                "title_en": "Field Enquiry",
                "title_ta": "நேரடி கள ஆய்வு",
                "description_en": "Revenue Inspector inspects living conditions to verify destitute status.",
                "description_ta": "வருவாய் ஆய்வாளர் இல்லத்திற்கு வந்து நிலைமையை சரிபார்ப்பார்."
            },
            {
                "step_number": 3,
                "mode": "both",
                "title_en": "Monthly Pension Credit",
                "title_ta": "மாதாந்திர ஓய்வூதிய வரவு",
                "description_en": "₹1,200 is disbursed monthly via bank account or postal money order.",
                "description_ta": "வங்கி அல்லது அஞ்சலகம் மூலம் மாதம் ₹1,200 ஓய்வூதியம் வழங்கப்படும்."
            }
        ],
        "source": {
            "source_name": "Revenue and Disaster Management Department, TN",
            "portal_url": "https://www.tnesevai.tn.gov.in",
            "verified_date": "2026-11-05",
            "verification_status": "verified",
            "helpline_number": "CM Helpline 1100"
        }
    },
    {
        "id": "differently-abled-welfare",
        "name": "Maintenance Allowance for Differently Abled Persons",
        "name_ta": "மாற்றுத்திறனாளிகள் மாதாந்திர பராமரிப்பு உதவித்தொகை திட்டம்",
        "department": "Welfare of Differently Abled Persons Department",
        "department_ta": "மாற்றுத்திறனாளிகள் நலத்துறை",
        "category": "disability",
        "beneficiary_type": "Persons with severe disabilities, intellectual disability, locomotor disability",
        "beneficiary_type_ta": "கடுமையான மாற்றுத்திறன் கொண்ட நபர்கள் (40% முதல் 75%+)",
        "benefit_summary": "₹1,500 to ₹2,000 monthly maintenance allowance + free bus pass & assistive devices",
        "benefit_summary_ta": "மாதம் ₹1,500 முதல் ₹2,000 பராமரிப்பு உதவித்தொகை + இலவச பேருந்து பயணம் & உதவி உபகரணங்கள்",
        "benefit_amount": "₹1,500 - ₹2,000 / month",
        "description": "Monthly maintenance grant and free assistive appliances (wheelchairs, retrofitted three-wheelers, hearing aids) given to differently abled individuals across Tamil Nadu.",
        "description_ta": "கடுமையான உடல் அல்லது மனநல மாற்றுத்திறன் கொண்ட நபர்களுக்கு மாதாந்திர வாழ்க்கை பராமரிப்பு தொகை மற்றும் இலவச உபகரணங்கள் வழங்கும் திட்டம்.",
        "conditions": [
            {
                "field_name": "disability",
                "operator": "eq",
                "expected_value": "true",
                "is_mandatory": True,
                "description_en": "Must possess a valid UDID Card or Disability Certificate (40% or more)",
                "description_ta": "அங்கீகரிக்கப்பட்ட UDID ஸ்மார்ட் கார்டு அல்லது 40% மேல் மாற்றுத்திறனாளி சான்றிதழ் பெற்றிருக்க வேண்டும்",
                "prompt_question_en": "Do you hold a valid UDID card or medical board disability certificate of 40% or more?",
                "prompt_question_ta": "உங்களிடம் 40% அல்லது அதற்கு மேற்பட்ட மாற்றுத்திறனாளி சான்றிதழ் அல்லது UDID அட்டை உள்ளதா?"
            }
        ],
        "documents": [
            {
                "name_en": "UDID Card / Medical Board Disability Certificate",
                "name_ta": "UDID அட்டை / மருத்துவ வாரிய மாற்றுத்திறனாளி சான்றிதழ்",
                "is_mandatory": True,
                "issuing_authority_en": "District Medical Board / Dept of Empowerment of PwDs"
            },
            {
                "name_en": "Aadhaar Card",
                "name_ta": "ஆதார் அட்டை",
                "is_mandatory": True,
                "issuing_authority_en": "UIDAI"
            },
            {
                "name_en": "Bank Passbook with Aadhaar linkage",
                "name_ta": "வங்கி சேமிப்புக் கணக்கு புத்தகம்",
                "is_mandatory": True,
                "issuing_authority_en": "Bank"
            }
        ],
        "steps": [
            {
                "step_number": 1,
                "mode": "both",
                "title_en": "UDID Assessment at District HQ Hospital",
                "title_ta": "தலைமை அரசு மருத்துவமனையில் பரிசோதனை",
                "description_en": "Attend the weekly Tuesday medical board at the Government Headquarters Hospital for disability percentage assessment.",
                "description_ta": "செவ்வாய்க்கிழமைகளில் மாவட்ட அரசு தலைமை மருத்துவமனையில் மருத்துவ வாரிய பரிசோதனைக்கு செல்லவும்.",
                "portal_url": "https://www.scd.tn.gov.in"
            },
            {
                "step_number": 2,
                "mode": "offline",
                "title_en": "District Differently Abled Welfare Office Submission",
                "title_ta": "மாவட்ட மாற்றுத்திறனாளிகள் நல அலுவலகத்தில் மனு",
                "description_en": "Submit certificate and bank passbook to the District Differently Abled Welfare Officer (DDAWO) at District Collectorate.",
                "description_ta": "மாவட்ட ஆட்சியர் அலுவலகத்தில் உள்ள DDAWO அலுவலரிடம் ஆவணங்களை சமர்ப்பிக்கவும்."
            },
            {
                "step_number": 3,
                "mode": "both",
                "title_en": "Direct Benefit Transfer & Assistive Devices",
                "title_ta": "மாத உதவித்தொகை & உபகரணங்கள் பெறுதல்",
                "description_en": "Monthly allowance is credited directly to bank account, alongside free assistive devices distribution.",
                "description_ta": "மாத உதவித்தொகையுடன் தேவையான சக்கர நாற்காலி போன்ற உபகரணங்கள் இலவசமாக வழங்கப்படும்."
            }
        ],
        "source": {
            "source_name": "Welfare of Differently Abled Persons Department, TN",
            "portal_url": "https://www.scd.tn.gov.in",
            "verified_date": "2026-10-28",
            "verification_status": "verified",
            "helpline_number": "Toll Free: 1800 425 0111"
        }
    },
    {
        "id": "muthulakshmi-maternity",
        "name": "Dr. Muthulakshmi Reddy Maternity Benefit Scheme (MRMBS)",
        "name_ta": "டாக்டர் முத்துலட்சுமி ரெட்டி மகப்பேறு நிதி உதவித் திட்டம்",
        "department": "Health and Family Welfare Department",
        "department_ta": "மக்கள் நல்வாழ்வு மற்றும் குடும்ப நலத்துறை",
        "category": "health",
        "beneficiary_type": "Pregnant and lactating mothers below poverty line",
        "beneficiary_type_ta": "ஏழை கர்ப்பிணி தாய்மார்கள் மற்றும் பாலூட்டும் தாய்மார்கள்",
        "benefit_summary": "₹18,000 total assistance (₹14,000 cash in 5 installments + ₹4,000 nutrition kit)",
        "benefit_summary_ta": "மொத்தம் ₹18,000 பலன் (₹14,000 ரொக்க உதவி + ₹4,000 மதிப்புள்ள ஊட்டச்சத்து பெட்டகம்)",
        "benefit_amount": "₹18,000 total benefit",
        "description": "Financial assistance and high-nutrition health kits to poor pregnant mothers to prevent maternal and infant mortality, ensuring institutional delivery and complete immunization.",
        "description_ta": "கர்ப்பிணித் தாய்மார்களுக்கு கர்ப்ப காலத்தில் ஊட்டச்சத்தை உறுதி செய்யவும், அரசு மருத்துவமனைகளில் பிரசவம் மற்றும் தடுப்பூசிகளை உறுதி செய்ய ₹18,000 வழங்கும் திட்டம்.",
        "conditions": [
            {
                "field_name": "gender",
                "operator": "eq",
                "expected_value": "female",
                "is_mandatory": True,
                "description_en": "Applicant must be female",
                "description_ta": "விண்ணப்பதாரர் பெண்ணாக இருக்க வேண்டும்",
                "prompt_question_en": "Are you a female applicant?",
                "prompt_question_ta": "நீங்கள் பெண்ணா?"
            },
            {
                "field_name": "is_pregnant_or_lactating",
                "operator": "eq",
                "expected_value": "true",
                "is_mandatory": True,
                "description_en": "Must be pregnant or a nursing mother",
                "description_ta": "கர்ப்பிணி அல்லது பாலூட்டும் தாயாக இருக்க வேண்டும்",
                "prompt_question_en": "Are you currently pregnant or a nursing mother?",
                "prompt_question_ta": "நீங்கள் கர்ப்பிணி அல்லது பாலூட்டும் தாயா?"
            },
            {
                "field_name": "annual_income",
                "operator": "lte",
                "expected_value": "120000",
                "is_mandatory": False,
                "description_en": "Family annual income below poverty line ceiling",
                "description_ta": "குடும்ப ஆண்டு வருமானம் வறுமைக் கோட்டிற்கு கீழ் இருக்க வேண்டும்",
                "prompt_question_en": "What is your approximate family annual income?",
                "prompt_question_ta": "உங்கள் குடும்ப ஆண்டு வருமானம் எவ்வளவு?"
            }
        ],
        "documents": [
            {
                "name_en": "RCH ID / PICME Number",
                "name_ta": "PICME பதிவு எண் (RCH ID)",
                "is_mandatory": True,
                "issuing_authority_en": "Village Health Nurse / Primary Health Centre",
                "issuing_authority_ta": "கிராம சுகாதார செவிலியர் / ஆரம்ப சுகாதார நிலையம்"
            },
            {
                "name_en": "Mother's Aadhaar Card",
                "name_ta": "தாயின் ஆதார் அட்டை",
                "is_mandatory": True,
                "issuing_authority_en": "UIDAI",
                "issuing_authority_ta": "இந்திய தனித்துவ அடையாள ஆணையம்"
            },
            {
                "name_en": "Bank Passbook seeded with Aadhaar",
                "name_ta": "ஆதார் இணைக்கப்பட்ட தனி வங்கி சேமிப்பு புத்தகம்",
                "is_mandatory": True,
                "issuing_authority_en": "Scheduled Commercial Bank",
                "issuing_authority_ta": "அங்கீகரிக்கப்பட்ட வங்கி"
            },
            {
                "name_en": "Smart Ration Card",
                "name_ta": "ஸ்மார்ட் குடும்ப அட்டை",
                "is_mandatory": True,
                "issuing_authority_en": "Civil Supplies & Consumer Protection Dept",
                "issuing_authority_ta": "உணவுப் பொருள் வழங்கல் துறை"
            }
        ],
        "steps": [
            {
                "step_number": 1,
                "mode": "offline",
                "title_en": "PICME Registration at Village Health Nurse (VHN)",
                "title_ta": "கிராம சுகாதார செவிலியரிடம் PICME பதிவு",
                "description_en": "Register pregnancy with VHN before 12th week of gestation to obtain 12-digit RCH ID.",
                "description_ta": "கர்ப்பமான 12 வாரங்களுக்குள் செவிலியரிடம் பதிவு செய்து 12 இலக்க RCH ஐடி பெறவும்."
            },
            {
                "step_number": 2,
                "mode": "both",
                "title_en": "Antenatal Checkups & Nutrition Kit",
                "title_ta": "மகப்பேறு கால பரிசோதனை & ஊட்டச்சத்து பெட்டகம்",
                "description_en": "Complete 3 antenatal visits at Primary Health Centre and collect ₹4,000 nutrition kit.",
                "description_ta": "அரசு மருத்துவமனையில் 3 முறை மருத்துவப் பரிசோதனை செய்து ஊட்டச்சத்து பெட்டகம் பெறலாம்."
            },
            {
                "step_number": 3,
                "mode": "both",
                "title_en": "Institutional Delivery & DBT Credit",
                "title_ta": "அரசு மருத்துவமனையில் பிரசவம் & வங்கி வரவு",
                "description_en": "Deliver child at government hospital and complete 3rd dose OPV/Rota vaccination to receive remaining cash installments.",
                "description_ta": "அரசு மருத்துவமனையில் பிரசவம் மற்றும் குழந்தை தடுப்பூசிகள் முடித்தவுடன் வங்கி கணக்கில் நிதி வரவு வைக்கப்படும்."
            }
        ],
        "source": {
            "source_name": "Directorate of Public Health and Preventive Medicine, TN",
            "portal_url": "https://picme.tn.gov.in",
            "verified_date": "2026-10-12",
            "verification_status": "verified",
            "helpline_number": "104 Health Helpline"
        }
    },
    {
        "id": "aabcs-scst-entrepreneur",
        "name": "Annal Ambedkar Business Champions Scheme (AABCS)",
        "name_ta": "அண்ணல் அம்பேத்கர் தொழில் முன்னோடிகள் திட்டம் (AABCS)",
        "department": "Micro, Small and Medium Enterprises (MSME) Department",
        "department_ta": "ஊரக மற்றும் குறு, சிறு மற்றும் நடுத்தரத் தொழில் நிறுவனங்கள் துறை",
        "category": "employment",
        "beneficiary_type": "Scheduled Caste (SC) and Scheduled Tribe (ST) aspiring entrepreneurs",
        "beneficiary_type_ta": "ஆதிதிராவிடர் (SC) மற்றும் பழங்குடியினர் (ST) தொழில் முனைவோர்",
        "benefit_summary": "35% capital subsidy up to ₹1.5 Crore + 6% interest subvention on term loans",
        "benefit_summary_ta": "35% மூலதன மானியம் (அதிகபட்சம் ₹1.5 கோடி வரை) + 6% வட்டி மானியம்",
        "benefit_amount": "35% Subsidy (up to ₹1.5 Cr)",
        "description": "Ambitious initiative promoting SC/ST entrepreneurship in manufacturing, services, transport, and trading by providing substantial capital subsidies and bank loan support.",
        "description_ta": "ஆதிதிராவிடர் மற்றும் பழங்குடியின இளைஞர்களை தொழில் முனைவோராக மாற்ற 35% நேரடி அரசு மூலதன மானியம் மற்றும் 6% வட்டி தள்ளுபடி வழங்கும் திட்டம்.",
        "conditions": [
            {
                "field_name": "community_category",
                "operator": "in",
                "expected_value": "SC,ST",
                "is_mandatory": True,
                "description_en": "Applicant must belong to Scheduled Caste (SC) or Scheduled Tribe (ST)",
                "description_ta": "விண்ணப்பதாரர் ஆதிதிராவிடர் (SC) அல்லது பழங்குடியினர் (ST) சமூகத்தை சேர்ந்தவராக இருக்க வேண்டும்",
                "prompt_question_en": "Do you belong to the SC or ST community?",
                "prompt_question_ta": "நீங்கள் ஆதிதிராவிடர் (SC) அல்லது பழங்குடியினர் (ST) சமூகத்தை சேர்ந்தவரா?"
            },
            {
                "field_name": "age",
                "operator": "gte",
                "expected_value": "18",
                "is_mandatory": True,
                "description_en": "Minimum applicant age is 18 years",
                "description_ta": "குறைந்தபட்ச வயது 18 பூர்த்தியாகியிருக்க வேண்டும்"
            },
            {
                "field_name": "age",
                "operator": "lte",
                "expected_value": "55",
                "is_mandatory": True,
                "description_en": "Maximum applicant age is 55 years",
                "description_ta": "அதிகபட்ச வயது 55-க்குள் இருக்க வேண்டும்"
            }
        ],
        "documents": [
            {
                "name_en": "Community Certificate (SC/ST)",
                "name_ta": "சாதிச் சான்றிதழ் (SC/ST)",
                "is_mandatory": True,
                "issuing_authority_en": "Tahsildar / Revenue Department",
                "issuing_authority_ta": "வட்டாட்சியர் / வருவாய்த் துறை"
            },
            {
                "name_en": "Detailed Project Report (DPR)",
                "name_ta": "தொழில் திட்ட அறிக்கை (DPR)",
                "is_mandatory": True,
                "issuing_authority_en": "Chartered Accountant / Certified Consultant",
                "issuing_authority_ta": "பட்டயக் கணக்காளர் / அங்கீகரிக்கப்பட்ட ஆலோசகர்"
            },
            {
                "name_en": "Aadhaar & PAN Card",
                "name_ta": "ஆதார் மற்றும் பான் அட்டை",
                "is_mandatory": True,
                "issuing_authority_en": "UIDAI / Income Tax Department",
                "issuing_authority_ta": "வருமான வரித்துறை / UIDAI"
            },
            {
                "name_en": "Bank Account Details & Quotations",
                "name_ta": "வங்கி கணக்கு மற்றும் உபகரணங்கள் விலைப்பட்டியல்",
                "is_mandatory": True,
                "issuing_authority_en": "Machinery Suppliers & Bank",
                "issuing_authority_ta": "இயந்திர விற்பனையாளர் மற்றும் வங்கி"
            }
        ],
        "steps": [
            {
                "step_number": 1,
                "mode": "online",
                "title_en": "Online Portal Application",
                "title_ta": "இணையதள விண்ணப்பம்",
                "description_en": "Submit application online on msmeonline.tn.gov.in under AABCS scheme portal with project details.",
                "description_ta": "msmeonline.tn.gov.in இணையதளம் வாயிலாக AABCS பிரிவில் திட்ட விவரங்களுடன் விண்ணப்பிக்கவும்.",
                "portal_url": "https://msmeonline.tn.gov.in"
            },
            {
                "step_number": 2,
                "mode": "offline",
                "title_en": "District Industries Centre (DIC) Interview",
                "title_ta": "மாவட்ட தொழில் மைய நேர்காணல்",
                "description_en": "Attend Task Force Committee interview led by District Collector / General Manager, DIC.",
                "description_ta": "மாவட்ட ஆட்சியர் தலைமையிலான குழுவின் திட்ட நேர்காணலில் பங்கேற்கவும்."
            },
            {
                "step_number": 3,
                "mode": "both",
                "title_en": "Bank Loan & 35% Capital Subsidy",
                "title_ta": "வங்கி கடன் மற்றும் 35% மானியம்",
                "description_en": "Bank sanctions term loan, and Tamil Nadu government releases 35% subsidy directly to bank subsidy reserve.",
                "description_ta": "வங்கி கடன் ஒப்புதல் மற்றும் அரசு 35% நேரடி மூலதன மானியத்தை விடுவிக்கும்."
            }
        ],
        "source": {
            "source_name": "Tamil Nadu MSME Department",
            "portal_url": "https://msmeonline.tn.gov.in",
            "verified_date": "2026-10-30",
            "verification_status": "verified",
            "helpline_number": "044-22501070 / DIC District Offices"
        }
    },
    {
        "id": "tamil-pudhalvan",
        "name": "Tamil Pudhalvan Higher Education Scheme for Boys",
        "name_ta": "தமிழ்ப் புதல்வன் திட்டம் (மாணவர்கள் உயர்கல்வி உதவி)",
        "department": "Social Welfare and Higher Education Department",
        "department_ta": "சமூக நலன் மற்றும் உயர்கல்வித் துறை",
        "category": "education",
        "beneficiary_type": "Male students from government schools joining higher education",
        "beneficiary_type_ta": "அரசுப் பள்ளியில் படித்து கல்லூரி சேரும் மாணவர்கள்",
        "benefit_summary": "₹1,000 per month deposited directly to bank account for textbook and college expenses",
        "benefit_summary_ta": "புத்தகங்கள் மற்றும் படிப்பு செலவுகளுக்கு மாதம் ₹1,000 வங்கி வரவு",
        "benefit_amount": "₹1,000 / month",
        "description": "Financial assistance program providing ₹1,000 monthly aid to male students who studied in Tamil Nadu government schools from 6th to 12th standard and joined higher education.",
        "description_ta": "தமிழ்நாடு அரசுப் பள்ளிகளில் 6 முதல் 12-ம் வகுப்பு வரை படித்து கல்லூரி, பாலிடெக்னிக், தொழிற்கல்வி பயிலும் மாணவர்களுக்கு மாதம் ₹1,000 வழங்கும் திட்டம்.",
        "conditions": [
            {
                "field_name": "gender",
                "operator": "eq",
                "expected_value": "male",
                "is_mandatory": True,
                "description_en": "Applicant must be a male student",
                "description_ta": "விண்ணப்பதாரர் மாணவராக (ஆண்) இருக்க வேண்டும்",
                "prompt_question_en": "Are you a male student?",
                "prompt_question_ta": "நீங்கள் மாணவரா (ஆண்)?"
            },
            {
                "field_name": "school_type",
                "operator": "eq",
                "expected_value": "government",
                "is_mandatory": True,
                "description_en": "Must have studied Classes 6 to 12 in Tamil Nadu Government schools",
                "description_ta": "6 முதல் 12-ம் வகுப்பு வரை தமிழ்நாடு அரசுப் பள்ளிகளில் படித்திருக்க வேண்டும்",
                "prompt_question_en": "Did you study in a Tamil Nadu Government school from 6th to 12th standard?",
                "prompt_question_ta": "நீங்கள் 6 முதல் 12-ம் வகுப்பு வரை அரசுப் பள்ளியில் படித்தீர்களா?"
            },
            {
                "field_name": "occupation",
                "operator": "eq",
                "expected_value": "student",
                "is_mandatory": True,
                "description_en": "Enrolled in recognized higher education college / university",
                "description_ta": "அங்கீகரிக்கப்பட்ட கல்லூரியில் பட்டப்படிப்பு அல்லது பட்டயப்படிப்பு பயில வேண்டும்",
                "prompt_question_en": "Are you currently enrolled in a college degree or diploma course?",
                "prompt_question_ta": "நீங்கள் தற்போது கல்லூரியில் பட்டப்படிப்பு அல்லது டிப்ளமோ பயில்கிறீர்களா?"
            }
        ],
        "documents": [
            {
                "name_en": "Aadhaar Card",
                "name_ta": "ஆதார் அட்டை",
                "is_mandatory": True,
                "issuing_authority_en": "UIDAI",
                "issuing_authority_ta": "இந்திய தனித்துவ அடையாள ஆணையம்"
            },
            {
                "name_en": "10th & 12th Marksheets",
                "name_ta": "10 மற்றும் 12-ம் வகுப்பு மதிப்பெண் சான்றிதழ்",
                "is_mandatory": True,
                "issuing_authority_en": "Directorate of Government Examinations, TN",
                "issuing_authority_ta": "அரசுத் தேர்வுகள் இயக்ககம், தமிழ்நாடு"
            },
            {
                "name_en": "Govt School Study Certificate (Bonafide)",
                "name_ta": "அரசுப் பள்ளி பயின்ற சான்றிதழ்",
                "is_mandatory": True,
                "issuing_authority_en": "Headmaster of respective Government School",
                "issuing_authority_ta": "படித்த அரசுப் பள்ளியின் தலைமை ஆசிரியர்"
            },
            {
                "name_en": "Bank Passbook with Aadhaar linkage",
                "name_ta": "வங்கி சேமிப்புக் கணக்கு புத்தகம்",
                "is_mandatory": True,
                "issuing_authority_en": "Scheduled Commercial Bank",
                "issuing_authority_ta": "அங்கீகரிக்கப்பட்ட வங்கி"
            }
        ],
        "steps": [
            {
                "step_number": 1,
                "mode": "both",
                "title_en": "College Nodal Officer Enrollment",
                "title_ta": "கல்லூரி ஒருங்கிணைப்பாளர் மூலம் பதிவு",
                "description_en": "Register through college nodal officer via Tamil Nadu Higher Education portal during admission.",
                "description_ta": "கல்லூரி சேர்க்கையின் போது கல்லூரி மூலமாக போர்ட்டலில் பதிவு செய்யப்படும்."
            },
            {
                "step_number": 2,
                "mode": "online",
                "title_en": "School EMIS Verification",
                "title_ta": "பள்ளி கல்வி மேலாண்மை (EMIS) சரிபார்ப்பு",
                "description_en": "Automatic verification of 6th to 12th government school study through Education EMIS database.",
                "description_ta": "பள்ளிக் கல்வித்துறை EMIS தரவு மூலம் 6 முதல் 12-ம் வகுப்பு அரசுப் பள்ளிப் படிப்பு தானாக சரிபார்க்கப்படும்."
            },
            {
                "step_number": 3,
                "mode": "both",
                "title_en": "Monthly ₹1,000 Direct Benefit Transfer",
                "title_ta": "மாதம் ₹1,000 நேரடி வங்கி வரவு",
                "description_en": "Monthly financial aid of ₹1,000 credited to student's bank account until completion of graduation.",
                "description_ta": "பட்டப்படிப்பு முடியும் வரை ஒவ்வொரு மாதமும் மாணவரின் வங்கிக் கணக்கில் ₹1,000 வரவு வைக்கப்படும்."
            }
        ],
        "source": {
            "source_name": "Tamil Nadu Higher Education Department",
            "portal_url": "https://www.tn.gov.in",
            "verified_date": "2026-11-02",
            "verification_status": "verified",
            "helpline_number": "CM Helpline 1100 / 14417"
        }
    },
    {
        "id": "kalaignar-kanavu-illam",
        "name": "Kalaignar Kanavu Illam Scheme (Rural Housing)",
        "name_ta": "கலைஞர் கனவு இல்லம் திட்டம் (கிராமப்புற வீடுகள்)",
        "department": "Rural Development and Panchayat Raj Department",
        "department_ta": "ஊரக வளர்ச்சி மற்றும் ஊராட்சித் துறை",
        "category": "housing",
        "beneficiary_type": "Rural families living in thatched or dilapidated huts",
        "beneficiary_type_ta": "குடிசை அல்லது பாழடைந்த வீடுகளில் வசிக்கும் கிராமப்புற மக்கள்",
        "benefit_summary": "Financial grant of ₹3,50,000 for constructing a durable pucca concrete house",
        "benefit_summary_ta": "புதிய கான்கிரீட் வீடு கட்ட ₹3,50,000 நேரடி அரசு நிதி உதவி",
        "benefit_amount": "₹3,50,000 per house",
        "description": "Ambitious initiative to eradicate rural huts in Tamil Nadu by helping impoverished families construct solid permanent concrete homes of at least 360 square feet.",
        "description_ta": "குடிசைகள் இல்லாத தமிழ்நாட்டை உருவாக்கும் நோக்கில் ஏழை எளிய மக்கள் 360 சதுர அடியில் புதிய கான்கிரீட் வீடு கட்ட ₹3.50 லட்சம் வழங்கும் திட்டம்.",
        "conditions": [
            {
                "field_name": "annual_income",
                "operator": "lte",
                "expected_value": "200000",
                "is_mandatory": True,
                "description_en": "Family annual income below ₹2,00,000",
                "description_ta": "குடும்ப ஆண்டு வருமானம் ₹2,00,000-க்கு மிகாமல் இருக்க வேண்டும்",
                "prompt_question_en": "What is your approximate family annual income?",
                "prompt_question_ta": "உங்கள் குடும்ப ஆண்டு வருமானம் எவ்வளவு?"
            }
        ],
        "documents": [
            {
                "name_en": "House Site Patta / Title Deed",
                "name_ta": "வீட்டு மனை பட்டா / ஆவண நகல்",
                "is_mandatory": True,
                "issuing_authority_en": "Revenue Department",
                "issuing_authority_ta": "வருவாய்த் துறை"
            },
            {
                "name_en": "Smart Ration Card",
                "name_ta": "ஸ்மார்ட் குடும்ப அட்டை",
                "is_mandatory": True,
                "issuing_authority_en": "Civil Supplies & Consumer Protection Dept",
                "issuing_authority_ta": "உணவுப் பொருள் வழங்கல் துறை"
            },
            {
                "name_en": "Aadhaar Card",
                "name_ta": "ஆதார் அட்டை",
                "is_mandatory": True,
                "issuing_authority_en": "UIDAI",
                "issuing_authority_ta": "இந்திய தனித்துவ அடையாள ஆணையம்"
            },
            {
                "name_en": "Photograph of existing hut",
                "name_ta": "தற்போதைய குடிசை வீட்டின் புகைப்படம்",
                "is_mandatory": True,
                "issuing_authority_en": "Self / Village Panchayat Secretary",
                "issuing_authority_ta": "சுய / கிராம ஊராட்சி செயலாளர்"
            },
            {
                "name_en": "Bank Passbook with Aadhaar linkage",
                "name_ta": "ஆதார் இணைக்கப்பட்ட வங்கி புத்தகம்",
                "is_mandatory": True,
                "issuing_authority_en": "Scheduled Commercial Bank",
                "issuing_authority_ta": "அங்கீகரிக்கப்பட்ட வங்கி"
            }
        ],
        "steps": [
            {
                "step_number": 1,
                "mode": "offline",
                "title_en": "Village Panchayat Survey & Grama Sabha Approval",
                "title_ta": "ஊராட்சி கணக்கெடுப்பு & கிராம சபை ஒப்புதல்",
                "description_en": "Hut dwelling surveyed by Panchayat Secretary and ratified in Grama Sabha resolution.",
                "description_ta": "குடிசை கணக்கெடுப்பு செய்யப்பட்டு கிராம சபை கூட்டத்தில் ஒப்புதல் பெறப்படும்."
            },
            {
                "step_number": 2,
                "mode": "offline",
                "title_en": "Work Order by Block Development Officer (BDO)",
                "title_ta": "வட்டார வளர்ச்சி அலுவலர் பணி ஆணை",
                "description_en": "Administrative sanction and construction work order issued by BDO.",
                "description_ta": "BDO அலுவலரால் வீடு கட்டும் பணி ஆணை வழங்கப்படும்."
            },
            {
                "step_number": 3,
                "mode": "both",
                "title_en": "Milestone-based Stage Payments (₹3.5 Lakhs)",
                "title_ta": "கட்டுமான நிலைக்கேற்ப ₹3.5 லட்சம் நிதி வரவு",
                "description_en": "Direct DBT installments released at foundation, lintel, roof, and finishing stages.",
                "description_ta": "அடித்தளம், மேற்கூரை மற்றும் பூச்சு வேலைகளின் போது நிலைகளாக வங்கி கணக்கில் நிதி வரவு வைக்கப்படும்."
            }
        ],
        "source": {
            "source_name": "Rural Development and Panchayat Raj Department, TN",
            "portal_url": "https://www.tnrd.tn.gov.in",
            "verified_date": "2026-10-15",
            "verification_status": "verified",
            "helpline_number": "CM Helpline 1100 / District Rural Wing"
        }
    },
    {
        "id": "pmegp-msme-business",
        "name": "Prime Minister's Employment Generation Programme (PMEGP)",
        "name_ta": "பிரதமரின் வேலைவாய்ப்பு உருவாக்கும் திட்டம் (PMEGP)",
        "department": "Ministry of Micro, Small and Medium Enterprises (MSME)",
        "department_ta": "குறு, சிறு மற்றும் நடுத்தர தொழில் அமைச்சகம் (MSME)",
        "category": "business",
        "beneficiary_type": "Aspiring entrepreneurs and micro-enterprise owners (Age 18+)",
        "beneficiary_type_ta": "புதிய தொழில் தொடங்குவோர் மற்றும் சிறு தொழில் முனைவோர் (18 வயதுக்கு மேற்பட்டோர்)",
        "benefit_summary": "15% to 35% margin money government subsidy on bank project loans up to ₹50 Lakhs (Manufacturing) / ₹20 Lakhs (Service)",
        "benefit_summary_ta": "ரூ. 50 லட்சம் வரை உற்பத்தி மற்றும் ரூ. 20 லட்சம் வரை சேவை தொழில் கடன்களுக்கு 15% முதல் 35% வரை அரசு மானியம்",
        "benefit_amount": "15% - 35% Subsidy (up to ₹50L project)",
        "description": "Credit-linked government subsidy programme to generate self-employment opportunities through establishment of micro-enterprises in manufacturing and service sectors.",
        "description_ta": "உற்பத்தி மற்றும் சேவை துறைகளில் புதிய சிறு தொழில் நிறுவனங்களை அமைத்து சுயவேலைவாய்ப்பை உருவாக்க மத்திய அரசு வழங்கும் கடன் மானியத் திட்டம்.",
        "conditions": [
            {
                "field_name": "age",
                "operator": "gte",
                "expected_value": 18,
                "is_mandatory": True,
                "description_en": "Applicant must be at least 18 years of age",
                "description_ta": "விண்ணப்பதாரர் குறைந்தபட்சம் 18 வயது பூர்த்தியடைந்தவராக இருக்க வேண்டும்",
                "prompt_question_en": "Are you at least 18 years old?",
                "prompt_question_ta": "உங்களுக்கு 18 வயது பூர்த்தியாகிவிட்டதா?"
            },
            {
                "field_name": "occupation",
                "operator": "in",
                "expected_value": "self_employed,business,entrepreneur,unemployed,artisan",
                "is_mandatory": True,
                "description_en": "Applicant must be an aspiring entrepreneur or establishing a new micro-enterprise",
                "description_ta": "புதிய தொழில் தொடங்கும் தொழில் முனைவோராக அல்லது சுயதொழில் ஆர்வலராக இருக்க வேண்டும்",
                "prompt_question_en": "Are you planning to establish a new business or self-employment venture?",
                "prompt_question_ta": "நீங்கள் புதிய தொழில் அல்லது சுயதொழில் தொடங்க திட்டமிடுகிறீர்களா?"
            }
        ],
        "documents": [
            {
                "name_en": "Aadhaar Card linked to Mobile and Bank",
                "name_ta": "மொபைல் மற்றும் வங்கி கணக்குடன் இணைக்கப்பட்ட ஆதார் அட்டை",
                "is_mandatory": True,
                "issuing_authority_en": "UIDAI",
                "issuing_authority_ta": "இந்திய தனித்துவ அடையாள ஆணையம்"
            },
            {
                "name_en": "Detailed Project Report (DPR) / Project Proposal",
                "name_ta": "திட்ட மதிப்பீட்டு அறிக்கை (DPR)",
                "is_mandatory": True,
                "issuing_authority_en": "Chartered Accountant / DIC / Self-prepared",
                "issuing_authority_ta": "பட்டயக் கணக்காளர் / மாவட்ட தொழில் மையம் (DIC)"
            },
            {
                "name_en": "Educational Qualification Certificate (8th / 10th / Diploma / Degree)",
                "name_ta": "கல்வித் தகுதிச் சான்றிதழ் (8-ம் வகுப்பு அல்லது அதற்கு மேல்)",
                "is_mandatory": True,
                "issuing_authority_en": "School / Board / University",
                "issuing_authority_ta": "பள்ளி / கல்வி வாரியம் / பல்கலைக்கழகம்"
            },
            {
                "name_en": "Special Category / Community Certificate (for higher 25-35% subsidy)",
                "name_ta": "சாதி / சிறப்புப் பிரிவுச் சான்றிதழ் (கூடுதல் மானியத்திற்கு)",
                "is_mandatory": False,
                "issuing_authority_en": "Revenue Department (Tahsildar)",
                "issuing_authority_ta": "வருவாய்த்துறை (வட்டாட்சியர்)"
            },
            {
                "name_en": "Bank Account Passbook / KYC Verification",
                "name_ta": "வங்கி பாஸ்புக் / KYC சரிபார்ப்பு",
                "is_mandatory": True,
                "issuing_authority_en": "Scheduled Commercial Bank",
                "issuing_authority_ta": "அங்கீகரிக்கப்பட்ட வணிக வங்கி"
            }
        ],
        "steps": [
            {
                "step_number": 1,
                "mode": "online",
                "title_en": "Online Application Submission on KVIC PMEGP e-Portal",
                "title_ta": "KVIC PMEGP இணையதளத்தில் ஆன்லைன் விண்ணப்பம் சமர்ப்பித்தல்",
                "description_en": "Register and fill the online application on kviconline.gov.in with DPR and KYC documents.",
                "description_ta": "kviconline.gov.in தளத்தில் திட்ட அறிக்கை மற்றும் ஆவணங்களுடன் விண்ணப்பிக்கவும்.",
                "portal_url": "https://www.kviconline.gov.in/pmegpeportal/"
            },
            {
                "step_number": 2,
                "mode": "both",
                "title_en": "District Task Force Committee (DTFC) Scrutiny & Bank Sanction",
                "title_ta": "மாவட்ட பணிக்குழு சரிபார்ப்பு மற்றும் வங்கி கடன் அனுமதி",
                "description_en": "District committee forwards application to selected bank branch for credit appraisal and loan sanction.",
                "description_ta": "மாவட்ட தொழில் குழுவால் வங்கிக்கு பரிந்துரைக்கப்பட்டு கடன் அனுமதி வழங்கப்படும்."
            },
            {
                "step_number": 3,
                "mode": "both",
                "title_en": "Entrepreneurship Development Programme (EDP) & Margin Money Credit",
                "title_ta": "தொழில்முனைவோர் பயிற்சி (EDP) மற்றும் மானிய நிதி வரவு",
                "description_en": "Undergo mandatory EDP training; bank disburses loan and claims margin money subsidy directly from KVIC.",
                "description_ta": "EDP பயிற்சி முடித்தவுடன் கடன் வழங்கப்பட்டு அரசு மானியம் வங்கி கணக்கில் பூட்டப்படும் (Lock-in)."
            }
        ],
        "source": {
            "source_name": "Khadi and Village Industries Commission (KVIC) / Ministry of MSME",
            "portal_url": "https://www.kviconline.gov.in/pmegpeportal/",
            "verified_date": "2026-10-15",
            "verification_status": "verified",
            "helpline_number": "1800-180-6763 / MSME Helpdesk"
        }
    },
    {
        "id": "nsp-post-matric-scholarship",
        "name": "National Scholarship Portal (NSP) - Post-Matric Scholarship Scheme",
        "name_ta": "தேசிய கல்வி உதவித்தொகை தளம் - மெட்ரிக் பின் கல்வி உதவித்தொகை",
        "department": "Ministry of Social Justice and Empowerment / Ministry of Minority Affairs, Govt. of India",
        "department_ta": "சமூக நீதி மற்றும் அதிகாரமளித்தல் அமைச்சகம் / மத்திய அரசு",
        "category": "education",
        "beneficiary_type": "Post-matric students enrolled in Classes 11, 12, ITI, Diploma, Undergraduate & Postgraduate courses",
        "beneficiary_type_ta": "11, 12, ஐடிஐ, பாலிடெக்னிக், கல்லூரி மற்றும் பல்கலைக்கழகத்தில் பயிலும் மாணவர்கள்",
        "benefit_summary": "Reimbursement of non-refundable tuition fees plus annual maintenance allowance up to ₹13,500/year",
        "benefit_summary_ta": "முழுக் கல்விக் கட்டண விலக்கு மற்றும் ஆண்டு பராமரிப்பு உதவித்தொகை ரூ. 13,500 வரை",
        "benefit_amount": "Tuition fee reimbursement + Maintenance allowance",
        "description": "Centrally sponsored nationwide scholarship scheme supporting eligible students from economically weaker backgrounds to complete higher education.",
        "description_ta": "குறைந்த வருமானம் கொண்ட குடும்பங்களைச் சேர்ந்த மாணவர்கள் 11-ம் வகுப்பு முதல் உயர்கல்வி வரை தடையின்றி படிக்க மத்திய அரசு வழங்கும் உதவித்தொகை.",
        "conditions": [
            {
                "field_name": "occupation",
                "operator": "eq",
                "expected_value": "student",
                "is_mandatory": True,
                "description_en": "Applicant must be an actively enrolled student in a recognized post-matric institution",
                "description_ta": "அங்கீகரிக்கப்பட்ட கல்லூரியில் மெட்ரிக் பின் படிப்பில் பயிலும் மாணவராக இருக்க வேண்டும்",
                "prompt_question_en": "Are you a student enrolled in a recognized institution?",
                "prompt_question_ta": "நீங்கள் அங்கீகரிக்கப்பட்ட கல்லூரியில் பயிலும் மாணவரா?"
            },
            {
                "field_name": "annual_income",
                "operator": "lte",
                "expected_value": 250000,
                "is_mandatory": True,
                "description_en": "Annual family income must not exceed ₹2,50,000",
                "description_ta": "குடும்ப ஆண்டு வருமானம் ரூ. 2,50,000-க்கு மிகாமல் இருக்க வேண்டும்",
                "prompt_question_en": "Is your annual family income within ₹2,50,000?",
                "prompt_question_ta": "உங்கள் குடும்ப ஆண்டு வருமானம் ரூ. 2.5 லட்சத்திற்குள் உள்ளதா?"
            }
        ],
        "documents": [
            {
                "name_en": "College Bonafide Student Certificate",
                "name_ta": "கல்லூரி படிப்புச் சான்றிதழ் (Bonafide)",
                "is_mandatory": True,
                "issuing_authority_en": "Head of Institution / College Principal",
                "issuing_authority_ta": "கல்லூரி முதல்வர் அலுவலகம்"
            },
            {
                "name_en": "Previous Qualifying Examination Marksheet",
                "name_ta": "முந்தைய ஆண்டு தேர்ச்சி மதிப்பெண் சான்றிதழ்",
                "is_mandatory": True,
                "issuing_authority_en": "School / University Exam Authority",
                "issuing_authority_ta": "பல்கலைக்கழக / தேர்வு வாரியம்"
            },
            {
                "name_en": "Income Certificate for Current Financial Year",
                "name_ta": "நடப்பு நிதியாண்டு வருமானச் சான்றிதழ்",
                "is_mandatory": True,
                "issuing_authority_en": "Revenue Department (e-Sevai / Tahsildar)",
                "issuing_authority_ta": "வருவாய்த்துறை (இ-சேவை / வட்டாட்சியர்)"
            },
            {
                "name_en": "Community / Caste Certificate",
                "name_ta": "சாதிச் சான்றிதழ் (Community Certificate)",
                "is_mandatory": True,
                "issuing_authority_en": "Revenue Department (Zonal Deputy Tahsildar)",
                "issuing_authority_ta": "மண்டல துணை வட்டாட்சியர்"
            },
            {
                "name_en": "Bank Passbook with Aadhaar Active DBT Seeding",
                "name_ta": "ஆதார் DBT இணைக்கப்பட்ட வங்கி பாஸ்புக்",
                "is_mandatory": True,
                "issuing_authority_en": "Scheduled Commercial Bank",
                "issuing_authority_ta": "அங்கீகரிக்கப்பட்ட வங்கி"
            }
        ],
        "steps": [
            {
                "step_number": 1,
                "mode": "online",
                "title_en": "One-Time Registration (OTR) on National Scholarship Portal",
                "title_ta": "தேசிய கல்வி உதவித்தொகை தளத்தில் ஒருமுறை பதிவு (OTR)",
                "description_en": "Create user profile using Aadhaar e-KYC on scholarships.gov.in.",
                "description_ta": "scholarships.gov.in தளத்தில் ஆதார் e-KYC மூலம் ஒருமுறை பதிவு செய்யவும்.",
                "portal_url": "https://scholarships.gov.in"
            },
            {
                "step_number": 2,
                "mode": "online",
                "title_en": "Scheme Selection and Document Upload",
                "title_ta": "திட்டம் தேர்வு செய்து சான்றிதழ்கள் பதிவேற்றம்",
                "description_en": "Select Post-Matric scheme, enter academic details and upload certificates.",
                "description_ta": "மெட்ரிக் பின் உதவித்தொகை திட்டத்தை தேர்வு செய்து விவரங்களை உள்ளிடவும்."
            },
            {
                "step_number": 3,
                "mode": "both",
                "title_en": "Institutional and State Nodal Officer Verification & DBT Release",
                "title_ta": "கல்வி நிறுவனம் மற்றும் மாநில அலுவலர் சரிபார்ப்பு & DBT வரவு",
                "description_en": "Institute verifies student records; scholarship disbursed via PFMS direct benefit transfer.",
                "description_ta": "கல்லூரி ஒப்புதலுக்கு பின் மத்திய அரசு DBT மூலம் வங்கி கணக்கில் நேரடியாக செலுத்தும்."
            }
        ],
        "source": {
            "source_name": "National Scholarship Portal, Govt. of India",
            "portal_url": "https://scholarships.gov.in",
            "verified_date": "2026-10-15",
            "verification_status": "verified",
            "helpline_number": "0120-6619540 (NSP Helpline)"
        }
    }
]

def seed_database():
    """Seeds the database with authentic Tamil Nadu government welfare schemes."""
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        inserted_count = 0
        for s_data in SCHEMES_SEED:
            existing = db.query(Scheme).filter(Scheme.id == s_data["id"]).first()
            if existing:
                continue

            scheme = Scheme(
                id=s_data["id"],
                name=s_data["name"],
                name_ta=s_data["name_ta"],
                department=s_data["department"],
                department_ta=s_data["department_ta"],
                category=s_data["category"],
                beneficiary_type=s_data.get("beneficiary_type"),
                beneficiary_type_ta=s_data.get("beneficiary_type_ta"),
                benefit_summary=s_data["benefit_summary"],
                benefit_summary_ta=s_data["benefit_summary_ta"],
                benefit_amount=s_data["benefit_amount"],
                description=s_data["description"],
                description_ta=s_data["description_ta"],
                is_active=True
            )
            db.add(scheme)
            db.flush()

            # Conditions
            for c_data in s_data.get("conditions", []):
                db.add(EligibilityCondition(
                    scheme_id=scheme.id,
                    field_name=c_data["field_name"],
                    operator=c_data.get("operator", "eq"),
                    expected_value=c_data["expected_value"],
                    is_mandatory=c_data.get("is_mandatory", True),
                    description_en=c_data["description_en"],
                    description_ta=c_data["description_ta"],
                    prompt_question_en=c_data.get("prompt_question_en"),
                    prompt_question_ta=c_data.get("prompt_question_ta")
                ))

            # Documents
            for d_data in s_data.get("documents", []):
                db.add(RequiredDocument(
                    scheme_id=scheme.id,
                    name_en=d_data["name_en"],
                    name_ta=d_data["name_ta"],
                    is_mandatory=d_data.get("is_mandatory", True),
                    issuing_authority_en=d_data.get("issuing_authority_en"),
                    issuing_authority_ta=d_data.get("issuing_authority_ta"),
                    description_en=d_data.get("description_en"),
                    description_ta=d_data.get("description_ta")
                ))

            # Steps
            for st_data in s_data.get("steps", []):
                db.add(ApplicationStep(
                    scheme_id=scheme.id,
                    step_number=st_data["step_number"],
                    mode=st_data.get("mode", "both"),
                    title_en=st_data["title_en"],
                    title_ta=st_data["title_ta"],
                    description_en=st_data["description_en"],
                    description_ta=st_data["description_ta"],
                    portal_url=st_data.get("portal_url")
                ))

            # Source
            src_data = s_data.get("source")
            if src_data:
                db.add(OfficialSource(
                    scheme_id=scheme.id,
                    source_name=src_data["source_name"],
                    portal_url=src_data["portal_url"],
                    verified_date=src_data["verified_date"],
                    verification_status=src_data.get("verification_status", "verified"),
                    helpline_number=src_data.get("helpline_number"),
                    government_order_ref=src_data.get("government_order_ref")
                ))

            inserted_count += 1

        db.commit()
        if inserted_count > 0:
            logger.info(f"Successfully seeded {inserted_count} new schemes. Total schemes: {len(SCHEMES_SEED)}.")
        else:
            logger.info(f"All {len(SCHEMES_SEED)} schemes are already present in the database.")

    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_database()
