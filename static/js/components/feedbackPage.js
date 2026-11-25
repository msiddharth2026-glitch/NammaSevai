// NammaSevai AI - Citizen Pilot Feedback Component (Privacy-Preserving, Zero-PII)
import { i18n } from '../i18n.js';

export function renderFeedbackPage(state) {
  const t = i18n[state.lang] || i18n.ta;
  const lang = state.lang || 'ta';

  const titles = {
    ta: "குடிமக்கள் கள ஆய்வு & அனுபவக் கருத்துக்கணிப்பு",
    en: "Citizen Pilot Feedback & Experience Survey",
    hi: "नागरिक पायलट प्रतिक्रिया एवं अनुभव सर्वेक्षण",
    ml: "പൗര പൈലറ്റ് ഫീഡ്‌ബാക്കും അനുഭവ സർവേയും",
    tanglish: "Citizen Pilot Feedback & Experience Survey",
    hinglish: "Citizen Pilot Feedback & Experience Survey"
  };

  const subtitles = {
    ta: "பாரத்சேவை AI தளத்தின் தகுதிப் பரிந்துரைகள் மற்றும் பயன்பாட்டு அனுபவத்தை மேம்படுத்த உங்கள் நேர்மையான கருத்துக்களைப் பகிருங்கள்.",
    en: "Share your honest voluntary feedback to improve scheme discovery, eligibility clarity, and accessibility for all Indian citizens.",
    hi: "सभी भारतीय नागरिकों के लिए योजना खोज और पात्रता स्पष्टता को बेहतर बनाने के लिए अपनी प्रतिक्रिया साझा करें।",
    ml: "എല്ലാ ഇന്ത്യൻ പൗരന്മാർക്കും പദ്ധതി കണ്ടെത്തലും യോഗ്യതാ വ്യക്തതയും മെച്ചപ്പെടുത്താൻ നിങ്ങളുടെ അഭിപ്രായം പങ്കിടുക.",
    tanglish: "Share your voluntary feedback to make scheme discovery clearer and easier for citizens.",
    hinglish: "BharatSevai AI ko aur behtar banane ke liye apna anubhav aur sujhav share karein."
  };

  return `
    <div class="container" style="max-width: 860px; margin: 2rem auto; padding: 0 1rem 4rem;">
      
      <!-- Top Title Box -->
      <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-2xl); padding: 1.75rem 2rem; box-shadow: var(--shadow-sm); margin-bottom: 1.5rem;">
        <div style="display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.2rem 0.75rem; border-radius: 9999px; background: rgba(217, 119, 6, 0.12); color: var(--secondary-saffron-dark); font-size: 0.8rem; font-weight: 700; margin-bottom: 0.5rem;">
          <span class="material-symbols-outlined" style="font-size: 16px;">rate_review</span>
          <span>Controlled Citizen Pilot — Phase 7.1</span>
        </div>
        <h1 style="font-size: 1.85rem; font-weight: 800; color: var(--primary-indigo); margin: 0 0 0.4rem; line-height: 1.25;">
          ${titles[lang] || titles.en}
        </h1>
        <p style="font-size: 0.95rem; color: var(--text-secondary); line-height: 1.6; margin: 0;">
          ${subtitles[lang] || subtitles.en}
        </p>

        <!-- Privacy Shield Banner -->
        <div style="margin-top: 1.25rem; background: var(--bg-canvas); border: 1px solid var(--border-color); border-radius: var(--radius-lg); padding: 0.85rem 1rem; display: flex; align-items: flex-start; gap: 0.75rem;">
          <span class="material-symbols-outlined" style="color: var(--tertiary-green); font-size: 22px; flex-shrink: 0; margin-top: 2px;">verified_user</span>
          <div style="font-size: 0.84rem; color: var(--text-secondary); line-height: 1.55;">
            <strong style="color: var(--primary-indigo);">Zero-PII Privacy Protection:</strong> 
            This feedback is strictly voluntary and anonymous. We never collect or store names, phone numbers, email addresses, Aadhaar numbers, or passwords.
          </div>
        </div>
      </div>

      <!-- Feedback Form Card -->
      <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-2xl); padding: 2rem; box-shadow: var(--shadow-md);" id="feedback-card">
        <form id="citizen-pilot-feedback-form">
          
          <!-- Row 1: Participant Category & Preferred Language -->
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.25rem; margin-bottom: 1.5rem;">
            <div>
              <label for="fb-category" style="display: block; font-size: 0.88rem; font-weight: 700; color: var(--primary-indigo); margin-bottom: 0.4rem;">
                Participant Category (Optional)
              </label>
              <select id="fb-category" class="form-input" style="width: 100%; padding: 0.65rem 0.85rem; border: 1px solid var(--border-color); border-radius: var(--radius-md); background: #ffffff; font-size: 0.9rem;">
                <option value="">Select your role / category...</option>
                <option value="College Student">College Student / மாணவர்</option>
                <option value="Farmer">Farmer / விவசாயி</option>
                <option value="Woman Entrepreneur">Woman Entrepreneur / பெண் தொழில்முனைவோர்</option>
                <option value="Senior Citizen">Senior Citizen (60+) / மூத்த குடிமக்கள்</option>
                <option value="Unemployed Youth">Unemployed Youth / வேலைதேடும் இளைஞர்</option>
                <option value="Daily-Wage / Construction Worker">Daily-Wage / Construction Worker / தொழிலாளி</option>
                <option value="Person with Disability">Person with Disability / மாற்றுத்திறனாளி</option>
                <option value="Self-Employed / Artisan">Self-Employed / Traditional Artisan / கைவினைஞர்</option>
                <option value="General Citizen">General Citizen / பொதுமக்கள்</option>
              </select>
            </div>

            <div>
              <label for="fb-language" style="display: block; font-size: 0.88rem; font-weight: 700; color: var(--primary-indigo); margin-bottom: 0.4rem;">
                Language Used
              </label>
              <select id="fb-language" class="form-input" style="width: 100%; padding: 0.65rem 0.85rem; border: 1px solid var(--border-color); border-radius: var(--radius-md); background: #ffffff; font-size: 0.9rem;">
                <option value="ta" ${lang === 'ta' ? 'selected' : ''}>தமிழ் (Tamil)</option>
                <option value="en" ${lang === 'en' ? 'selected' : ''}>English</option>
                <option value="hi" ${lang === 'hi' ? 'selected' : ''}>हिन्दी (Hindi)</option>
                <option value="ml" ${lang === 'ml' ? 'selected' : ''}>മലയാളം (Malayalam)</option>
                <option value="tanglish" ${lang === 'tanglish' ? 'selected' : ''}>Tanglish (Tamil in English script)</option>
                <option value="hinglish" ${lang === 'hinglish' ? 'selected' : ''}>Hinglish (Hindi in English script)</option>
              </select>
            </div>
          </div>

          <!-- Section 2: Star Ratings (1-5) -->
          <div style="border-top: 1px solid var(--border-color); border-bottom: 1px solid var(--border-color); padding: 1.5rem 0; margin-bottom: 1.5rem; display: flex; flex-direction: column; gap: 1.25rem;">
            
            <!-- Rating 1: Ease of Use -->
            <div>
              <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.35rem;">
                <label style="font-size: 0.92rem; font-weight: 700; color: var(--primary-indigo);">
                  1. Overall Ease of Use & Navigation (பயன்பாட்டு எளிமை)
                </label>
                <span id="ease-val" style="font-size: 0.84rem; font-weight: 700; color: var(--secondary-saffron);">5 / 5 (Very Easy)</span>
              </div>
              <input type="range" id="fb-ease" min="1" max="5" value="5" step="1" style="width: 100%; accent-color: var(--secondary-saffron); cursor: pointer;" />
              <div style="display: flex; justify-content: space-between; font-size: 0.74rem; color: var(--text-muted); margin-top: 2px;">
                <span>1 - Difficult / புரியவில்லை</span>
                <span>3 - Moderate / சுமாரானது</span>
                <span>5 - Very Easy / மிக எளிது</span>
              </div>
            </div>

            <!-- Rating 2: Clarity of Eligibility Rules -->
            <div>
              <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.35rem;">
                <label style="font-size: 0.92rem; font-weight: 700; color: var(--primary-indigo);">
                  2. Clarity of Eligibility Criteria & Questions (தகுதி நிபந்தனைகளின் தெளிவு)
                </label>
                <span id="clarity-val" style="font-size: 0.84rem; font-weight: 700; color: var(--secondary-saffron);">5 / 5 (Very Clear)</span>
              </div>
              <input type="range" id="fb-clarity" min="1" max="5" value="5" step="1" style="width: 100%; accent-color: var(--secondary-saffron); cursor: pointer;" />
              <div style="display: flex; justify-content: space-between; font-size: 0.74rem; color: var(--text-muted); margin-top: 2px;">
                <span>1 - Confusing / குழப்பமானது</span>
                <span>3 - Clear Enough / ஓரளவு தெளிவு</span>
                <span>5 - Very Clear / மிகத் தெளிவு</span>
              </div>
            </div>

            <!-- Rating 3: Usefulness of Recommendations -->
            <div>
              <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.35rem;">
                <label style="font-size: 0.92rem; font-weight: 700; color: var(--primary-indigo);">
                  3. Usefulness of Recommended Schemes & Checklist (பரிந்துரைகளின் பயன்)
                </label>
                <span id="useful-val" style="font-size: 0.84rem; font-weight: 700; color: var(--secondary-saffron);">5 / 5 (Highly Useful)</span>
              </div>
              <input type="range" id="fb-useful" min="1" max="5" value="5" step="1" style="width: 100%; accent-color: var(--secondary-saffron); cursor: pointer;" />
              <div style="display: flex; justify-content: space-between; font-size: 0.74rem; color: var(--text-muted); margin-top: 2px;">
                <span>1 - Not Useful / பயனில்லை</span>
                <span>3 - Somewhat Useful / பயனுள்ளது</span>
                <span>5 - Highly Useful / மிக பயனுள்ளது</span>
              </div>
            </div>

          </div>

          <!-- Section 3: Qualitative Feedback -->
          <div style="margin-bottom: 1.25rem;">
            <label for="fb-problems" style="display: block; font-size: 0.88rem; font-weight: 700; color: var(--primary-indigo); margin-bottom: 0.4rem;">
              Did you encounter any problems, confusing terms, or broken links? (எதிர்கொண்ட சிரமங்கள்)
            </label>
            <textarea id="fb-problems" class="form-input" rows="3" placeholder="e.g. Could not find specific certificate, voice synthesis was slow, or official link took time to load..." style="width: 100%; padding: 0.75rem; border: 1px solid var(--border-color); border-radius: var(--radius-md); font-family: inherit; font-size: 0.9rem; resize: vertical;"></textarea>
          </div>

          <div style="margin-bottom: 1.5rem;">
            <label for="fb-suggestions" style="display: block; font-size: 0.88rem; font-weight: 700; color: var(--primary-indigo); margin-bottom: 0.4rem;">
              Suggestions to make BharatSevai AI better for citizens (மேம்படுத்த உங்கள் ஆலோசனைகள்)
            </label>
            <textarea id="fb-suggestions" class="form-input" rows="3" placeholder="e.g. Add village-level filters, add WhatsApp checklist sharing, or simplify document descriptions..." style="width: 100%; padding: 0.75rem; border: 1px solid var(--border-color); border-radius: var(--radius-md); font-family: inherit; font-size: 0.9rem; resize: vertical;"></textarea>
          </div>

          <!-- Notice on Sensitive Information -->
          <div style="margin-bottom: 1.5rem; font-size: 0.8rem; color: var(--error-red); background: var(--error-red-light); padding: 0.65rem 0.85rem; border-radius: var(--radius-sm); display: flex; align-items: center; gap: 0.45rem;">
            <span class="material-symbols-outlined" style="font-size: 18px;">warning</span>
            <span>Do NOT enter your Aadhaar number, phone number, bank details, or passwords here.</span>
          </div>

          <!-- Submit Buttons -->
          <div style="display: flex; gap: 0.75rem; justify-content: flex-end; align-items: center;">
            <a href="#landing" class="btn btn-outline" style="padding: 0.6rem 1.25rem; font-size: 0.9rem; text-decoration: none;">
              Back to Home
            </a>
            <button type="submit" id="submit-feedback-btn" class="btn btn-primary" style="padding: 0.65rem 1.75rem; font-size: 0.92rem; display: flex; align-items: center; gap: 0.45rem;">
              <span class="material-symbols-outlined" style="font-size: 18px;">send</span>
              <span>Submit Voluntary Feedback / சமர்ப்பிக்கவும்</span>
            </button>
          </div>

        </form>

        <!-- Success Banner Placeholder -->
        <div id="feedback-success-banner" style="display: none; text-align: center; padding: 2.5rem 1rem;">
          <div style="width: 56px; height: 56px; border-radius: 9999px; background: rgba(21, 128, 61, 0.12); color: var(--tertiary-green); display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem;">
            <span class="material-symbols-outlined" style="font-size: 32px;">check_circle</span>
          </div>
          <h2 style="font-size: 1.5rem; font-weight: 800; color: var(--primary-indigo); margin-bottom: 0.5rem;">
            நன்றி! Feedback Received Successfully
          </h2>
          <p style="font-size: 0.92rem; color: var(--text-secondary); max-width: 500px; margin: 0 auto 1.5rem; line-height: 1.6;">
            Your valuable observations have been recorded anonymously. They directly inform our development team to enhance clarity, accessibility, and accuracy for citizens across India.
          </p>
          <div style="display: flex; gap: 0.75rem; justify-content: center;">
            <a href="#assistant" class="btn btn-primary" style="padding: 0.6rem 1.25rem; font-size: 0.88rem; text-decoration: none;">
              Find More Schemes
            </a>
            <a href="#landing" class="btn btn-outline" style="padding: 0.6rem 1.25rem; font-size: 0.88rem; text-decoration: none;">
              Back to Home
            </a>
          </div>
        </div>

      </div>

    </div>
  `;
}
