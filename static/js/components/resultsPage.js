// NammaSevai AI - Scheme Results Page Component
import { i18n } from '../i18n.js';

export function renderResultsPage(state) {
  const t = i18n[state.lang] || i18n.ta;
  const currentCategory = state.selectedCategory || 'all';
  const searchQuery = (state.searchQuery || '').toLowerCase();
  const allSchemes = state.schemes || [];
  const matchedMap = state.lastMatchedMap || {}; // contains scores and reasons if from assistant query

  // Filter schemes
  const filtered = allSchemes.filter(scheme => {
    // Category match
    if (currentCategory !== 'all' && scheme.category !== currentCategory) {
      return false;
    }
    // Search query match
    if (searchQuery.trim().length > 0) {
      const matchInName = (scheme.name + " " + scheme.name_ta).toLowerCase().includes(searchQuery);
      const matchInDept = (scheme.department + " " + scheme.department_ta).toLowerCase().includes(searchQuery);
      const matchInDesc = (scheme.description + " " + scheme.description_ta).toLowerCase().includes(searchQuery);
      const matchInKw = scheme.keywords && scheme.keywords.some(k => k.toLowerCase().includes(searchQuery));
      if (!matchInName && !matchInDept && !matchInDesc && !matchInKw) {
        return false;
      }
    }
    return true;
  });

  return `
    <div class="results-page-container container">
      <!-- Results Header Banner -->
      <div class="results-header-banner">
        <span class="badge badge-teal" style="background: rgba(255,255,255,0.18); color: white; margin-bottom: 0.85rem;">
          Welfare Schemes Catalog | நலத்திட்டங்கள் தகவல் களஞ்சியம்
        </span>
        <h1>${t.resultsTitle}</h1>
        <p>${t.resultsSubtitle}</p>
        ${state.lastAssistantQuery ? `
          <div style="margin-top: 1rem; background: rgba(255,255,255,0.12); padding: 0.65rem 1rem; border-radius: var(--radius-sm); font-size: 0.88rem; display: inline-flex; align-items: center; gap: 0.5rem;">
            <span>🔍 அண்மைய கேள்வி: "<strong>${state.lastAssistantQuery}</strong>"</span>
            <button id="clear-assistant-filter-btn" class="btn btn-outline btn-sm" style="background: transparent; color: white; border-color: rgba(255,255,255,0.3); padding: 0.2rem 0.6rem; font-size: 0.76rem;">அனைத்தையும் காட்டு</button>
          </div>
        ` : ''}
      </div>

      <!-- Filters & Search Toolbar -->
      <div class="filter-toolbar">
        <div class="filter-search-row">
          <div class="search-input-wrap">
            <span class="search-icon-inside">🔍</span>
            <input
              type="text"
              id="scheme-search-input"
              class="search-input"
              placeholder="${t.searchPlaceholder}"
              value="${state.searchQuery || ''}"
            />
          </div>
          ${state.searchQuery ? `
            <button class="btn btn-outline btn-sm" id="clear-search-btn">
              ✕
            </button>
          ` : ''}
        </div>

        <!-- Category Pills -->
        <div class="filter-category-pills">
          <span style="font-size: 0.82rem; font-weight: 700; color: var(--primary-navy); margin-right: 0.25rem;">
            ${t.filterCategory}
          </span>
          <button class="category-pill ${currentCategory === 'all' ? 'active' : ''}" data-cat="all">
            ${t.filterAll}
          </button>
          <button class="category-pill ${currentCategory === 'education' ? 'active' : ''}" data-cat="education">
            🎓 ${t.filterEducation}
          </button>
          <button class="category-pill ${currentCategory === 'women' ? 'active' : ''}" data-cat="women">
            👩 ${t.filterWomen}
          </button>
          <button class="category-pill ${currentCategory === 'agriculture' ? 'active' : ''}" data-cat="agriculture">
            🌾 ${t.filterAgri}
          </button>
          <button class="category-pill ${currentCategory === 'health' ? 'active' : ''}" data-cat="health">
            🏥 ${t.filterHealth}
          </button>
          <button class="category-pill ${currentCategory === 'employment' ? 'active' : ''}" data-cat="employment">
            💼 ${t.filterEmployment}
          </button>
          <button class="category-pill ${currentCategory === 'seniors' ? 'active' : ''}" data-cat="seniors">
            👴 ${t.filterSeniors}
          </button>
          <button class="category-pill ${currentCategory === 'disability' ? 'active' : ''}" data-cat="disability">
            ♿ ${t.filterDisability}
          </button>
          <button class="category-pill ${currentCategory === 'housing' ? 'active' : ''}" data-cat="housing">
            🏠 ${t.filterHousing}
          </button>
        </div>
      </div>

      <!-- Schemes Cards Grid -->
      ${filtered.length === 0 ? `
        <div style="text-align: center; padding: 4rem 2rem; background: var(--bg-surface); border-radius: var(--radius-lg); border: 1px dashed var(--border-color);">
          <div style="font-size: 3rem; margin-bottom: 0.75rem;">📋</div>
          <h3 style="color: var(--primary-navy); margin-bottom: 0.5rem;">${t.noResultsFound}</h3>
          <button class="btn btn-primary" id="reset-results-filters-btn" style="margin-top: 1rem;">
            ${t.resetFilters}
          </button>
        </div>
      ` : `
        <div style="margin-bottom: 1rem; font-size: 0.88rem; color: var(--text-light); font-weight: 600;">
          ${filtered.length} நலத்திட்டங்கள் காட்டப்படுகின்றன (Showing ${filtered.length} schemes)
        </div>
        <div class="schemes-grid">
          ${filtered.map(scheme => renderSchemeCard(scheme, state, matchedMap[scheme.id])).join('')}
        </div>
      `}
    </div>
  `;
}

