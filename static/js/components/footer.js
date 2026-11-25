// BharatSevai AI - Footer Component (Stitch / Bharat Pathways Design)
import { i18n } from '../i18n.js';

export function renderFooter(state) {
  const t = i18n[state.lang] || i18n.ta;
  const lang = state.lang || 'ta';

  // Localized disclaimer banner title
  const disclaimerTitles = {
    ta: "பொது வழிகாட்டுதல் மற்றும் விழிப்புணர்வு தளம் மட்டுமே (Civic Guidance & Awareness Only)",
    hi: "नागरिक मार्गदर्शन एवं जागरूकता मंच (Civic Guidance & Awareness Only)",
    ml: "പൗര മാർഗ്ഗനിർദ്ദേശവും അവബോധവും മാത്രം (Civic Guidance & Awareness Only)",
    hinglish: "Civic Guidance & Awareness Only (Sarkari Jankari Sahayak):",
    tanglish: "Civic Guidance & Awareness Only (Makkal Sevai Guide):",
    en: "Civic Guidance & Awareness Only:"
  };
  const disclaimerTitle = disclaimerTitles[lang] || disclaimerTitles.en;

  // Localized helpline sub-labels
  const eduHelplineLabel = {
    ta: "பள்ளிக் கல்வி வழிகாட்டுதல்",
    hi: "शिक्षा मार्गदर्शन हेल्पलाइन",
    ml: "വിദ്യാഭ്യാസ ഹെൽപ്പ്‌ലൈൻ",
    hinglish: "Education Helpline",
    tanglish: "Education Helpline",
    en: "Education Guidance Helpline"
  }[lang] || "Education Guidance Helpline";

  const womenHelplineLabel = {
    ta: "பெண்கள் உதவி மையம்",
    hi: "महिला हेल्पलाइन",
    ml: "വനിതാ ഹെൽപ്പ്‌ലൈൻ",
    hinglish: "Women Helpline",
    tanglish: "Women Helpline",
    en: "Women Welfare Helpline"
  }[lang] || "Women Welfare Helpline";

  const healthHelplineLabel = {
    ta: "மருத்துவ ஆலோசனை உதவி மையம்",
    hi: "स्वास्थ्य एवं चिकित्सा हेल्पलाइन",
    ml: "ആരോഗ്യ ഹെൽപ്പ്‌ലൈൻ",
    hinglish: "Health & Medical Helpline",
    tanglish: "Health & Medical Helpline",
    en: "State Health & Medical Helpline"
  }[lang] || "State Health & Medical Helpline";

  const emergencyLabel = {
    ta: "அவசர உதவி: 108 (ஆம்புலன்ஸ்) / 100 (காவல்துறை)",
    hi: "आपातकालीन सेवा: 108 (एम्बुलेंस) / 100 (पुलिस)",
    ml: "അടിയന്തിരം: 108 (ആംബുലൻസ്) / 100 (പോലീസ്)",
    hinglish: "Emergency Services: 108 (Ambulance) / 100 (Police)",
    tanglish: "Emergency Services: 108 (Ambulance) / 100 (Police)",
    en: "Emergency Services: 108 (Ambulance) / 100 (Police)"
  }[lang] || "Emergency Services: 108 (Ambulance) / 100 (Police)";

  return `
    <footer class="footer">
      <div class="container">
        <!-- Civic Guidance & Disclaimer Strip -->
        <div class="disclaimer-banner">
          <div style="display: flex; align-items: flex-start; gap: 0.75rem;">
            <span class="material-symbols-outlined" style="font-size: 24px; color: var(--secondary-saffron); flex-shrink: 0;">info</span>
            <div>
              <strong style="color: var(--primary-indigo); font-size: 0.95rem;">
                ${disclaimerTitle}
              </strong>
              <p style="margin-top: 0.25rem; font-size: 0.86rem; color: var(--text-secondary); line-height: 1.6;">
                ${t.disclaimerText || "BharatSevai AI simplifies public welfare scheme discovery. Official state and union departments determine final eligibility and financial approval. Please verify requirements at your nearest e-Sevai / CSC center or official department portal before applying."}
              </p>
            </div>
          </div>
        </div>

        <div class="footer-grid">
          <!-- Column 1: Brand & Civic Mission -->
          <div class="footer-brand">
            <div style="display: flex; align-items: center; gap: 0.65rem; margin-bottom: 0.75rem;">
              <img src="assets/bharatsevai_minimal.svg" alt="BharatSevai AI Logo" style="height: 34px; width: auto;" />
              <div style="font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: var(--primary-indigo);">
                BharatSevai AI
              </div>
            </div>
            <p style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.65; max-width: 360px;">
              ${t.footerDesc || "A voice-first welfare scheme discovery assistant for Indian citizens across all states and union territories. Discover benefits, documents, and procedures in plain language."}
            </p>
            <div style="display: flex; gap: 0.45rem; flex-wrap: wrap; margin-top: 1rem;">
              <span class="badge badge-indigo">
                <span class="material-symbols-outlined" style="font-size: 14px;">gavel</span>
                Civic Tech
              </span>
              <span class="badge badge-saffron">
                <span class="material-symbols-outlined" style="font-size: 14px;">mic</span>
                Voice First
              </span>
              <span class="badge badge-green">
                <span class="material-symbols-outlined" style="font-size: 14px;">lock</span>
                Zero-PII Storage
              </span>
            </div>
          </div>

          <!-- Column 2: Navigation Links -->
          <div>
            <h4 class="footer-col-title">${t.quickLinks || 'Quick Navigation'}</h4>
            <ul class="footer-links-list">
              <li><a href="#landing">${t.home || 'Home'}</a></li>
              <li><a href="#assistant">${t.assistant || 'Find Schemes (Voice/Text)'}</a></li>
              <li><a href="#schemes">${t.schemes || 'Explore All Schemes'}</a></li>
              <li><a href="#checklist">${t.checklist || t.savedChecklistNav || 'Saved Preparation Checklist'}</a></li>
              <li><a href="#feedback"><span class="material-symbols-outlined" style="font-size: 14px; vertical-align: middle;">rate_review</span> ${t.pilotFeedbackNav || 'Citizen Pilot Feedback'}</a></li>
              <li><a href="#admin">${t.admin || 'Portal Administration'}</a></li>
              <li><a href="https://tnesevai.tn.gov.in" target="_blank" rel="noopener">TNeGA e-Sevai Citizen Portal ↗</a></li>
              <li><a href="https://www.tn.gov.in" target="_blank" rel="noopener">Tamil Nadu Government Portal ↗</a></li>
            </ul>
          </div>

          <!-- Column 3: Helplines & Assistance -->
          <div>
            <h4 class="footer-col-title">${t.helplineTitle || t.citizenHelplines || 'Citizen Helplines'}</h4>
            <div class="helpline-item">
              <span class="material-symbols-outlined" style="color: var(--secondary-saffron); font-size: 18px;">school</span>
              <span><strong>14417</strong> — ${eduHelplineLabel}</span>
            </div>
            <div class="helpline-item">
              <span class="material-symbols-outlined" style="color: var(--secondary-saffron); font-size: 18px;">support_agent</span>
              <span><strong>181</strong> — ${womenHelplineLabel}</span>
            </div>
            <div class="helpline-item">
              <span class="material-symbols-outlined" style="color: var(--secondary-saffron); font-size: 18px;">local_hospital</span>
              <span><strong>104</strong> — ${healthHelplineLabel}</span>
            </div>
            <div style="margin-top: 0.75rem; font-size: 0.8rem; color: var(--text-muted);">
              ${emergencyLabel}
            </div>
          </div>
        </div>

        <!-- Footer Bottom Bar -->
        <div class="footer-bottom">
          <div>${t.copyright || '© 2026 BharatSevai AI. Developed for public welfare awareness.'}</div>
          <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
            <span>FastAPI + PostgreSQL Ready</span>
            <span>•</span>
            <span>WCAG AAA Contrast Compliant</span>
          </div>
        </div>
      </div>
    </footer>
  `;
}
