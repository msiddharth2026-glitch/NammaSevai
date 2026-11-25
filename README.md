# BharatSevai AI (பாரத்சேவை AI)

> **Voice-First National & State Government Welfare Scheme Discovery Assistant for Indian Citizens.**

BharatSevai AI allows citizens across India to describe their real-life situations in **Tamil (தமிழ்), Hindi (हिन्दी), Malayalam (മലയാളം), Tanglish, Hinglish, or English** without knowing bureaucratic government scheme names, government orders, or technical eligibility criteria. The platform extracts structured citizen profiles, detects missing critical criteria, generates targeted bilingual follow-up questions, evaluates eligibility against structured conditions, prepares an interactive printable required documents checklist, and directs citizens to authentic official government portals.

---

## 🏛️ Key Features

### 1. Voice-First Citizen Interface (Tamil, Tanglish, English)
- **Speech-to-Text (STT)**: Direct voice recording with Tamil (`ta-IN`) and English (`en-IN`) speech recognition, plus audio waveform visualization.
- **Text-to-Speech (TTS)**: Dual-mode speech synthesis supporting backend streaming MP3 audio (`gTTS`) and native browser Web SpeechSynthesis with **Speak** and **Stop** interactive controls.
- **Privacy First**: Explicit user consent modal prior to recording; raw audio is processed ephemerally and deleted immediately. No raw audio files are stored permanently.
- **Clickable Situation Prompts**: Quick prompt chips for student scholarships, farming subsidies, tailoring machines, maternity aid, and senior pensions.

### 2. Multi-Lingual AI Understanding & Structured Scheme Matching
- **Google Gemini 1.5 Flash Integration**: Real-time generative reasoning in Tamil, Tanglish, and English via `GEMINI_API_KEY`.
- **Verified Deterministic Rule Engine**: Instant fallback to high-precision Tamil/Tanglish regex & rule extraction if Gemini credentials are not configured, with transparent in-app setup instructions.
- **Structured Eligibility Rules**: Evaluates conditions using operators (`eq`, `gte`, `lte`, `in`, `contains`) without hallucinating schemes, benefits, deadlines, or URLs.
- **Missing Information Detection**: Detects missing mandatory criteria (e.g. government school background for Pudhumai Penn / Tamil Pudhalvan) and asks targeted polite follow-up questions.

### 3. 5 Comprehensive GovTech SaaS Pages
1. **Landing Page**: Official logo, Tamil headline (*"உங்களுக்கு தேவையான அரசு நலத்திட்டங்களை எளிதாக கண்டறியுங்கள்"*), English subtitle, interactive voice preview demo, feature highlights, and 3-step guide.
2. **AI Assistant Page**: Large microphone button, soundwave animation, language selector (Tamil, Tanglish, English), text input alternative, conversation bubbles, follow-up questions card, and preview cards for potential matches.
3. **Scheme Results Page**: Search bar, category filter pills (Education, Women, Health, Agriculture, Employment, Seniors, Disability, Housing), match confidence percentages, explanation rationale, and document preview pills.
4. **Scheme Details Page**: Scheme description, eligibility rules, interactive printable document checklist with checkboxes, online/offline procedure steps, important dates, official portal links, verified date, and helpline contacts (1100, 14417, 181, 104).
5. **Admin Dashboard**: Scheme catalog table, metrics summary cards, search and category filters, verification status toggle, Add Scheme modal, Edit Scheme modal, and Delete scheme action. Secured by `X-Admin-Key` header authentication.

---

## 📂 Project Architecture