function renderSchemeCard(scheme, state, matchInfo) {
  const t = i18n[state.lang] || i18n.ta;
  const isTa = state.lang === 'ta';

  // Determine match badge
  let matchBadgeHtml = '';
  if (matchInfo) {
    if (matchInfo.status === 'high') {
      matchBadgeHtml = `<span class="badge badge-green">${matchInfo.matchPercent}% Match | ${t.eligibilityHigh}</span>`;
    } else if (matchInfo.status === 'moderate') {
      matchBadgeHtml = `<span class="badge badge-teal">${matchInfo.matchPercent}% Match | ${t.eligibilityModerate}</span>`;
    } else {
      matchBadgeHtml = `<span class="badge badge-saffron">${t.eligibilityCheck}</span>`;
    }
  } else {
    matchBadgeHtml = `<span class="badge badge-navy">${scheme.category.toUpperCase()}</span>`;
  }

  // Reason text
  const reasonText = matchInfo ? (isTa ? matchInfo.reasonTa : matchInfo.reasonEn) : null;
  const portalUrl = scheme.official_portal || scheme.portal_url || (scheme.source ? scheme.source.portal_url : 'https://www.tn.gov.in');
  const docsList = scheme.required_documents || (scheme.documents ? scheme.documents.map(d => ({ name: d.name_en, name_ta: d.name_ta })) : []);

  return `
    <div class="scheme-card" data-scheme-id="${scheme.id}">
      <div class="scheme-card-top">
        <div class="scheme-card-tags">
          ${matchBadgeHtml}
          <span class="badge badge-teal" style="font-size: 0.72rem;">
            ✓ ${scheme.source_verification === 'verified' ? 'அரசு தளம்' : 'சரிபார்க்கப்பட்டது'}
          </span>
        </div>

        <h3 class="scheme-card-title">
          ${isTa ? scheme.name_ta : scheme.name}
        </h3>
        <div class="scheme-dept-label">
          🏛️ ${isTa ? scheme.department_ta : scheme.department}
        </div>

        <!-- Key Benefit Box -->
        <div class="scheme-benefit-badge-box">
          <div class="benefit-amount-text">💰 ${scheme.benefit_amount}</div>
          <div class="benefit-summary-text">${isTa ? scheme.benefit_summary_ta : scheme.benefit_summary}</div>
        </div>

        <!-- Why this matches reason box -->
        ${reasonText ? `
          <div class="scheme-match-reason-box">
            <strong>🎯 ${t.whyMatched}</strong> ${reasonText}
          </div>
        ` : ''}

        <!-- Required Documents Preview -->
        <div style="margin-top: 0.35rem;">
          <div style="font-size: 0.78rem; font-weight: 700; color: var(--text-light); margin-bottom: 0.35rem;">
            📄 ${t.requiredDocsPreview}
          </div>
          <div class="scheme-docs-preview-row">
            ${docsList.slice(0, 3).map(doc => `
              <span class="doc-pill">${isTa ? (doc.name_ta || doc.name) : (doc.name || doc.name_en)}</span>
            `).join('')}
            ${docsList.length > 3 ? `
              <span class="doc-pill" style="color: var(--primary-teal-dark);">+${docsList.length - 3} மேலும்</span>
            ` : ''}
          </div>
        </div>
      </div>

      <div class="scheme-card-actions">
        <a href="#scheme-details/${scheme.id}" class="btn btn-primary btn-sm" style="flex: 1;">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>
          <span>${t.viewDetails}</span>
        </a>
        <a href="${portalUrl}" target="_blank" rel="noopener" class="btn btn-outline btn-sm" title="Open official portal">
          <span>${t.officialPortal} ↗</span>
        </a>
      </div>
    </div>
  `;
}
