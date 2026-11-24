// NammaSevai AI - Schemes Results Page Component (BharatSevai AI / Stitch Theme Redesign)
import { i18n } from '../i18n.js';
import { getLocalizedScheme } from '../schemesData.js';

export function renderResultsPage(state) {
  const t = i18n[state.lang] || i18n.ta;
  const currentCategory = state.selectedCategory || 'all';
  const searchQuery = (state.searchQuery || '').toLowerCase();
  const allSchemes = state.schemes || [];
  const matchedMap = state.lastMatchedMap || {};

  // Filter schemes
  const filtered = allSchemes.filter(scheme => {
    if (currentCategory !== 'all' && scheme.category !== currentCategory) {
      return false;
    }
    if (searchQuery.trim().length > 0) {
      const matchInName = (scheme.name + " " + (scheme.name_ta || '') + " " + (scheme.name_hi || '') + " " + (scheme.name_ml || '')).toLowerCase().includes(searchQuery);
      const matchInDept = (scheme.department + " " + (scheme.department_ta || '') + " " + (scheme.department_hi || '') + " " + (scheme.department_ml || '')).toLowerCase().includes(searchQuery);
      const matchInDesc = (scheme.description + " " + (scheme.description_ta || '') + " " + (scheme.description_hi || '') + " " + (scheme.description_ml || '')).toLowerCase().includes(searchQuery);
      const matchInKw = scheme.keywords && scheme.keywords.some(k => k.toLowerCase().includes(searchQuery));
      if (!matchInName && !matchInDept && !matchInDesc && !matchInKw) {
        return false;
      }
    }
    return true;
  });

  // Calculate category counts
  const counts = { all: allSchemes.length };
  allSchemes.forEach(s => {
    counts[s.category] = (counts[s.category] || 0) + 1;
  });

  return `
    <div class="results-page-container container" style="max-width: 1150px; margin: 0 auto; padding: 1.5rem 1rem 3.5rem;">
      
      <!-- Top Civic Reassurance & Context Notification -->
      <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-xl); padding: 1rem 1.25rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm); display: flex; flex-direction: column; md:flex-row; justify-content: space-between; align-items: flex-start; md:align-items: center; gap: 0.75rem;">
        <div style="display: flex; align-items: flex-start; gap: 0.65rem;">
          <div style="width: 32px; height: 32px; border-radius: 9999px; background: rgba(217, 119, 6, 0.12); display: flex; align-items: center; justify-content: center; color: var(--secondary-saffron); flex-shrink: 0; margin-top: 2px;">
            <span class="material-symbols-outlined" style="font-size: 18px;">verified_user</span>
          </div>
          <div>
            <p style="font-size: 0.9rem; font-weight: 700; color: var(--primary-indigo); margin: 0;">
              ${t.resultsNoticeTitle || "These schemes may be relevant based on what you shared."}
            </p>
            <p style="font-size: 0.82rem; color: var(--text-secondary); margin: 0.15rem 0 0; line-height: 1.4;">
              ${t.resultsNoticeDesc || "Official departments determine actual eligibility and approval. Always verify with official departments before applying."}
            </p>
          </div>
        </div>

        <div style="display: flex; align-items: center; gap: 0.35rem; background: var(--bg-canvas); padding: 0.35rem 0.75rem; border-radius: 9999px; border: 1px solid var(--border-color); font-size: 0.78rem; color: var(--text-secondary); white-space: nowrap; align-self: flex-end; md:align-self: auto;">
          <span class="material-symbols-outlined" style="font-size: 15px; color: var(--secondary-saffron);">privacy_tip</span>
          <span>${t.zeroLogsBadge || "Zero personal identity logs"}</span>
        </div>
      </div>

      <!-- Primary Header & Discovery Counter Capsule -->
      <div style="display: flex; flex-direction: column; md:flex-row; justify-content: space-between; align-items: flex-start; md:align-items: flex-end; gap: 1rem; margin-bottom: 1.5rem;">
        <div>
          <div style="display: flex; align-items: center; gap: 0.35rem; color: var(--secondary-saffron); font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">
            <span class="material-symbols-outlined" style="font-size: 18px;">route</span>
            <span>${t.pathwaysEngineSubtitle || "Namma Pathways Discovery Engine"}</span>
          </div>
          <h1 style="font-size: 2rem; font-weight: 800; color: var(--primary-indigo); margin: 0; line-height: 1.2;">
            ${t.resultsTitle}
          </h1>
        </div>

        <!-- Discovery Counter Stat Capsule -->
        <div style="display: flex; align-items: center; gap: 0.85rem; background: #ffffff; padding: 0.5rem 1rem; border-radius: var(--radius-xl); border: 1px solid var(--border-color); box-shadow: var(--shadow-sm);">
          <div style="display: flex; align-items: center; gap: 0.4rem;">
            <span style="width: 8px; height: 8px; border-radius: 9999px; background: var(--tertiary-green); display: inline-block;"></span>
            <span style="font-size: 0.88rem; font-weight: 700; color: var(--primary-indigo);">
              ${filtered.length} ${t.optionsFound || "Potential Options Found"}
            </span>
          </div>
          <div style="width: 1px; height: 18px; background: var(--border-color);"></div>
          <button type="button" onclick="window.print()" style="background: none; border: none; display: flex; align-items: center; gap: 0.35rem; font-size: 0.82rem; color: var(--text-secondary); cursor: pointer; padding: 0;">
            <span class="material-symbols-outlined" style="font-size: 16px;">print</span>
            <span>${t.savePdfBtn || "Save PDF"}</span>
          </button>
        </div>
      </div>

      <!-- Interactive Search Persona Strip -->
      <div style="background: var(--bg-canvas); border: 1px solid var(--border-color); border-radius: var(--radius-xl); padding: 0.85rem 1.25rem; margin-bottom: 1.5rem; display: flex; flex-direction: column; sm:flex-row; justify-content: space-between; align-items: flex-start; sm:align-items: center; gap: 0.75rem;">
        <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
          <span style="font-size: 0.76rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary);">
            ${t.showingForLabel || "Showing for:"}
          </span>
          <span style="background: #ffffff; border: 1px solid var(--border-color); padding: 0.2rem 0.65rem; border-radius: 6px; font-size: 0.82rem; font-weight: 600; color: var(--primary-indigo);">
            🎓 ${t.tnCitizensPill || "Tamil Nadu Citizens"}
          </span>
          <span style="color: var(--border-color);">•</span>
          <span style="background: #ffffff; border: 1px solid var(--border-color); padding: 0.2rem 0.65rem; border-radius: 6px; font-size: 0.82rem; font-weight: 600; color: var(--primary-indigo);">
            💰 ${t.incomeEligiblePill || "Income Eligible"}
          </span>
          <span style="color: var(--border-color);">•</span>
          <span style="background: #ffffff; border: 1px solid var(--border-color); padding: 0.2rem 0.65rem; border-radius: 6px; font-size: 0.82rem; font-weight: 600; color: var(--primary-indigo);">
            🏛️ ${t.stateGuidelinesPill || "Published State Guidelines"}
          </span>
          ${state.lastAssistantQuery ? `
            <span style="background: rgba(217, 119, 6, 0.12); border: 1px solid rgba(217, 119, 6, 0.3); padding: 0.2rem 0.65rem; border-radius: 6px; font-size: 0.82rem; font-weight: 600; color: #9a3412;">
              🔍 "${state.lastAssistantQuery}"
            </span>
            <button id="clear-assistant-filter-btn" style="background: none; border: none; font-size: 0.78rem; color: #9a3412; cursor: pointer; text-decoration: underline;">
              ${t.showAllLink || "Show All"}
            </button>
          ` : ''}
        </div>

        <a href="#assistant" class="btn btn-outline btn-sm" style="padding: 0.35rem 0.85rem; font-size: 0.82rem; display: flex; align-items: center; gap: 0.35rem; align-self: flex-start; sm:align-self: auto;">
          <span class="material-symbols-outlined" style="font-size: 15px;">tune</span>
          <span>${t.editDetailsBtn || "Edit details"}</span>
        </a>
      </div>

      <!-- Filter Search & Category Ribbon -->
      <div style="margin-bottom: 1.5rem; display: flex; flex-direction: column; gap: 0.85rem;">
        <!-- Search Toolbar -->
        <div style="display: flex; gap: 0.5rem; align-items: center;">
          <div style="position: relative; flex: 1;">
            <span class="material-symbols-outlined" style="position: absolute; left: 0.85rem; top: 50%; transform: translateY(-50%); font-size: 20px; color: var(--text-secondary);">search</span>
            <input
              type="text"
              id="scheme-search-input"
              class="search-input"
              placeholder="${t.searchPlaceholder}"
              value="${state.searchQuery || ''}"
              style="width: 100%; padding: 0.65rem 0.85rem 0.65rem 2.5rem; border-radius: var(--radius-xl); border: 1.5px solid var(--border-color); background: #ffffff; font-size: 0.92rem; color: var(--text-primary);"
            />
          </div>
          ${state.searchQuery ? `
            <button class="btn btn-outline" id="clear-search-btn" style="padding: 0.6rem 0.85rem;">
              ✕
            </button>
          ` : ''}
        </div>

        <!-- Filter & Segment Ribbon -->
        <div style="display: flex; align-items: center; gap: 0.5rem; overflow-x: auto; padding-bottom: 0.35rem; scrollbar-width: none;">
          <button class="category-pill ${currentCategory === 'all' ? 'active' : ''}" data-cat="all" style="padding: 0.45rem 1rem; border-radius: 9999px; font-size: 0.84rem; font-weight: 600; cursor: pointer; white-space: nowrap; display: flex; align-items: center; gap: 0.4rem;">
            <span>${t.filterAll}</span>
            <span style="font-size: 0.72rem; padding: 0.1rem 0.45rem; border-radius: 9999px; background: rgba(0,0,0,0.08); font-weight: 700;">${counts.all || 0}</span>
          </button>

          <button class="category-pill ${currentCategory === 'education' ? 'active' : ''}" data-cat="education" style="padding: 0.45rem 1rem; border-radius: 9999px; font-size: 0.84rem; font-weight: 600; cursor: pointer; white-space: nowrap; display: flex; align-items: center; gap: 0.4rem;">
            <span>🎓 ${t.filterEducation}</span>
            <span style="font-size: 0.72rem; padding: 0.1rem 0.45rem; border-radius: 9999px; background: rgba(0,0,0,0.08); font-weight: 700;">${counts.education || 0}</span>
          </button>

          <button class="category-pill ${currentCategory === 'women' ? 'active' : ''}" data-cat="women" style="padding: 0.45rem 1rem; border-radius: 9999px; font-size: 0.84rem; font-weight: 600; cursor: pointer; white-space: nowrap; display: flex; align-items: center; gap: 0.4rem;">
            <span>👩 ${t.filterWomen}</span>
            <span style="font-size: 0.72rem; padding: 0.1rem 0.45rem; border-radius: 9999px; background: rgba(0,0,0,0.08); font-weight: 700;">${counts.women || 0}</span>
          </button>

          <button class="category-pill ${currentCategory === 'agriculture' ? 'active' : ''}" data-cat="agriculture" style="padding: 0.45rem 1rem; border-radius: 9999px; font-size: 0.84rem; font-weight: 600; cursor: pointer; white-space: nowrap; display: flex; align-items: center; gap: 0.4rem;">
            <span>🌾 ${t.filterAgri}</span>
            <span style="font-size: 0.72rem; padding: 0.1rem 0.45rem; border-radius: 9999px; background: rgba(0,0,0,0.08); font-weight: 700;">${counts.agriculture || 0}</span>
          </button>

          <button class="category-pill ${currentCategory === 'health' ? 'active' : ''}" data-cat="health" style="padding: 0.45rem 1rem; border-radius: 9999px; font-size: 0.84rem; font-weight: 600; cursor: pointer; white-space: nowrap; display: flex; align-items: center; gap: 0.4rem;">
            <span>🏥 ${t.filterHealth}</span>
            <span style="font-size: 0.72rem; padding: 0.1rem 0.45rem; border-radius: 9999px; background: rgba(0,0,0,0.08); font-weight: 700;">${counts.health || 0}</span>
          </button>

          <button class="category-pill ${currentCategory === 'employment' ? 'active' : ''}" data-cat="employment" style="padding: 0.45rem 1rem; border-radius: 9999px; font-size: 0.84rem; font-weight: 600; cursor: pointer; white-space: nowrap; display: flex; align-items: center; gap: 0.4rem;">
            <span>💼 ${t.filterEmployment}</span>
            <span style="font-size: 0.72rem; padding: 0.1rem 0.45rem; border-radius: 9999px; background: rgba(0,0,0,0.08); font-weight: 700;">${counts.employment || 0}</span>
          </button>

          <button class="category-pill ${currentCategory === 'business' ? 'active' : ''}" data-cat="business" style="padding: 0.45rem 1rem; border-radius: 9999px; font-size: 0.84rem; font-weight: 600; cursor: pointer; white-space: nowrap; display: flex; align-items: center; gap: 0.4rem;">
            <span>🏪 ${t.categoryBusiness || "Business & MSME"}</span>
            <span style="font-size: 0.72rem; padding: 0.1rem 0.45rem; border-radius: 9999px; background: rgba(0,0,0,0.08); font-weight: 700;">${counts.business || 0}</span>
          </button>

          <button class="category-pill ${currentCategory === 'seniors' ? 'active' : ''}" data-cat="seniors" style="padding: 0.45rem 1rem; border-radius: 9999px; font-size: 0.84rem; font-weight: 600; cursor: pointer; white-space: nowrap; display: flex; align-items: center; gap: 0.4rem;">
            <span>👵 ${t.filterSeniors}</span>
            <span style="font-size: 0.72rem; padding: 0.1rem 0.45rem; border-radius: 9999px; background: rgba(0,0,0,0.08); font-weight: 700;">${counts.seniors || 0}</span>
          </button>

          <button class="category-pill ${currentCategory === 'disability' ? 'active' : ''}" data-cat="disability" style="padding: 0.45rem 1rem; border-radius: 9999px; font-size: 0.84rem; font-weight: 600; cursor: pointer; white-space: nowrap; display: flex; align-items: center; gap: 0.4rem;">
            <span>♿ ${t.filterDisability}</span>
            <span style="font-size: 0.72rem; padding: 0.1rem 0.45rem; border-radius: 9999px; background: rgba(0,0,0,0.08); font-weight: 700;">${counts.disability || 0}</span>
          </button>
        </div>
      </div>

      <!-- Schemes Cards Stack -->
      ${filtered.length === 0 ? `
        <div style="text-align: center; padding: 3.5rem 1.5rem; background: #ffffff; border-radius: var(--radius-xl); border: 1px dashed var(--border-color); box-shadow: var(--shadow-sm);">
          <div style="font-size: 2.8rem; margin-bottom: 0.75rem;">📋</div>
          <h3 style="color: var(--primary-indigo); font-size: 1.25rem; font-weight: 700; margin-bottom: 0.5rem;">
            ${t.noResultsFound}
          </h3>
          <p style="color: var(--text-secondary); font-size: 0.9rem; max-width: 480px; margin: 0 auto 1.25rem;">
            ${t.resetFiltersNotice || "Try searching for a different keyword or reset active filters."}
          </p>
          <button class="btn btn-primary" id="reset-results-filters-btn" style="padding: 0.5rem 1.25rem;">
            ${t.resetFilters}
          </button>
        </div>
      ` : `
        <div style="display: flex; flex-direction: column; gap: 1.5rem;">
          ${filtered.map(scheme => renderStitchSchemeArticle(scheme, state, matchedMap[scheme.id])).join('')}
        </div>
      `}
    </div>
  `;
}

