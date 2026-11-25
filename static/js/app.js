// BharatSevai AI - Main Application Controller with Real Voice & AI Backend Integration
import { i18n } from './i18n.js';
import { initialSchemes } from './schemesData.js';
import { SchemeMatcher } from './nlpMatcher.js';
import { SpeechService } from './speechService.js';
import { renderNavbar } from './components/navbar.js';
import { renderFooter } from './components/footer.js';
import { renderLandingPage } from './components/landingPage.js';
import { renderAssistantPage } from './components/assistantPage.js';
import { renderResultsPage } from './components/resultsPage.js';
import { renderDetailsPage } from './components/detailsPage.js';
import { renderChecklistPage } from './components/checklistPage.js';
import { renderAdminPage } from './components/adminPage.js';
import { renderFeedbackPage } from './components/feedbackPage.js';

class App {
  constructor() {
    this.speechService = new SpeechService();
    this.currentAudioPlayer = null;

    const storedLang = localStorage.getItem('bharatsevai_lang') || localStorage.getItem('nammasevai_lang') || 'ta';
    const storedState = localStorage.getItem('bharatsevai_user_state') || '';

    this.state = {
      lang: storedLang,
      assistantLang: storedLang,
      route: 'landing',
      schemeDetailsId: null,
      schemes: this.loadSchemes(),
      currentQuery: '',
      chatHistory: [],
      selectedCategory: 'all',
      selectedLevel: 'all',
      selectedState: storedState || 'all',
      selectedBeneficiary: 'all',
      selectedSort: 'name',
      searchQuery: '',
      lastAssistantQuery: '',
      lastMatchedMap: {},
      userProfile: storedState ? { state: storedState } : {},
      isListening: false,
      isSpeaking: false,
      adminSearch: '',
      adminCategory: 'all',
      adminStatus: 'all',
      
      // Privacy and Voice Features
      micConsentGiven: (localStorage.getItem('bharatsevai_mic_consent') || localStorage.getItem('nammasevai_mic_consent')) === 'true',
      showMicConsentModal: false,
      showApiKeyModal: false,
      voiceConfig: {
        ai_model_configured: false,
        configuration_instruction: null
      }
    };

    this.matcher = new SchemeMatcher(this.state.schemes);
    this.init();
  }

