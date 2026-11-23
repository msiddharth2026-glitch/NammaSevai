// NammaSevai AI - Footer Component
import { i18n } from '../i18n.js';

export function renderFooter(state) {
  const t = i18n[state.lang] || i18n.ta;

  return `
    <footer class="footer">
      <div class="container">
        <div class="disclaimer-banner">
          <strong>⚠️ ${t.sampleDisclaimer}</strong><br/>
          <span>${t.disclaimerText}</span>
        </div>

        <div class="footer-grid">
          <div class="footer-brand">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
              <img src="assets/nammasevai_minimal.svg" alt="NammaSevai AI" style="height: 38px; width: auto; filter: brightness(1.2);" />
              <div class="footer-brand-title">NammaSevai AI</div>
            </div>
            <p class="footer-text">${t.footerDesc}</p>
            <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">
              <span class="badge badge-teal">Tamil Nadu GovTech</span>
              <span class="badge badge-saffron">Voice AI Assistant</span>
              <span class="badge badge-navy">Bilingual</span>
            </div>
          </div>

          <div>
            <h4 class="footer-col-title">${t.quickLinks}</h4>
            <ul class="footer-links-list">
              <li><a href="#landing">${t.home}</a></li>
              <li><a href="#assistant">${t.assistant}</a></li>
              <li><a href="#schemes">${t.schemes}</a></li>
              <li><a href="#admin">${t.admin}</a></li>
              <li><a href="https://tnesevai.tn.gov.in" target="_blank" rel="noopener">TNeGA e-Sevai Portal ↗</a></li>
              <li><a href="https://www.tn.gov.in" target="_blank" rel="noopener">TN.gov.in Official ↗</a></li>
            </ul>
          </div>

          <div>
            <h4 class="footer-col-title">${t.citizenHelplines}</h4>
            <div class="helpline-item">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
              <span>${t.cmHelpline}</span>
            </div>
            <div class="helpline-item">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"/><path d="M6 6h10"/><path d="M6 10h10"/></svg>
              <span>${t.studentHelpline}</span>
            </div>
            <div class="helpline-item">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
              <span>${t.womenHelpline}</span>
            </div>
            <div class="helpline-item" style="color: #94a3b8; font-size: 0.82rem; margin-top: 0.5rem;">
              <span>Emergency Services: 108 (Ambulance) / 100 (Police)</span>
            </div>
          </div>
        </div>

        <div class="footer-bottom">
          <div>${t.copyright}</div>
          <div>FastAPI + PostgreSQL Ready Architecture | Designed with accessibility in mind</div>
        </div>
      </div>
    </footer>
  `;
}