```
nammasevai/
├── assets/
│   ├── nammasevai_logo.svg            # Official brand logo
│   └── nammasevai_minimal.svg         # Minimal speech-mark logo & favicon
├── backend/
│   ├── config.py                      # Pydantic BaseSettings loading from .env
│   ├── database.py                    # SQLAlchemy engine (SQLite dev + PostgreSQL support)
│   ├── main.py                        # FastAPI application with static files and lifecycle seed
│   ├── models/                        # SQLAlchemy database models
│   │   ├── scheme.py                  # Scheme master table
│   │   ├── condition.py               # Structured eligibility conditions
│   │   ├── document.py                # Required documents & issuing authorities
│   │   ├── step.py                    # Online & offline application steps
│   │   ├── source.py                  # Official portal sources & verification dates
│   │   └── user.py                    # Optional citizen profile session store
│   ├── schemas/                       # Pydantic v2 schemas for requests & responses
│   │   ├── scheme.py
│   │   ├── assistant.py
│   │   ├── document.py
│   │   ├── step.py
│   │   └── source.py
│   ├── routers/                       # FastAPI REST API endpoints
│   │   ├── schemes.py                 # GET /api/schemes, GET /api/schemes/{id}, documents
│   │   ├── assistant.py               # POST /api/assistant/analyze, POST /api/assistant/match
│   │   ├── admin.py                   # POST/PUT/DELETE /api/admin/schemes, stats (Secured)
│   │   └── voice.py                   # GET /api/voice/config, transcribe, synthesize
│   ├── services/                      # Business logic & AI layer
│   │   ├── ai_service.py              # Gemini 1.5 Flash client & compassionate responder
│   │   ├── extractor.py               # Tamil/Tanglish/English demographic rule extractor
│   │   ├── matcher.py                 # Structured condition evaluator against database
│   │   ├── voice_service.py           # Ephemeral audio transcription
│   │   └── tts_service.py             # Dual-engine speech audio synthesis
│   └── seeds/
│       └── seed_data.py               # 12 authentic Tamil Nadu welfare schemes seed
├── static/
│   ├── css/
│   │   └── style.css                  # GovTech design system (Navy #092D50, Teal #008F8C, Saffron)
│   └── js/
│       ├── app.js                     # SPA router, state store, API client, audio coordinator
│       ├── i18n.js                    # Complete bilingual Tamil & English dictionary
│       ├── nlpMatcher.js              # Client-side NLP fallback matcher
│       ├── schemesData.js             # Client-side 12 schemes catalog
│       ├── speechService.js           # Web Speech API STT and Web SpeechSynthesis wrapper
│       └── components/
│           ├── navbar.js              # Responsive header, active route, Tamil/English toggle
│           ├── footer.js              # Citizen helplines, disclaimer, quick links
│           ├── landingPage.js         # Hero, interactive preview, feature cards
│           ├── assistantPage.js       # Voice mic, chat conversation, follow-up cards
│           ├── resultsPage.js         # Category pills, search bar, scheme cards
│           ├── detailsPage.js         # Interactive printable document checklist, portal links
│           └── adminPage.js           # Scheme CRUD table, modals, verification status
├── index.html                         # SPA shell entrypoint
├── .env                               # Active local environment variables
├── .env.example                       # Environment variables template
├── test_e2e_full_verification.py      # Comprehensive 15-test end-to-end verification suite
├── test_voice_ai_runner.py            # Direct service & router unit test runner
└── README.md                          # Full system documentation
```

---

## 📋 Catalog of 12 Tamil Nadu Welfare Schemes

