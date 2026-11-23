import re
from typing import List, Tuple, Dict, Any
from ..schemas.assistant import ExtractedUserProfile, MissingInformationItem

class CitizenInfoExtractor:
    """
    Extracts structured citizen profile attributes from natural language queries
    in Tamil, Tanglish, and English.
    """

    TAMIL_NADU_DISTRICTS = [
        "ariyalur", "chengalpattu", "chennai", "coimbatore", "cuddalore", "dharmapuri",
        "dindigul", "erode", "kallakurichi", "kanchipuram", "kanyakumari", "karur",
        "krishnagiri", "madurai", "mayiladuthurai", "nagapattinam", "namakkal", "nilgiris",
        "perambalur", "pudukkottai", "ramanathapuram", "ranipet", "salem", "sivaganga",
        "tenkasi", "thanjavur", "theni", "thoothukudi", "tiruchirappalli", "trichy",
        "tirunelveli", "tirupathur", "tiruppur", "tiruvallur", "tiruvannamalai",
        "tiruvarur", "vellore", "viluppuram", "virudhunagar"
    ]

    TAMIL_DISTRICT_NAMES = {
        "சென்னை": "chennai",
        "மதுரை": "madurai",
        "கோவை": "coimbatore",
        "கோயம்புத்தூர்": "coimbatore",
        "திருச்சி": "tiruchirappalli",
        "திருச்சிராப்பள்ளி": "tiruchirappalli",
        "சேலம்": "salem",
        "திருநெல்வேலி": "tirunelveli",
        "தஞ்சாவூர்": "thanjavur",
        "ஈரோடு": "erode",
        "திண்டுக்கல்": "dindigul",
        "வேலூர்": "vellore"
    }

    def normalize(self, text: str) -> str:
        return text.lower().replace("-", " ").replace(",", " ")

    def extract(self, text: str) -> Tuple[ExtractedUserProfile, List[str], List[MissingInformationItem]]:
        norm = self.normalize(text)
        profile = ExtractedUserProfile()
        intents = []
        missing = []

        # 1. Age extraction
        age_patterns = [
            r'(\d{1,2})\s*(?:years|year|yrs|yr|வயது|வயசு|vayasula|vayasu)',
            r'(?:age|வயது)\s*(?:is|:|\s)\s*(\d{1,2})'
        ]
        for pat in age_patterns:
            m = re.search(pat, norm)
            if m:
                val = int(m.group(1))
                if 1 <= val <= 110:
                    profile.age = val
                    break

        if not profile.age:
            if "senior" in norm or "முதியோர்" in norm or "தாத்தா" in norm or "பாட்டி" in norm or "elderly" in norm:
                profile.age = 65

        # 2. Gender extraction
        female_signals = [
            "girl", "female", "woman", "women", "mother", "lady", "sister", "daughter",
            "பெண்", "மாணவி", "மகளிர்", "தாய்", "அம்மா", "மனைவி", "vidhavai", "விதவை"
        ]
        male_signals = [
            "boy", "male", "man", "men", "son", "brother", "father",
            "ஆண்", "மாணவன்", "அப்பா", "மகன்"
        ]

        if any(w in norm for w in female_signals):
            profile.gender = "female"
        elif any(w in norm for w in male_signals):
            profile.gender = "male"

        # 3. Occupation & Education extraction
        student_signals = [
            "student", "college", "school", "degree", "12th", "10th", "diploma", "iti",
            "மாணவி", "மாணவர்", "கல்லூரி", "பள்ளி", "படிப்பு", "kalloori", "padipu"
        ]
        if any(w in norm for w in student_signals):
            profile.occupation = "student"
            intents.append("education")
            if "college" in norm or "degree" in norm or "கல்லூரி" in norm:
                profile.education_level = "college_ug"
            elif "12th" in norm or "12-ம்" in norm or "+2" in norm:
                profile.education_level = "school_12th"
            elif "10th" in norm or "10-ம்" in norm:
                profile.education_level = "school_10th"
            elif "diploma" in norm or "பாலிடெக்னிக்" in norm:
                profile.education_level = "diploma"

            # Check school type (government vs private)
            if "govt" in norm or "government" in norm or "அரசு" in norm or "arasu" in norm:
                profile.school_type = "government"
            elif "private" in norm or "தனியார்" in norm:
                profile.school_type = "private"

        # Agriculture / Farming
        farmer_signals = [
            "farmer", "agriculture", "crop", "land", "acres", "dryland", "wetland",
            "விவசாயி", "உழவர்", "பயிர்", "நிலம்", "ஏக்கர்", "வானம் பார்த்த", "vivasaayi"
        ]
        if any(w in norm for w in farmer_signals):
            profile.occupation = "farmer"
            intents.append("agriculture")
            acres_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:acres|acre|ஏக்கர்)', norm)
            if acres_match:
                profile.landholding_acres = float(acres_match.group(1))

        # Tailoring
        if "tailor" in norm or "tailoring" in norm or "sewing" in norm or "தையல்" in norm:
            profile.occupation = "tailor"
            profile.has_tailoring_training = True
            intents.append("women")
            intents.append("employment")

        # Widow / Destitute
        if "widow" in norm or "destitute" in norm or "deserted" in norm or "விதவை" in norm or "ஆதரவற்ற" in norm:
            profile.is_widow_or_destitute = True
            profile.gender = "female"
            intents.append("women")

        # Pregnancy / Maternity
        if "pregnant" in norm or "pregnancy" in norm or "baby" in norm or "maternity" in norm or "கர்ப்பிணி" in norm or "பிரசவம்" in norm:
            profile.is_pregnant_or_lactating = True
            profile.gender = "female"
            intents.append("health")

        # Senior citizen
        if "senior" in norm or "pension" in norm or "முதியோர்" in norm or "ஓய்வூதியம்" in norm or (profile.age and profile.age >= 60):
            profile.occupation = "senior"
            intents.append("seniors")

        # Jobs / Upskilling / Civil services
        if "skill" in norm or "coding" in norm or "job" in norm or "upsc" in norm or "tnpsc" in norm or "திறன்" in norm or "வேலை" in norm:
            intents.append("employment")
            if not profile.occupation:
                profile.occupation = "unemployed"

        # Business / MSME / Entrepreneur
        if "business" in norm or "startup" in norm or "msme" in norm or "தொழில்" in norm or "தொழில்முனைவோர்" in norm:
            intents.append("employment")
            if not profile.occupation:
                profile.occupation = "entrepreneur"

        # 4. District extraction
        for dist in self.TAMIL_NADU_DISTRICTS:
            if dist in norm:
                profile.district = dist.capitalize()
                break
        if not profile.district:
            for ta_name, eng_name in self.TAMIL_DISTRICT_NAMES.items():
                if ta_name in norm:
                    profile.district = eng_name.capitalize()
                    break

        # 5. Income extraction
        income_match = re.search(r'(?:income|வருமானம்|சம்பளம்)\s*(?:is|:|\s)?\s*(?:rs\.?|₹)?\s*(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:lakhs|lakh|லட்சம்)?', norm)
        if income_match:
            try:
                num_str = income_match.group(1).replace(",", "")
                val = float(num_str)
                if "lakh" in norm or "லட்சம்" in norm:
                    val = val * 100000
                profile.annual_income = val
            except Exception:
                pass
        elif "bpl" in norm or "poor" in norm or "ஏழை" in norm or "வறுமை" in norm:
            profile.annual_income = 72000.0

        # 6. Sensitive attributes (Only when voluntarily supplied and relevant)
        if "sc" in norm.split() or "st" in norm.split() or "dalit" in norm or "ஆதிதிராவிடர்" in norm or "பழங்குடியினர்" in norm:
            profile.community_category = "SC/ST"
        elif "bc" in norm.split() or "mbc" in norm.split() or "பிற்படுத்தப்பட்டோர்" in norm:
            profile.community_category = "BC/MBC"

        if "disabled" in norm or "handicapped" in norm or "wheelchair" in norm or "udid" in norm or "மாற்றுத்திறனாளி" in norm or "ஊனம்" in norm:
            profile.disability_status = True
            intents.append("disability")

        # 7. Identify Missing Essential Information for Specific Intents
        # Requirement 5: "If essential information is missing, ask follow-up questions instead of assuming values"
        if profile.occupation == "student":
            if not profile.school_type:
                missing.append(MissingInformationItem(
                    field_name="school_type",
                    relevance_to_scheme="Pudhumai Penn and Tamil Pudhalvan require schooling in Tamil Nadu Government schools (6th-12th standard)",
                    question_en="Did you study in a Tamil Nadu Government school from 6th to 12th standard?",
                    question_ta="நீங்கள் 6 முதல் 12-ம் வகுப்பு வரை தமிழ்நாடு அரசுப் பள்ளியில் படித்தீர்களா?"
                ))
            if not profile.gender:
                missing.append(MissingInformationItem(
                    field_name="gender",
                    relevance_to_scheme="Helps distinguish Pudhumai Penn (for girls) and Tamil Pudhalvan (for boys)",
                    question_en="Are you a female or male student?",
                    question_ta="நீங்கள் மாணவியா (Girl) அல்லது மாணவரா (Boy)?"
                ))

        if profile.occupation == "farmer":
            if profile.landholding_acres is None:
                missing.append(MissingInformationItem(
                    field_name="landholding_acres",
                    relevance_to_scheme="PM-Kisan and TN Uzhavar subsidies depend on owning cultivable land verified via Patta/Chitta",
                    question_en="How many acres of agricultural land do you own, and do you have a valid Patta in your name?",
                    question_ta="உங்களுக்கு எத்தனை ஏக்கர் விவசாய நிலம் உள்ளது? உங்கள் பெயரில் பட்டா / சிட்டா உள்ளதா?"
                ))

        if profile.occupation == "tailor" or "sewing" in norm or "தையல்" in norm:
            if profile.annual_income is None:
                missing.append(MissingInformationItem(
                    field_name="annual_income",
                    relevance_to_scheme="Free Sewing Machine scheme requires family annual income below ₹72,000",
                    question_en="Is your family annual income less than ₹72,000?",
                    question_ta="உங்கள் குடும்ப ஆண்டு வருமானம் ₹72,000-க்குள் உள்ளதா?"
                ))

        if "urimai" in norm or "magalir" in norm or "1000" in norm:
            if profile.annual_income is None:
                missing.append(MissingInformationItem(
                    field_name="annual_income",
                    relevance_to_scheme="Kalaignar Magalir Urimai Thittam requires annual income less than ₹2.5 Lakhs",
                    question_en="Is your family's annual income below ₹2.5 Lakhs?",
                    question_ta="உங்கள் குடும்ப ஆண்டு வருமானம் ₹2.5 லட்சத்திற்குள் உள்ளதா?"
                ))

        return profile, intents, missing
