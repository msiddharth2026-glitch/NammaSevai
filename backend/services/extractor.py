import re
from typing import List, Tuple, Dict, Any
from ..schemas.assistant import ExtractedUserProfile, MissingInformationItem

class CitizenInfoExtractor:
    """
    Extracts structured citizen profile attributes from natural language queries
    in Tamil, Hindi, Malayalam, English, Tanglish, and Hinglish.
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

    HINDI_DISTRICT_NAMES = {
        "चेन्नई": "chennai",
        "मदुरै": "madurai",
        "कोयंबटूर": "coimbatore",
        "तिरुचिरापल्ली": "tiruchirappalli",
        "सलेम": "salem",
        "तिरुनेलवेली": "tirunelveli",
        "तंजாவूर": "thanjavur",
        "वेल्लोर": "vellore"
    }

    MALAYALAM_DISTRICT_NAMES = {
        "ചെന്നൈ": "chennai",
        "മധുര": "madurai",
        "കോയമ്പത്തൂർ": "coimbatore",
        "തിരുച്ചിറപ്പള്ളി": "tiruchirappalli",
        "സേലം": "salem"
    }

    def normalize(self, text: str) -> str:
        # Preserve comma within digits by merging them (e.g. 1,50,000 -> 150000)
        cleaned = re.sub(r'(\d+),(?=\d)', r'\1', text.lower())
        return cleaned.replace("-", " ").replace(",", " ")

    def extract(self, text: str) -> Tuple[ExtractedUserProfile, List[str], List[MissingInformationItem]]:
        norm = self.normalize(text)
        profile = ExtractedUserProfile()
        intents = []
        missing = []

        # 1. Age extraction (Tamil, Hindi, Malayalam, English, Tanglish, Hinglish)
        age_patterns = [
            r'(\d{1,2})\s*(?:years|year|yrs|yr|வயது|வயசு|vayasula|vayasu|साल|वर्ष|उम्र|saal|umar|varsh|വയസ്സ്|വയസ്സുള്ള|വയസ്|വർഷം)',
            r'(?:age|வயது|उम्र|आयु|saal|umar|പ്രായം|വയസ്സ്)\s*(?:is|:|\s|है|ആണ്)\s*(\d{1,2})'
        ]
        for pat in age_patterns:
            m = re.search(pat, norm)
            if m:
                val = int(m.group(1))
                if 1 <= val <= 110:
                    profile.age = val
                    break

        if not profile.age:
            senior_terms = [
                "senior", "முதியோர்", "தாத்தா", "பாட்டி", "elderly",
                "बुजुर्ग", "वृद्ध", "दादा", "दादी", "buzurg", "vridha",
                "വൃദ്ധൻ", "പ്രായമായവർ", "മുത്തശ്ശൻ", "മുത്തശ്ശി"
            ]
            if any(w in norm for w in senior_terms):
                profile.age = 65

        # 2. Gender extraction
        female_signals = [
            "girl", "female", "woman", "women", "mother", "lady", "sister", "daughter",
            "பெண்", "மாணவி", "மகளிர்", "தாய்", "அம்மா", "மனைவி", "vidhavai", "விதவை",
            "लड़की", "महिला", "औरत", "माता", "माँ", "छात्रा", "बेटी", "बहन", "पत्नी", "विधवा", "ladki", "mahila", "aurat", "vidhwa",
            "സ്ത്രീ", "പെൺകുട്ടി", "അമ്മ", "വിദ്യാർത്ഥിനി", "മകൾ", "വിധവ"
        ]
        male_signals = [
            "boy", "male", "man", "men", "son", "brother", "father",
            "ஆண்", "மாணவன்", "அப்பா", "மகன்",
            "लड़का", "पुरुष", "आदमी", "पिता", "छात्र", "बेटा", "भाई", "पति", "ladka", "purush", "aadmi",
            "പുരുഷൻ", "ആൺകുട്ടി", "അച്ഛൻ", "വിദ്യാർത്ഥി", "മകൻ"
        ]

        if any(w in norm for w in female_signals):
            profile.gender = "female"
        elif any(w in norm for w in male_signals):
            profile.gender = "male"

        # 3. Occupation & Education extraction
        student_signals = [
            "student", "college", "school", "degree", "12th", "10th", "diploma", "iti",
            "மாணவி", "மாணவர்", "கல்லூரி", "பள்ளி", "படிப்பு", "kalloori", "padipu",
            "छात्र", "छात्रा", "विद्यार्थी", "कॉलेज", "स्कूल", "पढ़ाई", "डिग्री", "10वीं", "12वीं", "padhai", "padh raha", "padh rahi",
            "വിദ്യാർത്ഥി", "വിദ്യാർത്ഥിനി", "പഠനം", "സ്കൂൾ", "കോളേജ്"
        ]
        if any(w in norm for w in student_signals):
            profile.occupation = "student"
            intents.append("education")
            if any(w in norm for w in ["college", "degree", "கல்லூரி", "कॉलेज", "ഡിഗ്രി", "കോളേജ്"]):
                profile.education_level = "college_ug"
            elif any(w in norm for w in ["12th", "12-ம்", "+2", "12वीं", "പ്ലസ് ടു"]):
                profile.education_level = "school_12th"
            elif any(w in norm for w in ["10th", "10-ம்", "10वीं", "എസ്എസ്എൽസി"]):
                profile.education_level = "school_10th"
            elif any(w in norm for w in ["diploma", "பாலிடெக்னிக்", "डिप्लोमा", "ഡിപ്ലോമ"]):
                profile.education_level = "diploma"

            # Check school type (government vs private)
            if any(w in norm for w in ["govt", "government", "அரசு", "arasu", "सरकारी", "sarkari", "ഗവൺമെന്റ്", "സർക്കാർ"]):
                profile.school_type = "government"
            elif any(w in norm for w in ["private", "தனியார்", "प्राइवेट", "സ്വകാര്യ"]):
                profile.school_type = "private"

        # Agriculture / Farming
        farmer_signals = [
            "farmer", "agriculture", "crop", "land", "acres", "dryland", "wetland",
            "விவசாயி", "உழவர்", "பயிர்", "நிலம்", "ஏக்கர்", "வானம் பார்த்த", "vivasaayi",
            "किसान", "खेती", "कृषि", "फसल", "जमीन", "एकड़", "kisan", "kheti", "zameen", "ekad",
            "കർഷകൻ", "കൃഷി", "നിലം", "ഏക്കർ", "പാടം"
        ]
        if any(w in norm for w in farmer_signals):
            profile.occupation = "farmer"
            intents.append("agriculture")
            acres_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:acres|acre|ஏக்கர்|एकड़|ഏക്കർ|ekad)', norm)
            if acres_match:
                profile.landholding_acres = float(acres_match.group(1))

        # Tailoring
        tailor_signals = ["tailor", "tailoring", "sewing", "தையல்", "दर्जी", "सिलाई", "darzi", "silai", "तैयारी", "തയ്യൽ"]
        if any(w in norm for w in tailor_signals):
            profile.occupation = "tailor"
            profile.has_tailoring_training = True
            intents.append("women")
            intents.append("employment")

        # Widow / Destitute
        widow_signals = ["widow", "destitute", "deserted", "விதவை", "ஆதரவற்ற", "विधवा", "बेसहारा", "vidhwa", "വിധവ"]
        if any(w in norm for w in widow_signals):
            profile.is_widow_or_destitute = True
            profile.gender = "female"
            intents.append("women")

        # Pregnancy / Maternity
        maternity_signals = ["pregnant", "pregnancy", "baby", "maternity", "கர்ப்பிணி", "பிரசவம்", "गर्भवती", "प्रसव", "ഗർഭിണി"]
        if any(w in norm for w in maternity_signals):
            profile.is_pregnant_or_lactating = True
            profile.gender = "female"
            intents.append("health")

        # Senior citizen
        senior_check = ["senior", "pension", "முதியோர்", "ஓய்வூதியம்", "बुजुर्ग", "वृद्ध", "पेंशन", "buzurg", "vridha", "pension", "വൃദ്ധൻ", "വാർദ്ധക്യം", "പെൻഷൻ"]
        if any(w in norm for w in senior_check) or (profile.age and profile.age >= 60):
            profile.occupation = "senior"
            intents.append("seniors")

        # Jobs / Upskilling / Civil services
        skill_signals = ["skill", "coding", "job", "upsc", "tnpsc", "திறன்", "வேலை", "कौशल", "रोजगार", "नौकरी", "റോസ്ഗാർ", "നൈപുണ്യം", "തൊഴിൽ"]
        if any(w in norm for w in skill_signals):
            intents.append("employment")
            if not profile.occupation:
                profile.occupation = "unemployed"

        # Business / MSME / Entrepreneur
        business_signals = ["business", "startup", "msme", "தொழில்", "தொழில்முனைவோர்", "व्यापार", "दुकान", "व्यवसाय", "धंधा", "उद्योग", "dukaan", "dhandha", "vyapar", "संരംഭകൻ", "ചെറുകിട വ്യവസായം", "ബിസിനസ്സ്"]
        if any(w in norm for w in business_signals):
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
        if not profile.district:
            for hi_name, eng_name in self.HINDI_DISTRICT_NAMES.items():
                if hi_name in norm:
                    profile.district = eng_name.capitalize()
                    break
        if not profile.district:
            for ml_name, eng_name in self.MALAYALAM_DISTRICT_NAMES.items():
                if ml_name in norm:
                    profile.district = eng_name.capitalize()
                    break

        # State detection
        if "kerala" in norm or "കേരളം" in norm:
            profile.state = "Kerala"
        elif "delhi" in norm or "दिल्ली" in norm:
            profile.state = "Delhi"
        else:
            profile.state = "Tamil Nadu"

        # 5. Income extraction
        income_match = re.search(r'(?:income|வருமானம்|சம்பளம்|आय|कमाई|वेतन|सैलरी|aamdani|വരുമാനം|ശമ്പളം)\s*(?:is|:|\s|है|ആണ്)?\s*(?:rs\.?|₹)?\s*(\d+(?:\.\d+)?)\s*(?:lakhs|lakh|லட்சம்|लाख|ലക്ഷം)?', norm)
        if income_match:
            try:
                num_str = income_match.group(1)
                val = float(num_str)
                if any(w in norm for w in ["lakh", "லட்சம்", "लाख", "ലക്ഷം"]) and val < 1000:
                    val = val * 100000
                profile.annual_income = val
            except Exception:
                pass
        elif any(w in norm for w in ["bpl", "poor", "ஏழை", "வறுமை", "गरीब", "നിർധന"]):
            profile.annual_income = 72000.0

        # 6. Sensitive attributes (Only when voluntarily supplied and relevant)
        if any(w in norm.split() for w in ["sc", "st", "dalit", "ஆதிதிராவிடர்", "பழங்குடியினர்", "एससी", "एसटी", "दलित", "आदिवासी", "ദളിത്"]):
            profile.community_category = "SC/ST"
        elif any(w in norm.split() for w in ["bc", "mbc", "obc", "பிற்படுத்தப்பட்டோர்", "ओबीसी", "पिछड़ा", "ഒബിസി"]):
            profile.community_category = "BC/MBC"

        if any(w in norm for w in ["disabled", "handicapped", "wheelchair", "udid", "மாற்றுத்திறனாளி", "ஊனம்", "विकलांग", "दिव्यांग", "अपंग", "divyang", "viklang", "ഭിന്നശേഷി", "വികലാംഗ"]):
            profile.disability_status = True
            intents.append("disability")

        # 7. Identify Missing Essential Information for Specific Intents
        if profile.occupation == "student":
            if not profile.school_type:
                missing.append(MissingInformationItem(
                    field_name="school_type",
                    relevance_to_scheme="Pudhumai Penn, Tamil Pudhalvan, and state scholarships require schooling in Government schools (6th-12th standard)",
                    question_en="Did you study in a Government school from 6th to 12th standard?",
                    question_ta="நீங்கள் 6 முதல் 12-ம் வகுப்பு வரை அரசுப் பள்ளியில் படித்தீர்களா?",
                    question_hi="क्या आपने कक्षा 6 से 12 तक सरकारी स्कूल में पढ़ाई की है?",
                    question_ml="നിങ്ങൾ 6 മുതൽ 12 വരെ സർക്കാർ സ്കൂളിലാണോ പഠിച്ചത്?"
                ))
            if not profile.gender:
                missing.append(MissingInformationItem(
                    field_name="gender",
                    relevance_to_scheme="Distinguishes female-focused schemes (Pudhumai Penn) from male-focused schemes (Tamil Pudhalvan)",
                    question_en="Are you a female or male student?",
                    question_ta="நீங்கள் மாணவியா (Female) அல்லது மாணவரா (Male)?",
                    question_hi="क्या आप छात्रा (लड़की) हैं या छात्र (लड़का)?",
                    question_ml="നിങ്ങൾ വിദ്യാർത്ഥിനിയാണോ അതോ വിദ്യാർത്ഥിയാണോ?"
                ))

        if profile.occupation == "farmer":
            if profile.landholding_acres is None:
                missing.append(MissingInformationItem(
                    field_name="landholding_acres",
                    relevance_to_scheme="PM-Kisan and Uzhavar subsidies depend on owning cultivable agricultural land verified via Patta/Chitta",
                    question_en="How many acres of agricultural land do you own, and do you have a valid Patta in your name?",
                    question_ta="உங்களுக்கு எத்தனை ஏக்கர் விவசாய நிலம் உள்ளது? உங்கள் பெயரில் பட்டா / சிட்டா உள்ளதா?",
                    question_hi="आपके पास कितने एकड़ कृषि भूमि है, और क्या आपके नाम पर वैध पट्टा/खतौनी है?",
                    question_ml="നിങ്ങൾക്ക് എത്ര ഏക്കർ കൃഷിഭൂമിയുണ്ട്? നിങ്ങളുടെ പേരിൽ പട്ടയം ഉണ്ടോ?"
                ))

        if profile.occupation == "tailor" or any(w in norm for w in ["sewing", "தையல்", "सिलाई", "തയ്യൽ"]):
            if profile.annual_income is None:
                missing.append(MissingInformationItem(
                    field_name="annual_income",
                    relevance_to_scheme="Free Sewing Machine scheme requires family annual income below ₹72,000",
                    question_en="Is your family annual income less than ₹72,000?",
                    question_ta="உங்கள் குடும்ப ஆண்டு வருமானம் ₹72,000-க்குள் உள்ளதா?",
                    question_hi="क्या आपकी वार्षिक पारिवारिक आय ₹72,000 से कम है?",
                    question_ml="നിങ്ങളുടെ കുടുംബ വാർഷിക വരുമാനം ₹72,000-ൽ താഴെയാണോ?"
                ))

        if any(w in norm for w in ["urimai", "magalir", "1000", "urimai thittam"]):
            if profile.annual_income is None:
                missing.append(MissingInformationItem(
                    field_name="annual_income",
                    relevance_to_scheme="Kalaignar Magalir Urimai Thittam requires annual income less than ₹2.5 Lakhs",
                    question_en="Is your family's annual income below ₹2.5 Lakhs?",
                    question_ta="உங்கள் குடும்ப ஆண்டு வருமானம் ₹2.5 லட்சத்திற்குள் உள்ளதா?",
                    question_hi="क्या आपके परिवार की वार्षिक आय ₹2.5 लाख से कम है?",
                    question_ml="നിങ്ങളുടെ കുടുംബ വാർഷിക വരുമാനം ₹2.5 ലക്ഷത്തിൽ താഴെയാണോ?"
                ))

        # General missing information when essential demographic details are absent
        if not profile.occupation and not profile.age:
            missing.append(MissingInformationItem(
                field_name="occupation",
                relevance_to_scheme="Government welfare schemes are categorized by occupation (student, farmer, entrepreneur, senior citizen)",
                question_en="What is your current occupation or student status?",
                question_ta="உங்கள் தற்போதைய தொழில் அல்லது கல்வி நிலை என்ன?",
                question_hi="आपका वर्तमान व्यवसाय या छात्र स्थिति क्या है?",
                question_ml="നിങ്ങളുടെ ഇപ്പോഴത്തെ തൊഴിൽ അല്ലെങ്കിൽ പഠന നില എന്താണ്?"
            ))
            missing.append(MissingInformationItem(
                field_name="age",
                relevance_to_scheme="Eligibility age limits determine access to education, maternity, and pension schemes",
                question_en="What is your current age?",
                question_ta="உங்கள் வயது என்ன?",
                question_hi="आपकी वर्तमान आयु (उम्र) क्या है?",
                question_ml="നിങ്ങളുടെ പ്രായം എത്രയാണ്?"
            ))
            missing.append(MissingInformationItem(
                field_name="annual_income",
                relevance_to_scheme="Income ceilings determine eligibility for subsidized schemes and pensions",
                question_en="What is your approximate family annual income?",
                question_ta="உங்கள் குடும்ப ஆண்டு வருமானம் தோராயமாக எவ்வளவு?",
                question_hi="आपकी अनुमानित पारिवारिक वार्षिक आय कितनी है?",
                question_ml="നിങ്ങളുടെ ഏകദേശ കുടുംബ വാർഷിക വരുമാനം എത്രയാണ്?"
            ))

        return profile, intents, missing
