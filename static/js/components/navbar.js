// NammaSevai AI - Navbar Component
import { i18n } from '../i18n.js';

export function renderNavbar(state, onNavigate, onToggleLang) {
  const t = i18n[state.lang] || i18n.ta;
  const currentRoute = state.route || 'landing';

  return `
    <div class="gov-top-bar"></div>
    <div class="official-strip">
      <div class="container official-strip-content">
        <div class="official-badge-text">
          <span class="dot"></span>
          <span>தமிழ்நாடு அரசு & இந்திய அரசு நலத்திட்டங்கள் தகவல் தளம் | Citizen Public Discovery Initiative</span>
        </div>
        <div style="display: flex; gap: 1rem; align-items: center;">
          <span>ஹெல்ப்லைன்: 1100</span>
          <span>|</span>
          <span style="color: var(--accent-saffron);">வழிகாட்டுதல் மாதிரி தளம் (Demo Catalog)</span>
        </div>
      </div>
    </div>
    <header class="navbar">
      <div class="container navbar-inner">
        <a class="brand-link" id="nav-brand" href="#landing">
          <img src="assets/nammasevai_minimal.svg" alt="NammaSevai AI Logo" class="brand-logo-img" />
          <div class="brand-titles">
            <span class="brand-title-main">
              NammaSevai <span class="ai-pill">AI</span>
            </span>
            <span class="brand-subtitle">${t.tagline}</span>
          </div>
        </a>

        <ul class="nav-menu" id="nav-menu">
          <li class="nav-item">
            <a class="nav-link ${currentRoute === 'landing' ? 'active' : ''}" href="#landing" data-route="landing">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
              <span>${t.home}</span>
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link ${currentRoute === 'assistant' ? 'active' : ''}" href="#assistant" data-route="assistant">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>
              <span>${t.assistant}</span>
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link ${currentRoute === 'schemes' || currentRoute === 'scheme-details' ? 'active' : ''}" href="#schemes" data-route="schemes">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/></svg>
              <span>${t.schemes}</span>
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link ${currentRoute === 'admin' ? 'active' : ''}" href="#admin" data-route="admin">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>
              <span>${t.admin}</span>
            </a>
          </li>
        </ul>

        <div class="nav-actions">
          <button class="lang-toggle-btn" id="lang-toggle-btn" title="Switch Language">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" x2="22" y1="12" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
            <span>${t.languageToggle}</span>
          </button>
          <a class="btn btn-primary btn-sm" href="#assistant" id="nav-cta-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>
            <span>${t.tryVoiceNow}</span>
          </a>
          <button class="mobile-menu-toggle" id="mobile-toggle" aria-label="Toggle Navigation">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>
          </button>
        </div>
      </div>
    </header>
  `;
}
