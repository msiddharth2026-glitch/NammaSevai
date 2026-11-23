// NammaSevai AI - Admin Dashboard Component
import { i18n } from '../i18n.js';

export function renderAdminPage(state) {
  const t = i18n[state.lang] || i18n.ta;
  const isTa = state.lang === 'ta';
  const schemes = state.schemes || [];
  const adminSearch = (state.adminSearch || '').toLowerCase();
  const adminCategory = state.adminCategory || 'all';
  const adminStatus = state.adminStatus || 'all';

  // Metrics
  const totalSchemes = schemes.length;
  const verifiedCount = schemes.filter(s => s.source_verification === 'verified').length;
  const pendingCount = schemes.filter(s => s.source_verification !== 'verified').length;
  const categoriesCount = new Set(schemes.map(s => s.category)).size;

  // Filter schemes
  const filtered = schemes.filter(s => {
    if (adminCategory !== 'all' && s.category !== adminCategory) return false;
    if (adminStatus !== 'all' && s.source_verification !== adminStatus) return false;
    if (adminSearch.trim().length > 0) {
      const match = (s.name + " " + s.name_ta + " " + s.department + " " + s.department_ta).toLowerCase();
      if (!match.includes(adminSearch)) return false;
    }
    return true;
  });

  return `
    <div class="admin-container container">
      <!-- Admin Top Banner -->
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; flex-wrap: wrap; gap: 1rem;">
        <div>
          <span class="badge badge-navy" style="margin-bottom: 0.4rem;">Portal Administration</span>
          <h1 style="font-size: 2.1rem; font-weight: 800; color: var(--primary-navy);">${t.adminTitle}</h1>
          <p style="color: var(--text-muted); font-size: 0.95rem;">${t.adminSubtitle}</p>
        </div>
        <div style="display: flex; gap: 0.75rem;">
          <button class="btn btn-outline" id="reset-schemes-btn" title="Reset to default dataset">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
            <span>Reset Data</span>
          </button>
          <button class="btn btn-primary" id="open-add-scheme-modal-btn">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" x2="12" y1="5" y2="19"/><line x1="5" x2="19" y1="12" y2="12"/></svg>
            <span>${t.addSchemeBtn}</span>
          </button>
        </div>
      </div>

      <!-- Stats Grid -->
      <div class="admin-stats-grid">
        <div class="admin-stat-card">
          <div>
            <div class="admin-stat-num">${totalSchemes}</div>
            <div class="admin-stat-title">${t.statTotal}</div>
          </div>
          <div class="admin-stat-icon" style="background: rgba(9, 45, 80, 0.1); color: var(--primary-navy);">
            📋
          </div>
        </div>

        <div class="admin-stat-card">
          <div>
            <div class="admin-stat-num" style="color: var(--gov-green);">${verifiedCount}</div>
            <div class="admin-stat-title">${t.statVerified}</div>
          </div>
          <div class="admin-stat-icon" style="background: rgba(22, 131, 74, 0.12); color: var(--gov-green);">
            ✓
          </div>
        </div>

        <div class="admin-stat-card">
          <div>
            <div class="admin-stat-num" style="color: var(--accent-saffron-dark);">${pendingCount}</div>
            <div class="admin-stat-title">${t.statPending}</div>
          </div>
          <div class="admin-stat-icon" style="background: rgba(255, 148, 24, 0.15); color: var(--accent-saffron-dark);">
            ⚠️
          </div>
        </div>

        <div class="admin-stat-card">
          <div>
            <div class="admin-stat-num" style="color: var(--primary-teal);">${categoriesCount}</div>
            <div class="admin-stat-title">${t.statCategories}</div>
          </div>
          <div class="admin-stat-icon" style="background: rgba(0, 143, 140, 0.12); color: var(--primary-teal);">
            📑
          </div>
        </div>
      </div>

      <!-- Schemes Table Card -->
      <div class="admin-table-card">
        <div class="admin-table-toolbar">
          <div style="flex: 1; max-width: 360px;">
            <input
              type="text"
              id="admin-search-input"
              class="form-input"
              placeholder="${t.searchAdmin}"
              value="${state.adminSearch || ''}"
            />
          </div>

          <div style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
            <select id="admin-category-filter" class="form-select" style="width: auto;">
              <option value="all">அனைத்து பிரிவுகள் (All Categories)</option>
              <option value="education" ${adminCategory === 'education' ? 'selected' : ''}>Education</option>
              <option value="women" ${adminCategory === 'women' ? 'selected' : ''}>Women Welfare</option>
              <option value="agriculture" ${adminCategory === 'agriculture' ? 'selected' : ''}>Agriculture</option>
              <option value="health" ${adminCategory === 'health' ? 'selected' : ''}>Health</option>
              <option value="employment" ${adminCategory === 'employment' ? 'selected' : ''}>Employment</option>
              <option value="seniors" ${adminCategory === 'seniors' ? 'selected' : ''}>Senior Citizens</option>
              <option value="disability" ${adminCategory === 'disability' ? 'selected' : ''}>Disability</option>
              <option value="housing" ${adminCategory === 'housing' ? 'selected' : ''}>Housing</option>
            </select>

            <select id="admin-status-filter" class="form-select" style="width: auto;">
              <option value="all">அனைத்து நிலைகள் (All Status)</option>
              <option value="verified" ${adminStatus === 'verified' ? 'selected' : ''}>Verified</option>
              <option value="pending" ${adminStatus === 'pending' ? 'selected' : ''}>Pending Review</option>
            </select>
          </div>
        </div>

        <!-- Responsive Table -->
        <div class="admin-table-responsive">
          <table class="admin-table">
            <thead>
              <tr>
                <th>${t.tableColName}</th>
                <th>${t.tableColDept}</th>
                <th>${t.tableColCategory}</th>
                <th>${t.tableColBenefit}</th>
                <th>${t.tableColStatus}</th>
                <th style="text-align: right;">${t.tableColActions}</th>
              </tr>
            </thead>
            <tbody>
              ${filtered.length === 0 ? `
                <tr>
                  <td colspan="6" style="text-align: center; padding: 2.5rem; color: var(--text-light);">
                    பொருத்தமான திட்டங்கள் எதுவும் இல்லை (No schemes found)
                  </td>
                </tr>
              ` : filtered.map(scheme => `
                <tr data-scheme-id="${scheme.id}">
                  <td style="max-width: 280px;">
                    <div style="font-weight: 700; color: var(--primary-navy); line-height: 1.3;">
                      ${isTa ? scheme.name_ta : scheme.name}
                    </div>
                    <div style="font-size: 0.78rem; color: var(--text-light); margin-top: 0.2rem;">
                      ${isTa ? scheme.name : scheme.name_ta}
                    </div>
                  </td>
                  <td style="font-size: 0.82rem; color: var(--text-muted); max-width: 200px;">
                    ${isTa ? scheme.department_ta : scheme.department}
                  </td>
                  <td>
                    <span class="badge badge-navy">${scheme.category}</span>
                  </td>
                  <td style="font-size: 0.85rem; font-weight: 600; color: var(--primary-teal-dark);">
                    ${scheme.benefit_amount}
                  </td>
                  <td>
                    <button class="badge ${scheme.source_verification === 'verified' ? 'badge-green' : 'badge-saffron'} toggle-status-btn" data-id="${scheme.id}" title="Click to toggle status" style="cursor: pointer; border: none;">
                      ${scheme.source_verification === 'verified' ? '✓ ' + t.statusVerified : '⚠️ ' + t.statusPending}
                    </button>
                  </td>
                  <td style="text-align: right;">
                    <div class="table-actions-cell" style="justify-content: flex-end;">
                      <a href="#scheme-details/${scheme.id}" class="btn btn-outline btn-sm" title="View details">
                        👁️
                      </a>
                      <button class="btn btn-outline btn-sm edit-scheme-btn" data-id="${scheme.id}" title="Edit scheme">
                        ✏️
                      </button>
                      <button class="btn btn-outline btn-sm delete-scheme-btn" data-id="${scheme.id}" style="color: var(--gov-red);" title="Delete scheme">
                        🗑️
                      </button>
                    </div>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Add/Edit Scheme Modal -->
    <div class="modal-overlay" id="scheme-modal">
      <div class="modal-box">
        <div class="modal-header">
          <h3 class="modal-title" id="modal-title-text">${t.modalAddTitle}</h3>
          <button class="modal-close-btn" id="close-modal-btn">✕</button>
        </div>
        <form id="scheme-form">
          <input type="hidden" id="form-scheme-id" value="" />
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">${t.fieldNameEn} *</label>
              <input type="text" id="form-name-en" class="form-input" required placeholder="E.g.: Chief Minister Medical Insurance" />
            </div>

            <div class="form-group">
              <label class="form-label">${t.fieldNameTa} *</label>
              <input type="text" id="form-name-ta" class="form-input" required placeholder="எ.கா: முதலமைச்சரின் விரிவான மருத்துவக் காப்பீடு" />
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
              <div class="form-group">
                <label class="form-label">${t.fieldDeptEn} *</label>
                <input type="text" id="form-dept-en" class="form-input" required placeholder="Health Department" />
              </div>
              <div class="form-group">
                <label class="form-label">${t.fieldDeptTa} *</label>
                <input type="text" id="form-dept-ta" class="form-input" required placeholder="மக்கள் நல்வாழ்வுத்துறை" />
              </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
              <div class="form-group">
                <label class="form-label">${t.fieldCategory} *</label>
                <select id="form-category" class="form-select" required>
                  <option value="education">Education & Students</option>
                  <option value="women">Women Welfare</option>
                  <option value="agriculture">Agriculture & Farmers</option>
                  <option value="health">Healthcare & Insurance</option>
                  <option value="employment">Employment & MSME</option>
                  <option value="seniors">Senior Citizens</option>
                  <option value="disability">Differently Abled</option>
                  <option value="housing">Housing & Shelter</option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">${t.fieldStatus} *</label>
                <select id="form-status" class="form-select">
                  <option value="verified">Verified Official Source</option>
                  <option value="pending">Pending Verification</option>
                </select>
              </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
              <div class="form-group">
                <label class="form-label">${t.fieldBenefitEn} *</label>
                <input type="text" id="form-benefit-en" class="form-input" required placeholder="₹1,000 / month direct bank deposit" />
              </div>
              <div class="form-group">
                <label class="form-label">${t.fieldBenefitTa} *</label>
                <input type="text" id="form-benefit-ta" class="form-input" required placeholder="மாதம் ₹1,000 நேரடி வங்கி வரவு" />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">${t.fieldDescEn}</label>
              <textarea id="form-desc-en" class="form-textarea" rows="2" placeholder="Scheme objectives in English..."></textarea>
            </div>

            <div class="form-group">
              <label class="form-label">${t.fieldDescTa}</label>
              <textarea id="form-desc-ta" class="form-textarea" rows="2" placeholder="திட்ட விளக்கம் தமிழில்..."></textarea>
            </div>

            <div class="form-group">
              <label class="form-label">${t.fieldCriteria}</label>
              <textarea id="form-criteria" class="form-textarea" rows="3" placeholder="Resident of Tamil Nadu&#10;Income under ₹2.5 Lakhs&#10;Age 21+"></textarea>
            </div>

            <div class="form-group">
              <label class="form-label">${t.fieldDocs}</label>
              <textarea id="form-docs" class="form-textarea" rows="3" placeholder="Aadhaar Card&#10;Smart Ration Card&#10;Income Certificate"></textarea>
            </div>

            <div class="form-group">
              <label class="form-label">${t.fieldPortal} *</label>
              <input type="url" id="form-portal" class="form-input" required placeholder="https://www.tn.gov.in" />
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-outline" id="cancel-modal-btn">${t.btnCancel}</button>
            <button type="submit" class="btn btn-primary">${t.btnSave}</button>
          </div>
        </form>
      </div>
    </div>
  `;
}
