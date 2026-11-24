// NammaSevai AI - Landing Page Component (Stitch / Namma Pathways Design)
import { i18n } from '../i18n.js';

export function renderLandingPage(state) {
  const t = i18n[state.lang] || i18n.ta;

  return `
    <div class="landing-page-wrapper">
      <!-- Hero Section with Kolam Coordinate Geometry -->
      <section class="hero-section">
        <div class="container">
          <div class="kolam-wrapper" style="padding: 2.25rem 2rem;">
            <!-- Kolam Coordinate Network Background SVGs -->
            <svg class="kolam-bg-svg" style="top: -40px; right: -40px; width: 380px; height: 380px;" fill="none" stroke="currentColor" stroke-width="1.2" viewBox="0 0 200 200">
              <circle cx="100" cy="100" r="80" stroke-dasharray="4 6" stroke="#15233E"></circle>
              <circle cx="100" cy="100" r="48" stroke="#D97706"></circle>
              <path d="M20 100 Q100 20 180 100 Q100 180 20 100Z" stroke="#15233E"></path>
              <path d="M100 20 Q180 100 100 180 Q20 100 100 20Z" stroke="#D97706"></path>
              <circle cx="60" cy="60" fill="#15233E" r="3"></circle>
              <circle cx="140" cy="60" fill="#15233E" r="3"></circle>
              <circle cx="140" cy="140" fill="#15233E" r="3"></circle>
              <circle cx="60" cy="140" fill="#15233E" r="3"></circle>
            </svg>

            <div style="position: relative; z-index: 2; display: flex; flex-direction: column; gap: 1.5rem;">
              <!-- Trust Overline Badges -->
              <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 0.65rem;">
                <div class="badge badge-indigo" style="background: #ffffff; box-shadow: var(--shadow-xs);">
                  <span class="material-symbols-outlined" style="font-size: 16px; color: var(--secondary-saffron);">account_balance</span>
                  <span>${t.trustOverlineIndependent || 'Independent Civic Discovery Service'}</span>
                  <span style="display: inline-block; width: 4px; height: 4px; border-radius: 50%; background: var(--text-muted);"></span>
                  <span style="font-weight: normal; color: var(--text-secondary);">${t.trustOverlineNotGov || 'Not a Government Authority'}</span>
                </div>
                <div class="badge badge-green">
                  <span class="material-symbols-outlined" style="font-size: 16px;">verified</span>
                  <span>${t.trustOverlineWelfare || 'Tamil Nadu & Central Welfare Schemes'}</span>
                </div>
              </div>

              <!-- Main Hero Grid -->
              <div class="hero-grid">
                <div class="hero-content">
                  <h1 class="hero-title">
                    ${t.heroTitle}
                  </h1>
                  <p class="hero-subtitle">
                    ${t.heroSubtitle}
                  </p>

                  <div class="hero-actions">
                    <a href="#assistant" class="btn btn-saffron btn-lg" id="hero-get-started-btn">
                      <span class="material-symbols-outlined" style="font-size: 22px;">mic</span>
                      <span>${t.heroSpeakPrompt || t.tryVoiceNow || t.getStarted}</span>
                    </a>
                    <a href="#schemes" class="btn btn-outline btn-lg">
                      <span class="material-symbols-outlined" style="font-size: 20px;">explore</span>
                      <span>${t.schemes || 'Explore All Schemes'}</span>
                    </a>
                  </div>
                </div>

                <!-- Editorial Catalog Highlights Card -->
                <div class="editorial-stats-card">
                  <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.78rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em;">${t.catalogCoverageTitle || 'Catalog Coverage'}</span>
                    <span class="material-symbols-outlined" style="color: var(--secondary-saffron); font-size: 24px;">hub</span>
                  </div>
                  <div style="display: flex; align-items: baseline; gap: 0.5rem;">
                    <span class="editorial-stats-num">14+</span>
                    <span style="font-weight: 600; color: var(--text-secondary); font-size: 0.95rem;">${t.catalogCoverageCount}</span>
                  </div>
                  <p style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.55;">
                    ${t.catalogCoverageDesc}
                  </p>
                  <div style="display: flex; align-items: center; gap: 0.4rem; font-size: 0.8rem; font-weight: 600; color: var(--tertiary-green-dark); padding-top: 0.35rem; border-top: 1px solid var(--border-color);">
                    <span class="material-symbols-outlined" style="font-size: 16px;">policy</span>
                    <span>${t.catalogCoverageCurated}</span>
                  </div>
                </div>
              </div>

              <!-- Zero-Storage Privacy Reassurance Banner -->
              <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-lg); padding: 1.25rem 1.5rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem; box-shadow: var(--shadow-xs);">
                <div style="display: flex; align-items: center; gap: 1rem;">
                  <div style="width: 44px; height: 44px; border-radius: var(--radius-md); background: var(--tertiary-green-light); color: var(--tertiary-green-dark); display: flex; align-items: center; justify-content: center; shrink-0;">
                    <span class="material-symbols-outlined" style="font-size: 24px;">shield</span>
                  </div>
                  <div>
                    <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                      <span style="font-family: var(--font-heading); font-weight: 700; color: var(--primary-indigo); font-size: 1rem;">${t.privacyFirstTitle || 'Privacy First'}</span>
                      <span class="badge badge-indigo" style="font-size: 0.72rem;">${t.zeroStoragePolicy || 'Zero Storage Policy'}</span>
                    </div>
                    <p style="font-size: 0.86rem; color: var(--text-secondary); margin-top: 0.2rem;">
                      ${t.privacyHeroNotice}
                    </p>
                  </div>
                </div>
                <div style="background: var(--bg-container-low); padding: 0.45rem 0.85rem; border-radius: var(--radius-md); font-size: 0.8rem; color: var(--text-secondary); font-weight: 600; display: flex; align-items: center; gap: 0.35rem;">
                  <span class="material-symbols-outlined" style="font-size: 16px; color: var(--secondary-saffron);">info</span>
                  <span>${t.guidanceOnlyBadge || 'Guidance & Discovery Only'}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 3-Step Discovery Pathway Guide -->
      <section style="padding: 1rem 0 3rem;">
        <div class="container">
          <div style="text-align: center; max-width: 680px; margin: 0 auto 2.5rem;">
            <div style="display: inline-flex; align-items: center; gap: 0.35rem; color: var(--secondary-saffron); font-weight: 700; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.4rem;">
              <span class="material-symbols-outlined" style="font-size: 18px;">route</span>
              <span>${t.threeStepProcessOverline || 'Simple 3-Step Process'}</span>
            </div>
            <h2 style="font-size: 2rem; font-weight: 800; color: var(--primary-indigo);">
              ${t.howWorksHeading}
            </h2>
            <p style="color: var(--text-secondary); margin-top: 0.5rem; font-size: 1rem;">
              ${t.howWorksSub}
            </p>
          </div>

          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem;">
            <!-- Step 1 Card -->
            <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-xl); padding: 1.75rem; box-shadow: var(--shadow-sm); display: flex; flex-direction: column; gap: 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="width: 44px; height: 44px; border-radius: var(--radius-full); background: var(--primary-indigo); color: #ffffff; display: flex; align-items: center; justify-content: center; font-weight: 800;">
                  1
                </div>
                <span class="material-symbols-outlined" style="font-size: 26px; color: var(--secondary-saffron);">mic</span>
              </div>
              <h3 style="font-size: 1.18rem; font-weight: 700; color: var(--primary-indigo);">
                ${t.step1Heading}
              </h3>
              <p style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;">
                ${t.step1Description}
              </p>
            </div>

            <!-- Step 2 Card -->
            <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-xl); padding: 1.75rem; box-shadow: var(--shadow-sm); display: flex; flex-direction: column; gap: 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="width: 44px; height: 44px; border-radius: var(--radius-full); background: var(--secondary-saffron); color: #ffffff; display: flex; align-items: center; justify-content: center; font-weight: 800;">
                  2
                </div>
                <span class="material-symbols-outlined" style="font-size: 26px; color: var(--secondary-saffron);">manage_search</span>
              </div>
              <h3 style="font-size: 1.18rem; font-weight: 700; color: var(--primary-indigo);">
                ${t.step2Heading}
              </h3>
              <p style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;">
                ${t.step2Description}
              </p>
            </div>

            <!-- Step 3 Card -->
            <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-xl); padding: 1.75rem; box-shadow: var(--shadow-sm); display: flex; flex-direction: column; gap: 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="width: 44px; height: 44px; border-radius: var(--radius-full); background: var(--tertiary-green); color: #ffffff; display: flex; align-items: center; justify-content: center; font-weight: 800;">
                  3
                </div>
                <span class="material-symbols-outlined" style="font-size: 26px; color: var(--tertiary-green);">fact_check</span>
              </div>
              <h3 style="font-size: 1.18rem; font-weight: 700; color: var(--primary-indigo);">
                ${t.step3Heading}
              </h3>
              <p style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;">
                ${t.step3Description}
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Clickable Citizen Situations Section -->
      <section style="padding: 1rem 0 4rem; background: var(--bg-subtle); border-top: 1px solid var(--border-color);">
        <div class="container">
          <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 1.75rem; flex-wrap: wrap; gap: 1rem;">
            <div>
              <span style="font-size: 0.8rem; font-weight: 700; color: var(--secondary-saffron); text-transform: uppercase; letter-spacing: 0.05em;">${t.quickExamplesOverline || 'Quick Examples'}</span>
              <h2 style="font-size: 1.8rem; font-weight: 800; color: var(--primary-indigo); margin-top: 0.2rem;">
                ${t.commonSituationsHeading}
              </h2>
            </div>
            <a href="#assistant" class="btn btn-outline btn-sm">
              <span>${t.viewAssistantPrompts || 'View Assistant Prompts'}</span>
              <span class="material-symbols-outlined" style="font-size: 16px;">arrow_forward</span>
            </a>
          </div>

          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.25rem;">
            <div class="prompt-chip" data-example="${t.ex1}" style="padding: 1rem; border-radius: var(--radius-lg); flex-direction: column; align-items: flex-start; gap: 0.5rem; background: #ffffff;">
              <div style="font-size: 1.5rem;">🎓</div>
              <strong style="color: var(--primary-indigo); font-size: 0.95rem;">${t.chipGirlHigherEd}</strong>
              <span style="font-size: 0.84rem; color: var(--text-secondary);">"${t.ex1}"</span>
            </div>

            <div class="prompt-chip" data-example="${t.ex2}" style="padding: 1rem; border-radius: var(--radius-lg); flex-direction: column; align-items: flex-start; gap: 0.5rem; background: #ffffff;">
              <div style="font-size: 1.5rem;">👩</div>
              <strong style="color: var(--primary-indigo); font-size: 0.95rem;">${t.chipWomenIncome}</strong>
              <span style="font-size: 0.84rem; color: var(--text-secondary);">"${t.ex2}"</span>
            </div>

            <div class="prompt-chip" data-example="${t.ex3}" style="padding: 1rem; border-radius: var(--radius-lg); flex-direction: column; align-items: flex-start; gap: 0.5rem; background: #ffffff;">
              <div style="font-size: 1.5rem;">🌾</div>
              <strong style="color: var(--primary-indigo); font-size: 0.95rem;">${t.chipFarmerAid}</strong>
              <span style="font-size: 0.84rem; color: var(--text-secondary);">"${t.ex3}"</span>
            </div>

            <div class="prompt-chip" data-example="${t.ex4}" style="padding: 1rem; border-radius: var(--radius-lg); flex-direction: column; align-items: flex-start; gap: 0.5rem; background: #ffffff;">
              <div style="font-size: 1.5rem;">🧵</div>
              <strong style="color: var(--primary-indigo); font-size: 0.95rem;">${t.chipSewingMachine}</strong>
              <span style="font-size: 0.84rem; color: var(--text-secondary);">"${t.ex4}"</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  `;
}
