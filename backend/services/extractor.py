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

    # Major Indian Cities mapped to State & Display District
    MAJOR_INDIAN_CITIES = {
        # Maharashtra
        "mumbai": ("Maharashtra", "Mumbai"),
        "bombay": ("Maharashtra", "Mumbai"),
        "pune": ("Maharashtra", "Pune"),
        "nagpur": ("Maharashtra", "Nagpur"),
        "thane": ("Maharashtra", "Thane"),
        "nashik": ("Maharashtra", "Nashik"),
        "मुंबई": ("Maharashtra", "Mumbai"),
        "पुणे": ("Maharashtra", "Pune"),
        # Karnataka
        "bengaluru": ("Karnataka", "Bengaluru"),
        "bangalore": ("Karnataka", "Bengaluru"),
        "mysuru": ("Karnataka", "Mysuru"),
        "mysore": ("Karnataka", "Mysuru"),
        "hubli": ("Karnataka", "Hubli"),
        "mangalore": ("Karnataka", "Mangaluru"),
        "பெங்களூரு": ("Karnataka", "Bengaluru"),
        "बेंगलुरु": ("Karnataka", "Bengaluru"),
        "ബെംഗളൂരു": ("Karnataka", "Bengaluru"),
        # Kerala
        "thiruvananthapuram": ("Kerala", "Thiruvananthapuram"),
        "trivandrum": ("Kerala", "Thiruvananthapuram"),
        "kochi": ("Kerala", "Kochi"),
        "cochin": ("Kerala", "Kochi"),
        "kozhikode": ("Kerala", "Kozhikode"),
        "calicut": ("Kerala", "Kozhikode"),
        "thrissur": ("Kerala", "Thrissur"),
        "തിരുവനന്തപുരം": ("Kerala", "Thiruvananthapuram"),
        "കൊച്ചി": ("Kerala", "Kochi"),
        # Delhi
        "delhi": ("Delhi", "Delhi"),
        "new delhi": ("Delhi", "New Delhi"),
        "दिल्ली": ("Delhi", "Delhi"),
        "டெல்லி": ("Delhi", "Delhi"),
        "ഡൽഹി": ("Delhi", "Delhi"),
        # Uttar Pradesh
        "lucknow": ("Uttar Pradesh", "Lucknow"),
        "kanpur": ("Uttar Pradesh", "Kanpur"),
        "varanasi": ("Uttar Pradesh", "Varanasi"),
        "banaras": ("Uttar Pradesh", "Varanasi"),
        "noida": ("Uttar Pradesh", "Gautam Buddha Nagar"),
        "agra": ("Uttar Pradesh", "Agra"),
        "prayagraj": ("Uttar Pradesh", "Prayagraj"),
        "allahabad": ("Uttar Pradesh", "Prayagraj"),
        "लखनऊ": ("Uttar Pradesh", "Lucknow"),
        "वाराणसी": ("Uttar Pradesh", "Varanasi"),
        # Gujarat
        "ahmedabad": ("Gujarat", "Ahmedabad"),
        "surat": ("Gujarat", "Surat"),
        "vadodara": ("Gujarat", "Vadodara"),
        "gandhinagar": ("Gujarat", "Gandhinagar"),
        # West Bengal
        "kolkata": ("West Bengal", "Kolkata"),
        "calcutta": ("West Bengal", "Kolkata"),
        "howrah": ("West Bengal", "Howrah"),
        # Telangana & Andhra
        "hyderabad": ("Telangana", "Hyderabad"),
        "secunderabad": ("Telangana", "Hyderabad"),
        "warangal": ("Telangana", "Warangal"),
        "visakhapatnam": ("Andhra Pradesh", "Visakhapatnam"),
        "vizag": ("Andhra Pradesh", "Visakhapatnam"),
        "vijayawada": ("Andhra Pradesh", "Vijayawada"),
        # Rajasthan
        "jaipur": ("Rajasthan", "Jaipur"),
        "jodhpur": ("Rajasthan", "Jodhpur"),
        "udaipur": ("Rajasthan", "Udaipur"),
        # Bihar
        "patna": ("Bihar", "Patna"),
        "gaya": ("Bihar", "Gaya"),
        # Madhya Pradesh
        "bhopal": ("Madhya Pradesh", "Bhopal"),
        "indore": ("Madhya Pradesh", "Indore"),
        # Punjab & Haryana
        "chandigarh": ("Chandigarh", "Chandigarh"),
        "amritsar": ("Punjab", "Amritsar"),
        "ludhiana": ("Punjab", "Ludhiana"),
        "gurugram": ("Haryana", "Gurugram"),
        "gurgaon": ("Haryana", "Gurugram"),
        # Odisha
        "bhubaneswar": ("Odisha", "Bhubaneswar"),
        "cuttack": ("Odisha", "Cuttack"),
        # Assam
        "guwahati": ("Assam", "Kamrup Metropolitan"),
        # Uttarakhand & HP
        "dehradun": ("Uttarakhand", "Dehradun"),
        "shimla": ("Himachal Pradesh", "Shimla"),
        # Goa
        "panaji": ("Goa", "North Goa"),
        # J&K / Ladakh
        "srinagar": ("Jammu and Kashmir", "Srinagar"),
        "jammu": ("Jammu and Kashmir", "Jammu"),
        "leh": ("Ladakh", "Leh"),
        # Puducherry
        "puducherry": ("Puducherry", "Puducherry"),
        "pondicherry": ("Puducherry", "Puducherry")
    }

    # All 28 States & 8 UTs name variations in English, Tamil, Hindi, Malayalam
    STATE_NAMES_MULTILINGUAL = {
        # States
        "Andhra Pradesh": ["andhra pradesh", "andhra", "ஆந்திரப் பிரதேசம்", "ஆந்திரா", "आंध्र प्रदेश", "ആന്ധ്രാപ്രദേശ്"],
        "Arunachal Pradesh": ["arunachal pradesh", "arunachal", "அருணாச்சலப் பிரதேசம்", "अरुणाचल प्रदेश", "അരുണാചൽ പ്രദേശ്"],
        "Assam": ["assam", "asom", "அசாம்", "असम", "ആസാം", "അസം"],
        "Bihar": ["bihar", "பீகார்", "बिहार", "ബീഹാർ"],
        "Chhattisgarh": ["chhattisgarh", "chattisgarh", "சத்தீஸ்கர்", "छत्तीसगढ़", "ഛത്തീസ്ഗഡ്"],
        "Goa": ["goa", "கோவா", "गोवा", "ഗോവ"],
        "Gujarat": ["gujarat", "குஜராத்", "गुजरात", "ഗുജറാത്ത്"],
        "Haryana": ["haryana", "ஹரியானா", "हरियाणा", "ഹരിയാന"],
        "Himachal Pradesh": ["himachal pradesh", "himachal", "இமாச்சலப் பிரதேசம்", "हिमाचल प्रदेश", "ഹിമാചൽ പ്രദേശ്"],
        "Jharkhand": ["jharkhand", "ஜார்க்கண்ட்", "झारखंड", "ജാർഖണ്ഡ്"],
        "Karnataka": ["karnataka", "கர்நாடகா", "கர்நாடகம்", "कर्नाटक", "കർണാടക"],
        "Kerala": ["kerala", "கேரளா", "கேரளம்", "केरल", "കേരളം", "കേരള"],
        "Madhya Pradesh": ["madhya pradesh", "மத்திய பிரதேசம்", "मध्य प्रदेश", "മധ്യപ്രദേശ്"],
        "Maharashtra": ["maharashtra", "மகாராஷ்டிரா", "மகாராஷ்டிர", "महाराष्ट्र", "മഹാരാഷ്ട്ര"],
        "Manipur": ["manipur", "மணிப்பூர்", "मणिपुर", "മണിപ്പൂർ"],
        "Meghalaya": ["meghalaya", "மேகாலயா", "मेघालय", "മേഘാലയ"],
        "Mizoram": ["mizoram", "மிசோரம்", "मिजोरम", "മിസോറാം"],
        "Nagaland": ["nagaland", "நாகாலாந்து", "नागालैंड", "നാഗാലാൻഡ്"],
        "Odisha": ["odisha", "orissa", "ஒடிசா", "ஒரிசா", "ओडिशा", "उड़ीसा", "ഒഡീഷ"],
        "Punjab": ["punjab", "பஞ்சாப்", "पंजाब", "പഞ്ചാബ്"],
        "Rajasthan": ["rajasthan", "ராஜஸ்தான்", "राजस्थान", "രാജസ്ഥാൻ"],
        "Sikkim": ["sikkim", "சிக்கிம்", "सिक्किम", "സിക്കിം"],
        "Tamil Nadu": ["tamil nadu", "tamilnadu", "தமிழ்நாடு", "தமிழ் நாடு", "तमिलनाडु", "തമിഴ്നാട്"],
        "Telangana": ["telangana", "தெலுங்கானா", "तेलंगाना", "തെലങ്കാന"],
        "Tripura": ["tripura", "திரிபுரா", "त्रिपुरा", "ത്രിപുര"],
        "Uttar Pradesh": ["uttar pradesh", "உத்தரப் பிரதேசம்", "உத்தர பிரதேசம்", "उत्तर प्रदेश", "ഉത്തർപ്രദേശ്"],
        "Uttarakhand": ["uttarakhand", "uttaranchal", "உத்தரகாண்ட்", "उत्तराखंड", "ഉത്തരാഖണ്ഡ്"],
        "West Bengal": ["west bengal", "bengal", "மேற்கு வங்காளம்", "पश्चिम बंगाल", "പശ്ചിമ ബംഗാൾ"],
        # Union Territories
        "Andaman and Nicobar Islands": ["andaman", "nicobar", "அந்தமான்", "अंडमान", "ആൻഡമാൻ"],
        "Chandigarh": ["chandigarh", "சண்டிகர்", "चंडीगढ़", "ചണ്ഡീഗഡ്"],
        "Dadra and Nagar Haveli and Daman and Diu": ["daman", "diu", "dadra", "nagar haveli", "தாமன்", "दमन", "ദാമൻ"],
        "Delhi": ["delhi", "new delhi", "டெல்லி", "தில்லி", "दिल्ली", "ഡൽഹി"],
        "Jammu and Kashmir": ["jammu", "kashmir", "ஜம்மு", "காஷ்மீர்", "जम्मू और कश्मीर", "ജമ്മു കശ്മീർ"],
        "Ladakh": ["ladakh", "லடாக்", "लद्दाख", "ലഡാക്ക്"],
        "Lakshadweep": ["lakshadweep", "லட்சத்தீவு", "लक्षद्वीप", "ലക്ഷദ്വീപ്"],
        "Puducherry": ["puducherry", "pondicherry", "பாண்டிச்சேரி", "புதுச்சேரி", "पुदुचेरी", "പുതുച്ചേരി"]
    }

    def normalize(self, text: str) -> str:
        # Preserve comma within digits by merging them (e.g. 1,50,000 -> 150000)
        cleaned = re.sub(r'(\d+),(?=\d)', r'\1', text.lower())
        return cleaned.replace("-", " ").replace(",", " ")

    def _has_signal(self, text: str, signals: List[str]) -> bool:
        for s in signals:
            if s.isascii():
                if re.search(r'\b' + re.escape(s) + r'\b', text):
                    return True
            else:
                if s in text:
                    return True
        return False

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

        if self._has_signal(norm, female_signals):
            profile.gender = "female"
        elif self._has_signal(norm, male_signals):
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
            profile.is_student = True
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
            profile.is_farmer = True
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
            profile.marital_status = "widow"
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

        # Check major Indian cities across all states (longest name first e.g. "new delhi" before "delhi")
        detected_state_from_city = None
        for city_key in sorted(self.MAJOR_INDIAN_CITIES.keys(), key=len, reverse=True):
            if self._has_signal(norm, [city_key]):
                st_name, dist_name = self.MAJOR_INDIAN_CITIES[city_key]
                if not profile.district:
                    profile.district = dist_name
                detected_state_from_city = st_name
                break

        # Comprehensive State / Union Territory detection (All 28 States & 8 UTs)
        detected_state = None
        for canonical_state, signals in self.STATE_NAMES_MULTILINGUAL.items():
            if self._has_signal(norm, signals):
                detected_state = canonical_state
                break

        if detected_state:
            profile.state = detected_state
        elif detected_state_from_city:
            profile.state = detected_state_from_city
        elif profile.district:
            # If a Tamil Nadu district was identified earlier, state is Tamil Nadu
            profile.state = "Tamil Nadu"
        else:
            profile.state = None

        # 5. Income extraction
        if re.search(r'-\s*(?:rs\.?|₹)?\s*\d+', norm):
            profile.annual_income = -1.0
        else:
            income_match = re.search(r'(?:income|வருமானம்|சம்பளம்|आय|कमाई|वेतन|सैलरी|aamdani|വരുമാനം|ശമ്പളം)\s*(?:is|:|\s|है|ആണ്)?\s*(?:rs\.?|₹)?\s*(\d+(?:\.\d+)?)\s*(?:lakhs|lakh|லட்சம்|लाख|ലക്ഷം)?', norm)
            if income_match:
                try:
                    num_str = income_match.group(1)
                    val = float(num_str)
                    if any(w in norm for w in ["lakh", "லட்சம்", "लाख", "ലക്ഷம்"]) and val < 1000:
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

        # Ration card signals
        if any(w in norm for w in ["bpl", "phh", "aay", "antyodaya", "ration card", "ரேஷன் அட்டை", "राशन कार्ड"]):
            profile.ration_card_type = "bpl"

        # Housing / Residence type signals
        if any(w in norm for w in ["pucca", "own house", "independent house", "சொந்த வீடு", "पक्का मकान"]):
            profile.residence_type = "pucca"
        elif any(w in norm for w in ["rural", "கிராமம்", "ग्रामीण"]):
            profile.residence_type = "rural"

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

        if any(w in norm for w in ["solar", "rooftop", "சூரிய சக்தி", "छत", "सौर"]):
            if not profile.residence_type:
                missing.append(MissingInformationItem(
                    field_name="residence_type",
                    relevance_to_scheme="PM Surya Ghar Muft Bijli Yojana requires owning a residential house with suitable roof",
                    question_en="Do you own a residential house with a suitable rooftop for solar panel installation?",
                    question_ta="சூரிய மின் பலகைகள் நிறுவ பொருத்தமான கூரையுடன் கூடிய சொந்த குடியிருப்பு வீடு உங்களுக்கு உள்ளதா?",
                    question_hi="क्या आपके पास सौर पैनल स्थापित करने के लिए उपयुक्त छत वाला आवासीय मकान है?",
                    question_ml="സോളാർ പാനലുകൾ സ്ഥാപിക്കാൻ അനുയോജ്യമായ മേൽക്കൂരയുള്ള സ്വന്തം വീട് നിങ്ങൾക്കുണ്ടോ?"
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

        # 8. National Geographic Profile: Prompt for State/UT when not mentioned
        if not profile.state:
            missing.append(MissingInformationItem(
                field_name="state",
                relevance_to_scheme="State-specific welfare schemes require residency in that particular State or Union Territory",
                question_en="Which State or Union Territory do you currently reside in?",
                question_ta="நீங்கள் எந்த மாநிலம் அல்லது யூனியன் பிரதேசத்தில் வசிக்கிறீர்கள்?",
                question_hi="आप किस राज्य या केंद्र शासित प्रदेश में रहते हैं?",
                question_ml="നിങ്ങൾ ഏത് സംസ്ഥാനത്താണ് അല്ലെങ്കിൽ കേന്ദ്രഭരണ പ്രദേശത്താണ് താമസിക്കുന്നത്?"
            ))

        return profile, intents, missing