1. **Moovalur Ramamirtham Ammaiyar Higher Education Assurance Scheme (Pudhumai Penn)**: ₹1,000/month for female students from government schools pursuing higher education (`penkalvi.tn.gov.in`).
2. **Kalaignar Magalir Urimai Thittam (KMUT)**: ₹1,000/month basic income guarantee for eligible female family heads (`kmut.tn.gov.in`).
3. **Chief Minister's Comprehensive Health Insurance Scheme (CMCHIS)**: Cashless hospitalization up to ₹5,00,000 per family per year (`cmchistn.com`).
4. **Sathiyavani Muthu Ammaiyar Free Sewing Machine Scheme**: Free modern sewing machine for destitute women, widows, and differently abled women (`tnesevai.tn.gov.in`).
5. **PM-Kisan & Tamil Nadu Uzhavar Pathukappu Thittam**: ₹6,000/year income support + crop insurance and input subsidies for landholding farmers (`pmkisan.gov.in`).
6. **Naan Mudhalvan Youth Skill & Competitive Exam Assistance**: Free tech/vocational skill training and ₹7,500/month incentive for UPSC/TNPSC aspirants (`naanmudhalvan.tn.gov.in`).
7. **Dr. Muthulakshmi Reddy Maternity Benefit Scheme (MRMBS)**: ₹18,000 total assistance (₹14,000 cash in 5 installments + ₹4,000 nutrition kit) for pregnant women below poverty line (`picme.tn.gov.in`).
8. **Tamil Nadu Destitute Old Age Pension Scheme (OAP)**: ₹1,200/month pension + free rice and clothes for destitute senior citizens aged 60+ (`tnesevai.tn.gov.in`).
9. **Maintenance Allowance for Differently Abled Persons**: ₹1,500 to ₹2,000/month maintenance allowance + free bus pass and assistive appliances (`scd.tn.gov.in`).
10. **Annal Ambedkar Business Champions Scheme (AABCS)**: 35% capital subsidy (up to ₹1.5 Crore) + 6% interest subvention for SC/ST entrepreneurs (`msmeonline.tn.gov.in`).
11. **Tamil Pudhalvan Higher Education Scheme for Boys**: ₹1,000/month textbook & education aid for male students who studied in TN government schools (`tn.gov.in`).
12. **Kalaignar Kanavu Illam Scheme (Rural Housing)**: ₹3,50,000 direct grant for constructing a durable pucca concrete home for rural hut dwellers (`tnrd.tn.gov.in`).

---

## 🚀 How to Run the Application

### 1. Environment Configuration
Copy `.env.example` to `.env` (or use the pre-configured `.env`):
```env
APP_NAME="NammaSevai AI Backend"
APP_ENV="development"
DEBUG=True
HOST="0.0.0.0"
PORT=8000

# Database Configuration (Defaults to SQLite for instant local dev)
DATABASE_URL="sqlite:///./nammasevai.db"

# Admin Authentication Key
ADMIN_API_KEY="nammasevai-admin-secret-2026"

# Google Gemini AI API Configuration (Optional)
# If unset, the system uses verified Tamil/Tanglish deterministic NLP rule matching.
GEMINI_API_KEY=""
```

### 2. Start the Backend Server
Run the FastAPI application with Uvicorn:
```powershell
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 3. Open the Application
- **Citizen Web Portal**: [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative ReDoc API Docs**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check Endpoint**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 🗄️ PostgreSQL Production Setup

To connect to a live PostgreSQL database:
1. Ensure PostgreSQL is running on your machine or cloud provider.
2. In your `.env` file, update `DATABASE_URL`:
   ```env
   DATABASE_URL="postgresql://postgres:yourpassword@localhost:5432/nammasevai_db"
   ```
3. Restart the server. The application will automatically test the PostgreSQL connection and seed all 12 schemes. If PostgreSQL is offline, it safely falls back to local SQLite so the system never crashes.

---

## 🧪 Verification & Testing

Run the full end-to-end verification test suite:
```powershell
python test_e2e_full_verification.py
```
This tests all 15 core assertions across health, scheme listings, filtering, Tamil/Tanglish/English extraction, missing info detection, structured rule matching, voice privacy, TTS synthesis, and admin authorization.

---

## 🔒 Security & Admin Authorization

Administrative mutations are secured with header-based authorization:
- **Protected Endpoints**: `POST /api/admin/schemes`, `PUT /api/admin/schemes/{id}`, `DELETE /api/admin/schemes/{id}`, `POST /api/admin/schemes/{id}/toggle-status`.
- **Required Header**: `X-Admin-Key: <ADMIN_API_KEY>`.
- Any mutation attempted without a valid key returns `401 Unauthorized`.
- Overview metrics (`GET /api/admin/stats`) and public scheme discovery remain open for citizen access.

---

## ⚠️ Important Sample Demonstration Data Disclaimer

*The welfare scheme information, criteria, and benefits provided in this application are realistic sample demonstration data for discovery and educational testing purposes. They are not officially verified or endorsed by the Government of Tamil Nadu or the Government of India. Citizens must verify their eligibility, latest government orders, and required documents at their local Village Administrative Office, Taluk Office, or authorized e-Sevai Center before applying.*