function renderStitchSchemeArticle(scheme, state, matchInfo) {
  const t = i18n[state.lang] || i18n.ta;
  const hasScore = matchInfo && (matchInfo.score || matchInfo.match_confidence);
  const confidence = hasScore ? (matchInfo.match_confidence || Math.round(matchInfo.score * 100)) : 85;
  const isStrong = confidence >= 80;

  const loc = getLocalizedScheme(scheme, state.lang);
  const name = loc.displayName || scheme.name;
  const subName = (state.lang === 'ta' || state.lang === 'tanglish') ? scheme.name : (scheme.name_ta || '');
  const criteria = loc.displayCriteria || [];
  const docs = loc.displayDocuments || [];
  const dept = loc.displayDepartment || scheme.department;
  const benefit = loc.displayBenefit || scheme.benefit_summary;
  const desc = loc.displayDescription || scheme.description;
  const summaryForTts = `${name}. ${benefit}. ${dept}.`;

  return `
    <article style="background: #ffffff; border-radius: var(--radius-xl); border: 1px solid var(--border-color); box-shadow: var(--shadow-sm); padding: 1.5rem; position: relative; overflow: hidden; transition: box-shadow 0.2s ease;">
      <!-- Top Accent Bar: High contrast Leaf Green or Warm Saffron -->
      <div style="position: absolute; top: 0; left: 0; right: 0; height: 5px; background: ${isStrong ? 'var(--tertiary-green)' : 'var(--secondary-saffron)'};"></div>

      <!-- Header Row -->
      <div style="display: flex; flex-direction: column; md:flex-row; justify-content: space-between; align-items: flex-start; gap: 1rem; margin-bottom: 1rem; margin-top: 0.25rem;">
        <div style="flex: 1;">
          <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.4rem;">
            <!-- Confidence Pill -->
            <span style="display: inline-flex; align-items: center; gap: 0.35rem; padding: 0.25rem 0.75rem; border-radius: 9999px; background: ${isStrong ? 'rgba(21, 128, 61, 0.12)' : 'rgba(217, 119, 6, 0.12)'}; color: ${isStrong ? 'var(--tertiary-green)' : 'var(--secondary-saffron)'}; font-size: 0.8rem; font-weight: 700;">
              <span class="material-symbols-outlined" style="font-size: 16px;">${isStrong ? 'check_circle' : 'help_outline'}</span>
              <span>${isStrong ? (t.strongMatchBadge || "Strong potential match") : (t.worthCheckingBadge || "Worth checking")}</span>
            </span>

            <span style="padding: 0.2rem 0.65rem; border-radius: 9999px; background: var(--bg-canvas); border: 1px solid var(--border-color); font-size: 0.76rem; color: var(--text-secondary); text-transform: capitalize;">
              ${scheme.category} · ${scheme.coverage_type || (['pm-', 'pmegp', 'nsp-'].some(k => (scheme.id || '').includes(k)) ? (t.coverageCentral || 'Central Government') : (t.coverageState || 'Tamil Nadu State Government'))}
            </span>
          </div>

          <h2 style="font-size: 1.35rem; font-weight: 800; color: var(--primary-indigo); margin: 0 0 0.25rem; line-height: 1.3;">
            ${name}
          </h2>
          ${subName ? `
            <p style="font-size: 0.95rem; color: var(--secondary-saffron); font-style: italic; margin: 0; font-weight: 600;">
              ${subName}
            </p>
          ` : ''}
        </div>

        <!-- Criteria Alignment Tag -->
        <div style="background: var(--bg-canvas); border: 1px solid var(--border-color); padding: 0.45rem 0.85rem; border-radius: var(--radius-lg); display: flex; align-items: center; gap: 0.5rem; flex-shrink: 0;">
          <div>
            <span style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); display: block; font-weight: 600;">Criteria Alignment</span>
            <span style="font-size: 0.95rem; font-weight: 800; color: ${isStrong ? 'var(--tertiary-green)' : 'var(--secondary-saffron)'};">
              ${isStrong ? (t.eligibilityHigh || '100% Matched') : (t.eligibilityModerate || 'Verification Needed')}
            </span>
          </div>
          <span class="material-symbols-outlined" style="font-size: 22px; color: ${isStrong ? 'var(--tertiary-green)' : 'var(--secondary-saffron)'};">
            ${isStrong ? 'task_alt' : 'pending'}
          </span>
        </div>
      </div>

      <!-- Benefit Summary Paragraph -->
      <p style="font-size: 0.95rem; color: var(--text-primary); line-height: 1.6; margin: 0 0 1.25rem;">
        ${desc}
      </p>

      <!-- Transparent Breakdown Grid -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; margin-bottom: 1.25rem;">
        <!-- Why it matches -->
        <div style="background: var(--bg-canvas); padding: 1rem; border-radius: var(--radius-lg); border: 1px solid var(--border-color);">
          <div style="display: flex; align-items: center; gap: 0.4rem; color: var(--primary-indigo); font-weight: 700; font-size: 0.88rem; margin-bottom: 0.65rem;">
            <span class="material-symbols-outlined" style="font-size: 18px; color: var(--secondary-saffron);">psychology_alt</span>
            <span>${t.whyMatched || "Why it may match your situation"}</span>
          </div>
          <ul style="margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 0.45rem; font-size: 0.84rem; color: var(--text-primary);">
            ${criteria.slice(0, 3).map(c => `
              <li style="display: flex; align-items: flex-start; gap: 0.4rem;">
                <span class="material-symbols-outlined" style="font-size: 16px; color: var(--tertiary-green); flex-shrink: 0; margin-top: 1px;">check_circle</span>
                <span>${typeof c === 'string' ? c : (c.criterion || c.name || '')}</span>
              </li>
            `).join('')}
          </ul>
        </div>

        <!-- Metadata & Issuing Body -->
        <div style="background: var(--bg-canvas); padding: 1rem; border-radius: var(--radius-lg); border: 1px solid var(--border-color); display: flex; flex-direction: column; justify-content: space-between; gap: 0.65rem;">
          <div>
            <div style="display: flex; align-items: center; gap: 0.4rem; font-size: 0.82rem; color: var(--primary-indigo); font-weight: 600; margin-bottom: 0.35rem;">
              <span class="material-symbols-outlined" style="font-size: 16px; color: var(--secondary-saffron);">event_available</span>
              <span>Open for Academic &amp; Financial Year 2024–25</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.4rem; font-size: 0.82rem; color: var(--text-secondary);">
              <span class="material-symbols-outlined" style="font-size: 16px; color: var(--text-secondary);">description</span>
              <span>${docs.length > 0 ? docs.length + " " + (t.requiredDocsPreview || "core documents typically required") : (t.requiredDocsPreview || "Basic identity documents required")}</span>
            </div>
          </div>
          <div style="border-top: 1px solid var(--border-color); padding-top: 0.5rem; font-size: 0.78rem;">
            <span style="color: var(--text-secondary); display: block;">${t.departmentLabel || "Primary Issuing Body"}:</span>
            <strong style="color: var(--primary-indigo); font-size: 0.84rem;">${dept}</strong>
          </div>
        </div>
      </div>

      <!-- Action Footer -->
      <div style="display: flex; flex-direction: column; sm:flex-row; justify-content: space-between; align-items: stretch; sm:align-items: center; gap: 0.75rem; pt: 0.5rem; border-top: 1px solid var(--border-color);">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <button class="tts-listen-btn btn btn-outline btn-sm" data-tts-text="${encodeURIComponent(summaryForTts)}" type="button" title="Listen to summary" style="padding: 0.35rem 0.75rem; font-size: 0.8rem; display: flex; align-items: center; gap: 0.35rem;">
            <span class="material-symbols-outlined" style="font-size: 16px; color: var(--secondary-saffron);">volume_up</span>
            <span>${t.listenAudioSummary || t.listenAudio || "Listen"}</span>
          </button>
          <span style="font-size: 0.76rem; color: var(--text-secondary); display: none; sm:inline;">${t.voicePreviewBadge || "Spoken guide"}</span>
        </div>

        <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
          ${(scheme.application_url || scheme.official_portal || scheme.portal_url) ? `
            <a href="${scheme.application_url || scheme.official_portal || scheme.portal_url}" target="_blank" rel="noopener" class="btn btn-outline btn-sm" style="padding: 0.4rem 0.85rem; font-size: 0.82rem; display: flex; align-items: center; gap: 0.35rem;" title="Official Government Portal">
              <span class="material-symbols-outlined" style="font-size: 15px; color: var(--secondary-saffron);">open_in_new</span>
              <span>${t.officialApplyBtn || "Apply (Official)"}</span>
            </a>
          ` : ''}
          <a href="#checklist" class="btn btn-outline btn-sm" style="padding: 0.4rem 0.85rem; font-size: 0.82rem; display: flex; align-items: center; gap: 0.35rem;">
            <span class="material-symbols-outlined" style="font-size: 16px;">bookmark_add</span>
            <span>${t.addToChecklistBtn || "Save to Checklist"}</span>
          </a>
          <a href="#scheme-details/${scheme.id}" class="btn btn-primary btn-sm" style="padding: 0.4rem 1.15rem; font-size: 0.84rem; display: flex; align-items: center; gap: 0.35rem;">
            <span>${t.viewDetails}</span>
            <span class="material-symbols-outlined" style="font-size: 16px;">arrow_forward</span>
          </a>
        </div>
      </div>
    </article>
  `;
}
