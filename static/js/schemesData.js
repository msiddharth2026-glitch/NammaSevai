// NammaSevai AI - Welfare Schemes Database
// Realistic sample data for Tamil Nadu & Central Government schemes
export const initialSchemes = [
  {
    id: "pudhumai-penn",
    name: "Moovalur Ramamirtham Ammaiyar Higher Education Assurance Scheme (Pudhumai Penn)",
    name_ta: "மூவலூர் ராமாமிர்தம் அம்மையார் புதுமைப் பெண் திட்டம்",
    department: "Social Welfare and Women Empowerment Department",
    department_ta: "சமூக நலன் மற்றும் மகளிர் உரிமைத் துறை",
    category: "education",
    beneficiary_type: "Girl students joining undergraduate/diploma courses",
    beneficiary_type_ta: "அரசுப் பள்ளியில் படித்து கல்லூரி சேரும் மாணவிகள்",
    benefit_summary: "₹1,000 per month deposited directly into bank account until graduation",
    benefit_summary_ta: "கல்லூரி படிப்பு முடியும் வரை மாதம் ₹1,000 நேரடி வங்கி வரவு",
    benefit_amount: "₹1,000 / month",
    description: "Financial assistance to encourage female students who studied from 6th to 12th standard in Tamil Nadu government schools to pursue higher education without financial constraints.",
    description_ta: "தமிழ்நாடு அரசுப் பள்ளிகளில் 6 முதல் 12-ம் வகுப்பு வரை பயின்று உயர்கல்வியில் (டிகிரி, பாலிடெக்னிக், தொழிற்கல்வி) சேரும் மாணவிகளுக்கு மாதம் ₹1,000 உதவித்தொகை வழங்கும் திட்டம்.",
    eligibility_criteria: [
      "Must have studied Classes 6 to 12 in Tamil Nadu Government schools",
      "Must be enrolled in recognized higher education (UG degree, diploma, ITI, or professional degree)",
      "Applicable regardless of community or annual family income ceiling",
      "Student must have a valid individual bank account seeded with Aadhaar"
    ],
    eligibility_criteria_ta: [
      "6 முதல் 12-ம் வகுப்பு வரை தமிழ்நாடு அரசுப் பள்ளிகளில் படித்திருக்க வேண்டும்",
      "அங்கீகரிக்கப்பட்ட கல்லூரியில் பட்டப்படிப்பு, பட்டயப்படிப்பு அல்லது தொழிற்கல்வி பயில வேண்டும்",
      "சாதி அல்லது குடும்ப வருமான வரம்பு எதுவும் இல்லை",
      "ஆதார் இணைக்கப்பட்ட மாணவியின் சொந்த வங்கிக் கணக்கு இருக்க வேண்டும்"
    ],
    required_documents: [
      { name: "Aadhaar Card", name_ta: "ஆதார் அட்டை", mandatory: true },
      { name: "10th & 12th Marksheet", name_ta: "10 மற்றும் 12-ம் வகுப்பு மதிப்பெண் சான்றிதழ்", mandatory: true },
      { name: "Govt School Study Bonafide (6th-12th)", name_ta: "அரசுப் பள்ளி பயின்றதற்கான சான்றிதழ் (Bonafide)", mandatory: true },
      { name: "College Admission ID / Bonafide", name_ta: "கல்லூரி சேர்க்கை அட்டை / பயிலும் சான்றிதழ்", mandatory: true },
      { name: "Bank Passbook with IFSC", name_ta: "வங்கி சேமிப்புக் கணக்கு புத்தகம்", mandatory: true }
    ],
    application_procedure: {
      online: "Apply through the official portal or through college nodal officer via penkalvi.tn.gov.in during college admission cycle.",
      online_ta: "கல்லூரி சேர்க்கையின் போது penkalvi.tn.gov.in போர்ட்டலில் கல்லூரி ஒருங்கிணைப்பாளர் மூலம் விண்ணப்பிக்கலாம்.",
      offline: "Submit documents directly to your college principal/nodal officer or nearest Taluk Social Welfare Office.",
      offline_ta: "கல்லூரி முதல்வர் அல்லது தாலுகா சமூக நல அலுவலகத்தில் நேரடியாக ஆவணங்களை சமர்ப்பிக்கலாம்."
    },
    official_portal: "https://www.penkalvi.tn.gov.in",
    official_source: "Tamil Nadu Social Welfare Dept (Sample Demo Entry)",
    source_verification: "verified",
    verified_date: "2026-10-20",
    important_dates: "Applications accepted at the start of each academic year (July - October)",
    important_dates_ta: "ஒவ்வொரு கல்வியாண்டு துவக்கத்திலும் (ஜூலை - அக்டோபர்) விண்ணப்பிக்கலாம்",
    helpline: "044-24351885 / CM Helpline 1100",
    keywords: ["girl", "student", "college", "scholarship", "1000", "pudhumai penn", "education", "degree", "penkalvi", "பள்ளி", "கல்லூரி", "மாணவி", "உதவித்தொகை", "பெண்"]
  },
  {
    id: "kmut-magalir",
    name: "Kalaignar Magalir Urimai Thittam (KMUT)",
    name_ta: "கலைஞர் மகளிர் உரிமைத் திட்டம்",
    department: "Special Programme Implementation & Revenue Department",
    department_ta: "சிறப்புத் திட்டச் செயலாக்கம் மற்றும் வருவாய்த் துறை",
    category: "women",
    beneficiary_type: "Eligible female heads of family in Tamil Nadu",
    beneficiary_type_ta: "குடும்பத் தலைவிகள் (பெண்கள்)",
    benefit_summary: "₹1,000 monthly basic income guarantee directly credited to bank account",
    benefit_summary_ta: "குடும்பத் தலைவிகளுக்கு மாதம் ₹1,000 உரிமைத் தொகை வங்கி வரவு",
    benefit_amount: "₹1,000 / month",
    description: "A flagship universal basic income program recognizing unpaid care work and providing economic independence to women heads of family across Tamil Nadu.",
    description_ta: "குடும்பத் தலைவிகளின் உழைப்பை அங்கீகரித்து, அவர்களின் பொருளாதார சுதந்திரத்திற்காக மாதம் ₹1,000 வழங்கும் வரலாற்றுச் சிறப்புமிக்க திட்டம்.",
    eligibility_criteria: [
      "Female head of family named in the Smart Family Ration Card",
      "Family annual income should be less than ₹2.5 Lakhs",
      "Family must consume less than 3,600 units of domestic electricity per year",
      "Family owns less than 5 acres of wetland or 10 acres of dryland",
      "Applicant age should be 21 years or older"
    ],
    eligibility_criteria_ta: [
      "ஸ்மார்ட் ரேஷன் கார்டில் குடும்பத் தலைவியாக பெயர் இருக்க வேண்டும்",
      "குடும்ப ஆண்டு வருமானம் ₹2.5 லட்சத்திற்கு மிகாமல் இருக்க வேண்டும்",
      "ஆண்டுக்கு 3,600 யூனிட்டிற்கும் குறைவாக மின்சாரம் பயன்படுத்துபவராக இருக்க வேண்டும்",
      "5 ஏக்கருக்கு குறைவான நன்செய் அல்லது 10 ஏக்கருக்கு குறைவான புன்செய் நிலம் இருக்க வேண்டும்",
      "விண்ணப்பதாரருக்கு 21 வயது பூர்த்தியாகியிருக்க வேண்டும்"
    ],
    required_documents: [
      { name: "Smart Ration Card", name_ta: "ஸ்மார்ட் குடும்ப அட்டை", mandatory: true },
      { name: "Aadhaar Card", name_ta: "ஆதார் அட்டை", mandatory: true },
      { name: "Electricity Consumer Number / Bill", name_ta: "மின் இணைப்பு அட்டை / மின் நுகர்வோர் எண்", mandatory: true },
      { name: "Bank Passbook with IFSC", name_ta: "வங்கி சேமிப்புக் கணக்கு புத்தகம்", mandatory: true }
    ],
    application_procedure: {
      online: "Apply through special camp enrollment or e-Sevai citizen portal at kmut.tn.gov.in.",
      online_ta: "சிறப்பு முகாம்கள் அல்லது kmut.tn.gov.in மற்றும் இ-சேவை மூலம் விண்ணப்பிக்கலாம்.",
      offline: "Visit the Revenue Inspector (RI) office, Village Administrative Officer (VAO), or e-Sevai center.",
      offline_ta: "கிராம நிர்வாக அலுவலர் (VAO), வருவாய் ஆய்வாளர் அல்லது வட்டார இ-சேவை மையத்தை அணுகலாம்."
    },
    official_portal: "https://kmut.tn.gov.in",
    official_source: "Tamil Nadu Revenue Department (Sample Demo Entry)",
    source_verification: "verified",
    verified_date: "2026-11-01",
    important_dates: "Continuous enrollment & grievance appeals processed at Taluk level",
    important_dates_ta: "வட்டார அலுவலகங்களில் தொடர் பதிவு மற்றும் மேல்முறையீடு வசதி உண்டு",
    helpline: "044-25619224 / CM Helpline 1100",
    keywords: ["women", "mother", "magalir", "urimai", "1000", "kmut", "ration card", "pension", "family", "பெண்", "மகளிர்", "உரிமைத்தொகை", "ரேஷன்", "அம்மா", "குடும்பத்தலைவி"]
  },
  {
    id: "cmchis-health",
    name: "Chief Minister's Comprehensive Health Insurance Scheme (CMCHIS)",
    name_ta: "முதலமைச்சரின் விரிவான மருத்துவக் காப்பீட்டுத் திட்டம்",
    department: "Health and Family Welfare Department",
    department_ta: "மக்கள் நல்வாழ்வு மற்றும் குடும்ப நலத்துறை",
    category: "health",
    beneficiary_type: "Low-income families, daily wage earners, rural citizens",
    beneficiary_type_ta: "ஏழை மற்றும் நடுத்தர குடும்பங்கள், அமைப்புசாரா தொழிலாளர்கள்",
    benefit_summary: "Cashless medical treatment up to ₹5,00,000 per family per year",
    benefit_summary_ta: "ஆண்டுக்கு ₹5 லட்சம் வரை கட்டணமில்லா சிகிச்சை காப்பீடு",
    benefit_amount: "Up to ₹5,00,000 / family / year",
    description: "Comprehensive cashless hospitalization and surgical treatment across empanelled government and top private hospitals for 1,500+ listed medical procedures.",
    description_ta: "அரசு மற்றும் தனியார் மருத்துவமனைகளில் 1,500-க்கும் மேற்பட்ட அறுவை சிகிச்சைகள் மற்றும் தீவிர சிகிச்சைகளுக்கு குடும்பத்திற்கு ₹5 லட்சம் வரை கட்டணமில்லா மருத்துவ உதவி.",
    eligibility_criteria: [
      "Resident of Tamil Nadu with name present on Smart Ration Card",
      "Family annual income should be less than ₹1,20,000 per annum (or registered unorganized worker)",
      "Members enrolled under unorganized welfare boards are eligible automatically"
    ],
    eligibility_criteria_ta: [
      "தமிழ்நாடு ஸ்மார்ட் ரேஷன் கார்டில் குடும்ப உறுப்பினராக இருக்க வேண்டும்",
      "குடும்ப ஆண்டு வருமானம் ₹1,20,000-க்கு மிகாமல் இருக்க வேண்டும் (வருமானச் சான்றிதழ் தேவை)",
      "அமைப்புசாரா தொழிலாளர் நல வாரிய உறுப்பினர்களுக்கு தானாக தகுதி உண்டு"
    ],
    required_documents: [
      { name: "Smart Ration Card", name_ta: "ஸ்மார்ட் குடும்ப அட்டை", mandatory: true },
      { name: "Aadhaar Card for all family members", name_ta: "குடும்ப உறுப்பினர்களின் ஆதார் அட்டைகள்", mandatory: true },
      { name: "Income Certificate (from VAO/Tahsildar)", name_ta: "வருமானச் சான்றிதழ் (வருவாய் துறை)", mandatory: true }
    ],
    application_procedure: {
      online: "Check card status and empanelled hospital list at cmchistn.com.",
      online_ta: "cmchistn.com இணையதளத்தில் மருத்துவமனைகள் பட்டியல் மற்றும் நிலையை அறியலாம்.",
      offline: "Visit the District Collectorate CMCHIS kiosk or Taluk hospital for biometric enrollment and instant smart card.",
      offline_ta: "மாவட்ட ஆட்சியர் அலுவலகத்தில் உள்ள CMCHIS மையத்தில் கைரேகை பதிவு செய்து உடனடியாக அட்டை பெறலாம்."
    },
    official_portal: "https://www.cmchistn.com",
    official_source: "Tamil Nadu Health Systems Project (Sample Demo Entry)",
    source_verification: "verified",
    verified_date: "2026-10-18",
    important_dates: "Enrollment open year-round at all District Collectorates",
    important_dates_ta: "வருடம் முழுவதும் அனைத்து மாவட்ட ஆட்சியர் அலுவலகங்களிலும் விண்ணப்பிக்கலாம்",
    helpline: "Toll Free: 1800 425 3993",
    keywords: ["health", "hospital", "insurance", "medical", "treatment", "operation", "cmchis", "surgery", "மருத்துவம்", "காப்பீடு", "மருத்துவமனை", "சிகிச்சை", "ஆபரேஷன்", "நோய்"]
  },
  {
    id: "sewing-machine-welfare",
    name: "Sathiyavani Muthu Ammaiyar Free Sewing Machine Scheme",
    name_ta: "சத்தியவாணி முத்து அம்மையார் நினைவு இலவச தையல் இயந்திரம் திட்டம்",
    department: "Social Welfare and Women Empowerment Department",
    department_ta: "சமூக நலன் மற்றும் மகளிர் உரிமைத் துறை",
    category: "women",
    beneficiary_type: "Widows, destitute women, deserted wives, physically challenged women",
    beneficiary_type_ta: "விதவைகள், ஆதரவற்ற பெண்கள், கணவரால் கைவிடப்பட்ட பெண்கள், மாற்றுத்திறனாளிகள்",
    benefit_summary: "Free motorized / manual sewing machine for home-based self-employment",
    benefit_summary_ta: "சுயதொழில் தொடங்க இலவச நவீன தையல் இயந்திரம் வழங்கப்படுகிறது",
    benefit_amount: "Free Sewing Machine",
    description: "Empowers destitute women, widows, and economically disadvantaged women by providing free sewing machines to earn a sustainable livelihood from home.",
    description_ta: "பொருளாதாரத்தில் பின்தங்கிய பெண்கள், விதவைகள் மற்றும் கணவரால் கைவிடப்பட்ட பெண்களுக்கு தையல் மூலம் வாழ்வாதாரம் பெற இலவச தையல் இயந்திரம் வழங்கும் திட்டம்.",
    eligibility_criteria: [
      "Applicant must be female aged between 20 to 40 years",
      "Family annual income should not exceed ₹72,000",
      "Must possess Tailoring Training Certificate (minimum 6 months duration)",
      "Priority given to widows, destitute deserted wives, and differently abled women"
    ],
    eligibility_criteria_ta: [
      "20 முதல் 40 வயதுக்குட்பட்ட பெண்களாக இருக்க வேண்டும்",
      "குடும்ப ஆண்டு வருமானம் ₹72,000-க்கு மிகாமல் இருக்க வேண்டும்",
      "குறைந்தபட்சம் 6 மாத தையல் பயிற்சி முடித்த சான்றிதழ் பெற்றிருக்க வேண்டும்",
      "விதவைகள், கைவிடப்பட்ட பெண்கள் மற்றும் மாற்றுத்திறனாளிகளுக்கு முன்னுரிமை"
    ],
    required_documents: [
      { name: "Tailoring Course Certificate", name_ta: "தையல் பயிற்சி முடித்த சான்றிதழ்", mandatory: true },
      { name: "Income Certificate (Below ₹72k)", name_ta: "வருமானச் சான்றிதழ் (ஆண்டுக்கு ₹72,000-க்குள்)", mandatory: true },
      { name: "Community Certificate", name_ta: "சாதிச் சான்றிதழ்", mandatory: true },
      { name: "Destitute / Widow Certificate (if applicable)", name_ta: "விதவை / ஆதரவற்ற பெண் சான்றிதழ் (பொருந்தினால்)", mandatory: false },
      { name: "Aadhaar & Smart Ration Card", name_ta: "ஆதார் மற்றும் ரேஷன் அட்டை", mandatory: true }
    ],
    application_procedure: {
      online: "Apply through TNeGA citizen e-Sevai portal at tnesevai.tn.gov.in.",
      online_ta: "tnesevai.tn.gov.in மூலம் இ-சேவை மையங்களில் இணையவழியாக விண்ணப்பிக்கலாம்.",
      offline: "Submit hardcopy application to the District Social Welfare Officer (DSWO) or Taluk Office.",
      offline_ta: "மாவட்ட சமூக நல அலுவலர் அல்லது ஊராட்சி ஒன்றிய அலுவலகத்தில் நேரடியாக விண்ணப்பிக்கலாம்."
    },
    official_portal: "https://www.tnesevai.tn.gov.in",
    official_source: "Tamil Nadu Social Welfare Dept (Sample Demo Entry)",
    source_verification: "verified",
    verified_date: "2026-10-05",
    important_dates: "Applications invited annually during May - August",
    important_dates_ta: "ஆண்டுதோறும் மே முதல் ஆகஸ்ட் வரை விண்ணப்பங்கள் பெறப்படுகின்றன",
    helpline: "044-24351885 / 181 Women Helpline",
    keywords: ["sewing machine", "tailor", "tailoring", "widow", "women employment", "self employment", "free", "தையல்", "இயந்திரம்", "விதவை", "தையல் கலைஞர்", "மகளிர்", "சுயதொழில்"]
  },
  {
    id: "pm-kisan-tn",
    name: "PM-Kisan Samman Nidhi & Tamil Nadu Uzhavar Pathukappu Thittam",
    name_ta: "பிரதமர் கிசான் & தமிழ்நாடு உழவர் பாதுகாப்புத் திட்டம்",
    department: "Agriculture and Farmers Welfare Department",
    department_ta: "வேளாண்மை மற்றும் உழவர் நலத்துறை",
    category: "agriculture",
    beneficiary_type: "Small, marginal, and landholding farmer families",
    beneficiary_type_ta: "சிறு மற்றும் குறு விவசாயிகள், நில உரிமையாளர்கள்",
    benefit_summary: "₹6,000 / year direct income support + subsidized seeds, fertilizers & crop insurance",
    benefit_summary_ta: "ஆண்டுக்கு ₹6,000 நேரடி உதவித்தொகை + பயிர்க் காப்பீடு மற்றும் மானியங்கள்",
    benefit_amount: "₹6,000 / year + Subsidies",
    description: "Financial assistance given in 3 installments of ₹2,000 every four months to small and marginal farming families to purchase agricultural inputs, alongside Tamil Nadu state crop relief.",
    description_ta: "சிறு, குறு விவசாய குடும்பங்களுக்கு விவசாய இடுபொருட்கள் வாங்க 4 மாதங்களுக்கு ஒருமுறை ₹2,000 வீதம் ஆண்டுக்கு ₹6,000 வழங்கும் திட்டம்.",
    eligibility_criteria: [
      "Farmer family holding cultivable agricultural land registered in their name",
      "Land ownership verified via Tamil Nadu Patta / Chitta records",
      "Excludes institutional landholders, income tax payers, and government employees",
      "Must have Aadhaar seeded, e-KYC verified active bank account"
    ],
    eligibility_criteria_ta: [
      "விவசாய நிலம் சொந்தமாக பட்டா வைத்துள்ள சிறு மற்றும் குறு விவசாயிகள்",
      "தமிழ்நாடு பட்டா / சிட்டா ஆவணம் பதிவு செய்திருக்க வேண்டும்",
      "வருமான வரி செலுத்துபவர்கள் மற்றும் அரசு ஊழியர்கள் இதில் தகுதி பெற மாட்டார்கள்",
      "வங்கி கணக்குடன் ஆதார் e-KYC சரிபார்க்கப்பட்டிருக்க வேண்டும்"
    ],
    required_documents: [
      { name: "Land Patta / Chitta Copy", name_ta: "நில பட்டா / சிட்டா நகல்", mandatory: true },
      { name: "Aadhaar Card", name_ta: "ஆதார் அட்டை", mandatory: true },
      { name: "Bank Passbook with NPCI Aadhaar Seed", name_ta: "ஆதார் இணைக்கப்பட்ட வங்கி கணக்கு புத்தகம்", mandatory: true },
      { name: "Smart Ration Card", name_ta: "குடும்ப அட்டை (Ration Card)", mandatory: true }
    ],
    application_procedure: {
      online: "Self-register on pmkisan.gov.in or through Uzhavan Mobile App (உழவன் செயலி).",
      online_ta: "pmkisan.gov.in தளம் அல்லது உழவன் செயலி மூலம் சுயமாக பதிவு செய்யலாம்.",
      offline: "Visit the Assistant Agricultural Officer (AAO) at your local Block Office or e-Sevai center.",
      offline_ta: "வட்டார வேளாண்மை உதவி இயக்குநர் அலுவலகம் அல்லது இ-சேவை மையத்தில் பதிவு செய்யலாம்."
    },
    official_portal: "https://pmkisan.gov.in",
    official_source: "Ministry of Agriculture & TN Agri Dept (Sample Demo Entry)",
    source_verification: "verified",
    verified_date: "2026-11-10",
    important_dates: "Enrollment and e-KYC updates accepted continuously",
    important_dates_ta: "வருடம் முழுவதும் பதிவு மற்றும் e-KYC புதுப்பித்தல் இயங்குகிறது",
    helpline: "Kisan Call Centre: 1800-180-1551 / TN Agri: 044-28583320",
    keywords: ["farmer", "agriculture", "land", "crop", "seeds", "pm kisan", "uzhavar", "patta", "chitta", "விவசாயி", "உழவர்", "பயிர்", "நிலம்", "பட்டா", "மானியங்கள்", "விவசாய கடன்"]
  },
  {
    id: "naan-mudhalvan",
    name: "Naan Mudhalvan Youth Skill & Competitive Exam Assistance",
    name_ta: "நான் முதல்வன் இளைஞர் திறன் மேம்பாடு & போட்டித் தேர்வு திட்டம்",
    department: "Tamil Nadu Skill Development Corporation (TNSDC)",
    department_ta: "தமிழ்நாடு திறன் மேம்பாட்டுக் கழகம்",
    category: "employment",
    beneficiary_type: "College students, engineering/arts graduates, job seekers, civil service aspirants",
    beneficiary_type_ta: "கல்லூரி மாணவர்கள், பட்டதாரிகள், வேலை தேடுவோர், போட்டித் தேர்வு எழுதுவோர்",
    benefit_summary: "Free industry-recognized tech/vocational skills + ₹7,500/mo incentive for prelims clears",
    benefit_summary_ta: "இலவச தொழில்நுட்ப திறன் பயிற்சி மற்றும் சிவில் சர்வீஸ் தேர்வர்களுக்கு மாதம் ₹7,500",
    benefit_amount: "Free Training + ₹7,500 / month incentive",
    description: "Transformative upskilling platform equipping Tamil Nadu youth with cutting-edge industry training (AI, Data, Coding, Core engineering, Banking) and financial incentives for UPSC/TNPSC aspirants.",
    description_ta: "தமிழ்நாடு இளைஞர்களுக்கு செயற்கை நுண்ணறிவு, மென்பொருள், வங்கிப் பணி போன்ற தொழில்முறை திறன்களை இலவசமாக வழங்கி வேலைவாய்ப்பை உறுதி செய்யும் அரசு திட்டம்.",
    eligibility_criteria: [
      "Students currently pursuing degree or diploma in Tamil Nadu educational institutions",
      "Graduates seeking employment within Tamil Nadu",
      "For Civil Service coaching allowance: Must have cleared UPSC Prelims or TNPSC Group 1 Prelims",
      "Native of Tamil Nadu"
    ],
    eligibility_criteria_ta: [
      "தமிழ்நாட்டில் கல்லூரி அல்லது பாலிடெக்னிக் பயிலும் மாணவர்கள் மற்றும் பட்டதாரிகள்",
      "தமிழ்நாடு இளைஞர் நல வாரியத்தில் பதிவு செய்தவர்கள்",
      "போட்டித் தேர்வு உதவித்தொகைக்கு: UPSC அல்லது TNPSC முதல்நிலைத் தேர்வில் தேர்ச்சி பெற்றிருக்க வேண்டும்",
      "தமிழ்நாட்டை பூர்வீகமாகக் கொண்டவராக இருக்க வேண்டும்"
    ],
    required_documents: [
      { name: "College ID / Degree Certificate", name_ta: "கல்லூரி அடையாள அட்டை / பட்டச் சான்றிதழ்", mandatory: true },
      { name: "Aadhaar Card", name_ta: "ஆதார் அட்டை", mandatory: true },
      { name: "Resume / Educational Records", name_ta: "கல்வித் தகுதி ஆவணங்கள்", mandatory: true }
    ],
    application_procedure: {
      online: "Register on naanmudhalvan.tn.gov.in portal using college credentials or student email.",
      online_ta: "naanmudhalvan.tn.gov.in இணையதளத்தில் மாணவர் கணக்கு துவங்கி பயிற்சிக்கு இணையலாம்.",
      offline: "Access placement cells across government engineering and arts/science colleges.",
      offline_ta: "அரசு கலை, அறிவியல் மற்றும் பொறியியல் கல்லூரிகளின் வேலைவாய்ப்பு மையங்களை அணுகலாம்."
    },
    official_portal: "https://www.naanmudhalvan.tn.gov.in",
    official_source: "Tamil Nadu Skill Development Corp (Sample Demo Entry)",
    source_verification: "verified",
    verified_date: "2026-10-25",
    important_dates: "Batch enrollments coincide with university semester cycles",
    important_dates_ta: "பல்கலைக்கழக செமஸ்டர் கால அட்டவணைக்கு ஏற்ப புதிய பயிற்சிகள் துவங்குகின்றன",
    helpline: "044-22501070",
    keywords: ["skill", "training", "coding", "course", "job", "employment", "graduate", "upsc", "tnpsc", "degree", "இளைஞர்", "வேலை", "திறன்", "பயிற்சி", "பட்டதாரி", "நான் முதல்வன்"]
  },
  {
    id: "muthulakshmi-maternity",
    name: "Dr. Muthulakshmi Reddy Maternity Benefit Scheme (MRMBS)",
    name_ta: "டாக்டர் முத்துலட்சுமி ரெட்டி மகப்பேறு நிதி உதவித் திட்டம்",
    department: "Health and Family Welfare Department",
    department_ta: "மக்கள் நல்வாழ்வு மற்றும் குடும்ப நலத்துறை",
    category: "health",
    beneficiary_type: "Pregnant and lactating mothers below poverty line",
    beneficiary_type_ta: "ஏழை கர்ப்பிணி தாய்மார்கள் மற்றும் பாலூட்டும் தாய்மார்கள்",
    benefit_summary: "₹18,000 total assistance (₹14,000 cash in 5 installments + ₹4,000 nutrition kit)",
    benefit_summary_ta: "மொத்தம் ₹18,000 பலன் (₹14,000 ரொக்க உதவி + ₹4,000 மதிப்புள்ள ஊட்டச்சத்து பெட்டகம்)",
    benefit_amount: "₹18,000 total benefit",
    description: "Financial assistance and high-nutrition health kits to poor pregnant mothers to prevent maternal and infant mortality, ensuring institutional delivery and complete immunization.",
    description_ta: "கர்ப்பிணித் தாய்மார்களுக்கு கர்ப்ப காலத்தில் ஊட்டச்சத்தை உறுதி செய்யவும், அரசு மருத்துவமனைகளில் பிரசவம் மற்றும் தடுப்பூசிகளை உறுதி செய்ய ₹18,000 வழங்கும் திட்டம்.",
    eligibility_criteria: [
      "Pregnant woman aged 19 years and above",
      "Family annual income below poverty line (BPL) guidelines",
      "Must register pregnancy with Village Health Nurse (VHN) before 12th week of gestation",
      "Benefit restricted to first two live births"
    ],
    eligibility_criteria_ta: [
      "19 வயது அல்லது அதற்கு மேற்பட்ட கர்ப்பிணித் தாய்மார்கள்",
      "வறுமைக் கோட்டிற்கு கீழ் உள்ள குடும்பங்கள்",
      "கர்ப்பம் தரித்த 12 வாரங்களுக்குள் கிராம சுகாதார செவிலியரிடம் (VHN) பதிவு செய்திருக்க வேண்டும் (RCH ID)",
      "முதல் இரண்டு குழந்தைகளுக்கு மட்டுமே இந்த உதவித்தொகை பொருந்தும்"
    ],
    required_documents: [
      { name: "RCH ID / PICME Number", name_ta: "PICME பதிவு எண் (RCH ID)", mandatory: true },
      { name: "Mother's Aadhaar Card", name_ta: "தாயின் ஆதார் அட்டை", mandatory: true },
      { name: "Bank Passbook seeded with Aadhaar", name_ta: "ஆதார் இணைக்கப்பட்ட தனி வங்கி சேமிப்பு புத்தகம்", mandatory: true },
      { name: "Smart Ration Card", name_ta: "ஸ்மார்ட் குடும்ப அட்டை", mandatory: true }
    ],
    application_procedure: {
      online: "Track PICME registration and cash transfer status at picme.tn.gov.in.",
      online_ta: "picme.tn.gov.in தளத்தில் RCH ஐடி கொண்டு நிலையை சரிபார்க்கலாம்.",
      offline: "Approach the local Primary Health Centre (PHC) or Village Health Nurse (VHN).",
      offline_ta: "அருகிலுள்ள அரசு ஆரம்ப சுகாதார நிலையம் (PHC) அல்லது கிராம சுகாதார செவிலியரை அணுகவும்."
    },
    official_portal: "https://picme.tn.gov.in",
    official_source: "Tamil Nadu Directorate of Public Health (Sample Demo Entry)",
    source_verification: "verified",
    verified_date: "2026-10-12",
    important_dates: "Registration mandatory before 12th week of pregnancy",
    important_dates_ta: "கர்ப்பமான 12 வாரங்களுக்குள் கட்டாயம் பதிவு செய்ய வேண்டும்",
    helpline: "104 Health Helpline",
    keywords: ["pregnant", "pregnancy", "baby", "mother", "maternity", "muthulakshmi", "nutrition", "delivery", "picme", "கர்ப்பிணி", "பிரசவம்", "குழந்தை", "தாய்மை", "ஊட்டச்சத்து"]
  },
  {
    id: "oap-senior-pension",
    name: "Tamil Nadu Destitute Old Age Pension Scheme (OAP)",
    name_ta: "முதியோர் உதவித்தொகை திட்டம் (OAP)",
    department: "Revenue and Disaster Management Department",
    department_ta: "வருவாய் மற்றும் பேரிடர் மேலாண்மைத் துறை",
    category: "seniors",
    beneficiary_type: "Destitute senior citizens with no means of regular subsistence",
    beneficiary_type_ta: "ஆதரவற்ற 60 வயதுக்கு மேற்பட்ட முதியவர்கள்",
    benefit_summary: "₹1,200 monthly pension deposited directly to bank account + free rice & dhotis",
    benefit_summary_ta: "மாதம் ₹1,200 ஓய்வூதியம் + இலவச அரிசி மற்றும் வேட்டி/சேலை",
    benefit_amount: "₹1,200 / month",
    description: "Monthly financial pension provided to impoverished senior citizens who have no surviving adult earning members or sufficient source of livelihood.",
    description_ta: "வாழ்க்கை நடத்த எவ்வித வருமானமும் அல்லது ஆதரவும் இல்லாத ஏழை முதியவர்களுக்கு மாதம் ₹1,200 ஓய்வூதியம் வழங்கும் திட்டம்.",
    eligibility_criteria: [
      "Age of applicant must be 60 years or above (65+ for Indira Gandhi NOAPS)",
      "Applicant must be destitute without income or regular support from major sons/daughters",
      "Total family assets should not exceed ₹50,000",
      "Should not be in receipt of any other government pension"
    ],
    eligibility_criteria_ta: [
      "விண்ணப்பதாரரின் வயது 60 அல்லது அதற்கு மேல் இருக்க வேண்டும்",
      "வாழ்க்கை நடத்த எவ்வித ஆதரவும் இல்லாத ஏழையாக இருக்க வேண்டும்",
      "சொத்து மதிப்பு ₹50,000-க்கு மிகாமல் இருக்க வேண்டும்",
      "வேறு எந்த அரசு ஓய்வூதியமும் பெறுபவராக இருக்கக்கூடாது"
    ],
    required_documents: [
      { name: "Age Proof (Aadhaar / Voter ID)", name_ta: "வயது சான்று (ஆதார் / வாக்காளர் அட்டை)", mandatory: true },
      { name: "Smart Ration Card", name_ta: "ஸ்மார்ட் குடும்ப அட்டை", mandatory: true },
      { name: "Destitute / Income Certificate from VAO", name_ta: "ஆதரவற்றோர் / வருமானச் சான்றிதழ் (VAO)", mandatory: true },
      { name: "Bank Passbook with Aadhaar link", name_ta: "வங்கி சேமிப்புக் கணக்கு புத்தகம்", mandatory: true }
    ],
    application_procedure: {
      online: "Apply online at nearest e-Sevai center through TNeGA portal.",
      online_ta: "அருகிலுள்ள இ-சேவை மையம் மூலம் TNeGA போர்ட்டலில் விண்ணப்பிக்கலாம்.",
      offline: "Submit paper application to the Special Tahsildar (Social Security Schemes) at Taluk Office.",
      offline_ta: "வட்டார வட்டாட்சியர் (சமூக பாதுகாப்புத் திட்டம்) அலுவலகத்தில் சமர்ப்பிக்கலாம்."
    },
    official_portal: "https://www.tnesevai.tn.gov.in",
    official_source: "Tamil Nadu Revenue Department (Sample Demo Entry)",
    source_verification: "verified",
    verified_date: "2026-11-05",
    important_dates: "Applications accepted continuously throughout the year",
    important_dates_ta: "வருடம் முழுவதும் எந்த நேரத்திலும் விண்ணப்பிக்கலாம்",
    helpline: "CM Helpline 1100 / Taluk Social Security Cell",
    keywords: ["senior", "old age", "pension", "60", "elderly", "destitute", "oap", "retirement", "முதியோர்", "ஓய்வூதியம்", "தாத்தா", "பாட்டி", "வயதானவர்"]
  },
  {
    id: "differently-abled-welfare",
    name: "Maintenance Allowance for Differently Abled Persons",
    name_ta: "மாற்றுத்திறனாளிகள் மாதாந்திர பராமரிப்பு உதவித்தொகை திட்டம்",
    department: "Welfare of Differently Abled Persons Department",
    department_ta: "மாற்றுத்திறனாளிகள் நலத்துறை",
    category: "disability",
    beneficiary_type: "Persons with severe disabilities, intellectual disability, locomotor disability",
    beneficiary_type_ta: "கடுமையான மாற்றுத்திறன் கொண்ட நபர்கள் (40% முதல் 75%+)",
    benefit_summary: "₹1,500 to ₹2,000 monthly maintenance allowance + free bus pass & assistive devices",
    benefit_summary_ta: "மாதம் ₹1,500 முதல் ₹2,000 பராமரிப்பு உதவித்தொகை + இலவச பேருந்து பயணம் & உதவி உபகரணங்கள்",
    benefit_amount: "₹1,500 - ₹2,000 / month",
    description: "Monthly maintenance grant and free assistive appliances (wheelchairs, retrofitted three-wheelers, hearing aids) given to differently abled individuals across Tamil Nadu.",
    description_ta: "கடுமையான உடல் அல்லது மனநல மாற்றுத்திறன் கொண்ட நபர்களுக்கு மாதாந்திர வாழ்க்கை பராமரிப்பு தொகை மற்றும் இலவச உபகரணங்கள் வழங்கும் திட்டம்.",
    eligibility_criteria: [
      "Must have a valid Unique Disability ID (UDID) card or National Disability ID",
      "Disability percentage must be 40% or more (special categories for intellectual/spinal disability)",
      "Applicant must be a native of Tamil Nadu",
      "No upper age bar"
    ],
    eligibility_criteria_ta: [
      "அங்கீகரிக்கப்பட்ட UDID ஸ்மார்ட் கார்டு அல்லது மாற்றுத்திறனாளி சான்றிதழ் பெற்றிருக்க வேண்டும்",
      "மாற்றுத்திறன் அளவு 40% அல்லது அதற்கு மேல் இருக்க வேண்டும்",
      "தமிழ்நாட்டை பூர்வீகமாகக் கொண்டவராக இருக்க வேண்டும்",
      "வயது வரம்பு எதுவும் இல்லை"
    ],
    required_documents: [
      { name: "UDID Card / Disability Certificate", name_ta: "UDID அட்டை / மருத்துவ வாரிய மாற்றுத்திறனாளி சான்றிதழ்", mandatory: true },
      { name: "Aadhaar Card", name_ta: "ஆதார் அட்டை", mandatory: true },
      { name: "Smart Ration Card", name_ta: "ஸ்மார்ட் குடும்ப அட்டை", mandatory: true },
      { name: "Bank Passbook with Aadhaar linkage", name_ta: "வங்கி சேமிப்புக் கணக்கு புத்தகம்", mandatory: true }
    ],
    application_procedure: {
      online: "Apply online through udid.gov.in and Tamil Nadu Differently Abled Welfare portal.",
      online_ta: "swabhawansamarthya.gov.in அல்லது udid.gov.in மூலம் இணையத்தில் விண்ணப்பிக்கலாம்.",
      offline: "Visit the District Differently Abled Welfare Officer (DDAWO) at District Collectorate.",
      offline_ta: "மாவட்ட ஆட்சியர் அலுவலகத்தில் உள்ள மாவட்ட மாற்றுத்திறனாளிகள் நல அலுவலரை (DDAWO) அணுகவும்."
    },
    official_portal: "https://www.scd.tn.gov.in",
    official_source: "TN Differently Abled Welfare Dept (Sample Demo Entry)",
    source_verification: "verified",
    verified_date: "2026-10-28",
    important_dates: "Weekly medical assessment boards held every Tuesday at District HQ hospitals",
    important_dates_ta: "ஒவ்வொரு செவ்வாய்க்கிழமையும் தலைமை அரசு மருத்துவமனைகளில் மருத்துவ பரிசோதனை நடக்கும்",
    helpline: "Toll Free: 1800 425 0111",
    keywords: ["differently abled", "handicapped", "disability", "udid", "wheelchair", "special needs", "blind", "deaf", "மாற்றுத்திறனாளி", "ஊனம்", "சக்கர நாற்காலி", "பராமரிப்பு", "உதவித்தொகை"]
  },
  {
    id: "aabcs-scst-entrepreneur",
    name: "Annal Ambedkar Business Champions Scheme (AABCS)",
    name_ta: "அண்ணல் அம்பேத்கர் தொழில் முன்னோடிகள் திட்டம் (AABCS)",
    department: "Micro, Small and Medium Enterprises (MSME) Department",
    department_ta: "ஊரக மற்றும் குறு, சிறு மற்றும் நடுத்தரத் தொழில் நிறுவனங்கள் துறை",
    category: "employment",
    beneficiary_type: "Scheduled Caste (SC) and Scheduled Tribe (ST) aspiring entrepreneurs",
    beneficiary_type_ta: "ஆதிதிராவிடர் (SC) மற்றும் பழங்குடியினர் (ST) தொழில் முனைவோர்",
    benefit_summary: "35% capital subsidy up to ₹1.5 Crore + 6% interest subvention on term loans",
    benefit_summary_ta: "35% மூலதன மானியம் (அதிகபட்சம் ₹1.5 கோடி வரை) + 6% வட்டி மானியம்",
    benefit_amount: "35% Subsidy (up to ₹1.5 Cr)",
    description: "Ambitious initiative promoting SC/ST entrepreneurship in manufacturing, services, transport, and trading by providing substantial capital subsidies and bank loan support.",
    description_ta: "ஆதிதிராவிடர் மற்றும் பழங்குடியின இளைஞர்களை தொழில் முனைவோராக மாற்ற 35% நேரடி அரசு மூலதன மானியம் மற்றும் 6% வட்டி தள்ளுபடி வழங்கும் திட்டம்.",
    eligibility_criteria: [
      "Applicant must belong to Scheduled Caste (SC) or Scheduled Tribe (ST) community",
      "Proprietary firm must be 100% owned by SC/ST entrepreneurs",
      "No minimum educational qualification required for projects up to ₹1 Crore",
      "Age of applicant must be between 18 and 55 years"
    ],
    eligibility_criteria_ta: [
      "ஆதிதிராவிடர் (SC) அல்லது பழங்குடியினர் (ST) சமூகத்தை சேர்ந்தவராக இருக்க வேண்டும்",
      "நிறுவனத்தின் 100% உரிமை SC/ST நபர்களிடம் இருக்க வேண்டும்",
      "₹1 கோடி வரையிலான திட்டங்களுக்கு குறைந்தபட்ச கல்வித் தகுதி தேவையில்லை",
      "விண்ணப்பதாரர் வயது 18 முதல் 55-க்குள் இருக்க வேண்டும்"
    ],
    required_documents: [
      { name: "Community Certificate (SC/ST)", name_ta: "சாதிச் சான்றிதழ் (SC/ST)", mandatory: true },
      { name: "Detailed Project Report (DPR)", name_ta: "தொழில் திட்ட அறிக்கை (DPR)", mandatory: true },
      { name: "Aadhaar & PAN Card", name_ta: "ஆதார் மற்றும் பான் அட்டை", mandatory: true },
      { name: "Bank Account Details & Quotations", name_ta: "வங்கி கணக்கு மற்றும் உபகரணங்கள் விலைப்பட்டியல்", mandatory: true }
    ],
    application_procedure: {
      online: "Apply online at msmeonline.tn.gov.in under AABCS scheme portal.",
      online_ta: "msmeonline.tn.gov.in இணையதளம் வாயிலாக AABCS பிரிவில் விண்ணப்பிக்கலாம்.",
      offline: "Approach the General Manager, District Industries Centre (DIC) in your district.",
      offline_ta: "உங்கள் மாவட்டத்தில் உள்ள மாவட்ட தொழில் மையம் (DIC) பொது மேலாளரை அணுகவும்."
    },
    official_portal: "https://msmeonline.tn.gov.in",
    official_source: "Tamil Nadu MSME Department (Sample Demo Entry)",
    source_verification: "verified",
    verified_date: "2026-10-30",
    important_dates: "Applications accepted continuously on the online portal",
    important_dates_ta: "இணையதளம் மூலம் எப்போதும் விண்ணப்பிக்கலாம்",
    helpline: "044-22501070 / DIC District Offices",
    keywords: ["business", "loan", "entrepreneur", "sc", "st", "subsidy", "startup", "msme", "factory", "aabcs", "தொழில்", "கடன்", "மானியம்", "தொழில்முனைவோர்", "ஆதிதிராவிடர்", "பழங்குடியினர்"]
  },
  {
    id: "tamil-pudhalvan",
    name: "Tamil Pudhalvan Higher Education Scheme for Boys",
    name_ta: "தமிழ்ப் புதல்வன் திட்டம் (மாணவர்கள் உயர்கல்வி உதவி)",
    department: "Social Welfare and Higher Education Department",
    department_ta: "சமூக நலன் மற்றும் உயர்கல்வித் துறை",
    category: "education",
    beneficiary_type: "Male students from government schools joining higher education",
    beneficiary_type_ta: "அரசுப் பள்ளியில் படித்து கல்லூரி சேரும் மாணவர்கள்",
    benefit_summary: "₹1,000 per month deposited directly to bank account for textbook and college expenses",
    benefit_summary_ta: "புத்தகங்கள் மற்றும் படிப்பு செலவுகளுக்கு மாதம் ₹1,000 வங்கி வரவு",
    benefit_amount: "₹1,000 / month",
    description: "Financial assistance program providing ₹1,000 monthly aid to male students who studied in Tamil Nadu government schools from 6th to 12th standard and joined higher education.",
    description_ta: "தமிழ்நாடு அரசுப் பள்ளிகளில் 6 முதல் 12-ம் வகுப்பு வரை படித்து கல்லூரி, பாலிடெக்னிக், தொழிற்கல்வி பயிலும் மாணவர்களுக்கு மாதம் ₹1,000 வழங்கும் திட்டம்.",
    eligibility_criteria: [
      "Must have studied in Tamil Nadu Government schools from Class 6 to 12",
      "Enrolled in recognized higher education college / university",
      "Valid bank account seeded with Aadhaar in student's name"
    ],
    eligibility_criteria_ta: [
      "6 முதல் 12-ம் வகுப்பு வரை தமிழ்நாடு அரசுப் பள்ளிகளில் படித்திருக்க வேண்டும்",
      "அங்கீகரிக்கப்பட்ட கல்லூரியில் பட்டப்படிப்பு அல்லது பட்டயப்படிப்பு பயில வேண்டும்",
      "மாணவரின் பெயரில் ஆதார் இணைக்கப்பட்ட வங்கிக் கணக்கு இருக்க வேண்டும்"
    ],
    required_documents: [
      { name: "Aadhaar Card", name_ta: "ஆதார் அட்டை", mandatory: true },
      { name: "10th & 12th Marksheets", name_ta: "10 மற்றும் 12-ம் வகுப்பு மதிப்பெண் சான்றிதழ்", mandatory: true },
      { name: "Govt School Study Certificate (Bonafide)", name_ta: "அரசுப் பள்ளி பயின்ற சான்றிதழ்", mandatory: true },
      { name: "Bank Passbook", name_ta: "வங்கி சேமிப்புக் கணக்கு புத்தகம்", mandatory: true }
    ],
    application_procedure: {
      online: "Apply through college nodal officer via Tamil Nadu Higher Education portal.",
      online_ta: "கல்லூரி மூலமாக உயர்கல்வித் துறை போர்ட்டலில் பதிவு செய்யப்படும்.",
      offline: "Submit documents directly to your college administration.",
      offline_ta: "கல்லூரி நிர்வாகத்தில் ஆவணங்களை சமர்ப்பிக்கவும்."
    },
    official_portal: "https://www.tn.gov.in",
    official_source: "Tamil Nadu Higher Education Dept (Sample Demo Entry)",
    source_verification: "verified",
    verified_date: "2026-11-02",
    important_dates: "Enrolled at the commencement of university academic session",
    important_dates_ta: "கல்வியாண்டு துவக்கத்தில் பதிவு செய்யப்படுகிறது",
    helpline: "CM Helpline 1100 / 14417",
    keywords: ["boy", "student", "college", "tamil pudhalvan", "education", "1000", "scholarship", "பள்ளி", "கல்லூரி", "மாணவன்", "உதவித்தொகை", "தமிழ்ப் புதல்வன்"]
  },
  {
    id: "kalaignar-kanavu-illam",
    name: "Kalaignar Kanavu Illam Scheme (Rural Housing)",
    name_ta: "கலைஞர் கனவு இல்லம் திட்டம் (கிராமப்புற வீடுகள்)",
    department: "Rural Development and Panchayat Raj Department",
    department_ta: "ஊரக வளர்ச்சி மற்றும் ஊராட்சித் துறை",
    category: "housing",
    beneficiary_type: "Rural families living in thatched or dilapidated huts",
    beneficiary_type_ta: "குடிசை அல்லது பாழடைந்த வீடுகளில் வசிக்கும் கிராமப்புற மக்கள்",
    benefit_summary: "Financial grant of ₹3,50,000 for constructing a durable pucca concrete house",
    benefit_summary_ta: "புதிய கான்கிரீட் வீடு கட்ட ₹3,50,000 நேரடி அரசு நிதி உதவி",
    benefit_amount: "₹3,50,000 per house",
    description: "Ambitious initiative to eradicate rural huts in Tamil Nadu by helping impoverished families construct solid permanent concrete homes of at least 360 square feet.",
    description_ta: "குடிசைகள் இல்லாத தமிழ்நாட்டை உருவாக்கும் நோக்கில் ஏழை எளிய மக்கள் 360 சதுர அடியில் புதிய கான்கிரீட் வீடு கட்ட ₹3.50 லட்சம் வழங்கும் திட்டம்.",
    eligibility_criteria: [
      "Must reside in a thatched hut or kutcha house in rural Tamil Nadu",
      "Must own a house site with clear title or enjoy valid government patta",
      "Should not own any other concrete pucca house in the state",
      "Priority to widows, differently abled persons, and primitive tribal families"
    ],
    eligibility_criteria_ta: [
      "கிராமப்புறத்தில் குடிசை அல்லது தற்காலிக கூரை வீட்டில் வசிப்பவராக இருக்க வேண்டும்",
      "சொந்தமாக வீட்டு மனை அல்லது அரசு வழங்கிய பட்டா நிலம் இருக்க வேண்டும்",
      "வேறு எங்கும் சொந்தமாக கான்கிரீட் வீடு இருக்கக்கூடாது",
      "விதவைகள், மாற்றுத்திறனாளிகள் மற்றும் பழங்குடியினருக்கு முன்னுரிமை"
    ],
    required_documents: [
      { name: "House Site Patta / Title Deed", name_ta: "வீட்டு மனை பட்டா / ஆவண நகல்", mandatory: true },
      { name: "Smart Ration Card", name_ta: "ஸ்மார்ட் குடும்ப அட்டை", mandatory: true },
      { name: "Aadhaar Card", name_ta: "ஆதார் அட்டை", mandatory: true },
      { name: "Photograph of existing hut", name_ta: "தற்போதைய குடிசை வீட்டின் புகைப்படம்", mandatory: true },
      { name: "Bank Passbook with Aadhaar linkage", name_ta: "ஆதார் இணைக்கப்பட்ட வங்கி புத்தகம்", mandatory: true }
    ],
    application_procedure: {
      online: "Track village beneficiary list via tnrd.tn.gov.in portal.",
      online_ta: "tnrd.tn.gov.in இணையதளத்தில் ஊரக வளர்ச்சி திட்ட பட்டியலை அறியலாம்.",
      offline: "Approach your Village Panchayat President, Panchayat Secretary, or Block Development Officer (BDO).",
      offline_ta: "கிராம ஊராட்சி செயலாளர், தலைவர் அல்லது வட்டார வளர்ச்சி அலுவலரை (BDO) அணுகவும்."
    },
    official_portal: "https://www.tnrd.tn.gov.in",
    official_source: "Tamil Nadu Rural Development Dept (Sample Demo Entry)",
    source_verification: "verified",
    verified_date: "2026-10-15",
    important_dates: "Annual village beneficiary selection conducted in Grama Sabha meetings",
    important_dates_ta: "கிராம சபை கூட்டங்கள் மூலம் பயனாளிகள் தேர்வு செய்யப்படுகின்றனர்",
    helpline: "CM Helpline 1100 / District Collectorate Rural Wing",
    keywords: ["house", "housing", "hut", "home", "kanavu illam", "construction", "concrete", "patta", "வீடு", "குடிசை", "கான்கிரீட்", "கனவு இல்லம்", "ஊராட்சி", "பட்டா"]
  }
];
