// NammaSevai AI - Header Navigation Component (Stitch / Namma Pathways Design)
import { i18n } from '../i18n.js';

export function renderNavbar(state) {
  const t = i18n[state.lang] || i18n.ta;
  const currentRoute = state.route || 'landing';
  const currentLang = state.lang || 'ta';

  // Compact label displayed on the Language button: "🌐 English ▼"
  const langDisplayMap = {
    en: 'English',
    ta: 'தமிழ்',
    hi: 'हिन्दी',
    ml: 'മലയാളம்',
    tanglish: 'Tanglish',
    hinglish: 'Hinglish'
  };
  const currentLangLabel = langDisplayMap[currentLang] || 'English';

  // Dropdown menu options as required:
  // 1. English
  // 2. தமிழ் (Tamil)
  // 3. हिन्दी (Hindi)
  // 4. മലയാളம் (Malayalam)
  // 5. Tanglish
  // 6. Hinglish
  const languageOptions = [
    { code: 'en', label: 'English' },
    { code: 'ta', label: 'தமிழ் (Tamil)' },
    { code: 'hi', label: 'हिन्दी (Hindi)' },
    { code: 'ml', label: 'മലയാളം (Malayalam)' },
    { code: 'tanglish', label: 'Tanglish' },
    { code: 'hinglish', label: 'Hinglish' }
  ];

  return `
    <div class="gov-top-bar"></div>
    <div class="official-strip">
      <div class="container official-strip-content">
        <div class="official-badge-text">
          <span class="dot"></span>
          <span>${t.officialSchemeGuidance || "Tamil Nadu & Central Welfare Schemes Guidance | Independent Civic Discovery Service"}</span>
        </div>
        <div style="display: flex; gap: 1rem; align-items: center; font-size: 0.78rem;">
          <span style="display: flex; align-items: center; gap: 0.25rem;">
            <span class="material-symbols-outlined" style="font-size: 14px; color: var(--secondary-saffron);">call</span>
            <span>${t.helplineTitle || "Helpline"}: <strong>1100</strong></span>
          </span>
          <span style="color: var(--border-color);">|</span>
          <span style="color: var(--secondary-saffron); font-weight: 600;">${currentLang === 'ta' ? "வழிகாட்டுதல் மாதிரி தளம் (Demonstration Catalog)" : currentLang === 'hi' ? "नागरिक मार्गदर्शन सूची (Demonstration Catalog)" : currentLang === 'ml' ? "മാർഗ്ഗനിർദ്ദേശ കാറ്റലോഗ് (Demonstration Catalog)" : "Demonstration Catalog"}</span>
        </div>
      </div>
    </div>

    <header class="navbar">
      <div class="container navbar-inner">
        <!-- Brand Link -->
        <a class="brand-link" id="nav-brand" href="#landing">
          <img src="assets/nammasevai_minimal.svg" alt="NammaSevai AI Logo" class="brand-logo-img" />
          <div class="brand-titles">
            <span class="brand-title-main">
              NammaSevai <span class="ai-pill">AI</span>
            </span>
            <span class="brand-subtitle">Public Service Scheme Discovery</span>
          </div>
        </a>

        <!-- Civic Privacy Reassurance Badge with Tooltip -->
        <div class="header-privacy-badge" tabindex="0" role="button" aria-haspopup="true" aria-expanded="false" aria-label="Privacy guarantee: No Aadhaar, OTP or Bank details required">
          <span class="material-symbols-outlined header-privacy-icon" aria-hidden="true">lock</span>
          <span class="header-privacy-text">${currentLang === 'ta' ? 'பாதுகாப்பானது' : currentLang === 'hi' ? 'गोपनीयता सुरक्षित' : currentLang === 'ml' ? 'സുരക്ഷിതം' : (currentLang === 'tanglish' ? 'Privacy Safe' : currentLang === 'hinglish' ? 'Privacy Safe' : 'Citizen Privacy')}</span>
          <div class="header-privacy-tooltip" role="tooltip">
            No Aadhaar, OTP or Bank details required
          </div>
        </div>

        <!-- Right Side Nav Actions: Links + Language Dropdown + Mobile Menu -->
        <div class="navbar-actions-group">
          <!-- Navigation Segmented Tabs -->
          <nav class="nav-menu-wrapper" id="nav-menu">
            <ul class="nav-menu">
              <li>
                <a class="nav-link ${currentRoute === 'landing' ? 'active' : ''}" href="#landing" data-route="landing">
                  <span class="material-symbols-outlined nav-icon">home</span>
                  <span>${t.home || 'Home'}</span>
                </a>
              </li>
              <li>
                <a class="nav-link ${currentRoute === 'assistant' ? 'active' : ''}" href="#assistant" data-route="assistant">
                  <span class="material-symbols-outlined nav-icon">record_voice_over</span>
                  <span>${t.assistant || 'Find Schemes'}</span>
                </a>
              </li>
              <li>
                <a class="nav-link ${currentRoute === 'schemes' || currentRoute === 'scheme-details' ? 'active' : ''}" href="#schemes" data-route="schemes">
                  <span class="material-symbols-outlined nav-icon">explore</span>
                  <span>${t.schemes || 'Explore All'}</span>
                </a>
              </li>
              <li>
                <a class="nav-link ${currentRoute === 'checklist' ? 'active' : ''}" href="#checklist" data-route="checklist">
                  <span class="material-symbols-outlined nav-icon">fact_check</span>
                  <span>${t.checklist || 'Saved Checklist'}</span>
                </a>
              </li>
              <li>
                <a class="nav-link ${currentRoute === 'admin' ? 'active' : ''}" href="#admin" data-route="admin">
                  <span class="material-symbols-outlined nav-icon">admin_panel_settings</span>
                  <span>${t.admin || 'Admin'}</span>
                </a>
              </li>
              <li>
                <a class="nav-link ${currentRoute === 'feedback' ? 'active' : ''}" href="#feedback" data-route="feedback">
                  <span class="material-symbols-outlined nav-icon">rate_review</span>
                  <span>${t.pilotFeedbackNav || (currentLang === 'ta' ? 'கருத்துக்கணிப்பு' : currentLang === 'hi' ? 'प्रतिक्रिया' : currentLang === 'ml' ? 'ഫീഡ്‌ബാക്ക്' : 'Feedback')}</span>
                </a>
              </li>
            </ul>

            <!-- Mobile Navigation Language Section (visible inside drawer on mobile) -->
            <div class="mobile-nav-lang-section" aria-label="Mobile Language Selection">
              <div class="mobile-nav-lang-title">
                <span class="lang-globe-icon" aria-hidden="true">🌐</span>
                <span>${t.language || 'Language / மொழி'}</span>
              </div>
              <div class="mobile-nav-lang-grid">
                ${languageOptions.map(opt => `
                  <button
                    type="button"
                    class="mobile-lang-btn ${currentLang === opt.code ? 'active' : ''}"
                    data-set-lang="${opt.code}"
                    role="menuitemradio"
                    aria-checked="${currentLang === opt.code ? 'true' : 'false'}"
                  >
                    <span>${opt.label}</span>
                    ${currentLang === opt.code ? '<span class="material-symbols-outlined mobile-lang-check" aria-hidden="true">check</span>' : ''}
                  </button>
                `).join('')}
              </div>
            </div>
          </nav>

          <!-- Single Compact Language Selector Dropdown -->
          <div class="lang-dropdown-wrapper" id="lang-dropdown-wrapper">
            <button
              type="button"
              class="lang-dropdown-btn"
              id="lang-dropdown-btn"
              aria-haspopup="true"
              aria-expanded="false"
              aria-label="Language selector. Currently selected: ${currentLangLabel}"
            >
              <span class="lang-globe-icon" aria-hidden="true">🌐</span>
              <span class="lang-current-label">${currentLangLabel}</span>
              <span class="material-symbols-outlined lang-arrow-icon" aria-hidden="true">arrow_drop_down</span>
            </button>
            
            <div class="lang-dropdown-menu" id="lang-dropdown-menu" role="menu" aria-label="Select language">
              ${languageOptions.map(opt => `
                <button
                  type="button"
                  class="lang-dropdown-item ${currentLang === opt.code ? 'active' : ''}"
                  data-set-lang="${opt.code}"
                  role="menuitemradio"
                  aria-checked="${currentLang === opt.code ? 'true' : 'false'}"
                >
                  <span class="lang-item-name">${opt.label}</span>
                  ${currentLang === opt.code ? '<span class="material-symbols-outlined lang-check-icon" aria-hidden="true">check</span>' : ''}
                </button>
              `).join('')}
            </div>
          </div>

          <!-- Mobile Drawer Toggle -->
          <button class="mobile-menu-toggle" id="mobile-toggle" aria-label="Toggle Navigation">
            <span class="material-symbols-outlined" style="font-size: 24px;">menu</span>
          </button>
        </div>
      </div>
    </header>
  `;
}
