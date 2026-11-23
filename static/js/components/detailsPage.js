// NammaSevai AI - Scheme Details Page Component
import { i18n } from '../i18n.js';

export function renderDetailsPage(scheme, state) {
  const t = i18n[state.lang] || i18n.ta;
  const isTa = state.lang === 'ta';

  if (!scheme) {
    return `
      <div class="container" style="padding: 4rem 1.5rem; text-align: center;">
        <h2>நலத்திட்டம் காணப்படவில்லை (Scheme Not Found)</h2>
        <p style="margin: 1rem 0;">கேட்கப்பட்ட நலத்திட்டம் தரவுத்தளத்தில் இல்லை.</p>
        <a href="#schemes" class="btn btn-primary">← ${t.backToResults}</a>
      </div>
    `;
  }

  const criteriaList = isTa ? (scheme.eligibility_criteria_ta || scheme.eligibility_criteria || [])
                            : (scheme.eligibility_criteria || []);

  const docsList = scheme.required_documents || (scheme.documents ? scheme.documents.map(d => ({ name: d.name_en, name_ta: d.name_ta, mandatory: d.is_mandatory })) : []);
  const portalUrl = scheme.official_portal || scheme.portal_url || (scheme.source ? scheme.source.portal_url : 'https://www.tn.gov.in');

  return `
    <div class="details-page-container container">
      <!-- Breadcrumb & Back -->
      <a href="#schemes" class="details-back-btn" id="details-back-link">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m15 18-6-6 6-6"/></svg>
        <span>${t.backToResults}</span>
      </a>

      <!-- Scheme Header Card -->
      <div class="details-header-card">
        <div class="details-badge-row">
          <span class="badge badge-teal">${scheme.category.toUpperCase()}</span>
          <span class="badge badge-green">
            ✓ ${scheme.source_verification === 'verified' ? 'அரசு தளம் தகவல்' : 'Verified Source'}
          </span>
          <span class="badge badge-navy">Tamil Nadu Scheme</span>
        </div>

        <div>
          <h1 class="details-title-en">${scheme.name}</h1>
          <h2 class="details-title-ta">${scheme.name_ta}</h2>
        </div>

        <div class="details-dept-text">
          <strong>🏛️ ${t.departmentLabel}</strong> ${isTa ? scheme.department_ta : scheme.department}
        </div>

        <div class="details-benefit-banner">
          <div>
            <div style="font-size: 0.85rem; font-weight: 700; color: var(--primary-teal-dark); text-transform: uppercase;">
              ${t.benefitAmount}
            </div>
            <div style="font-size: 1.45rem; font-weight: 800; color: var(--primary-navy); margin-top: 0.2rem;">
              💰 ${scheme.benefit_amount}
            </div>
            <div style="font-size: 0.92rem; color: var(--text-muted); margin-top: 0.25rem;">
              ${isTa ? scheme.benefit_summary_ta : scheme.benefit_summary}
            </div>
          </div>

          <div>
            <a href="${portalUrl}" target="_blank" rel="noopener" class="btn btn-primary btn-lg">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" x2="21" y1="14" y2="3"/></svg>
              <span>${t.officialApplyBtn} ↗</span>
            </a>
          </div>
        </div>
      </div>

      <!-- Main Layout Grid -->
      <div class="details-grid">
        <div class="details-main-content">
          <!-- Description Card -->
          <div class="content-card">
            <h3 class="content-card-title">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--primary-teal)" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="16" y2="12"/><line x1="12" x2="12.01" y1="8" y2="8"/></svg>
              <span>${t.schemeDescription}</span>
            </h3>
            <p style="font-size: 1rem; color: var(--text-main); line-height: 1.7;">
              ${isTa ? scheme.description_ta : scheme.description}
            </p>
          </div>

          <!-- Eligibility Criteria Card -->
          <div class="content-card">
            <h3 class="content-card-title">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--gov-green)" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              <span>${t.eligibilityCriteria}</span>
            </h3>
            <div style="font-size: 0.88rem; color: var(--text-light); margin-bottom: 1rem;">
              விண்ணப்பதாரர் பூர்த்தி செய்ய வேண்டிய குறைந்தபட்ச நிபந்தனைகள்:
            </div>
            <ul style="list-style: none; display: flex; flex-direction: column; gap: 0.85rem;">
              ${criteriaList.map(criterion => `
                <li style="display: flex; align-items: flex-start; gap: 0.75rem;">
                  <span style="color: var(--gov-green); font-size: 1.1rem; line-height: 1;">✓</span>
                  <span style="font-size: 0.95rem; color: var(--text-main); line-height: 1.5;">${criterion}</span>
                </li>
              `).join('')}
            </ul>
          </div>

          <!-- Interactive Documents Checklist Card -->
          <div class="content-card" id="printable-documents-checklist">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem;">
              <h3 class="content-card-title" style="margin-bottom: 0;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent-saffron-dark)" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/></svg>
                <span>${t.documentsChecklist}</span>
              </h3>
              <button class="btn btn-outline btn-sm" id="print-checklist-btn" type="button">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect width="12" height="8" x="6" y="14"/></svg>
                <span>${t.printChecklist}</span>
              </button>
            </div>
            <p style="font-size: 0.88rem; color: var(--text-light); margin-bottom: 1.25rem;">
              ${t.docsSubtitle}
            </p>

            <div class="checklist-group">
              ${docsList.map((doc, idx) => `
                <label class="checklist-item" data-doc-index="${idx}">
                  <input type="checkbox" class="checklist-checkbox" />
                  <div style="display: flex; flex-direction: column;">
                    <span class="checklist-text" style="font-weight: 600;">
                      ${isTa ? doc.name_ta : doc.name}
                    </span>
                    <span style="font-size: 0.78rem; color: var(--text-light);">
                      ${doc.mandatory ? '(கட்டாயம் தேவை / Mandatory)' : '(பொருந்தினால் மட்டும் / If Applicable)'}
                    </span>
                  </div>
                </label>
              `).join('')}
            </div>
          </div>

          <!-- Application Procedure Steps -->
          <div class="content-card">
            <h3 class="content-card-title">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--primary-navy)" stroke-width="2"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/></svg>
              <span>${t.applicationSteps}</span>
            </h3>

            <div class="procedure-steps">
              <div class="procedure-mode-box">
                <div class="procedure-mode-title">🌐 ${t.onlineMode}</div>
                <div class="procedure-mode-text">
                  ${isTa ? (scheme.application_procedure?.online_ta || scheme.application_procedure?.online) : scheme.application_procedure?.online}
                </div>
              </div>

              <div class="procedure-mode-box" style="border-left-color: var(--accent-saffron);">
                <div class="procedure-mode-title">🏢 ${t.offlineMode}</div>
                <div class="procedure-mode-text">
                  ${isTa ? (scheme.application_procedure?.offline_ta || scheme.application_procedure?.offline) : scheme.application_procedure?.offline}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar Metadata -->
        <div class="details-side-content">
          <!-- Timelines & Dates -->
          <div class="content-card">
            <h4 style="font-size: 1.05rem; font-weight: 700; color: var(--primary-navy); margin-bottom: 0.85rem; display: flex; align-items: center; gap: 0.45rem;">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              <span>${t.importantDates}</span>
            </h4>
            <div style="font-size: 0.92rem; color: var(--text-main); background: var(--bg-surface); padding: 0.85rem; border-radius: var(--radius-sm); border-left: 3px solid var(--primary-teal);">
              ${isTa ? (scheme.important_dates_ta || scheme.important_dates) : scheme.important_dates}
            </div>
          </div>

          <!-- Official Portal & Verification -->
          <div class="content-card">
            <h4 style="font-size: 1.05rem; font-weight: 700; color: var(--primary-navy); margin-bottom: 0.85rem; display: flex; align-items: center; gap: 0.45rem;">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
              <span>${t.sourceAndVerified}</span>
            </h4>
            <div style="display: flex; flex-direction: column; gap: 0.65rem; font-size: 0.88rem;">
              <div>
                <span style="color: var(--text-light);">தகவல் மூலம்:</span><br/>
                <strong>${scheme.official_source}</strong>
              </div>
              <div>
                <span style="color: var(--text-light);">சரிபார்க்கப்பட்ட தேதி:</span><br/>
                <strong>${scheme.verified_date || '2026-10-15'}</strong>
              </div>
              <div style="margin-top: 0.5rem; padding: 0.75rem; background: var(--bg-surface); border-radius: var(--radius-sm); font-size: 0.8rem; color: var(--text-muted);">
                ℹ️ ${t.sampleDisclaimer}
              </div>
            </div>

            <div style="margin-top: 1.25rem;">
              <a href="${portalUrl}" target="_blank" rel="noopener" class="btn btn-navy" style="width: 100%;">
                <span>அரசு தளம் செல்லவும் ↗</span>
              </a>
            </div>
          </div>

          <!-- Citizen Helplines -->
          <div class="content-card">
            <h4 style="font-size: 1.05rem; font-weight: 700; color: var(--primary-navy); margin-bottom: 0.85rem; display: flex; align-items: center; gap: 0.45rem;">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
              <span>${t.helplineTitle}</span>
            </h4>
            <div style="font-size: 0.9rem; color: var(--text-main); display: flex; flex-direction: column; gap: 0.5rem;">
              <div><strong>துறை உதவி எண்:</strong> ${scheme.helpline || '1100'}</div>
              <div><strong>முதலமைச்சர் உதவி மையம்:</strong> 1100</div>
              <div><strong>இ-சேவை உதவி:</strong> 1800-425-1333</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}
