// NammaSevai AI - Main Application Controller with Real Voice & AI Backend Integration
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
import { renderAdminPage } from './components/adminPage.js';

class App {
  constructor() {
    this.speechService = new SpeechService();
    this.currentAudioPlayer = null;

    this.state = {
      lang: localStorage.getItem('nammasevai_lang') || 'ta',
      assistantLang: 'ta',
      route: 'landing',
      schemeDetailsId: null,
      schemes: this.loadSchemes(),
      currentQuery: '',
      chatHistory: [],
      selectedCategory: 'all',
      searchQuery: '',
      lastAssistantQuery: '',
      lastMatchedMap: {},
      isListening: false,
      isSpeaking: false,
      adminSearch: '',
      adminCategory: 'all',
      adminStatus: 'all',
      
      // Privacy and Voice Features
      micConsentGiven: localStorage.getItem('nammasevai_mic_consent') === 'true',
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
    const saved = localStorage.getItem('nammasevai_schemes');
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
      const res = await fetch('/api/schemes');
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
    } else if (['landing', 'assistant', 'schemes', 'admin'].includes(hash)) {
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
    localStorage.setItem('nammasevai_lang', lang);
    this.render();
  }

  attachGlobalEvents() {
    const appRoot = document.getElementById('app-root');

    appRoot.addEventListener('click', (e) => {
      // Language Toggle in Navbar
      if (e.target.closest('#lang-toggle-btn')) {
        const nextLang = this.state.lang === 'ta' ? 'en' : 'ta';
        this.setLanguage(nextLang);
        return;
      }

      // Mobile Menu Toggle
      if (e.target.closest('#mobile-toggle')) {
        const menu = document.getElementById('nav-menu');
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

      // Print Checklist Button
      if (e.target.closest('#print-checklist-btn')) {
        window.print();
        return;
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

      // Admin Actions
      if (e.target.closest('#open-add-scheme-modal-btn')) {
        this.openSchemeModal();
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
    });

    // Enter key submit in assistant textarea
    appRoot.addEventListener('keydown', (e) => {
      if (e.target.id === 'assistant-query-input' && e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        const query = e.target.value.trim();
        if (query) this.handleQuerySubmit(query);
      }
    });

    // Form submit in Modal
    appRoot.addEventListener('submit', (e) => {
      if (e.target.id === 'scheme-form') {
        e.preventDefault();
        this.saveModalScheme();
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
    const lang = this.state.assistantLang === 'en' ? 'en' : 'ta';

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
        alert("குரல் பதிவில் பிழை / Microphone issue: " + err + ". தயவுசெய்து தட்டச்சு செய்யவும்.");
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

    // Attempt real backend call to /api/assistant/match
    try {
      const res = await fetch('/api/assistant/match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          lang: this.state.lang
        })
      });

      if (res.ok) {
        const data = await res.json();
        matches = data.matches || [];
        followUpsEn = data.follow_up_questions_en || [];
        followUpsTa = data.follow_up_questions_ta || [];

        // Save matched map for schemes results page
        this.state.lastAssistantQuery = query;
        this.state.lastMatchedMap = {};
        for (const item of matches) {
          this.state.lastMatchedMap[item.scheme_id] = {
            matchPercent: item.match_confidence,
            status: item.match_status,
            reasonEn: item.eligibility_explanation_en,
            reasonTa: item.eligibility_explanation_ta
          };
        }

        // Formulate response text
        const isTa = this.state.lang === 'ta';
        if (matches.length > 0) {
          const top = matches[0];
          const name = isTa ? top.scheme_name_ta : top.scheme_name_en;
          const benefit = isTa ? top.benefit_summary_ta : top.benefit_summary_en;
          
          if (isTa) {
            responseText = `உங்கள் தேவையை ஆய்வு செய்து ${matches.length} சாத்தியமான அரசு நலத்திட்டங்களை கண்டறிந்துள்ளேன். முதன்மையான திட்டம் "${name}" (பலன்: ${benefit}). கீழே உள்ள விவரங்களை சரிபார்க்கவும்.`;
          } else {
            responseText = `I analyzed your profile and discovered ${matches.length} potential welfare schemes. The top recommendation is "${name}" (${benefit}). Please verify the eligibility rules and documents below.`;
          }
        } else {
          responseText = isTa
            ? "உங்கள் தகவலுக்கு நேரடி திட்டம் எதுவும் கிடைக்கவில்லை. உங்கள் படிப்பு, தொழில், நில அளவு போன்ற விவரங்களை குறிப்பிட்டு மீண்டும் கேட்கவும்."
            : "No exact schemes matched your description. Please provide more details about your education, farming, or occupation.";
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
      follow_ups_ta: followUpsTa
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
      }
    } else {
      titleText.textContent = "புதிய அரசு நலத்திட்டத்தை சேர்க்க (Add New Scheme)";
      idField.value = '';
      document.getElementById('scheme-form').reset();
    }

    modal.classList.add('open');
  }

  closeSchemeModal() {
    const modal = document.getElementById('scheme-modal');
    if (modal) modal.classList.remove('open');
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
        source_name: "Tamil Nadu Government Portal",
        portal_url: portal,
        verified_date: new Date().toISOString().split('T')[0],
        verification_status: status
      }
    };

    // Try posting to backend
    const adminKey = localStorage.getItem('nammasevai_admin_key') || 'nammasevai-admin-secret-2026';
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
    const adminKey = localStorage.getItem('nammasevai_admin_key') || 'nammasevai-admin-secret-2026';
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
      const adminKey = localStorage.getItem('nammasevai_admin_key') || 'nammasevai-admin-secret-2026';
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
      case 'admin':
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
  window.nammaSevaiApp = new App();
});
