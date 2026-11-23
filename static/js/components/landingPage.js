// NammaSevai AI - Landing Page Component
import { i18n } from '../i18n.js';

export function renderLandingPage(state, onSelectExample) {
  const t = i18n[state.lang] || i18n.ta;

  return `
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="container hero-grid">
        <div class="hero-content">
          <div class="hero-badge-wrap">
            <span class="badge badge-teal">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/></svg>
              ${t.voicePreviewBadge}
            </span>
            <span class="badge badge-saffron">தமிழ்நாடு அரசு நலத்திட்டங்கள்</span>
          </div>

          <h1 class="hero-title">${t.heroTitle}</h1>
          <p class="hero-subtitle">${t.heroSubtitle}</p>

          <div class="hero-actions">
            <a href="#assistant" class="btn btn-primary btn-lg" id="hero-get-started-btn">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>
              <span>${t.getStarted}</span>
            </a>
            <a href="#schemes" class="btn btn-outline btn-lg">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/></svg>
              <span>${t.schemes}</span>
            </a>
          </div>

          <div class="hero-stats-row">
            <div class="hero-stat-card">
              <span class="stat-number">12+</span>
              <span class="stat-label">${t.statsTotalSchemes}</span>
            </div>
            <div class="hero-stat-card">
              <span class="stat-number">100%</span>
              <span class="stat-label">${t.statsTamilNaduFocus}</span>
            </div>
            <div class="hero-stat-card">
              <span class="stat-number">3 Languages</span>
              <span class="stat-label">${t.statsVoiceSupported}</span>
            </div>
            <div class="hero-stat-card">
              <span class="stat-number">Free</span>
              <span class="stat-label">${t.statsFreeCitizenTool}</span>
            </div>
          </div>
        </div>

        <!-- Voice-First Assistant Interactive Preview -->
        <div class="hero-preview-box">
          <div class="preview-box-header">
            <div style="display: flex; align-items: center; gap: 0.65rem;">
              <span style="font-size: 1.25rem;">🎙️</span>
              <span style="font-weight: 700; color: var(--primary-navy); font-size: 0.95rem;">குரல் வழி மாதிரி (Live Preview)</span>
            </div>
            <div class="preview-status">
              <span class="pulse-indicator"></span>
              <span>Online & Ready</span>
            </div>
          </div>

          <div class="preview-speech-demo">
            <div class="speech-bubble-user">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--primary-teal)" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              <span>${t.heroSampleQuery}</span>
            </div>

            <div class="speech-bubble-ai">
              <div class="ai-match-header">
                <span class="badge badge-green">98% Match</span>
                <span style="font-size: 0.76rem; color: var(--text-light);">AI Analysis</span>
              </div>
              <div class="ai-scheme-name">மூவலூர் ராமாமிர்தம் அம்மையார் புதுமைப் பெண் திட்டம்</div>
              <div class="ai-scheme-benefit">💰 பலன்: மாதம் ₹1,000 நேரடி வங்கி வரவு</div>
              <p style="font-size: 0.84rem; color: var(--text-muted); line-height: 1.5;">
                அரசுப் பள்ளியில் 6 முதல் 12-ம் வகுப்பு வரை படித்து கல்லூரி சேரும் மாணவிகளுக்கு தகுதி உண்டு.
              </p>
              <div style="display: flex; gap: 0.4rem; flex-wrap: wrap;">
                <span class="doc-pill">ஆதார் அட்டை</span>
                <span class="doc-pill">12-ம் வகுப்பு மதிப்பெண்</span>
                <span class="doc-pill">போனஃபைட் சான்று</span>
              </div>
            </div>
          </div>

          <div class="preview-mic-cta">
            <a href="#assistant" class="btn btn-saffron" style="width: 100%; border-radius: var(--radius-md);">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/></svg>
              <span>உங்களுடைய கேள்வியை பேசத் தொடங்குங்கள்</span>
            </a>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
      <div class="container">
        <div class="section-header">
          <span class="badge badge-teal" style="margin-bottom: 0.75rem;">அம்சங்கள் | Features</span>
          <h2 class="section-title">${t.featuresTitle}</h2>
          <p class="section-subtitle">${t.featuresSubtitle}</p>
        </div>

        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon-wrapper" style="background: rgba(0, 143, 140, 0.12); color: var(--primary-teal);">
              <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>
            </div>
            <h3 class="feature-title">${t.feat1Title}</h3>
            <p class="feature-desc">${t.feat1Desc}</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon-wrapper" style="background: rgba(9, 45, 80, 0.1); color: var(--primary-navy);">
              <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" x2="12" y1="22.08" y2="12"/></svg>
            </div>
            <h3 class="feature-title">${t.feat2Title}</h3>
            <p class="feature-desc">${t.feat2Desc}</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon-wrapper" style="background: rgba(255, 148, 24, 0.14); color: var(--accent-saffron-dark);">
              <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
            </div>
            <h3 class="feature-title">${t.feat3Title}</h3>
            <p class="feature-desc">${t.feat3Desc}</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon-wrapper" style="background: rgba(22, 131, 74, 0.12); color: var(--gov-green);">
              <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" x2="21" y1="14" y2="3"/></svg>
            </div>
            <h3 class="feature-title">${t.feat4Title}</h3>
            <p class="feature-desc">${t.feat4Desc}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works Section -->
    <section class="how-it-works-section">
      <div class="container">
        <div class="section-header">
          <span class="badge badge-navy" style="margin-bottom: 0.75rem;">எளிய வழிமுறை | Process</span>
          <h2 class="section-title">${t.howItWorksTitle}</h2>
          <p class="section-subtitle">${t.howItWorksSubtitle}</p>
        </div>

        <div class="steps-grid">
          <div class="step-card">
            <div class="step-number">1</div>
            <h3 class="step-title">${t.step1Title}</h3>
            <p class="step-desc">${t.step1Desc}</p>
            <div style="font-size: 0.85rem; color: var(--primary-teal-dark); font-weight: 600; margin-top: auto;">
              ✓ தமிழ், Tanglish & English
            </div>
          </div>

          <div class="step-card">
            <div class="step-number">2</div>
            <h3 class="step-title">${t.step2Title}</h3>
            <p class="step-desc">${t.step2Desc}</p>
            <div style="font-size: 0.85rem; color: var(--primary-teal-dark); font-weight: 600; margin-top: auto;">
              ✓ வயது, வருமானம் & தொழில் ஆய்வு
            </div>
          </div>

          <div class="step-card">
            <div class="step-number">3</div>
            <h3 class="step-title">${t.step3Title}</h3>
            <p class="step-desc">${t.step3Desc}</p>
            <div style="font-size: 0.85rem; color: var(--primary-teal-dark); font-weight: 600; margin-top: auto;">
              ✓ ஆவணங்கள் பட்டியல் அச்சிடும் வசதி
            </div>
          </div>
        </div>

        <div style="text-align: center; margin-top: 3.5rem;">
          <a href="#assistant" class="btn btn-primary btn-lg">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>
            <span>${t.tryVoiceNow}</span>
          </a>
        </div>
      </div>
    </section>
  `;
}
