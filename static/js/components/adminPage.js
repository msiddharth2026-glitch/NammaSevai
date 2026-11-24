// NammaSevai AI - Admin Dashboard Component (BharatSevai AI / Stitch Theme Redesign)
import { i18n } from '../i18n.js';
import { getLocalizedScheme } from '../schemesData.js';

export function renderAdminPage(state) {
  const t = i18n[state.lang] || i18n.ta;
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
      const match = (s.name + " " + (s.name_ta || '') + " " + (s.name_hi || '') + " " + (s.name_ml || '') + " " + s.department + " " + (s.department_ta || '')).toLowerCase();
      if (!match.includes(adminSearch)) return false;
    }
    return true;
  });

  return `
    <div class="admin-container container" style="max-width: 1150px; margin: 0 auto; padding: 1.5rem 1rem 3.5rem;">
      
      <!-- Admin Top Banner -->
      <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-2xl); padding: 1.5rem 1.75rem; box-shadow: var(--shadow-sm); margin-bottom: 1.75rem; display: flex; flex-direction: column; md:flex-row; justify-content: space-between; align-items: flex-start; md:align-items: center; gap: 1rem;">
        <div>
          <div style="display: inline-flex; align-items: center; gap: 0.35rem; padding: 0.2rem 0.65rem; border-radius: 9999px; background: rgba(21, 35, 62, 0.08); color: var(--primary-indigo); font-size: 0.76rem; font-weight: 700; margin-bottom: 0.35rem;">
            <span class="material-symbols-outlined" style="font-size: 14px;">admin_panel_settings</span>
            <span>${t.securedAdminBadge || "Secured Administration Portal"}</span>
          </div>
          <h1 style="font-size: 2rem; font-weight: 800; color: var(--primary-indigo); margin: 0; line-height: 1.25;">
            ${t.adminTitle}
          </h1>
          <p style="font-size: 0.9rem; color: var(--text-secondary); margin: 0.25rem 0 0;">
            ${t.adminSubtitle}
          </p>
        </div>

        <div style="display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap;">
          <button class="btn btn-outline" id="reset-schemes-btn" title="Reset to default catalog" style="padding: 0.45rem 1rem; font-size: 0.86rem; display: flex; align-items: center; gap: 0.35rem;">
            <span class="material-symbols-outlined" style="font-size: 18px;">restart_alt</span>
            <span>${t.resetDataBtn || "Reset Data"}</span>
          </button>
          
          <button class="btn btn-primary" id="open-add-scheme-modal-btn" style="padding: 0.5rem 1.25rem; font-size: 0.88rem; display: flex; align-items: center; gap: 0.45rem;">
            <span class="material-symbols-outlined" style="font-size: 20px;">add_circle</span>
            <span>${t.addSchemeBtn}</span>
          </button>
        </div>
      </div>

      <!-- Stats Grid -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 1.75rem;">
        <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-xl); padding: 1.25rem; box-shadow: var(--shadow-sm); display: flex; justify-content: space-between; align-items: center;">
          <div>
            <div style="font-size: 2rem; font-weight: 800; color: var(--primary-indigo); line-height: 1;">${totalSchemes}</div>
            <div style="font-size: 0.84rem; color: var(--text-secondary); font-weight: 600; margin-top: 0.35rem;">${t.statTotal}</div>
          </div>
          <div style="width: 44px; height: 44px; border-radius: 12px; background: rgba(21, 35, 62, 0.08); color: var(--primary-indigo); display: flex; align-items: center; justify-content: center;">
            <span class="material-symbols-outlined" style="font-size: 24px;">dataset</span>
          </div>
        </div>

        <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-xl); padding: 1.25rem; box-shadow: var(--shadow-sm); display: flex; justify-content: space-between; align-items: center;">
          <div>
            <div style="font-size: 2rem; font-weight: 800; color: var(--tertiary-green); line-height: 1;">${verifiedCount}</div>
            <div style="font-size: 0.84rem; color: var(--text-secondary); font-weight: 600; margin-top: 0.35rem;">${t.statVerified}</div>
          </div>
          <div style="width: 44px; height: 44px; border-radius: 12px; background: rgba(21, 128, 61, 0.12); color: var(--tertiary-green); display: flex; align-items: center; justify-content: center;">
            <span class="material-symbols-outlined" style="font-size: 24px;">verified</span>
          </div>
        </div>

        <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-xl); padding: 1.25rem; box-shadow: var(--shadow-sm); display: flex; justify-content: space-between; align-items: center;">
          <div>
            <div style="font-size: 2rem; font-weight: 800; color: var(--secondary-saffron); line-height: 1;">${pendingCount}</div>
            <div style="font-size: 0.84rem; color: var(--text-secondary); font-weight: 600; margin-top: 0.35rem;">${t.statPending}</div>
          </div>
          <div style="width: 44px; height: 44px; border-radius: 12px; background: rgba(217, 119, 6, 0.12); color: var(--secondary-saffron); display: flex; align-items: center; justify-content: center;">
            <span class="material-symbols-outlined" style="font-size: 24px;">warning</span>
          </div>
        </div>

        <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-xl); padding: 1.25rem; box-shadow: var(--shadow-sm); display: flex; justify-content: space-between; align-items: center;">
          <div>
            <div style="font-size: 2rem; font-weight: 800; color: var(--primary-indigo); line-height: 1;">${categoriesCount}</div>
            <div style="font-size: 0.84rem; color: var(--text-secondary); font-weight: 600; margin-top: 0.35rem;">${t.statCategories}</div>
          </div>
          <div style="width: 44px; height: 44px; border-radius: 12px; background: rgba(21, 35, 62, 0.08); color: var(--primary-indigo); display: flex; align-items: center; justify-content: center;">
            <span class="material-symbols-outlined" style="font-size: 24px;">category</span>
          </div>
        </div>
      </div>

      <!-- Schemes Management Card -->
      <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-xl); box-shadow: var(--shadow-sm); overflow: hidden;">
        
        <!-- Toolbar -->
        <div style="padding: 1.25rem; border-bottom: 1px solid var(--border-color); background: var(--bg-canvas); display: flex; flex-direction: column; sm:flex-row; justify-content: space-between; align-items: stretch; sm:align-items: center; gap: 0.75rem;">
          <div style="flex: 1; max-width: 360px; position: relative;">
            <span class="material-symbols-outlined" style="position: absolute; left: 0.75rem; top: 50%; transform: translateY(-50%); font-size: 18px; color: var(--text-secondary);">search</span>
            <input
              type="text"
              id="admin-search-input"
              class="form-input"
              placeholder="${t.searchAdmin}"
              value="${state.adminSearch || ''}"
              style="width: 100%; padding: 0.5rem 0.75rem 0.5rem 2.25rem; border-radius: var(--radius-lg); border: 1px solid var(--border-color); font-size: 0.88rem;"
            />
          </div>

          <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
            <select id="admin-category-filter" class="form-select" style="padding: 0.5rem 0.85rem; border-radius: var(--radius-lg); border: 1px solid var(--border-color); font-size: 0.84rem; background: #ffffff;">
              <option value="all">${t.allCategoriesOption || "All Categories"}</option>
              <option value="education" ${adminCategory === 'education' ? 'selected' : ''}>${t.filterEducation || 'Education'}</option>
              <option value="women" ${adminCategory === 'women' ? 'selected' : ''}>${t.filterWomen || 'Women Welfare'}</option>
              <option value="agriculture" ${adminCategory === 'agriculture' ? 'selected' : ''}>${t.filterAgri || 'Agriculture'}</option>
              <option value="health" ${adminCategory === 'health' ? 'selected' : ''}>${t.filterHealth || 'Health'}</option>
              <option value="employment" ${adminCategory === 'employment' ? 'selected' : ''}>${t.filterEmployment || 'Employment'}</option>
              <option value="seniors" ${adminCategory === 'seniors' ? 'selected' : ''}>${t.filterSeniors || 'Senior Citizens'}</option>
              <option value="disability" ${adminCategory === 'disability' ? 'selected' : ''}>${t.filterDisability || 'Disability'}</option>
              <option value="housing" ${adminCategory === 'housing' ? 'selected' : ''}>${t.filterHousing || 'Housing'}</option>
            </select>

            <select id="admin-status-filter" class="form-select" style="padding: 0.5rem 0.85rem; border-radius: var(--radius-lg); border: 1px solid var(--border-color); font-size: 0.84rem; background: #ffffff;">
              <option value="all">${t.allStatusOption || "All Status"}</option>
              <option value="verified" ${adminStatus === 'verified' ? 'selected' : ''}>${t.statusVerified || 'Verified'}</option>
              <option value="pending" ${adminStatus === 'pending' ? 'selected' : ''}>${t.statusPending || 'Pending Review'}</option>
            </select>
          </div>
        </div>

        <!-- Responsive Table -->
        <div style="overflow-x: auto;">
          <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.88rem;">
            <thead>
              <tr style="background: var(--bg-canvas); border-bottom: 1px solid var(--border-color); color: var(--text-secondary); font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.05em;">
                <th style="padding: 0.85rem 1.25rem;">${t.tableColName}</th>
                <th style="padding: 0.85rem 1rem;">${t.tableColDept}</th>
                <th style="padding: 0.85rem 1rem;">${t.tableColCategory}</th>
                <th style="padding: 0.85rem 1rem;">${t.tableColBenefit}</th>
                <th style="padding: 0.85rem 1rem;">${t.tableColStatus}</th>
                <th style="padding: 0.85rem 1.25rem; text-align: right;">${t.tableColActions}</th>
              </tr>
            </thead>
            <tbody>
              ${filtered.length === 0 ? `
                <tr>
                  <td colspan="6" style="text-align: center; padding: 3rem 1rem; color: var(--text-secondary);">
                    ${t.tableNoSchemesFound || "No schemes found"}
                  </td>
                </tr>
              ` : filtered.map(scheme => {
                const loc = getLocalizedScheme(scheme, state.lang);
                const displayName = loc.displayName || scheme.name;
                const subName = (state.lang === 'ta' || state.lang === 'tanglish') ? scheme.name : (scheme.name_ta || '');
                const displayDept = loc.displayDepartment || scheme.department;

                return `
                  <tr data-scheme-id="${scheme.id}" style="border-bottom: 1px solid var(--border-color); transition: background 0.15s ease;">
                    <td style="padding: 1rem 1.25rem; max-width: 280px;">
                      <div style="font-weight: 700; color: var(--primary-indigo); line-height: 1.3;">
                        ${displayName}
                      </div>
                      ${subName ? `
                        <div style="font-size: 0.78rem; color: var(--text-secondary); margin-top: 0.2rem;">
                          ${subName}
                        </div>
                      ` : ''}
                    </td>
                    <td style="padding: 1rem; font-size: 0.82rem; color: var(--text-secondary); max-width: 200px;">
                      ${displayDept}
                    </td>
                    <td style="padding: 1rem;">
                      <span style="display: inline-block; padding: 0.2rem 0.55rem; border-radius: 9999px; background: var(--bg-canvas); border: 1px solid var(--border-color); font-size: 0.75rem; font-weight: 600; text-transform: capitalize; color: var(--primary-indigo);">
                        ${scheme.category}
                      </span>
                    </td>
                    <td style="padding: 1rem; font-size: 0.85rem; font-weight: 700; color: var(--primary-indigo);">
                      ${scheme.benefit_amount || loc.displayBenefit}
                    </td>
                    <td style="padding: 1rem;">
                      <button class="toggle-status-btn" data-id="${scheme.id}" title="Click to toggle status" style="cursor: pointer; border: none; padding: 0.25rem 0.65rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; background: ${scheme.source_verification === 'verified' ? 'rgba(21, 128, 61, 0.12)' : 'rgba(217, 119, 6, 0.12)'}; color: ${scheme.source_verification === 'verified' ? 'var(--tertiary-green)' : 'var(--secondary-saffron)'};">
                        ${scheme.source_verification === 'verified' ? '✓ ' + (t.statusVerified || 'Verified') : '⚠️ ' + (t.statusPending || 'Pending Review')}
                      </button>
                    </td>
                    <td style="padding: 1rem 1.25rem; text-align: right;">
                      <div style="display: inline-flex; align-items: center; gap: 0.35rem;">
                        <a href="#scheme-details/${scheme.id}" class="btn btn-outline btn-sm" title="View details" style="padding: 0.3rem 0.55rem;">
                          <span class="material-symbols-outlined" style="font-size: 16px;">visibility</span>
                        </a>
                        <button class="btn btn-outline btn-sm edit-scheme-btn" data-id="${scheme.id}" title="Edit scheme" style="padding: 0.3rem 0.55rem;">
                          <span class="material-symbols-outlined" style="font-size: 16px;">edit</span>
                        </button>
                        <button class="btn btn-outline btn-sm delete-scheme-btn" data-id="${scheme.id}" style="padding: 0.3rem 0.55rem; color: #dc2626; border-color: rgba(220, 38, 38, 0.3);" title="Delete scheme">
                          <span class="material-symbols-outlined" style="font-size: 16px;">delete</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Add/Edit Scheme Modal -->
    <div class="modal-overlay" id="scheme-modal">
      <div class="modal-box" style="max-width: 640px; background: #ffffff; border-radius: var(--radius-xl); border: 1px solid var(--border-color); box-shadow: var(--shadow-lg); padding: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border-color);">
          <h3 style="font-size: 1.25rem; font-weight: 800; color: var(--primary-indigo); margin: 0;" id="modal-title-text">${t.modalAddTitle}</h3>
          <button id="close-modal-btn" style="background: none; border: none; font-size: 1.25rem; color: var(--text-secondary); cursor: pointer;">✕</button>
        </div>

        <form id="scheme-form">
          <input type="hidden" id="form-scheme-id" value="" />
          <div style="display: flex; flex-direction: column; gap: 1rem; max-height: 70vh; overflow-y: auto; padding-right: 0.5rem;">
            
            <div>
              <label style="font-size: 0.84rem; font-weight: 700; color: var(--primary-indigo); display: block; margin-bottom: 0.25rem;">${t.fieldNameEn} *</label>
              <input type="text" id="form-name-en" class="form-input" required placeholder="E.g.: Chief Minister Comprehensive Health Insurance" style="width: 100%; padding: 0.55rem; border-radius: var(--radius-md); border: 1px solid var(--border-color);" />
            </div>

            <div>
              <label style="font-size: 0.84rem; font-weight: 700; color: var(--primary-indigo); display: block; margin-bottom: 0.25rem;">${t.fieldNameTa} *</label>
              <input type="text" id="form-name-ta" class="form-input" required placeholder="எ.கா: முதலமைச்சரின் விரிவான மருத்துவக் காப்பீடு" style="width: 100%; padding: 0.55rem; border-radius: var(--radius-md); border: 1px solid var(--border-color);" />
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
              <div>
                <label style="font-size: 0.84rem; font-weight: 700; color: var(--primary-indigo); display: block; margin-bottom: 0.25rem;">${t.fieldDeptEn} *</label>
                <input type="text" id="form-dept-en" class="form-input" required placeholder="Health Department" style="width: 100%; padding: 0.55rem; border-radius: var(--radius-md); border: 1px solid var(--border-color);" />
              </div>
              <div>
                <label style="font-size: 0.84rem; font-weight: 700; color: var(--primary-indigo); display: block; margin-bottom: 0.25rem;">${t.fieldDeptTa} *</label>
                <input type="text" id="form-dept-ta" class="form-input" required placeholder="மக்கள் நல்வாழ்வுத்துறை" style="width: 100%; padding: 0.55rem; border-radius: var(--radius-md); border: 1px solid var(--border-color);" />
              </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
              <div>
                <label style="font-size: 0.84rem; font-weight: 700; color: var(--primary-indigo); display: block; margin-bottom: 0.25rem;">${t.fieldCategory} *</label>
                <select id="form-category" class="form-select" required style="width: 100%; padding: 0.55rem; border-radius: var(--radius-md); border: 1px solid var(--border-color); background: #fff;">
                  <option value="education">${t.filterEducation || 'Education'}</option>
                  <option value="women">${t.filterWomen || 'Women Welfare'}</option>
                  <option value="agriculture">${t.filterAgri || 'Agriculture'}</option>
                  <option value="health">${t.filterHealth || 'Healthcare & Insurance'}</option>
                  <option value="employment">${t.filterEmployment || 'Employment & MSME'}</option>
                  <option value="seniors">${t.filterSeniors || 'Senior Citizens'}</option>
                  <option value="disability">${t.filterDisability || 'Differently Abled'}</option>
                  <option value="housing">${t.filterHousing || 'Housing & Shelter'}</option>
                </select>
              </div>

              <div>
                <label style="font-size: 0.84rem; font-weight: 700; color: var(--primary-indigo); display: block; margin-bottom: 0.25rem;">${t.fieldStatus} *</label>
                <select id="form-status" class="form-select" style="width: 100%; padding: 0.55rem; border-radius: var(--radius-md); border: 1px solid var(--border-color); background: #fff;">
                  <option value="verified">${t.statusVerified || 'Verified Official Source'}</option>
                  <option value="pending">${t.statusPending || 'Pending Verification'}</option>
                </select>
              </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
              <div>
                <label style="font-size: 0.84rem; font-weight: 700; color: var(--primary-indigo); display: block; margin-bottom: 0.25rem;">${t.fieldBenefitEn} *</label>
                <input type="text" id="form-benefit-en" class="form-input" required placeholder="₹1,000 / month direct bank deposit" style="width: 100%; padding: 0.55rem; border-radius: var(--radius-md); border: 1px solid var(--border-color);" />
              </div>
              <div>
                <label style="font-size: 0.84rem; font-weight: 700; color: var(--primary-indigo); display: block; margin-bottom: 0.25rem;">${t.fieldBenefitTa} *</label>
                <input type="text" id="form-benefit-ta" class="form-input" required placeholder="மாதம் ₹1,000 நேரடி வங்கி வரவு" style="width: 100%; padding: 0.55rem; border-radius: var(--radius-md); border: 1px solid var(--border-color);" />
              </div>
            </div>

            <div>
              <label style="font-size: 0.84rem; font-weight: 700; color: var(--primary-indigo); display: block; margin-bottom: 0.25rem;">${t.fieldDescEn}</label>
              <textarea id="form-desc-en" rows="2" placeholder="Scheme objectives in English..." style="width: 100%; padding: 0.55rem; border-radius: var(--radius-md); border: 1px solid var(--border-color);"></textarea>
            </div>

            <div>
              <label style="font-size: 0.84rem; font-weight: 700; color: var(--primary-indigo); display: block; margin-bottom: 0.25rem;">${t.fieldDescTa}</label>
              <textarea id="form-desc-ta" rows="2" placeholder="திட்ட விளக்கம் தமிழில்..." style="width: 100%; padding: 0.55rem; border-radius: var(--radius-md); border: 1px solid var(--border-color);"></textarea>
            </div>

            <div>
              <label style="font-size: 0.84rem; font-weight: 700; color: var(--primary-indigo); display: block; margin-bottom: 0.25rem;">${t.fieldCriteria}</label>
              <textarea id="form-criteria" rows="3" placeholder="Resident of Tamil Nadu&#10;Income under ₹2.5 Lakhs&#10;Age 21+" style="width: 100%; padding: 0.55rem; border-radius: var(--radius-md); border: 1px solid var(--border-color);"></textarea>
            </div>

            <div>
              <label style="font-size: 0.84rem; font-weight: 700; color: var(--primary-indigo); display: block; margin-bottom: 0.25rem;">${t.fieldDocs}</label>
              <textarea id="form-docs" rows="3" placeholder="Aadhaar Card&#10;Smart Ration Card&#10;Income Certificate" style="width: 100%; padding: 0.55rem; border-radius: var(--radius-md); border: 1px solid var(--border-color);"></textarea>
            </div>

            <div>
              <label style="font-size: 0.84rem; font-weight: 700; color: var(--primary-indigo); display: block; margin-bottom: 0.25rem;">${t.fieldPortal} *</label>
              <input type="url" id="form-portal" required placeholder="https://www.tn.gov.in" style="width: 100%; padding: 0.55rem; border-radius: var(--radius-md); border: 1px solid var(--border-color);" />
            </div>
          </div>

          <div style="display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 1.25rem; pt: 0.75rem; border-top: 1px solid var(--border-color);">
            <button type="button" class="btn btn-outline" id="cancel-modal-btn" style="padding: 0.5rem 1rem;">${t.btnCancel}</button>
            <button type="submit" class="btn btn-primary" style="padding: 0.5rem 1.25rem;">${t.btnSave}</button>
          </div>
        </form>
      </div>
    </div>
  `;
}
