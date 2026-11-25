// NammaSevai AI / BharatSevai AI - National Scheme Discovery Results Page Component
import { i18n } from '../i18n.js';
import { getLocalizedScheme, INDIAN_STATES, INDIAN_UNION_TERRITORIES, GOVERNMENT_LEVELS } from '../schemesData.js';

export function renderResultsPage(state) {
  const t = i18n[state.lang] || i18n.ta;
  const currentCategory = state.selectedCategory || 'all';
  const currentLevel = state.selectedLevel || 'all';
  const currentState = state.selectedState || 'all';
  const currentBeneficiary = state.selectedBeneficiary || 'all';
  const currentSort = state.selectedSort || 'name';
  const searchQuery = (state.searchQuery || '').toLowerCase().trim();
  const allSchemes = state.schemes || [];
  const matchedMap = state.lastMatchedMap || {};

  // National Filter Pipeline
  let filtered = allSchemes.filter(scheme => {
    // 1. Level Filter
    if (currentLevel !== 'all') {
      const sLevel = scheme.level || (['pm-', 'pmegp', 'nsp-', 'ayushman', 'pmay'].some(k => (scheme.id || '').toLowerCase().includes(k)) ? 'Central' : 'State');
      if (sLevel.toLowerCase() !== currentLevel.toLowerCase()) return false;
    }

    // 2. Geographical Jurisdiction Filter
    if (currentState !== 'all') {
      const sLevel = scheme.level || 'State';
      const sState = (scheme.state || (sLevel === 'Central' ? 'All India' : 'Tamil Nadu')).toLowerCase();
      const targetState = currentState.toLowerCase();

      if (targetState === 'all india' || targetState === 'central') {
        if (sLevel.toLowerCase() !== 'central') return false;
      } else {
        // A citizen selecting State X can view State X schemes AND national Central schemes
        const isTargetState = sState === targetState;
        const isCentral = sLevel.toLowerCase() === 'central' || sState === 'all india';
        if (!isTargetState && !isCentral) return false;
      }
    }

    // 3. Category Filter
    if (currentCategory !== 'all' && scheme.category !== currentCategory) {
      return false;
    }

    // 4. Beneficiary Group Filter
    if (currentBeneficiary !== 'all') {
      const benText = ((scheme.beneficiary_type || '') + " " + (scheme.target_beneficiaries || '') + " " + (scheme.keywords || '')).toLowerCase();
      if (!benText.includes(currentBeneficiary.toLowerCase())) return false;
    }

    // 5. Multi-Lingual Full Text Search Filter
    if (searchQuery.length > 0) {
      const matchInName = (scheme.name + " " + (scheme.name_ta || '') + " " + (scheme.name_hi || '') + " " + (scheme.name_ml || '')).toLowerCase().includes(searchQuery);
      const matchInDept = (scheme.department + " " + (scheme.department_ta || '') + " " + (scheme.department_hi || '') + " " + (scheme.department_ml || '')).toLowerCase().includes(searchQuery);
      const matchInDesc = (scheme.description + " " + (scheme.description_ta || '') + " " + (scheme.description_hi || '') + " " + (scheme.description_ml || '')).toLowerCase().includes(searchQuery);
      const matchInState = (scheme.state || '').toLowerCase().includes(searchQuery);
      const matchInLevel = (scheme.level || '').toLowerCase().includes(searchQuery);
      const matchInKw = scheme.keywords && (typeof scheme.keywords === 'string' ? scheme.keywords.toLowerCase().includes(searchQuery) : scheme.keywords.some(k => k.toLowerCase().includes(searchQuery)));
      if (!matchInName && !matchInDept && !matchInDesc && !matchInState && !matchInLevel && !matchInKw) {
        return false;
      }
    }

    return true;
  });

  // Sorting
  filtered.sort((a, b) => {
    if (currentSort === 'state') {
      return (a.state || 'All India').localeCompare(b.state || 'All India');
    } else if (currentSort === 'level') {
      return (a.level || 'State').localeCompare(b.level || 'State');
    } else if (currentSort === 'category') {
      return (a.category || '').localeCompare(b.category || '');
    }
    return (a.name || '').localeCompare(b.name || '');
  });

  // Calculate dynamic category counts
  const counts = { all: allSchemes.length };
  allSchemes.forEach(s => {
    counts[s.category] = (counts[s.category] || 0) + 1;
  });

  // Coverage statistics for honest transparency badge
  const centralCount = allSchemes.filter(s => (s.level || '').toLowerCase() === 'central' || ['pm-', 'pmegp', 'nsp-'].some(k => (s.id || '').includes(k))).length;
  const stateCount = allSchemes.filter(s => (s.level || '').toLowerCase() === 'state').length;
  const utCount = allSchemes.filter(s => (s.level || '').toLowerCase() === 'union territory').length;
  const uniqueJurisdictions = new Set(allSchemes.map(s => s.state).filter(Boolean)).size;

  return `
    <div class="results-page-container container" style="max-width: 1150px; margin: 0 auto; padding: 1.5rem 1rem 3.5rem;">
      
      <!-- Top Civic Reassurance & Context Notification -->
      <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-xl); padding: 1rem 1.25rem; margin-bottom: 1.25rem; box-shadow: var(--shadow-sm); display: flex; flex-direction: column; md:flex-row; justify-content: space-between; align-items: flex-start; md:align-items: center; gap: 0.75rem;">
        <div style="display: flex; align-items: flex-start; gap: 0.65rem;">
          <div style="width: 34px; height: 34px; border-radius: 9999px; background: rgba(217, 119, 6, 0.12); display: flex; align-items: center; justify-content: center; color: var(--secondary-saffron); flex-shrink: 0; margin-top: 2px;">
            <span class="material-symbols-outlined" style="font-size: 20px;">verified_user</span>
          </div>
          <div>
            <p style="font-size: 0.92rem; font-weight: 700; color: var(--primary-indigo); margin: 0;">
              ${t.resultsNoticeTitle || "All-India Scheme Discovery & Verification Engine"}
            </p>
            <p style="font-size: 0.82rem; color: var(--text-secondary); margin: 0.15rem 0 0; line-height: 1.4;">
              ${t.resultsNoticeDesc || "Covering Central Government, 28 States & 8 Union Territories. Results are guidance for discovery; final eligibility is determined by the responsible government department."}
            </p>
          </div>
        </div>

        <div style="display: flex; align-items: center; gap: 0.45rem; background: var(--bg-canvas); padding: 0.35rem 0.8rem; border-radius: 9999px; border: 1px solid var(--border-color); font-size: 0.78rem; color: var(--text-secondary); white-space: nowrap; align-self: flex-end; md:align-self: auto;">
          <span class="material-symbols-outlined" style="font-size: 16px; color: var(--tertiary-green);">lock</span>
          <span>${t.zeroLogsBadge || "Zero personal identity logs"}</span>
        </div>
      </div>

      <!-- National Coverage & Scope Transparency Ribbon -->
      <div style="background: linear-gradient(135deg, rgba(21, 35, 62, 0.04), rgba(217, 119, 6, 0.06)); border: 1px solid var(--border-color); border-radius: var(--radius-xl); padding: 0.85rem 1.25rem; margin-bottom: 1.5rem; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 0.75rem;">
        <div style="display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;">
          <span style="font-size: 0.8rem; font-weight: 700; color: var(--primary-indigo); display: flex; align-items: center; gap: 0.35rem;">
            <span class="material-symbols-outlined" style="font-size: 18px; color: var(--secondary-saffron);">public</span>
            <span>National Scope:</span>
          </span>
          <span style="font-size: 0.78rem; background: #ffffff; padding: 0.2rem 0.65rem; border-radius: 9999px; border: 1px solid var(--border-color); font-weight: 600; color: var(--primary-indigo);">
            🇮🇳 Central: <strong>${centralCount}</strong>
          </span>
          <span style="font-size: 0.78rem; background: #ffffff; padding: 0.2rem 0.65rem; border-radius: 9999px; border: 1px solid var(--border-color); font-weight: 600; color: var(--primary-indigo);">
            🏛️ 28 States: <strong>${stateCount} active</strong>
          </span>
          <span style="font-size: 0.78rem; background: #ffffff; padding: 0.2rem 0.65rem; border-radius: 9999px; border: 1px solid var(--border-color); font-weight: 600; color: var(--primary-indigo);">
            🏙️ 8 UTs: <strong>${utCount} active</strong>
          </span>
        </div>

        <div style="font-size: 0.76rem; color: var(--text-secondary); display: flex; align-items: center; gap: 0.35rem;">
          <span class="material-symbols-outlined" style="font-size: 15px; color: var(--tertiary-green);">verified</span>
          <span>Verified from Official Portals (MyScheme, India.gov.in, State Portals)</span>
        </div>
      </div>

      <!-- Primary Header & Discovery Counter Capsule -->
      <div style="display: flex; flex-direction: column; md:flex-row; justify-content: space-between; align-items: flex-start; md:align-items: flex-end; gap: 1rem; margin-bottom: 1.25rem;">
        <div>
          <div style="display: flex; align-items: center; gap: 0.35rem; color: var(--secondary-saffron); font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">
            <span class="material-symbols-outlined" style="font-size: 18px;">travel_explore</span>
            <span>${t.pathwaysEngineSubtitle || "National Scheme Discovery Engine"}</span>
          </div>
          <h1 style="font-size: 2rem; font-weight: 800; color: var(--primary-indigo); margin: 0; line-height: 1.2;">
            ${t.resultsTitle || "All Government Schemes"}
          </h1>
        </div>

        <!-- Discovery Counter Stat Capsule -->
        <div style="display: flex; align-items: center; gap: 0.85rem; background: #ffffff; padding: 0.5rem 1rem; border-radius: var(--radius-xl); border: 1px solid var(--border-color); box-shadow: var(--shadow-sm);">
          <div style="display: flex; align-items: center; gap: 0.4rem;">
            <span style="width: 8px; height: 8px; border-radius: 9999px; background: var(--tertiary-green); display: inline-block;"></span>
            <span style="font-size: 0.88rem; font-weight: 700; color: var(--primary-indigo);">
              ${filtered.length} ${t.optionsFound || "Schemes Available"}
            </span>
          </div>
          <div style="width: 1px; height: 18px; background: var(--border-color);"></div>
          <button type="button" onclick="window.print()" style="background: none; border: none; display: flex; align-items: center; gap: 0.35rem; font-size: 0.82rem; color: var(--text-secondary); cursor: pointer; padding: 0;">
            <span class="material-symbols-outlined" style="font-size: 16px;">print</span>
            <span>${t.savePdfBtn || "Save PDF"}</span>
          </button>
        </div>
      </div>

      <!-- Comprehensive National Filter Controls Toolbar -->
      <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-xl); padding: 1.25rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm); display: flex; flex-direction: column; gap: 1rem;">
        
        <!-- Search Toolbar Row -->
        <div style="display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap;">
          <div style="position: relative; flex: 1; min-width: min(100%, 240px);">
            <span class="material-symbols-outlined" style="position: absolute; left: 0.85rem; top: 50%; transform: translateY(-50%); font-size: 20px; color: var(--text-secondary);">search</span>
            <input
              type="text"
              id="scheme-search-input"
              class="search-input"
              placeholder="${t.searchPlaceholder || 'Search schemes by keyword, ministry, benefit, state or language...'}"
              value="${state.searchQuery || ''}"
              style="width: 100%; padding: 0.65rem 0.85rem 0.65rem 2.5rem; border-radius: var(--radius-lg); border: 1.5px solid var(--border-color); background: #ffffff; font-size: 0.92rem; color: var(--text-primary);"
            />
          </div>

          <!-- Sort Selector -->
          <div style="display: flex; align-items: center; gap: 0.4rem;">
            <label for="scheme-sort-select" style="font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); white-space: nowrap;">Sort by:</label>
            <select id="scheme-sort-select" class="form-select" style="padding: 0.55rem 0.85rem; border-radius: var(--radius-lg); border: 1px solid var(--border-color); font-size: 0.84rem; background: #ffffff; color: var(--text-primary);">
              <option value="name" ${currentSort === 'name' ? 'selected' : ''}>Scheme Name (A-Z)</option>
              <option value="level" ${currentSort === 'level' ? 'selected' : ''}>Government Level</option>
              <option value="state" ${currentSort === 'state' ? 'selected' : ''}>State / Jurisdiction</option>
              <option value="category" ${currentSort === 'category' ? 'selected' : ''}>Category</option>
            </select>
          </div>

          ${(state.searchQuery || currentCategory !== 'all' || currentLevel !== 'all' || currentState !== 'all' || currentBeneficiary !== 'all') ? `
            <button class="btn btn-outline" id="reset-results-filters-btn" style="padding: 0.55rem 0.95rem; font-size: 0.82rem; display: flex; align-items: center; gap: 0.35rem; color: #dc2626; border-color: #fca5a5;">
              <span class="material-symbols-outlined" style="font-size: 16px;">filter_alt_off</span>
              <span>Clear Filters</span>
            </button>
          ` : ''}
        </div>

        <!-- 3-Dropdown Multi-Jurisdiction Filter Strip -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.75rem; border-top: 1px solid var(--border-color); padding-top: 0.85rem;">
          
          <!-- 1. Government Level Selector -->
          <div>
            <label for="scheme-level-select" style="font-size: 0.76rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--secondary-saffron); display: block; margin-bottom: 0.3rem;">
              🏛️ Government Level
            </label>
            <select id="scheme-level-select" class="form-select" style="width: 100%; padding: 0.5rem 0.75rem; border-radius: var(--radius-lg); border: 1px solid var(--border-color); font-size: 0.84rem; background: var(--bg-canvas);">
              <option value="all" ${currentLevel === 'all' ? 'selected' : ''}>All Government Levels (National)</option>
              <option value="Central" ${currentLevel === 'Central' ? 'selected' : ''}>🇮🇳 Central Government (All India)</option>
              <option value="State" ${currentLevel === 'State' ? 'selected' : ''}>🏛️ State Governments (28 States)</option>
              <option value="Union Territory" ${currentLevel === 'Union Territory' ? 'selected' : ''}>🏙️ Union Territories (8 UTs)</option>
            </select>
          </div>

          <!-- 2. State & Union Territory Selector (All 28 States & 8 UTs) -->
          <div>
            <label for="scheme-state-select" style="font-size: 0.76rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--secondary-saffron); display: block; margin-bottom: 0.3rem;">
              📍 State / UT Jurisdiction
            </label>
            <select id="scheme-state-select" class="form-select" style="width: 100%; padding: 0.5rem 0.75rem; border-radius: var(--radius-lg); border: 1px solid var(--border-color); font-size: 0.84rem; background: var(--bg-canvas);">
              <option value="all" ${currentState === 'all' ? 'selected' : ''}>All Jurisdictions (Pan-India)</option>
              <option value="All India" ${currentState === 'All India' ? 'selected' : ''}>🇮🇳 Central Only (All India Schemes)</option>
              
              <optgroup label="28 Indian States">
                ${INDIAN_STATES.map(st => `
                  <option value="${st}" ${currentState === st ? 'selected' : ''}>${st}</option>
                `).join('')}
              </optgroup>

              <optgroup label="8 Union Territories">
                ${INDIAN_UNION_TERRITORIES.map(ut => `
                  <option value="${ut}" ${currentState === ut ? 'selected' : ''}>${ut}</option>
                `).join('')}
              </optgroup>
            </select>
          </div>

          <!-- 3. Target Beneficiary Group Selector -->
          <div>
            <label for="scheme-beneficiary-select" style="font-size: 0.76rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--secondary-saffron); display: block; margin-bottom: 0.3rem;">
              👥 Target Beneficiary
            </label>
            <select id="scheme-beneficiary-select" class="form-select" style="width: 100%; padding: 0.5rem 0.75rem; border-radius: var(--radius-lg); border: 1px solid var(--border-color); font-size: 0.84rem; background: var(--bg-canvas);">
              <option value="all" ${currentBeneficiary === 'all' ? 'selected' : ''}>All Beneficiary Groups</option>
              <option value="student" ${currentBeneficiary === 'student' ? 'selected' : ''}>🎓 Students & Youth</option>
              <option value="farmer" ${currentBeneficiary === 'farmer' ? 'selected' : ''}>🌾 Farmers & Agriculture</option>
              <option value="women" ${currentBeneficiary === 'women' ? 'selected' : ''}>👩 Women & Children</option>
              <option value="senior" ${currentBeneficiary === 'senior' ? 'selected' : ''}>👵 Senior Citizens</option>
              <option value="vendor" ${currentBeneficiary === 'vendor' ? 'selected' : ''}>🏪 Street Vendors & MSME</option>
              <option value="tailor" ${currentBeneficiary === 'tailor' ? 'selected' : ''}>🧵 Tailors & Artisans</option>
              <option value="disability" ${currentBeneficiary === 'disability' ? 'selected' : ''}>♿ Persons with Disabilities</option>
            </select>
          </div>
        </div>

        <!-- 4. Category Ribbon -->
        <div style="border-top: 1px solid var(--border-color); padding-top: 0.75rem;">
          <div style="font-size: 0.76rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 0.5rem;">
            Filter by Welfare Category:
          </div>
          <div style="display: flex; align-items: center; gap: 0.45rem; overflow-x: auto; padding-bottom: 0.35rem; scrollbar-width: none;">
            <button class="category-pill ${currentCategory === 'all' ? 'active' : ''}" data-cat="all" style="padding: 0.4rem 0.85rem; border-radius: 9999px; font-size: 0.82rem; font-weight: 600; cursor: pointer; white-space: nowrap; display: flex; align-items: center; gap: 0.35rem;">
              <span>${t.filterAll || "All Categories"}</span>
              <span style="font-size: 0.72rem; padding: 0.1rem 0.45rem; border-radius: 9999px; background: rgba(0,0,0,0.08); font-weight: 700;">${counts.all || 0}</span>
            </button>

            <button class="category-pill ${currentCategory === 'education' ? 'active' : ''}" data-cat="education" style="padding: 0.4rem 0.85rem; border-radius: 9999px; font-size: 0.82rem; font-weight: 600; cursor: pointer; white-space: nowrap; display: flex; align-items: center; gap: 0.35rem;">
              <span>🎓 ${t.filterEducation || "Education"}</span>
              <span style="font-size: 0.72rem; padding: 0.1rem 0.45rem; border-radius: 9999px; background: rgba(0,0,0,0.08); font-weight: 700;">${counts.education || 0}</span>
            </button>

            <button class="category-pill ${currentCategory === 'health' ? 'active' : ''}" data-cat="health" style="padding: 0.4rem 0.85rem; border-radius: 9999px; font-size: 0.82rem; font-weight: 600; cursor: pointer; white-space: nowrap; display: flex; align-items: center; gap: 0.35rem;">
              <span>🏥 ${t.filterHealth || "Healthcare"}</span>
              <span style="font-size: 0.72rem; padding: 0.1rem 0.45rem; border-radius: 9999px; background: rgba(0,0,0,0.08); font-weight: 700;">${counts.health || 0}</span>
            </button>

            <button class="category-pill ${currentCategory === 'women' ? 'active' : ''}" data-cat="women" style="padding: 0.4rem 0.85rem; border-radius: 9999px; font-size: 0.82rem; font-weight: 600; cursor: pointer; white-space: nowrap; display: flex; align-items: center; gap: 0.35rem;">
              <span>👩 ${t.filterWomen || "Women & Child"}</span>
              <span style="font-size: 0.72rem; padding: 0.1rem 0.45rem; border-radius: 9999px; background: rgba(0,0,0,0.08); font-weight: 700;">${counts.women || 0}</span>
            </button>

            <button class="category-pill ${currentCategory === 'agriculture' ? 'active' : ''}" data-cat="agriculture" style="padding: 0.4rem 0.85rem; border-radius: 9999px; font-size: 0.82rem; font-weight: 600; cursor: pointer; white-space: nowrap; display: flex; align-items: center; gap: 0.35rem;">
              <span>🌾 ${t.filterAgri || "Agriculture"}</span>
              <span style="font-size: 0.72rem; padding: 0.1rem 0.45rem; border-radius: 9999px; background: rgba(0,0,0,0.08); font-weight: 700;">${counts.agriculture || 0}</span>
            </button>

            <button class="category-pill ${currentCategory === 'business' ? 'active' : ''}" data-cat="business" style="padding: 0.4rem 0.85rem; border-radius: 9999px; font-size: 0.82rem; font-weight: 600; cursor: pointer; white-space: nowrap; display: flex; align-items: center; gap: 0.35rem;">
              <span>🏪 ${t.categoryBusiness || "Business & MSME"}</span>
              <span style="font-size: 0.72rem; padding: 0.1rem 0.45rem; border-radius: 9999px; background: rgba(0,0,0,0.08); font-weight: 700;">${counts.business || 0}</span>
            </button>

            <button class="category-pill ${currentCategory === 'housing' ? 'active' : ''}" data-cat="housing" style="padding: 0.4rem 0.85rem; border-radius: 9999px; font-size: 0.82rem; font-weight: 600; cursor: pointer; white-space: nowrap; display: flex; align-items: center; gap: 0.35rem;">
              <span>🏠 ${t.filterHousing || "Housing"}</span>
              <span style="font-size: 0.72rem; padding: 0.1rem 0.45rem; border-radius: 9999px; background: rgba(0,0,0,0.08); font-weight: 700;">${counts.housing || 0}</span>
            </button>

            <button class="category-pill ${currentCategory === 'employment' ? 'active' : ''}" data-cat="employment" style="padding: 0.4rem 0.85rem; border-radius: 9999px; font-size: 0.82rem; font-weight: 600; cursor: pointer; white-space: nowrap; display: flex; align-items: center; gap: 0.35rem;">
              <span>💼 ${t.filterEmployment || "Employment"}</span>
              <span style="font-size: 0.72rem; padding: 0.1rem 0.45rem; border-radius: 9999px; background: rgba(0,0,0,0.08); font-weight: 700;">${counts.employment || 0}</span>
            </button>

            <button class="category-pill ${currentCategory === 'seniors' ? 'active' : ''}" data-cat="seniors" style="padding: 0.4rem 0.85rem; border-radius: 9999px; font-size: 0.82rem; font-weight: 600; cursor: pointer; white-space: nowrap; display: flex; align-items: center; gap: 0.35rem;">
              <span>👵 ${t.filterSeniors || "Senior Citizens"}</span>
              <span style="font-size: 0.72rem; padding: 0.1rem 0.45rem; border-radius: 9999px; background: rgba(0,0,0,0.08); font-weight: 700;">${counts.seniors || 0}</span>
            </button>

            <button class="category-pill ${currentCategory === 'disability' ? 'active' : ''}" data-cat="disability" style="padding: 0.4rem 0.85rem; border-radius: 9999px; font-size: 0.82rem; font-weight: 600; cursor: pointer; white-space: nowrap; display: flex; align-items: center; gap: 0.35rem;">
              <span>♿ ${t.filterDisability || "Disability"}</span>
              <span style="font-size: 0.72rem; padding: 0.1rem 0.45rem; border-radius: 9999px; background: rgba(0,0,0,0.08); font-weight: 700;">${counts.disability || 0}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Schemes Cards Stack -->
      ${filtered.length === 0 ? `
        <div style="text-align: center; padding: 3.5rem 1.5rem; background: #ffffff; border-radius: var(--radius-xl); border: 1px dashed var(--border-color); box-shadow: var(--shadow-sm);">
          <div style="font-size: 2.8rem; margin-bottom: 0.75rem;">📋</div>
          <h3 style="color: var(--primary-indigo); font-size: 1.25rem; font-weight: 700; margin-bottom: 0.5rem;">
            ${t.noResultsFound || "No schemes match the selected filters"}
          </h3>
          <p style="color: var(--text-secondary); font-size: 0.9rem; max-width: 480px; margin: 0 auto 1.25rem;">
            ${t.resetFiltersNotice || "Try expanding your jurisdiction or selecting All Government Levels to view available options."}
          </p>
          <button class="btn btn-primary" id="reset-results-filters-btn" style="padding: 0.5rem 1.25rem;">
            ${t.resetFilters || "Reset All Filters"}
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

  const sLevel = scheme.level || 'State';
  const sState = scheme.state || (sLevel === 'Central' ? 'All India' : 'Tamil Nadu');
  const isCentral = sLevel.toLowerCase() === 'central' || sState.toLowerCase() === 'all india';

  return `
    <article style="background: #ffffff; border-radius: var(--radius-xl); border: 1px solid var(--border-color); box-shadow: var(--shadow-sm); padding: 1.5rem; position: relative; overflow: hidden; transition: box-shadow 0.2s ease;">
      <!-- Top Accent Bar: Central (Navy/Saffron) or State (Leaf Green) -->
      <div style="position: absolute; top: 0; left: 0; right: 0; height: 5px; background: ${isCentral ? 'var(--secondary-saffron)' : isStrong ? 'var(--tertiary-green)' : 'var(--primary-indigo)'};"></div>

      <!-- Header Row -->
      <div style="display: flex; flex-direction: column; md:flex-row; justify-content: space-between; align-items: flex-start; gap: 1rem; margin-bottom: 1rem; margin-top: 0.25rem;">
        <div style="flex: 1;">
          <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.4rem;">
            
            <!-- Geographical Level Badge -->
            <span style="display: inline-flex; align-items: center; gap: 0.35rem; padding: 0.2rem 0.65rem; border-radius: 9999px; background: ${isCentral ? 'rgba(217, 119, 6, 0.12)' : 'rgba(21, 35, 62, 0.08)'}; color: ${isCentral ? 'var(--secondary-saffron)' : 'var(--primary-indigo)'}; font-size: 0.78rem; font-weight: 700;">
              <span>${isCentral ? '🇮🇳' : sLevel === 'Union Territory' ? '🏙️' : '🏛️'}</span>
              <span>${loc.displayCoverage || (isCentral ? 'Central Government (All India)' : `${sState} Government`)}</span>
            </span>

            <!-- Category Tag -->
            <span style="padding: 0.2rem 0.65rem; border-radius: 9999px; background: var(--bg-canvas); border: 1px solid var(--border-color); font-size: 0.76rem; color: var(--text-secondary); text-transform: capitalize;">
              ${scheme.category}
            </span>

            <!-- Official Verification Status -->
            <span style="display: inline-flex; align-items: center; gap: 0.25rem; font-size: 0.74rem; color: var(--tertiary-green); font-weight: 600;">
              <span class="material-symbols-outlined" style="font-size: 15px;">verified</span>
              <span>Verified Official Source</span>
            </span>
          </div>

          <h2 style="font-size: 1.35rem; font-weight: 800; color: var(--primary-indigo); margin: 0 0 0.25rem; line-height: 1.3;">
            ${name}
          </h2>
          ${subName && subName !== name ? `
            <p style="font-size: 0.92rem; color: var(--secondary-saffron); font-style: italic; margin: 0; font-weight: 600;">
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
            ${criteria.length > 0 ? criteria.slice(0, 3).map(c => `
              <li style="display: flex; align-items: flex-start; gap: 0.4rem;">
                <span class="material-symbols-outlined" style="font-size: 16px; color: var(--tertiary-green); flex-shrink: 0; margin-top: 1px;">check_circle</span>
                <span>${typeof c === 'string' ? c : (c.criterion || c.name || '')}</span>
              </li>
            `).join('') : `
              <li style="display: flex; align-items: flex-start; gap: 0.4rem;">
                <span class="material-symbols-outlined" style="font-size: 16px; color: var(--tertiary-green); flex-shrink: 0; margin-top: 1px;">check_circle</span>
                <span>Open for eligible residents of ${sState}</span>
              </li>
            `}
          </ul>
        </div>

        <!-- Metadata & Issuing Body -->
        <div style="background: var(--bg-canvas); padding: 1rem; border-radius: var(--radius-lg); border: 1px solid var(--border-color); display: flex; flex-direction: column; justify-content: space-between; gap: 0.65rem;">
          <div>
            <div style="display: flex; align-items: center; gap: 0.4rem; font-size: 0.82rem; color: var(--primary-indigo); font-weight: 600; margin-bottom: 0.35rem;">
              <span class="material-symbols-outlined" style="font-size: 16px; color: var(--secondary-saffron);">event_available</span>
              <span>Benefit Amount: <strong>${scheme.benefit_amount}</strong></span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.4rem; font-size: 0.82rem; color: var(--text-secondary);">
              <span class="material-symbols-outlined" style="font-size: 16px; color: var(--text-secondary);">description</span>
              <span>${docs.length > 0 ? docs.length + " core documents required" : "Standard KYC & identity documents required"}</span>
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
            <span>${t.viewDetails || "View Details"}</span>
            <span class="material-symbols-outlined" style="font-size: 16px;">arrow_forward</span>
          </a>
        </div>
      </div>
    </article>
  `;
}