  loadSchemes() {
    const saved = localStorage.getItem('bharatsevai_schemes') || localStorage.getItem('nammasevai_schemes');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      } catch (e) {
        console.error("Failed to parse saved schemes:", e);
      }
    }
    return [...initialSchemes];
  }

  saveSchemes() {
    localStorage.setItem('bharatsevai_schemes', JSON.stringify(this.state.schemes));
    localStorage.setItem('nammasevai_schemes', JSON.stringify(this.state.schemes));
    this.matcher.setSchemes(this.state.schemes);
  }

  resetSchemes() {
    if (confirm("Reset all schemes data to default catalog? / மாதிரி தரவுகளை மீட்டமைக்கவா?")) {
      this.state.schemes = [...initialSchemes];
      this.saveSchemes();
      this.render();
    }
  }

  async runPortalHealthCheck() {
    const btn = document.getElementById('run-portal-health-btn');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<span class="material-symbols-outlined" style="font-size: 18px; animation: spin 1s linear infinite;">sync</span> Running Health Audit...`;
    }
    try {
      const res = await fetch('/api/admin/portal-monitor/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Admin-Token': 'nammasevai-admin-dev-secret'
        }
      });
      if (res.ok) {
        const summary = await res.json();
        alert(`Portal Health Audit Completed:\n• ${summary.total_checked} Portals Checked\n• ${summary.available_count} Available\n• ${summary.redirects_detected} Redirects Detected\n• ${summary.domain_migrations_detected} Migrations Detected\n• ${summary.unavailable_count} Unavailable`);
      }
    } catch (e) {
      console.error("Portal health check failed:", e);
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = `<span class="material-symbols-outlined" style="font-size: 18px;">sync</span> Run Health Audit Now`;
      }
    }
  }

  async runQualityBenchmark() {
    const btn = document.getElementById('run-quality-benchmark-btn');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<span class="material-symbols-outlined" style="font-size: 18px; animation: spin 1s linear infinite;">sync</span> Running Benchmark Audit...`;
    }
    try {
      const res = await fetch('/api/admin/quality-benchmark', {
        headers: {
          'X-Admin-Key': 'nammasevai-admin-dev-secret'
        }
      });
      if (res.ok) {
        const report = await res.json();
        this.state.qualityBenchmark = report;
        this.render();
      } else {
        alert("Failed to run quality benchmark. Ensure admin authorization.");
      }
    } catch (e) {
      console.error("Quality benchmark audit failed:", e);
    } finally {
      const btnAfter = document.getElementById('run-quality-benchmark-btn');
      if (btnAfter) {
        btnAfter.disabled = false;
        btnAfter.innerHTML = `<span class="material-symbols-outlined" style="font-size: 18px;">sync</span> Run Benchmark Audit Now`;
      }
    }
  }

  async runContentAudit() {
    const btn = document.getElementById('run-content-audit-btn');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<span class="material-symbols-outlined" style="font-size: 18px; animation: spin 1s linear infinite;">sync</span> Running Content Audit...`;
    }
    try {
      const res = await fetch('/api/admin/content-monitor/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Admin-Key': 'nammasevai-admin-dev-secret'
        },
        body: JSON.stringify(null)
      });
      if (res.ok) {
        const audit = await res.json();
        await this.loadContentMonitoringSummary();
        alert(`Content Audit Completed:\n• ${audit.sources_audited} Sources Audited\n• ${audit.changes_detected} Changes Detected\n• ${audit.unchanged_sources} Unchanged Baselines\n• ${audit.pending_admin_reviews} Pending Human Reviews`);
      } else {
        alert("Failed to run content audit. Ensure admin authorization.");
      }
    } catch (e) {
      console.error("Content audit failed:", e);
    } finally {
      const btnAfter = document.getElementById('run-content-audit-btn');
      if (btnAfter) {
        btnAfter.disabled = false;
        btnAfter.innerHTML = `<span class="material-symbols-outlined" style="font-size: 18px;">sync</span> Run Content Audit Now`;
      }
    }
  }

  async loadContentMonitoringSummary() {
    try {
      const [sumRes, chRes] = await Promise.all([
        fetch('/api/admin/content-monitor/summary', { headers: { 'X-Admin-Key': 'nammasevai-admin-dev-secret' } }),
        fetch('/api/admin/content-monitor/changes', { headers: { 'X-Admin-Key': 'nammasevai-admin-dev-secret' } })
      ]);
      if (sumRes.ok) {
        this.state.contentSummary = await sumRes.json();
      }
      if (chRes.ok) {
        this.state.detectedChanges = await chRes.json();
      }
      this.render();
    } catch (e) {
      console.error("Error loading content monitoring summary:", e);
    }
  }

  async reviewDetectedChange(changeId) {
    const change = (this.state.detectedChanges || []).find(c => c.id === changeId);
    const summary = change ? `Scheme: ${change.scheme_name}\nClassification: ${change.change_classification}\nSummary: ${change.change_summary}` : `Change ID: ${changeId}`;
    const action = prompt(`${summary}\n\nEnter action: "approve", "reject", or "evidence":`, "approve");
    if (!action) return;
    const notes = prompt("Enter review notes / reason for record:", "Verified against official gazette / portal notification");
    const adminKey = localStorage.getItem('bharatsevai_admin_key') || localStorage.getItem('nammasevai_admin_key') || 'nammasevai-admin-dev-secret';

    try {
      const res = await fetch(`/api/admin/content-monitor/changes/${changeId}/review`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Admin-Key': adminKey
        },
        body: JSON.stringify({
          action: action.trim().toLowerCase(),
          admin_id: "admin@bharatsevai.gov.in",
          review_notes: notes || "Manual verification complete"
        })
      });
      if (res.ok) {
        const result = await res.json();
        alert(`Change successfully processed (${action.toUpperCase()}):\n${result.message}`);
        await this.loadContentMonitoringSummary();
        // Refresh schemes in memory
        try {
          const sRes = await fetch('/api/schemes?limit=200');
          if (sRes.ok) {
            this.state.schemes = await sRes.json();
            this.saveSchemes();
          }
        } catch (_) {}
        this.render();
      } else {
        const err = await res.json();
        alert(`Review failed: ${err.detail || "Server error"}`);
      }
    } catch (e) {
      alert(`Network error: ${e.message}`);
    }
  }

  async init() {
    // Check backend voice and AI config
    try {
      const res = await fetch('/api/voice/config');
      if (res.ok) {
        const data = await res.json();
        this.state.voiceConfig = data;
      }
    } catch (e) {
      console.log("Backend offline or local static mode:", e.message);
    }

    // Sync schemes from backend if available
    try {
      const res = await fetch('/api/schemes?limit=200');
      if (res.ok) {
        const backendSchemes = await res.json();
        if (Array.isArray(backendSchemes) && backendSchemes.length > 0) {
          // Merge with initial data for full criteria, documents, and procedures
          this.state.schemes = backendSchemes.map(s => {
            const initial = initialSchemes.find(init => init.id === s.id) || {};
            return {
              ...initial,
              ...s,
              official_portal: s.official_portal || s.portal_url || initial.official_portal || 'https://www.tn.gov.in',
              portal_url: s.portal_url || s.official_portal || initial.official_portal || 'https://www.tn.gov.in',
              required_documents: (s.required_documents && s.required_documents.length > 0)
                ? s.required_documents
                : (initial.required_documents || []),
              eligibility_criteria: (s.conditions && s.conditions.length > 0)
                ? s.conditions.map(c => c.description_en)
                : (initial.eligibility_criteria || []),
              eligibility_criteria_ta: (s.conditions && s.conditions.length > 0)
                ? s.conditions.map(c => c.description_ta)
                : (initial.eligibility_criteria_ta || []),
              application_procedure: initial.application_procedure || {
                online: "Apply online at " + (s.portal_url || "https://www.tn.gov.in"),
                offline: "Contact nearest Taluk Office / e-Sevai Center"
              }
            };
          });
          this.saveSchemes();
        }
      }
    } catch (e) {
      console.log("Using cached schemes catalog:", e.message);
    }

    // Window hash routing
    window.addEventListener('hashchange', () => this.handleRouting());
    this.handleRouting();

    // Delegate global event listeners
    this.attachGlobalEvents();
  }

  handleRouting() {
    const hash = window.location.hash.slice(1) || 'landing';
    if (hash.startsWith('scheme-details/')) {
      this.state.route = 'scheme-details';
      this.state.schemeDetailsId = hash.replace('scheme-details/', '');
    } else if (['landing', 'assistant', 'schemes', 'checklist', 'admin', 'feedback'].includes(hash)) {
      this.state.route = hash;
      this.state.schemeDetailsId = null;
    } else {
      this.state.route = 'landing';
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
    this.render();
  }

  navigate(route, param = null) {
    if (route === 'scheme-details' && param) {
      window.location.hash = `#scheme-details/${param}`;
    } else {
      window.location.hash = `#${route}`;
    }
  }

  setLanguage(lang) {
    this.state.lang = lang;
    this.state.assistantLang = lang;
    localStorage.setItem('bharatsevai_lang', lang);
    localStorage.setItem('nammasevai_lang', lang);
    this.render();
  }

  attachGlobalEvents() {
    const appRoot = document.getElementById('app-root');

    appRoot.addEventListener('click', (e) => {
      // Compact Language Dropdown button toggle in Navbar
      const dropdownBtn = e.target.closest('#lang-dropdown-btn');
      if (dropdownBtn) {
        const wrapper = document.getElementById('lang-dropdown-wrapper');
        if (wrapper) {
          const isOpen = wrapper.classList.toggle('open');
          dropdownBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        }
        return;
      }

      // Language selection option (dropdown menu item or mobile drawer button)
      const setLangBtn = e.target.closest('[data-set-lang]');
      if (setLangBtn) {
        const nextLang = setLangBtn.getAttribute('data-set-lang');
        this.setLanguage(nextLang);
        return;
      }

      // Close mobile drawer if open when user clicks a nav link or outside
      const menu = document.getElementById('nav-menu');
      if (menu && menu.classList.contains('open')) {
        if (e.target.closest('.nav-link') || (!e.target.closest('#nav-menu') && !e.target.closest('#mobile-toggle'))) {
          menu.classList.remove('open');
        }
      }

      // Legacy Language Toggle in Navbar fallback
      if (e.target.closest('#lang-toggle-btn')) {
        const nextLang = this.state.lang === 'ta' ? 'en' : 'ta';
        this.setLanguage(nextLang);
        return;
      }

      // Mobile Menu Toggle
      if (e.target.closest('#mobile-toggle')) {
        if (menu) menu.classList.toggle('open');
        return;
      }

      // Assistant Language Selector
      const langChip = e.target.closest('[data-lang-choice]');
      if (langChip) {
        const choice = langChip.getAttribute('data-lang-choice');
        this.state.assistantLang = choice;
        this.render();
        return;
      }

      // Microphone Button Click
      if (e.target.closest('#main-mic-btn')) {
        this.handleMicClick();
        return;
      }

      // Privacy Consent Modal Actions
      if (e.target.closest('#grant-mic-consent-btn')) {
        this.state.micConsentGiven = true;
        localStorage.setItem('bharatsevai_mic_consent', 'true');
        localStorage.setItem('nammasevai_mic_consent', 'true');
        this.state.showMicConsentModal = false;
        this.render();
        this.startVoiceRecording();
        return;
      }

      if (e.target.closest('#deny-mic-consent-btn') || e.target.closest('#close-mic-consent-btn')) {
        this.state.showMicConsentModal = false;
        this.render();
        const textarea = document.getElementById('assistant-query-input');
        if (textarea) textarea.focus();
        return;
      }

      // API Key Info Modal Actions
      if (e.target.closest('#view-ai-config-btn')) {
        this.state.showApiKeyModal = true;
        this.render();
        return;
      }

      if (e.target.closest('#close-api-key-modal-btn') || e.target.closest('#dismiss-api-key-modal-btn')) {
        this.state.showApiKeyModal = false;
        this.render();
        return;
      }

      // Submit Query Button
      if (e.target.closest('#submit-query-btn')) {
        const textarea = document.getElementById('assistant-query-input');
        const query = textarea ? textarea.value.trim() : this.state.currentQuery;
        if (query) {
          this.handleQuerySubmit(query);
        }
        return;
      }

      // Clear Query Button
      if (e.target.closest('#clear-query-btn')) {
        this.state.currentQuery = '';
        const textarea = document.getElementById('assistant-query-input');
        if (textarea) textarea.value = '';
        return;
      }

      // Example Prompt Chips
      const promptChip = e.target.closest('[data-example]');
      if (promptChip) {
        const text = promptChip.getAttribute('data-example');
        this.state.currentQuery = text;
        const textarea = document.getElementById('assistant-query-input');
        if (textarea) textarea.value = text;
        this.handleQuerySubmit(text);
        return;
      }

      // Text-To-Speech Listen Button
      const ttsBtn = e.target.closest('.tts-listen-btn');
      if (ttsBtn) {
        const encodedText = ttsBtn.getAttribute('data-tts-text');
        if (encodedText) {
          const textToSpeak = decodeURIComponent(encodedText);
          this.playTts(textToSpeak, ttsBtn);
        }
        return;
      }

      // Text-To-Speech Stop Button
      const stopBtn = e.target.closest('.tts-stop-btn');
      if (stopBtn) {
        this.stopTts();
        return;
      }

      // Results Category Pill Click
      const catPill = e.target.closest('.category-pill');
      if (catPill) {
        const cat = catPill.getAttribute('data-cat');
        this.state.selectedCategory = cat;
        this.render();
        return;
      }

      // Clear search
      if (e.target.closest('#clear-search-btn') || e.target.closest('#reset-results-filters-btn')) {
        this.state.searchQuery = '';
        this.state.selectedCategory = 'all';
        this.render();
        return;
      }

      // Clear assistant filter in results
      if (e.target.closest('#clear-assistant-filter-btn')) {
        this.state.lastAssistantQuery = '';
        this.state.lastMatchedMap = {};
        this.state.selectedCategory = 'all';
        this.render();
        return;
      }

      // Reset All Results Filters
      if (e.target.closest('#reset-results-filters-btn')) {
        this.state.selectedCategory = 'all';
        this.state.selectedLevel = 'all';
        this.state.selectedState = 'all';
        this.state.selectedBeneficiary = 'all';
        this.state.searchQuery = '';
        this.state.lastAssistantQuery = '';
        this.state.lastMatchedMap = {};
        this.render();
        return;
      }

      // Clear Search Button
      if (e.target.closest('#clear-search-btn')) {
        this.state.searchQuery = '';
        this.render();
        return;
      }

      // Print Checklist Button
      if (e.target.closest('#print-checklist-btn')) {
        window.print();
        return;
      }

      // Download Text Checklist (.txt)
      if (e.target.closest('#downloadTextChecklistBtn')) {
        const saved = JSON.parse(localStorage.getItem('bharatsevai_checklist_state') || localStorage.getItem('nammasevai_checklist_state') || '{}');
        const defaultDocs = [
          { id: 'doc-1', name: 'College Bonafide Certificate & Student ID', authority: 'College office / Principal' },
          { id: 'doc-2', name: 'Aadhaar Card (Linked with Mobile & Bank DBT)', authority: 'UIDAI' },
          { id: 'doc-3', name: 'Class 10 & 12 Marksheets', authority: 'State Board / CBSE' },
          { id: 'doc-4', name: 'Bank Passbook Front Page (Clear IFSC & A/C)', authority: 'Scheduled Bank' },
          { id: 'doc-5', name: 'Community Certificate (சாதிச் சான்றிதழ்)', authority: 'Revenue Department / e-Sevai' },
          { id: 'doc-6', name: 'Income Certificate for Current FY (வருமானச் சான்றிதழ்)', authority: 'Revenue Department / Tahsildar' }
        ];

        let content = "=====================================================\n";
        content += "BHARATSEVAI AI — CITIZEN SCHEME PREPARATION CHECKLIST\n";
        content += "Generated: " + new Date().toLocaleString() + "\n";
        content += "=====================================================\n\n";
        content += "STATUS     | DOCUMENT NAME                                  | ISSUING AUTHORITY\n";
        content += "-----------------------------------------------------------------------------\n";
        let readyCount = 0;
        defaultDocs.forEach((d, idx) => {
          const isDone = saved[d.id] !== undefined ? saved[d.id] : idx < 4;
          if (isDone) readyCount++;
          const mark = isDone ? "[X] READY  " : "[ ] PENDING";
          content += `${mark} | ${d.name.padEnd(46)} | ${d.authority}\n`;
        });
        content += "-----------------------------------------------------------------------------\n";
        content += `Summary: ${readyCount} of ${defaultDocs.length} documents ready (${Math.round(readyCount / defaultDocs.length * 100)}% prepared)\n\n`;
        content += "PUBLIC-SERVICE GUIDANCE DISCLAIMER:\n";
        content += "This document checklist is generated for preliminary preparation guidance only.\n";
        content += "Official departments determine actual eligibility, document validity, and scheme approval.\n";
        content += "=====================================================\n";

        const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'bharatsevai_document_checklist.txt';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(link.href);
        return;
      }

      // Copy / Share Checklist
      if (e.target.closest('#copyShareChecklistBtn')) {
        const saved = JSON.parse(localStorage.getItem('bharatsevai_checklist_state') || localStorage.getItem('nammasevai_checklist_state') || '{}');
        const defaultDocs = [
          { id: 'doc-1', name: 'College Bonafide Certificate & Student ID' },
          { id: 'doc-2', name: 'Aadhaar Card (DBT Active)' },
          { id: 'doc-3', name: 'Class 10 & 12 Marksheets' },
          { id: 'doc-4', name: 'Bank Passbook (IFSC & A/C)' },
          { id: 'doc-5', name: 'Community Certificate (e-Sevai)' },
          { id: 'doc-6', name: 'Income Certificate (Revenue Dept)' }
        ];

        let readyCount = 0;
        let textSummary = "📋 BharatSevai AI Document Preparation Checklist:\n\n";
        defaultDocs.forEach((d, idx) => {
          const isDone = saved[d.id] !== undefined ? saved[d.id] : idx < 4;
          if (isDone) readyCount++;
          textSummary += (isDone ? "✅ " : "⏳ ") + d.name + (isDone ? " (Ready)" : " (Pending)") + "\n";
        });
        textSummary += `\nProgress: ${readyCount}/${defaultDocs.length} ready (${Math.round(readyCount / defaultDocs.length * 100)}% prepared).\n`;
        textSummary += "Guidance disclaimer: Preliminary preparation checklist. Final verification at official government desks.";

        if (navigator.share) {
          navigator.share({
            title: 'BharatSevai AI Scheme Checklist',
            text: textSummary
          }).catch(() => {});
        } else if (navigator.clipboard) {
          navigator.clipboard.writeText(textSummary).then(() => {
            alert("சரிபார்ப்பு பட்டியல் நகலெடுக்கப்பட்டது! / Checklist summary copied to clipboard!");
          }).catch(() => {
            alert(textSummary);
          });
        } else {
          alert(textSummary);
        }
        return;
      }

      // Header Privacy Badge Tooltip toggle for touch/click
      const privacyBadge = e.target.closest('.header-privacy-badge');
      if (privacyBadge) {
        privacyBadge.classList.toggle('active');
        return;
      } else {
        document.querySelectorAll('.header-privacy-badge.active').forEach(b => b.classList.remove('active'));
      }

      // Document Checklist item toggling
      const checklistItem = e.target.closest('.checklist-item');
      if (checklistItem && e.target.type !== 'checkbox') {
        const checkbox = checklistItem.querySelector('.checklist-checkbox');
        if (checkbox) {
          checkbox.checked = !checkbox.checked;
          checklistItem.classList.toggle('checked', checkbox.checked);
        }
        return;
      }

      // Dedicated Saved Checklist Page Item Toggling
      const interactiveDocItem = e.target.closest('.checklist-item-interactive');
      if (interactiveDocItem && e.target.type !== 'checkbox') {
        const checkbox = interactiveDocItem.querySelector('.interactive-doc-checkbox');
        if (checkbox) {
          checkbox.checked = !checkbox.checked;
          const id = checkbox.getAttribute('data-id');
          const saved = JSON.parse(localStorage.getItem('bharatsevai_checklist_state') || localStorage.getItem('nammasevai_checklist_state') || '{}');
          saved[id] = checkbox.checked;
          localStorage.setItem('bharatsevai_checklist_state', JSON.stringify(saved));
          localStorage.setItem('nammasevai_checklist_state', JSON.stringify(saved));
          this.render();
        }
        return;
      }

      const interactiveCheckbox = e.target.closest('.interactive-doc-checkbox');
      if (interactiveCheckbox) {
        const id = interactiveCheckbox.getAttribute('data-id');
        const saved = JSON.parse(localStorage.getItem('bharatsevai_checklist_state') || localStorage.getItem('nammasevai_checklist_state') || '{}');
        saved[id] = interactiveCheckbox.checked;
        localStorage.setItem('bharatsevai_checklist_state', JSON.stringify(saved));
        localStorage.setItem('nammasevai_checklist_state', JSON.stringify(saved));
        this.render();
        return;
      }

      // Reset All Checklist
      if (e.target.closest('#resetAllChecklist')) {
        localStorage.removeItem('bharatsevai_checklist_state');
        localStorage.removeItem('nammasevai_checklist_state');
        this.render();
        return;
      }

      // Admin Actions
      if (e.target.closest('#open-add-scheme-modal-btn')) {
        this.openSchemeModal();
        return;
      }
      if (e.target.closest('#open-bulk-import-modal-btn')) {
        this.openBulkImportModal();
        return;
      }
      if (e.target.closest('#close-bulk-modal-btn') || e.target.closest('#cancel-bulk-modal-btn')) {
        this.closeBulkImportModal();
        return;
      }
      if (e.target.closest('#load-sample-import-btn')) {
        this.loadSampleImportTemplate();
        return;
      }
      if (e.target.closest('#submit-bulk-import-btn')) {
        this.submitBulkImport();
        return;
      }
      if (e.target.closest('#close-modal-btn') || e.target.closest('#cancel-modal-btn')) {
        this.closeSchemeModal();
        return;
      }
      if (e.target.closest('#reset-schemes-btn')) {
        this.resetSchemes();
        return;
      }
      if (e.target.closest('#run-portal-health-btn')) {
        this.runPortalHealthCheck();
        return;
      }
      if (e.target.closest('#run-quality-benchmark-btn')) {
        this.runQualityBenchmark();
        return;
      }
      if (e.target.closest('#run-content-audit-btn')) {
        this.runContentAudit();
        return;
      }
      const reviewChangeBtn = e.target.closest('.review-change-btn');
      if (reviewChangeBtn) {
        const changeId = parseInt(reviewChangeBtn.getAttribute('data-change-id'), 10);
        this.reviewDetectedChange(changeId);
        return;
      }
      const toggleStatusBtn = e.target.closest('.toggle-status-btn');
      if (toggleStatusBtn) {
        const id = toggleStatusBtn.getAttribute('data-id');
        this.toggleSchemeStatus(id);
        return;
      }
      const editBtn = e.target.closest('.edit-scheme-btn');
      if (editBtn) {
        const id = editBtn.getAttribute('data-id');
        this.openSchemeModal(id);
        return;
      }
      const deleteBtn = e.target.closest('.delete-scheme-btn');
      if (deleteBtn) {
        const id = deleteBtn.getAttribute('data-id');
        this.deleteScheme(id);
        return;
      }
    });

    // Checkbox direct change
    appRoot.addEventListener('change', (e) => {
      if (e.target.classList.contains('checklist-checkbox')) {
        const item = e.target.closest('.checklist-item');
        if (item) item.classList.toggle('checked', e.target.checked);
      }
      if (e.target.id === 'admin-category-filter') {
        this.state.adminCategory = e.target.value;
        this.render();
      }
      if (e.target.id === 'admin-status-filter') {
        this.state.adminStatus = e.target.value;
        this.render();
      }
      if (e.target.id === 'scheme-level-select') {
        this.state.selectedLevel = e.target.value;
        this.render();
      }
      if (e.target.id === 'scheme-state-select') {
        this.state.selectedState = e.target.value;
        if (e.target.value && e.target.value !== 'all' && e.target.value !== 'All India') {
          this.state.userProfile = { ...(this.state.userProfile || {}), state: e.target.value };
          localStorage.setItem('bharatsevai_user_state', e.target.value);
        }
        this.render();
      }
      if (e.target.id === 'assistant-state-select') {
        const selVal = e.target.value;
        this.state.selectedState = selVal;
        if (selVal && selVal !== 'all') {
          this.state.userProfile = { ...(this.state.userProfile || {}), state: selVal };
          localStorage.setItem('bharatsevai_user_state', selVal);
        } else {
          if (this.state.userProfile) {
            delete this.state.userProfile.state;
          }
          localStorage.removeItem('bharatsevai_user_state');
        }
        this.render();
      }
      if (e.target.id === 'scheme-beneficiary-select') {
        this.state.selectedBeneficiary = e.target.value;
        this.render();
      }
      if (e.target.id === 'scheme-sort-select') {
        this.state.selectedSort = e.target.value;
        this.render();
      }
    });

    // Search input
    appRoot.addEventListener('input', (e) => {
      if (e.target.id === 'scheme-search-input') {
        this.state.searchQuery = e.target.value;
        this.updateSchemesGrid();
      }
      if (e.target.id === 'admin-search-input') {
        this.state.adminSearch = e.target.value;
        this.render();
      }
      if (e.target.id === 'assistant-query-input') {
        this.state.currentQuery = e.target.value;
      }
      if (e.target.id === 'fb-ease') {
        const span = document.getElementById('ease-val');
        const map = { 1: '1 / 5 (Difficult / புரியவில்லை)', 2: '2 / 5', 3: '3 / 5 (Moderate / சுமாரானது)', 4: '4 / 5', 5: '5 / 5 (Very Easy / மிக எளிது)' };
        if (span) span.innerText = map[e.target.value] || `${e.target.value} / 5`;
      }
      if (e.target.id === 'fb-clarity') {
        const span = document.getElementById('clarity-val');
        const map = { 1: '1 / 5 (Confusing / குழப்பமானது)', 2: '2 / 5', 3: '3 / 5 (Clear Enough / ஓரளவு தெளிவு)', 4: '4 / 5', 5: '5 / 5 (Very Clear / மிகத் தெளிவு)' };
        if (span) span.innerText = map[e.target.value] || `${e.target.value} / 5`;
      }
      if (e.target.id === 'fb-useful') {
        const span = document.getElementById('useful-val');
        const map = { 1: '1 / 5 (Not Useful / பயனில்லை)', 2: '2 / 5', 3: '3 / 5 (Somewhat Useful / பயனுள்ளது)', 4: '4 / 5', 5: '5 / 5 (Highly Useful / மிக பயனுள்ளது)' };
        if (span) span.innerText = map[e.target.value] || `${e.target.value} / 5`;
      }
    });

    // Enter key submit in assistant textarea
    appRoot.addEventListener('keydown', (e) => {
      if (e.target.id === 'assistant-query-input' && e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        const query = e.target.value.trim();
        if (query) this.handleQuerySubmit(query);
      }
    });

    // Form submit in Modal & Feedback
    appRoot.addEventListener('submit', (e) => {
      if (e.target.id === 'scheme-form') {
        e.preventDefault();
        this.saveModalScheme();
      }
      if (e.target.id === 'citizen-pilot-feedback-form') {
        e.preventDefault();
        this.handleFeedbackSubmit();
      }
    });

    // Close Language Dropdown when clicking outside
    document.addEventListener('click', (e) => {
      const wrapper = document.getElementById('lang-dropdown-wrapper');
      if (wrapper && wrapper.classList.contains('open') && !e.target.closest('#lang-dropdown-wrapper')) {
        wrapper.classList.remove('open');
        const btn = document.getElementById('lang-dropdown-btn');
        if (btn) btn.setAttribute('aria-expanded', 'false');
      }
    });

    // Close Language Dropdown on Escape key & Arrow navigation
    document.addEventListener('keydown', (e) => {
      const wrapper = document.getElementById('lang-dropdown-wrapper');
      if (!wrapper || !wrapper.classList.contains('open')) return;

      if (e.key === 'Escape') {
        wrapper.classList.remove('open');
        const btn = document.getElementById('lang-dropdown-btn');
        if (btn) {
          btn.setAttribute('aria-expanded', 'false');
          btn.focus();
        }
        return;
      }

      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        const items = Array.from(wrapper.querySelectorAll('.lang-dropdown-item'));
        if (items.length === 0) return;
        e.preventDefault();
        const activeIdx = items.indexOf(document.activeElement);
        let nextIdx = 0;
        if (e.key === 'ArrowDown') {
          nextIdx = activeIdx >= 0 ? (activeIdx + 1) % items.length : 0;
        } else {
          nextIdx = activeIdx > 0 ? (activeIdx - 1) % items.length : items.length - 1;
        }
        items[nextIdx].focus();
      }
    });
  }

  handleMicClick() {
    if (this.state.isListening) {
      this.speechService.stopListening();
      this.state.isListening = false;
      this.render();
      return;
    }

    // Check privacy consent first (Requirement 6: "Ask permission before recording")
    if (!this.state.micConsentGiven) {
      this.state.showMicConsentModal = true;
      this.render();
      return;
    }

    this.startVoiceRecording();
  }

  startVoiceRecording() {
    const lang = this.state.assistantLang || this.state.lang || 'ta';

    this.speechService.startListening({
      lang,
      onStart: () => {
        this.state.isListening = true;
        this.render();
      },
      onTranscript: (transcript, isFinal) => {
        this.state.currentQuery = transcript;
        const textarea = document.getElementById('assistant-query-input');
        if (textarea) textarea.value = transcript;

        if (isFinal) {
          this.state.isListening = false;
          this.handleQuerySubmit(transcript);
        }
      },
      onError: (err) => {
        this.state.isListening = false;
        alert("குரல் பதிவில் தகவல் / Speech recognition notice: " + err + ". நீங்கள் நேரடியாக கீழே தட்டச்சு செய்து கேட்கலாம் / You can also type your query directly.");
        this.render();
      },
      onEnd: () => {
        this.state.isListening = false;
        this.render();
      }
    });
  }

  async handleQuerySubmit(query) {
    if (!query || !query.trim()) return;

    const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Push user message
    this.state.chatHistory.push({
      sender: 'user',
      text: query,
      time: currentTime
    });

    this.state.currentQuery = '';
    this.render();

    let matches = [];
    let responseText = "";
    let followUpsEn = [];
    let followUpsTa = [];
    let followUpsHi = [];
    let followUpsMl = [];

    // Attempt real backend call to /api/assistant/match
    try {
      const activeLang = this.state.assistantLang || this.state.lang || 'ta';
      const res = await fetch('/api/assistant/match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          lang: activeLang,
          profile: this.state.userProfile || {}
        })
      });

      if (res.ok) {
        const data = await res.json();
        matches = data.matches || [];
        followUpsEn = data.follow_up_questions_en || [];
        followUpsTa = data.follow_up_questions_ta || [];
        followUpsHi = data.follow_up_questions_hi || [];
        followUpsMl = data.follow_up_questions_ml || [];

        const detectedProf = data.extracted_profile || data.detected_profile;
        if (detectedProf) {
          this.state.userProfile = {
            ...(this.state.userProfile || {}),
            ...detectedProf
          };
          if (detectedProf.state) {
            this.state.selectedState = detectedProf.state;
            localStorage.setItem('bharatsevai_user_state', detectedProf.state);
          }
        }

        // Save matched map for schemes results page
        this.state.lastAssistantQuery = query;
        this.state.lastMatchedMap = {};
        for (const item of matches) {
          this.state.lastMatchedMap[item.scheme_id] = {
            matchPercent: item.match_confidence,
            status: item.match_status,
            reasonEn: item.eligibility_explanation_en,
            reasonTa: item.eligibility_explanation_ta,
            reasonHi: item.eligibility_explanation_hi,
            reasonMl: item.eligibility_explanation_ml
          };
        }

        // Formulate response text
        const curLang = activeLang;
        if (data.compassionate_response) {
          responseText = data.compassionate_response;
        } else if (matches.length > 0) {
          const top = matches[0];
          let name = top.scheme_name_en;
          let benefit = top.benefit_summary_en;

          if (curLang === 'ta') {
            name = top.scheme_name_ta || top.scheme_name_en;
            benefit = top.benefit_summary_ta || top.benefit_summary_en;
            responseText = `உங்கள் தேவையை ஆய்வு செய்து ${matches.length} சாத்தியமான அரசு நலத்திட்டங்களை கண்டறிந்துள்ளேன். முதன்மையான திட்டம் "${name}" (பலன்: ${benefit}). கீழே உள்ள விவரங்களை சரிபார்க்கவும்.`;
          } else if (curLang === 'tanglish') {
            name = top.scheme_name_ta || top.scheme_name_en;
            benefit = top.benefit_summary_ta || top.benefit_summary_en;
            responseText = `Unga situation-ah analyze panni ${matches.length} matching welfare schemes kandupidichirukken. Top scheme "${name}" (Benefit: ${benefit}). Keela irukkira eligibility rules & documents check pannunga.`;
          } else if (curLang === 'hi') {
            name = top.scheme_name_hi || top.scheme_name_en;
            benefit = top.benefit_summary_hi || top.benefit_summary_en;
            responseText = `आपकी जानकारी का विश्लेषण कर ${matches.length} संभावित सरकारी कल्याणकारी योजनाओं की पहचान की गई है। प्रमुख योजना "${name}" (लाभ: ${benefit}) है। कृपया नीचे पात्रता और आवश्यक दस्तावेज़ देखें।`;
          } else if (curLang === 'hinglish') {
            name = top.scheme_name_hi || top.scheme_name_en;
            benefit = top.benefit_summary_hi || top.benefit_summary_en;
            responseText = `Aapki profile analyze karke ${matches.length} matching welfare schemes identify hui hain. Top scheme "${name}" (Benefit: ${benefit}) hai. Kripya neeche eligibility rules aur documents verify karein.`;
          } else if (curLang === 'ml') {
            name = top.scheme_name_ml || top.scheme_name_en;
            benefit = top.benefit_summary_ml || top.benefit_summary_en;
            responseText = `നിങ്ങളുടെ വിവരങ്ങൾ വിശകലനം ചെയ്ത് ${matches.length} സാധ്യമായ സർക്കാർ ക്ഷേമപദ്ധതികൾ കണ്ടെത്തി. പ്രധാന പദ്ധതി "${name}" (പ്രയോജനം: ${benefit}) ആണ്. താഴെ നൽകിയിട്ടുള്ള യോഗ്യതാ വ്യവസ്ഥകൾ പരിശോധിക്കുക.`;
          } else {
            responseText = `I analyzed your profile and discovered ${matches.length} potential welfare schemes. The top recommendation is "${name}" (${benefit}). Please verify the eligibility rules and documents below.`;
          }
        } else {
          if (curLang === 'ta') {
            responseText = "உங்கள் தகவலுக்கு நேரடி திட்டம் எதுவும் கிடைக்கவில்லை. உங்கள் படிப்பு, தொழில், நில அளவு போன்ற விவரங்களை குறிப்பிட்டு மீண்டும் கேட்கவும்.";
          } else if (curLang === 'tanglish') {
            responseText = "Unga details-kku direct scheme match aagala. Unga education, land, income, or velai pathi innum konjam sollunga.";
          } else if (curLang === 'hi') {
            responseText = "आपकी वर्तमान जानकारी से कोई प्रत्यक्ष योजना मेल नहीं खाती। कृपया अपनी शिक्षा, व्यवसाय या आय का अतिरिक्त विवरण प्रदान करें।";
          } else if (curLang === 'hinglish') {
            responseText = "Aapki details se matching koi direct scheme nahi mili. Kripya apni education, zameen, income ya occupation ke baare mein thoda aur batayein.";
          } else if (curLang === 'ml') {
            responseText = "നിങ്ങളുടെ വിവരങ്ങൾക്ക് അനുയോജ്യമായ നേരിട്ടുള്ള പദ്ധതിയൊന്നും കണ്ടെത്തിയില്ല. ദയവായി നിങ്ങളുടെ വിദ്യാഭ്യാസം, തൊഴിൽ എന്നിവയെക്കുറിച്ചുള്ള കൂടുതൽ വിവരങ്ങൾ നൽകുക.";
          } else {
            responseText = "No exact schemes matched your description. Please provide more details about your education, farming, or occupation.";
          }
        }
      } else {
        throw new Error("Backend response error");
      }
    } catch (err) {
      console.warn("Backend API unavailable, using local high-precision NLP matcher:", err);
      // Client-side fallback matching
      const matchResult = this.matcher.match(query, this.state.lang);
      matches = matchResult.matches;
      responseText = matchResult.responseMessage;

      this.state.lastAssistantQuery = query;
      this.state.lastMatchedMap = {};
      for (const item of matches) {
        this.state.lastMatchedMap[item.scheme.id] = item;
      }
    }

    // Push AI response
    this.state.chatHistory.push({
      sender: 'ai',
      text: responseText,
      time: currentTime,
      matches: matches,
      follow_ups_en: followUpsEn,
      follow_ups_ta: followUpsTa,
      follow_ups_hi: followUpsHi,
      follow_ups_ml: followUpsMl,
      extracted_profile: this.state.userProfile || {}
    });

    this.render();

    // Auto-scroll chat to latest message
    setTimeout(() => {
      const area = document.getElementById('chat-conversation-area');
      if (area) area.scrollTop = area.scrollHeight;
    }, 100);
  }

  async playTts(text, buttonElement) {
    this.stopTts();
    const lang = this.state.lang;

    // Toggle button UI to playing state
    if (buttonElement) {
      buttonElement.innerHTML = `<span>🔊 பேச்சைக் கேட்கிறது...</span>`;
      const stopBtn = buttonElement.parentElement.querySelector('.tts-stop-btn');
      if (stopBtn) stopBtn.style.display = 'inline-flex';
    }
    this.state.isSpeaking = true;

    // 1. Try backend TTS endpoint (/api/voice/synthesize with gTTS)
    try {
      const res = await fetch('/api/voice/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, lang })
      });

      if (res.ok) {
        const blob = await res.blob();
        const audioUrl = URL.createObjectURL(blob);
        this.currentAudioPlayer = new Audio(audioUrl);

        this.currentAudioPlayer.onended = () => {
          this.resetTtsButtons();
        };
        this.currentAudioPlayer.onerror = () => {
          this.fallbackNativeTts(text, lang, buttonElement);
        };

        await this.currentAudioPlayer.play();
        return;
      }
    } catch (e) {
      console.log("Backend TTS unavailable, falling back to Web SpeechSynthesis:", e);
    }

    // 2. Fallback to browser Web SpeechSynthesis
    this.fallbackNativeTts(text, lang, buttonElement);
  }

  fallbackNativeTts(text, lang, buttonElement) {
    this.speechService.speak(text, lang, {
      onStart: () => {
        this.state.isSpeaking = true;
      },
      onEnd: () => {
        this.resetTtsButtons();
      },
      onError: () => {
        this.resetTtsButtons();
      }
    });
  }

  stopTts() {
    if (this.currentAudioPlayer) {
      this.currentAudioPlayer.pause();
      this.currentAudioPlayer.currentTime = 0;
      this.currentAudioPlayer = null;
    }
    this.speechService.stopSpeaking();
    this.resetTtsButtons();
  }

  resetTtsButtons() {
    this.state.isSpeaking = false;
    const isTa = this.state.lang === 'ta';
    document.querySelectorAll('.tts-listen-btn').forEach(btn => {
      btn.innerHTML = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg><span>${isTa ? "குரலில் கேட்கவும் (Speak)" : "Speak"}</span>`;
    });
    document.querySelectorAll('.tts-stop-btn').forEach(btn => {
      btn.style.display = 'none';
    });
  }

  updateSchemesGrid() {
    const container = document.querySelector('.results-page-container');
    if (container) {
      const parent = container.parentNode;
      const temp = document.createElement('div');
      temp.innerHTML = renderResultsPage(this.state);
      parent.replaceChild(temp.firstElementChild, container);

      const searchInput = document.getElementById('scheme-search-input');
      if (searchInput) {
        searchInput.focus();
        searchInput.setSelectionRange(searchInput.value.length, searchInput.value.length);
      }
    }
  }

  // Admin Scheme Actions
  openSchemeModal(schemeId = null) {
    const modal = document.getElementById('scheme-modal');
    if (!modal) return;

    const titleText = document.getElementById('modal-title-text');
    const idField = document.getElementById('form-scheme-id');
    const nameEn = document.getElementById('form-name-en');
    const nameTa = document.getElementById('form-name-ta');
    const deptEn = document.getElementById('form-dept-en');
    const deptTa = document.getElementById('form-dept-ta');
    const cat = document.getElementById('form-category');
    const status = document.getElementById('form-status');
    const benEn = document.getElementById('form-benefit-en');
    const benTa = document.getElementById('form-benefit-ta');
    const descEn = document.getElementById('form-desc-en');
    const descTa = document.getElementById('form-desc-ta');
    const crit = document.getElementById('form-criteria');
    const docs = document.getElementById('form-docs');
    const portal = document.getElementById('form-portal');
    const levelEl = document.getElementById('form-level');
    const stateEl = document.getElementById('form-state');
    const benEl = document.getElementById('form-beneficiaries');

    if (schemeId) {
      const scheme = this.state.schemes.find(s => s.id === schemeId);
      if (scheme) {
        titleText.textContent = "நலத்திட்ட விவரங்களை திருத்த (Edit Scheme)";
        idField.value = scheme.id;
        nameEn.value = scheme.name || '';
        nameTa.value = scheme.name_ta || '';
        deptEn.value = scheme.department || '';
        deptTa.value = scheme.department_ta || '';
        cat.value = scheme.category || 'education';
        status.value = scheme.source_verification || 'verified';
        benEn.value = scheme.benefit_summary || '';
        benTa.value = scheme.benefit_summary_ta || '';
        descEn.value = scheme.description || '';
        descTa.value = scheme.description_ta || '';
        crit.value = (scheme.eligibility_criteria || []).join('\n');
        docs.value = (scheme.required_documents || []).map(d => d.name || d.name_en).join('\n');
        portal.value = scheme.official_portal || '';
        if (levelEl) levelEl.value = scheme.level || 'State';
        if (stateEl) stateEl.value = scheme.state || 'Tamil Nadu';
        if (benEl) benEl.value = (scheme.target_beneficiaries || []).join(', ');
      }
    } else {
      titleText.textContent = "புதிய அரசு நலத்திட்டத்தை சேர்க்க (Add New Scheme)";
      idField.value = '';
      document.getElementById('scheme-form').reset();
      if (levelEl) levelEl.value = 'State';
      if (stateEl) stateEl.value = 'Tamil Nadu';
      if (benEl) benEl.value = '';
    }

    modal.classList.add('open');
  }

  closeSchemeModal() {
    const modal = document.getElementById('scheme-modal');
    if (modal) modal.classList.remove('open');
  }

  // Bulk Import Modal Handlers
  openBulkImportModal() {
    const modal = document.getElementById('bulk-import-modal');
    if (!modal) return;
    const res = document.getElementById('bulk-import-result');
    if (res) res.style.display = 'none';
    modal.style.display = 'flex';
  }

  closeBulkImportModal() {
    const modal = document.getElementById('bulk-import-modal');
    if (modal) modal.style.display = 'none';
  }

  loadSampleImportTemplate() {
    const formatEl = document.querySelector('input[name="bulk-import-format"]:checked');
    const format = formatEl ? formatEl.value : 'json';
    const contentEl = document.getElementById('bulk-import-content');
    if (!contentEl) return;

    if (format === 'json') {
      contentEl.value = JSON.stringify([
        {
          "id": "pm-kisan-national",
          "name": "Pradhan Mantri Kisan Samman Nidhi",
          "name_ta": "பிரதமர் கிசான் சம்மான் நிதி",
          "name_hi": "प्रधानमंत्री किसान सम्मान निधि",
          "name_ml": "പ്രധാനമന്ത്രി കിസാൻ സമ്മാൻ നിധി",
          "department": "Ministry of Agriculture and Farmers Welfare",
          "department_ta": "வேளாண்மை மற்றும் உழவர் நல அமைச்சகம்",
          "category": "agriculture",
          "level": "Central",
          "state": "All India",
          "benefit_amount": "₹6,000 / year in 3 equal installments",
          "benefit_summary": "₹6,000 per year direct income support in three 4-monthly installments of ₹2,000",
          "description": "Central Sector Scheme to augment the income of all landholding farmer families across the country.",
          "official_portal": "https://pmkisan.gov.in",
          "source_name": "Ministry of Agriculture, Government of India",
          "source_verification": "verified",
          "eligibility_criteria": ["Cultivable landholding in own name", "Registered on PM-Kisan portal", "Aadhaar seeded bank account"],
          "required_documents": ["Aadhaar Card", "Land Ownership Record (Patta/Chitta/Khasra)", "Bank Account Details"]
        }
      ], null, 2);
    } else {
      contentEl.value = `name,level,state,category,department,benefit_amount,official_portal,source_name
Pradhan Mantri Awas Yojana (Urban),Central,All India,housing,Ministry of Housing and Urban Affairs,Up to ₹2.67 Lakhs interest subsidy,https://pmay-urban.gov.in,Ministry of Housing and Urban Affairs
Kanya Sumangala Yojana,State,Uttar Pradesh,women,Department of Women and Child Development,₹15000 conditional grant,https://mksy.up.gov.in,Government of Uttar Pradesh`;
    }
  }

  async submitBulkImport() {
    const contentEl = document.getElementById('bulk-import-content');
    const resEl = document.getElementById('bulk-import-result');
    const submitBtn = document.getElementById('submit-bulk-import-btn');
    const formatEl = document.querySelector('input[name="bulk-import-format"]:checked');
    const skipDupEl = document.getElementById('bulk-skip-duplicates');

    if (!contentEl || !contentEl.value.trim()) {
      alert("Please enter JSON or CSV scheme records to import.");
      return;
    }

    const isJson = (formatEl ? formatEl.value : 'json') === 'json';
    const allowOverwrite = !(skipDupEl ? skipDupEl.checked : true);
    let payload;
    if (isJson) {
      try {
        const parsed = JSON.parse(contentEl.value.trim());
        payload = {
          records: Array.isArray(parsed) ? parsed : [parsed],
          allow_overwrite: allowOverwrite
        };
      } catch (err) {
        alert("Invalid JSON format: " + err.message);
        return;
      }
    } else {
      payload = {
        csv_content: contentEl.value.trim(),
        allow_overwrite: allowOverwrite
      };
    }

    const adminKey = localStorage.getItem('bharatsevai_admin_key') || localStorage.getItem('nammasevai_admin_key') || 'nammasevai-admin-secret-2026';
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="material-symbols-outlined spin" style="font-size: 18px;">sync</span> Validating...';
    }

    try {
      const resp = await fetch('/api/admin/schemes/import', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Admin-Key': adminKey
        },
        body: JSON.stringify(payload)
      });

      const report = await resp.json();
      if (resEl) {
        resEl.style.display = 'block';
        if (resp.ok) {
          resEl.style.background = 'rgba(21, 128, 61, 0.1)';
          resEl.style.border = '1px solid rgba(21, 128, 61, 0.3)';
          resEl.style.color = 'var(--tertiary-green)';
          resEl.innerHTML = `
            <strong>Bulk Import Complete:</strong><br>
            &bull; Total Processed: <strong>${report.total_processed}</strong> records<br>
            &bull; New Schemes Added: <strong>${report.imported}</strong><br>
            &bull; Existing Skipped (Duplicates): <strong>${report.duplicates}</strong><br>
            &bull; Invalid Records: <strong>${report.invalid}</strong><br>
            &bull; Failed: <strong>${report.failed}</strong>
            ${report.details && report.details.length > 0 ? `<div style="margin-top: 0.5rem; max-height: 120px; overflow-y: auto; font-size: 0.75rem; border-top: 1px solid var(--border-color); padding-top: 0.35rem;">${report.details.map(d => `<div>${d.action === 'imported' ? '✓' : d.action === 'duplicate' ? '↷' : '✕'} [${d.id || 'N/A'}] ${d.name}: ${d.message}</div>`).join('')}</div>` : ''}
          `;
          // Reload schemes
          await this.loadSchemes();
          this.render();
        } else {
          resEl.style.background = 'rgba(220, 38, 38, 0.1)';
          resEl.style.border = '1px solid rgba(220, 38, 38, 0.3)';
          resEl.style.color = '#dc2626';
          resEl.innerHTML = `<strong>Import Failed:</strong> ${report.detail || "Server error"}`;
        }
      }
    } catch (e) {
      if (resEl) {
        resEl.style.display = 'block';
        resEl.style.background = 'rgba(220, 38, 38, 0.1)';
        resEl.style.border = '1px solid rgba(220, 38, 38, 0.3)';
        resEl.style.color = '#dc2626';
        resEl.innerHTML = `<strong>Network Error:</strong> ${e.message}`;
      }
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span class="material-symbols-outlined" style="font-size: 18px;">cloud_upload</span> Validate & Import';
      }
    }
  }

  async saveModalScheme() {
    const id = document.getElementById('form-scheme-id').value;
    const nameEn = document.getElementById('form-name-en').value.trim();
    const nameTa = document.getElementById('form-name-ta').value.trim();
    const deptEn = document.getElementById('form-dept-en').value.trim();
    const deptTa = document.getElementById('form-dept-ta').value.trim();
    const cat = document.getElementById('form-category').value;
    const status = document.getElementById('form-status').value;
    const benEn = document.getElementById('form-benefit-en').value.trim();
    const benTa = document.getElementById('form-benefit-ta').value.trim();
    const descEn = document.getElementById('form-desc-en').value.trim();
    const descTa = document.getElementById('form-desc-ta').value.trim();
    const critText = document.getElementById('form-criteria').value.trim();
    const docsText = document.getElementById('form-docs').value.trim();
    const portal = document.getElementById('form-portal').value.trim();
    const levelVal = document.getElementById('form-level') ? document.getElementById('form-level').value : 'State';
    const stateVal = document.getElementById('form-state') ? document.getElementById('form-state').value.trim() : 'Tamil Nadu';
    const benVal = document.getElementById('form-beneficiaries') ? document.getElementById('form-beneficiaries').value.trim() : '';

    const criteria = critText ? critText.split('\n').map(s => s.trim()).filter(Boolean) : [];
    const docItems = docsText ? docsText.split('\n').map(s => s.trim()).filter(Boolean).map(name => ({
      name,
      name_en: name,
      name_ta: name,
      mandatory: true,
      is_mandatory: true
    })) : [];

    const schemePayload = {
      id: id || 'scheme-' + Date.now(),
      name: nameEn,
      name_ta: nameTa,
      department: deptEn,
      department_ta: deptTa,
      category: cat,
      level: levelVal,
      state: stateVal,
      target_beneficiaries: benVal ? benVal.split(',').map(s => s.trim()).filter(Boolean) : [],
      benefit_summary: benEn,
      benefit_summary_ta: benTa,
      benefit_amount: benEn,
      description: descEn,
      description_ta: descTa,
      is_active: true,
      conditions: criteria.map(c => ({
        field_name: "custom_rule",
        operator: "eq",
        expected_value: "met",
        is_mandatory: true,
        description_en: c,
        description_ta: c
      })),
      documents: docItems,
      steps: [
        {
          step_number: 1,
          mode: "online",
          title_en: "Online Portal Application",
          title_ta: "இணையதள விண்ணப்பம்",
          description_en: "Apply via " + portal,
          description_ta: portal + " வழியாக விண்ணப்பிக்கலாம்."
        }
      ],
      source: {
        source_name: levelVal === 'Central' ? "National Government Portal" : (stateVal + " Government Portal"),
        portal_url: portal,
        verified_date: new Date().toISOString().split('T')[0],
        verification_status: status
      }
    };

    // Try posting to backend
    const adminKey = localStorage.getItem('bharatsevai_admin_key') || localStorage.getItem('nammasevai_admin_key') || 'nammasevai-admin-secret-2026';
    try {
      if (id) {
        await fetch(`/api/admin/schemes/${id}`, {
          method: 'PUT',
          headers: { 
            'Content-Type': 'application/json',
            'X-Admin-Key': adminKey
          },
          body: JSON.stringify(schemePayload)
        });
      } else {
        await fetch('/api/admin/schemes', {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'X-Admin-Key': adminKey
          },
          body: JSON.stringify(schemePayload)
        });
      }
    } catch (e) {
      console.log("Backend offline, updating local cache:", e);
    }

    // Update local state
    if (id) {
      const idx = this.state.schemes.findIndex(s => s.id === id);
      if (idx !== -1) this.state.schemes[idx] = schemePayload;
    } else {
      this.state.schemes.unshift(schemePayload);
    }

    this.saveSchemes();
    this.closeSchemeModal();
    this.render();
  }

  async toggleSchemeStatus(id) {
    const adminKey = localStorage.getItem('bharatsevai_admin_key') || localStorage.getItem('nammasevai_admin_key') || 'nammasevai-admin-secret-2026';
    try {
      await fetch(`/api/admin/schemes/${id}/toggle-status`, { 
        method: 'POST',
        headers: { 'X-Admin-Key': adminKey }
      });
    } catch (e) {
      console.log("Toggling locally:", e);
    }

    const scheme = this.state.schemes.find(s => s.id === id);
    if (scheme) {
      scheme.source_verification = scheme.source_verification === 'verified' ? 'pending' : 'verified';
      this.saveSchemes();
      this.render();
    }
  }

  async deleteScheme(id) {
    const scheme = this.state.schemes.find(s => s.id === id);
    if (!scheme) return;

    if (confirm(`Delete scheme "${scheme.name}"?`)) {
      const adminKey = localStorage.getItem('bharatsevai_admin_key') || localStorage.getItem('nammasevai_admin_key') || 'nammasevai-admin-secret-2026';
      try {
        await fetch(`/api/admin/schemes/${id}`, { 
          method: 'DELETE',
          headers: { 'X-Admin-Key': adminKey }
        });
      } catch (e) {
        console.log("Deleting locally:", e);
      }

      this.state.schemes = this.state.schemes.filter(s => s.id !== id);
      this.saveSchemes();
      this.render();
    }
  }

  async handleFeedbackSubmit() {
    const btn = document.getElementById('submit-feedback-btn');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<span class="material-symbols-outlined" style="font-size: 18px; animation: spin 1s linear infinite;">sync</span> Submitting...`;
    }

    const category = document.getElementById('fb-category')?.value || null;
    const language = document.getElementById('fb-language')?.value || this.state.lang || 'ta';
    const ease = parseInt(document.getElementById('fb-ease')?.value || '5', 10);
    const clarity = parseInt(document.getElementById('fb-clarity')?.value || '5', 10);
    const useful = parseInt(document.getElementById('fb-useful')?.value || '5', 10);
    const problems = document.getElementById('fb-problems')?.value?.trim() || null;
    const suggestions = document.getElementById('fb-suggestions')?.value?.trim() || null;

    try {
      const res = await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          participant_category: category,
          preferred_language: language,
          ease_of_use_rating: ease,
          clarity_rating: clarity,
          usefulness_rating: useful,
          problems_encountered: problems,
          suggestions: suggestions
        })
      });

      if (res.ok) {
        const form = document.getElementById('citizen-pilot-feedback-form');
        const banner = document.getElementById('feedback-success-banner');
        if (form) form.style.display = 'none';
        if (banner) banner.style.display = 'block';
      } else {
        const err = await res.json();
        alert(err.detail || "Error submitting feedback. Please try again.");
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = `<span class="material-symbols-outlined" style="font-size: 18px;">send</span> Submit Voluntary Feedback`;
        }
      }
    } catch (e) {
      console.error("Feedback submission error:", e);
      alert("Network error submitting feedback. Please check connection.");
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = `<span class="material-symbols-outlined" style="font-size: 18px;">send</span> Submit Voluntary Feedback`;
      }
    }
  }

  render() {
    const appRoot = document.getElementById('app-root');
    if (!appRoot) return;

    let pageHtml = '';

    switch (this.state.route) {
      case 'landing':
        pageHtml = renderLandingPage(this.state);
        break;
      case 'assistant':
        pageHtml = renderAssistantPage(this.state);
        break;
      case 'schemes':
        pageHtml = renderResultsPage(this.state);
        break;
      case 'scheme-details':
        const currentScheme = this.state.schemes.find(s => s.id === this.state.schemeDetailsId);
        pageHtml = renderDetailsPage(currentScheme, this.state);
        break;
      case 'checklist':
        pageHtml = renderChecklistPage(this.state);
        break;
      case 'feedback':
        pageHtml = renderFeedbackPage(this.state);
        break;
      case 'admin':
        if (!this.state.aiProvidersStatusLoaded) {
          this.state.aiProvidersStatusLoaded = true;
          fetch('/api/assistant/provider-status')
            .then(r => r.ok ? r.json() : null)
            .then(data => {
              if (data) {
                this.state.aiProvidersStatus = data;
                this.render();
              }
            }).catch(() => {});
        }
        if (!this.state.contentSummaryLoaded) {
          this.state.contentSummaryLoaded = true;
          this.loadContentMonitoringSummary();
        }
        pageHtml = renderAdminPage(this.state);
        break;
      default:
        pageHtml = renderLandingPage(this.state);
    }

    appRoot.innerHTML = `
      ${renderNavbar(this.state)}
      <main id="main-content" style="flex: 1;">
        ${pageHtml}
      </main>
      ${renderFooter(this.state)}
    `;
  }
}

// Bootstrap application on DOM load
document.addEventListener('DOMContentLoaded', () => {
  window.bharatSevaiApp = window.nammaSevaiApp = new App();
});
