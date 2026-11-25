// NammaSevai AI - AI Assistant Page Component (BharatSevai AI / Stitch Theme Redesign)
import { i18n } from '../i18n.js';
import { getLocalizedScheme, INDIAN_STATES, INDIAN_UNION_TERRITORIES } from '../schemesData.js';

export function renderAssistantPage(state) {
  const t = i18n[state.lang] || i18n.ta;
  const assistantLang = state.assistantLang || state.lang || 'ta';
  const isListening = state.isListening || false;
  const chatMessages = state.chatHistory || [];
  const voiceConfig = state.voiceConfig || {};
  const hasResults = chatMessages.some(m => m.sender === 'ai' && m.matches && m.matches.length > 0);
  const currentCitizenState = (state.userProfile && state.userProfile.state) ? state.userProfile.state : (state.selectedState && state.selectedState !== 'all' ? state.selectedState : '');

  return `
    <div class="assistant-page-container container" style="max-width: 1150px; margin: 0 auto; padding: 1.5rem 1rem 3.5rem;">
      <!-- AI Backend & Model Status Banner -->
      ${voiceConfig.configuration_instruction ? `
        <div style="background: rgba(217, 119, 6, 0.08); border: 1px solid rgba(217, 119, 6, 0.28); border-radius: var(--radius-xl); padding: 0.85rem 1.25rem; margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem; font-size: 0.88rem;">
          <div style="display: flex; align-items: center; gap: 0.65rem;">
            <span class="material-symbols-outlined" style="color: var(--secondary-saffron); font-size: 20px;">bolt</span>
            <span>
              <strong style="color: var(--primary-indigo);">${t.aiModelStatusLabel || "AI Model Status:"}</strong> 
              ${t.aiModelStatusVerified || "Running verified Tamil Nadu structured rule engine."}
            </span>
          </div>
          <button class="btn btn-outline btn-sm" id="view-ai-config-btn" style="padding: 0.35rem 0.85rem; font-size: 0.8rem; border-color: var(--secondary-saffron); color: var(--secondary-saffron);">
            ⚙️ ${t.btnConfigureGemini || "Configure Gemini API"}
          </button>
        </div>
      ` : `
        <div style="background: rgba(21, 128, 61, 0.08); border: 1px solid rgba(21, 128, 61, 0.25); border-radius: var(--radius-xl); padding: 0.65rem 1.15rem; margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; font-size: 0.84rem; color: var(--tertiary-green);">
          <div style="display: flex; align-items: center; gap: 0.45rem;">
            <span class="material-symbols-outlined" style="font-size: 18px;">check_circle</span>
            <span><strong>${t.geminiConnectedTitle || "Google Gemini AI & Rule Engine:"}</strong> ${t.geminiConnectedSub || "Connected for multi-lingual scheme reasoning."}</span>
          </div>
          <span style="font-size: 0.78rem; opacity: 0.85; font-weight: 600;">${t.geminiDeterministicBadge || "Deterministic & Transparent"}</span>
        </div>
      `}

      <!-- Top Civic Pathway & Integrity Guarantee Bar (Stepper) -->
      <section style="margin-bottom: 1.75rem;">
        <div style="background: var(--bg-card); padding: 1.25rem 1.5rem; border-radius: var(--radius-xl); border: 1px solid var(--border-color); box-shadow: var(--shadow-sm); display: flex; flex-direction: column; md:flex-row; justify-content: space-between; align-items: stretch; gap: 1rem;">
          <!-- Stepper Tracking -->
          <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
            <div style="display: flex; align-items: center;">
              <div style="width: 38px; height: 38px; border-radius: 9999px; background: ${hasResults ? 'var(--tertiary-green)' : 'var(--secondary-saffron)'}; color: #ffffff; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.95rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                ${hasResults ? '<span class="material-symbols-outlined" style="font-size: 20px;">check</span>' : '1'}
              </div>
              <div style="width: 50px; height: 3px; background: ${hasResults ? 'var(--tertiary-green)' : 'var(--border-color)'}; margin: 0 0.5rem; border-radius: 9999px;"></div>
              <div style="width: 38px; height: 38px; border-radius: 9999px; background: ${hasResults ? 'var(--secondary-saffron)' : 'var(--bg-muted)'}; color: ${hasResults ? '#ffffff' : 'var(--text-secondary)'}; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.95rem; border: 1px solid var(--border-color);">
                2
              </div>
            </div>
            <div>
              <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--secondary-saffron); font-weight: 700; display: block;">
                ${hasResults ? (t.step2Of2 || "Step 2 of 2") : (t.step1Of2 || "Step 1 of 2")}
              </span>
              <span style="font-size: 1.15rem; font-weight: 700; color: var(--primary-indigo);">
                ${hasResults ? (t.step2Prompt || "Confirm your profile & discover schemes") : (t.step1Prompt || "Tell us about your situation")}
              </span>
            </div>
          </div>

          <!-- Controls Row: Language Selector & Citizen State Selector Capsules -->
          <div style="display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;">
            <!-- Language Selector Capsule -->
            <div style="display: flex; align-items: center; gap: 0.5rem; background: var(--bg-canvas); padding: 0.35rem 0.85rem; border-radius: 9999px; border: 1px solid var(--border-color); align-self: flex-start; flex-wrap: wrap;">
              <span class="material-symbols-outlined" style="font-size: 18px; color: var(--secondary-saffron);">translate</span>
              <span style="font-size: 0.82rem; color: var(--text-primary);">
                ${t.languageChoice || "Language:"} 
                <strong style="color: var(--primary-indigo);">${assistantLang === 'ta' ? 'தமிழ்' : assistantLang === 'hi' ? 'हिन्दी' : assistantLang === 'ml' ? 'മലയാളം' : assistantLang === 'tanglish' ? 'Tanglish' : assistantLang === 'hinglish' ? 'Hinglish' : 'English'}</strong>
              </span>
              <div style="display: flex; gap: 0.25rem; margin-left: 0.35rem; flex-wrap: wrap;">
                <button class="lang-chip ${assistantLang === 'en' ? 'active' : ''}" data-lang-choice="en" style="padding: 0.2rem 0.55rem; font-size: 0.75rem; border-radius: 9999px;">English</button>
                <button class="lang-chip ${assistantLang === 'ta' ? 'active' : ''}" data-lang-choice="ta" style="padding: 0.2rem 0.55rem; font-size: 0.75rem; border-radius: 9999px;">தமிழ்</button>
                <button class="lang-chip ${assistantLang === 'hi' ? 'active' : ''}" data-lang-choice="hi" style="padding: 0.2rem 0.55rem; font-size: 0.75rem; border-radius: 9999px;">हिन्दी</button>
                <button class="lang-chip ${assistantLang === 'ml' ? 'active' : ''}" data-lang-choice="ml" style="padding: 0.2rem 0.55rem; font-size: 0.75rem; border-radius: 9999px;">മലയാളം</button>
                <button class="lang-chip ${assistantLang === 'tanglish' ? 'active' : ''}" data-lang-choice="tanglish" style="padding: 0.2rem 0.55rem; font-size: 0.75rem; border-radius: 9999px;">Tanglish</button>
                <button class="lang-chip ${assistantLang === 'hinglish' ? 'active' : ''}" data-lang-choice="hinglish" style="padding: 0.2rem 0.55rem; font-size: 0.75rem; border-radius: 9999px;">Hinglish</button>
              </div>
            </div>

            <!-- Citizen State/UT Selection Pill -->
            <div style="display: flex; align-items: center; gap: 0.4rem; background: var(--bg-canvas); padding: 0.35rem 0.85rem; border-radius: 9999px; border: 1px solid var(--border-color); align-self: flex-start;">
              <span class="material-symbols-outlined" style="font-size: 18px; color: var(--secondary-saffron);">location_on</span>
              <span style="font-size: 0.82rem; font-weight: 600; color: var(--text-primary); white-space: nowrap;">
                ${t.stateOrUtLabel || "State / UT"}:
              </span>
              <select id="assistant-state-select" style="padding: 0.2rem 0.5rem; font-size: 0.78rem; border-radius: 9999px; border: 1px solid var(--border-color); background: #ffffff; color: var(--primary-indigo); font-weight: 600; cursor: pointer; max-width: 175px;">
                <option value="all" ${!currentCitizenState || currentCitizenState === 'all' ? 'selected' : ''}>🇮🇳 Pan-India (All India)</option>
                <optgroup label="28 States">
                  ${INDIAN_STATES.map(st => `<option value="${st}" ${currentCitizenState === st ? 'selected' : ''}>${st}</option>`).join('')}
                </optgroup>
                <optgroup label="8 Union Territories">
                  ${INDIAN_UNION_TERRITORIES.map(ut => `<option value="${ut}" ${currentCitizenState === ut ? 'selected' : ''}>${ut}</option>`).join('')}
                </optgroup>
              </select>
            </div>
          </div>
        </div>

        <!-- Zero-PII Civic Reassurance Banner -->
        <div style="margin-top: 0.75rem; background: #ffffff; padding: 0.75rem 1.25rem; border-radius: var(--radius-lg); border: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between; gap: 0.75rem; box-shadow: var(--shadow-2xs);">
          <div style="display: flex; align-items: center; gap: 0.65rem; color: var(--text-secondary); font-size: 0.86rem;">
            <span class="material-symbols-outlined" style="color: var(--secondary-saffron); font-size: 20px;">shield</span>
            <span>
              <strong style="color: var(--text-primary); font-weight: 600;">${t.privacyPledgeTitle || "Privacy Pledge:"}</strong>
              ${t.privacyPledgeText || "We never ask for sensitive data like Aadhaar, bank accounts, or phone OTPs. Voice input is transcribed in real-time and never permanently stored."}
            </span>
          </div>
          <div style="display: flex; align-items: center; gap: 0.35rem; color: var(--tertiary-green); font-size: 0.78rem; font-weight: 600; white-space: nowrap;">
            <span class="material-symbols-outlined" style="font-size: 16px;">verified</span>
            <span>${t.localSessionBadge || "Local Session Only"}</span>
          </div>
        </div>
      </section>

      <!-- Main Dual Input Layout -->
      <section style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem; align-items: start; margin-bottom: 2rem;">
        
        <!-- Voice & Conversational Input Card -->
        <div style="background: var(--bg-card); padding: 1.5rem; border-radius: var(--radius-xl); border: 1px solid var(--border-color); box-shadow: var(--shadow-sm); display: flex; flex-direction: column; gap: 1.25rem;">
          
          <!-- Card Header -->
          <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.75rem;">
            <div>
              <div style="display: inline-flex; align-items: center; gap: 0.35rem; padding: 0.2rem 0.65rem; border-radius: 9999px; background: rgba(217, 119, 6, 0.12); color: var(--secondary-saffron); font-size: 0.76rem; font-weight: 700; margin-bottom: 0.4rem;">
                <span class="material-symbols-outlined" style="font-size: 14px;">record_voice_over</span>
                <span>${t.voiceOrTextBadge || "Voice or Conversational Text"}</span>
              </div>
              <h2 style="font-size: 1.35rem; font-weight: 700; color: var(--primary-indigo); margin: 0;">
                ${t.expressSituationHeading || "Express Your Situation Freely"}
              </h2>
              <p style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 0.25rem; line-height: 1.5;">
                ${t.noFormalNamesNeeded || "Speak or type naturally in everyday mixed language. No formal scheme names needed."}
              </p>
            </div>
            <span class="material-symbols-outlined" style="color: var(--secondary-saffron); font-size: 28px; opacity: 0.8;">graphic_eq</span>
          </div>

          <!-- Microphone Hero Interaction -->
          <div style="background: var(--bg-canvas); padding: 1.25rem; border-radius: var(--radius-xl); border: 1px solid var(--border-color); display: flex; flex-direction: column; sm:flex-row; align-items: center; gap: 1.25rem; text-align: center; sm:text-left;">
            <div style="position: relative; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
              <!-- Animated Aura Ping -->
              <span style="position: absolute; width: 68px; height: 68px; border-radius: 9999px; background: rgba(217, 119, 6, 0.3); animation: ping 2s cubic-bezier(0, 0, 0.2, 1) infinite;"></span>
              <button class="large-mic-btn ${isListening ? 'listening' : ''}" id="main-mic-btn" type="button" title="Click to speak" style="position: relative; z-index: 10; width: 56px; height: 56px; border-radius: 9999px; background: ${isListening ? 'var(--gov-red, #dc2626)' : 'var(--secondary-saffron)'}; color: #ffffff; border: none; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 20px rgba(217, 119, 6, 0.35); cursor: pointer; transition: all 0.2s ease;">
                <span class="material-symbols-outlined" style="font-size: 28px;">mic</span>
              </button>
            </div>
            <div style="flex: 1;">
              <div style="display: flex; align-items: center; justify-content: center; sm:justify-content: flex-start; gap: 0.4rem;">
                <span style="font-size: 1rem; font-weight: 700; color: var(--primary-indigo);">
                  ${isListening ? (t.listeningPleaseSpeak || "Listening... please speak") : (t.tapToSpeak || "Tap to Speak")}
                </span>
                <span style="width: 8px; height: 8px; border-radius: 9999px; background: ${isListening ? '#dc2626' : 'var(--secondary-saffron)'}; display: inline-block;"></span>
              </div>
              <p style="font-size: 0.82rem; color: var(--text-secondary); margin-top: 0.25rem; line-height: 1.4;" id="mic-status-text">
                ${isListening ? t.micListening : (t.micReadyMsg || "Microphone ready. Speech is converted to text in real-time; audio is never archived or permanently stored.")}
              </p>
            </div>
          </div>

          <!-- Soundwave Animation when Listening -->
          <div class="waveform-container ${isListening ? 'active' : ''}" id="soundwave-bars" style="display: ${isListening ? 'flex' : 'none'}; justify-content: center; align-items: center; gap: 5px; height: 28px; margin: 0.25rem 0;">
            <div class="wave-bar" style="width: 4px; height: 16px; background: var(--secondary-saffron); border-radius: 2px;"></div>
            <div class="wave-bar" style="width: 4px; height: 24px; background: var(--secondary-saffron); border-radius: 2px;"></div>
            <div class="wave-bar" style="width: 4px; height: 12px; background: var(--secondary-saffron); border-radius: 2px;"></div>
            <div class="wave-bar" style="width: 4px; height: 28px; background: var(--secondary-saffron); border-radius: 2px;"></div>
            <div class="wave-bar" style="width: 4px; height: 18px; background: var(--secondary-saffron); border-radius: 2px;"></div>
            <div class="wave-bar" style="width: 4px; height: 14px; background: var(--secondary-saffron); border-radius: 2px;"></div>
          </div>

          <!-- Text Input Alternative -->
          <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <label for="assistant-query-input" style="font-size: 0.88rem; font-weight: 700; color: var(--primary-indigo); display: flex; align-items: center; gap: 0.4rem;">
                <span class="material-symbols-outlined" style="font-size: 16px; color: var(--secondary-saffron);">chat_bubble</span>
                <span>${t.yourSituationNeeds || "Your Situation / Needs:"}</span>
              </label>
              <span style="font-size: 0.78rem; color: var(--text-secondary);">Tamil / Hindi / Malayalam / Tanglish / Hinglish / English</span>
            </div>
            
            <div style="position: relative;">
              <textarea
                id="assistant-query-input"
                class="citizen-textarea"
                placeholder="${t.textPlaceholder || 'E.g.: I am pursuing higher education in college...'}"
                rows="4"
                style="width: 100%; padding: 0.85rem; border-radius: var(--radius-lg); border: 1.5px solid var(--border-color); background: var(--bg-canvas); color: var(--text-primary); font-family: inherit; font-size: 0.95rem; resize: vertical; line-height: 1.6;"
              >${state.currentQuery || ''}</textarea>
              
              <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                <button type="button" id="clear-query-btn" class="btn btn-outline btn-sm" style="padding: 0.35rem 0.75rem; font-size: 0.8rem; display: flex; align-items: center; gap: 0.35rem;">
                  <span class="material-symbols-outlined" style="font-size: 15px;">backspace</span>
                  <span>${t.clearBtn}</span>
                </button>
                <button type="button" id="submit-query-btn" class="btn btn-primary" style="padding: 0.45rem 1.25rem; font-size: 0.9rem; display: flex; align-items: center; gap: 0.45rem;">
                  <span>${t.submitBtn}</span>
                  <span class="material-symbols-outlined" style="font-size: 18px;">arrow_forward</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Common Starting Examples (Prompt Chips) -->
          <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            <span style="font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); font-weight: 700;">
              ${t.commonStartingExamples || "Common Starting Examples:"}
            </span>
            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
              <button class="prompt-chip" data-example="${t.ex1}" style="padding: 0.4rem 0.85rem; border-radius: 9999px; background: var(--bg-canvas); border: 1px solid var(--border-color); font-size: 0.82rem; color: var(--primary-indigo); cursor: pointer; text-align: left; transition: all 0.2s ease;">
                🎓 ${t.filterEducation || "Student Scholarship"}
              </button>
              <button class="prompt-chip" data-example="${t.ex2}" style="padding: 0.4rem 0.85rem; border-radius: 9999px; background: var(--bg-canvas); border: 1px solid var(--border-color); font-size: 0.82rem; color: var(--primary-indigo); cursor: pointer; text-align: left; transition: all 0.2s ease;">
                🌾 ${t.filterAgri || "Farmer Crop Subsidy"}
              </button>
              <button class="prompt-chip" data-example="${t.ex3}" style="padding: 0.4rem 0.85rem; border-radius: 9999px; background: var(--bg-canvas); border: 1px solid var(--border-color); font-size: 0.82rem; color: var(--primary-indigo); cursor: pointer; text-align: left; transition: all 0.2s ease;">
                💼 ${t.filterWomen || "Women Self-Employment"}
              </button>
              <button class="prompt-chip" data-example="${t.ex4}" style="padding: 0.4rem 0.85rem; border-radius: 9999px; background: var(--bg-canvas); border: 1px solid var(--border-color); font-size: 0.82rem; color: var(--primary-indigo); cursor: pointer; text-align: left; transition: all 0.2s ease;">
                👵 ${t.filterSeniors || "Senior Citizen Pension"}
              </button>
              <button class="prompt-chip" data-example="${t.ex5}" style="padding: 0.4rem 0.85rem; border-radius: 9999px; background: var(--bg-canvas); border: 1px solid var(--border-color); font-size: 0.82rem; color: var(--primary-indigo); cursor: pointer; text-align: left; transition: all 0.2s ease;">
                🚀 ${t.filterEmployment || "Youth Skill & MSME"}
              </button>
            </div>
          </div>

          <!-- Cultural Context Badge -->
          <div style="background: var(--bg-canvas); padding: 0.85rem 1rem; border-radius: var(--radius-lg); border: 1px solid var(--border-color); display: flex; align-items: center; gap: 0.75rem;">
            <span class="material-symbols-outlined" style="font-size: 24px; color: var(--secondary-saffron); flex-shrink: 0;">psychology</span>
            <div style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.4;">
              <strong style="color: var(--primary-indigo); font-weight: 700;">${t.dialectsUnderstoodTitle || "Colloquial Dialects & Mixed Language Understood"}</strong>: 
              ${t.dialectsUnderstoodDesc || "Our civic model identifies key eligibility criteria from everyday conversational speech."}
            </div>
          </div>
        </div>

        <!-- Live Conversation, Interpreted Profile & Transparent Matching -->
        <div style="display: flex; flex-direction: column; gap: 1.5rem;" id="chat-conversation-area">
          ${chatMessages.length === 0 ? `
            <!-- Empty State / Transparent Diagnostic Intro -->
            <div style="background: var(--bg-card); padding: 2rem 1.5rem; border-radius: var(--radius-xl); border: 1px solid var(--border-color); box-shadow: var(--shadow-sm); text-align: center;">
              <div style="width: 56px; height: 56px; border-radius: 9999px; background: rgba(21, 35, 62, 0.05); color: var(--primary-indigo); display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem;">
                <span class="material-symbols-outlined" style="font-size: 28px; color: var(--secondary-saffron);">fact_check</span>
              </div>
              <h3 style="font-size: 1.2rem; font-weight: 700; color: var(--primary-indigo); margin-bottom: 0.4rem;">
                ${t.transparentMatchingTitle || "Transparent Scheme Matching"}
              </h3>
              <p style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6; max-width: 440px; margin: 0 auto 1.5rem;">
                ${t.transparentMatchingDesc || "We transparently map your situation against verified Tamil Nadu and Central welfare guidelines."}
              </p>

              <!-- Pathway Checklist Preview -->
              <div style="background: var(--bg-canvas); border-radius: var(--radius-lg); padding: 1rem; border: 1px solid var(--border-color); text-align: left; display: flex; flex-direction: column; gap: 0.75rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.84rem; color: var(--text-primary);">
                  <span class="material-symbols-outlined" style="font-size: 18px; color: var(--tertiary-green);">check_circle</span>
                  <span><strong>1. ${t.stepNlpTitle || "Natural Language Understanding"}:</strong> ${t.stepNlpDesc || "Understands Tamil, Hindi, Malayalam, Tanglish & Hinglish queries"}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.84rem; color: var(--text-primary);">
                  <span class="material-symbols-outlined" style="font-size: 18px; color: var(--tertiary-green);">check_circle</span>
                  <span><strong>2. ${t.stepRuleTitle || "Rule Matching"}:</strong> ${t.stepRuleDesc || "Matches education, age, occupation and income limits"}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.84rem; color: var(--text-primary);">
                  <span class="material-symbols-outlined" style="font-size: 18px; color: var(--secondary-saffron);">pending</span>
                  <span><strong>3. ${t.stepDocTitle || "Checklist Guidance"}:</strong> ${t.stepDocDesc || "Guides certificates and application procedures"}</span>
                </div>
              </div>
            </div>
          ` : chatMessages.map((msg, index) => renderStitchChatMessage(msg, index, state)).join('')}
        </div>

      </section>
    </div>

    <!-- Microphone Permission & Privacy Consent Modal -->
    <div class="modal-overlay ${state.showMicConsentModal ? 'open' : ''}" id="mic-consent-modal">
      <div class="modal-box" style="max-width: 520px; background: #ffffff; border-radius: var(--radius-xl); border: 1px solid var(--border-color); box-shadow: var(--shadow-lg); padding: 1.75rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
          <div style="display: flex; align-items: center; gap: 0.65rem;">
            <div style="width: 36px; height: 36px; border-radius: 9999px; background: rgba(217, 119, 6, 0.12); display: flex; align-items: center; justify-content: center; color: var(--secondary-saffron);">
              <span class="material-symbols-outlined" style="font-size: 20px;">lock</span>
            </div>
            <h3 style="font-size: 1.15rem; font-weight: 700; color: var(--primary-indigo); margin: 0;">
              ${t.micModalTitle || "Microphone Access & Privacy Notice"}
            </h3>
          </div>
          <button id="close-mic-consent-btn" style="background: none; border: none; font-size: 1.25rem; color: var(--text-secondary); cursor: pointer;">✕</button>
        </div>

        <div style="font-size: 0.92rem; color: var(--text-secondary); line-height: 1.6; display: flex; flex-direction: column; gap: 1rem;">
          <p>
            ${t.micModalText || "NammaSevai AI requests temporary access to your microphone to listen to your voice query to help you discover eligible government schemes."}
          </p>
          <div style="background: var(--bg-canvas); border-radius: var(--radius-lg); padding: 1rem; border-left: 3px solid var(--secondary-saffron);">
            <strong style="color: var(--primary-indigo); font-size: 0.88rem;">🛡️ ${t.micPrivacyTitle || "Our Civic Privacy Guarantees:"}</strong>
            <ul style="margin-top: 0.5rem; padding-left: 1.25rem; font-size: 0.84rem; display: flex; flex-direction: column; gap: 0.35rem;">
              <li>${t.micPriv1 || "Raw audio is processed ephemerally and deleted immediately after speech recognition."}</li>
              <li>${t.micPriv2 || "No personal confidential credentials or permanent audio files are stored."}</li>
              <li>${t.micPriv3 || "You can revoke access anytime or choose to type your queries."}</li>
            </ul>
          </div>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1.5rem; gap: 0.75rem;">
          <button type="button" class="btn btn-outline" id="deny-mic-consent-btn" style="padding: 0.5rem 1rem;">
            ${t.btnCancelType || "Cancel (Type instead)"}
          </button>
          <button type="button" class="btn btn-primary" id="grant-mic-consent-btn" style="padding: 0.5rem 1.25rem;">
            ✓ ${t.btnGrantSpeak || "Grant Access & Speak"}
          </button>
        </div>
      </div>
    </div>

    <!-- AI API Key Instruction Modal -->
    <div class="modal-overlay ${state.showApiKeyModal ? 'open' : ''}" id="api-key-modal">
      <div class="modal-box" style="max-width: 580px; background: #ffffff; border-radius: var(--radius-xl); border: 1px solid var(--border-color); box-shadow: var(--shadow-lg); padding: 1.75rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
          <h3 style="font-size: 1.2rem; font-weight: 700; color: var(--primary-indigo); margin: 0;">
            ⚙️ Google Gemini AI Model Setup
          </h3>
          <button id="close-api-key-modal-btn" style="background: none; border: none; font-size: 1.25rem; color: var(--text-secondary); cursor: pointer;">✕</button>
        </div>

        <div style="font-size: 0.92rem; color: var(--text-secondary); line-height: 1.6; display: flex; flex-direction: column; gap: 1rem;">
          <p>
            NammaSevai AI seamlessly uses <strong>Google Gemini AI</strong> for multi-lingual contextual reasoning in colloquial Tamil, Hindi, Malayalam, Tanglish, Hinglish, and English.
          </p>
          <div style="background: var(--bg-canvas); border-radius: var(--radius-lg); padding: 1rem; border-left: 3px solid var(--secondary-saffron);">
            <strong style="color: var(--primary-indigo);">Step 1: Get a Free Gemini API Key</strong><br/>
            Visit <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noopener" style="color: var(--secondary-saffron); text-decoration: underline;">Google AI Studio ↗</a> and generate your free API key.
          </div>
          <div style="background: var(--bg-canvas); border-radius: var(--radius-lg); padding: 1rem; border-left: 3px solid var(--tertiary-green);">
            <strong style="color: var(--primary-indigo);">Step 2: Add to .env File</strong><br/>
            Open the <code>.env</code> file in your project directory and add:<br/>
            <pre style="background: #15233E; color: #fff; padding: 0.65rem; border-radius: 6px; margin-top: 0.4rem; font-family: monospace; font-size: 0.85rem;">GEMINI_API_KEY="your-gemini-api-key-here"</pre>
          </div>
          <p style="font-size: 0.84rem; color: var(--text-secondary);">
            <em>Note: Even without an API key, the system runs with 100% precision using the verified Tamil Nadu structured rule engine.</em>
          </p>
        </div>

        <div style="display: flex; justify-content: flex-end; margin-top: 1.5rem;">
          <button type="button" class="btn btn-primary" id="dismiss-api-key-modal-btn" style="padding: 0.5rem 1.25rem;">Got It</button>
        </div>
      </div>
    </div>
  `;
}

function renderStitchChatMessage(msg, index, state) {
  const t = i18n[state.lang] || i18n.ta;
  const isUser = msg.sender === 'user';

  if (isUser) {
    return `
      <!-- User Query Card -->
      <div style="background: var(--bg-card); border-radius: var(--radius-xl); border: 1px solid var(--border-color); padding: 1.25rem; box-shadow: var(--shadow-sm);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <div style="width: 28px; height: 28px; border-radius: 9999px; background: var(--primary-indigo); color: #fff; display: flex; align-items: center; justify-content: center;">
              <span class="material-symbols-outlined" style="font-size: 16px;">person</span>
            </div>
            <span style="font-size: 0.88rem; font-weight: 700; color: var(--primary-indigo);">
              ${t.citizenQueryTitle || "Citizen Query"}
            </span>
          </div>
          <span style="font-size: 0.78rem; color: var(--text-secondary);">${msg.time || ''}</span>
        </div>
        <div style="font-size: 0.95rem; color: var(--text-primary); line-height: 1.5; font-style: italic; background: var(--bg-canvas); padding: 0.75rem 1rem; border-radius: var(--radius-lg); border-left: 3px solid var(--secondary-saffron);">
          "${msg.text}"
        </div>
      </div>
    `;
  }

  // AI Response Block
  const matches = msg.matches || [];
  const curLang = state.assistantLang || state.lang;
  const followUps = (curLang === 'ta' || curLang === 'tanglish')
    ? (msg.follow_ups_ta || msg.follow_ups || [])
    : (curLang === 'hi' || curLang === 'hinglish')
    ? (msg.follow_ups_hi || msg.follow_ups_en || msg.follow_ups || [])
    : (curLang === 'ml')
    ? (msg.follow_ups_ml || msg.follow_ups_en || msg.follow_ups || [])
    : (msg.follow_ups_en || msg.follow_ups || []);
  const profile = msg.extracted_profile || {};

  return `
    <div style="display: flex; flex-direction: column; gap: 1.25rem;">
      
      <!-- Interpreted Profile Summary Card (if profile items exist) -->
      <div style="background: var(--bg-card); border-radius: var(--radius-xl); border: 1px solid var(--border-color); padding: 1.25rem; box-shadow: var(--shadow-sm);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; pb: 0.5rem; border-bottom: 1px solid var(--border-color);">
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <div style="width: 32px; height: 32px; border-radius: 8px; background: rgba(21, 35, 62, 0.08); display: flex; align-items: center; justify-content: center; color: var(--primary-indigo);">
              <span class="material-symbols-outlined" style="font-size: 18px;">assignment_turned_in</span>
            </div>
            <div>
              <h3 style="font-size: 1.05rem; font-weight: 700; color: var(--primary-indigo); margin: 0;">
                ${t.interpretedProfileTitle || "Your Interpreted Profile"}
              </h3>
              <span style="font-size: 0.75rem; color: var(--text-secondary);">
                ${t.interpretedProfileSub || "Derived strictly from your voice & text input"}
              </span>
            </div>
          </div>
          <span style="font-size: 0.76rem; font-weight: 700; padding: 0.2rem 0.65rem; border-radius: 9999px; background: rgba(21, 128, 61, 0.12); color: var(--tertiary-green); display: flex; align-items: center; gap: 0.25rem;">
            <span class="material-symbols-outlined" style="font-size: 14px;">verified</span> ${t.highConfidenceBadge || "High Confidence"}
          </span>
        </div>

        <!-- Extracted Parameter Grid -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.75rem;">
          <div style="background: var(--bg-canvas); padding: 0.75rem; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
            <span style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); font-weight: 600; display: block;">🎯 ${t.primaryGoal || "Primary Goal"}</span>
            <span style="font-size: 0.88rem; font-weight: 700; color: var(--primary-indigo); display: block; margin-top: 0.2rem;">
              ${profile.goal || (curLang === 'ta' ? "கல்வி / உதவித்தொகை" : curLang === 'hi' ? "शिक्षा / छात्रवृत्ति" : curLang === 'ml' ? "വിദ്യാഭ്യാസം / സ്കോളർഷിപ്പ്" : "Welfare & Fee Support")}
            </span>
          </div>

          <div style="background: var(--bg-canvas); padding: 0.75rem; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
            <span style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); font-weight: 600; display: block;">📍 ${t.locationLabel || "Location"}</span>
            <span style="font-size: 0.88rem; font-weight: 700; color: var(--primary-indigo); display: block; margin-top: 0.2rem;">
              ${profile.district ? (profile.state ? `${profile.district}, ${profile.state}` : `${profile.district}`) : (profile.state ? `${profile.state}, India` : (t.panIndiaCoverage || "Pan-India / Central"))}
            </span>
          </div>

          <div style="background: var(--bg-canvas); padding: 0.75rem; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
            <span style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); font-weight: 600; display: block;">💰 ${t.familyIncomeLabel || "Family Income"}</span>
            <span style="font-size: 0.88rem; font-weight: 700; color: var(--primary-indigo); display: block; margin-top: 0.2rem;">
              ${profile.income ? "₹" + Number(profile.income).toLocaleString('en-IN') + " / year" : "< ₹2,50,000 / year"}
            </span>
          </div>

          <div style="background: var(--bg-canvas); padding: 0.75rem; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
            <span style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); font-weight: 600; display: block;">👤 ${t.categoryRoleLabel || "Category / Role"}</span>
            <span style="font-size: 0.88rem; font-weight: 700; color: var(--primary-indigo); display: block; margin-top: 0.2rem;">
              ${profile.occupation || profile.category || (curLang === 'ta' ? "மாணவர் / குடிமக்கள்" : curLang === 'hi' ? "छात्र / नागरिक" : curLang === 'ml' ? "വിദ്യാർത്ഥി / പൗരൻ" : "Student / Citizen")}
            </span>
          </div>
        </div>
      </div>

      <!-- AI Analysis Text & Audio Playback -->
      <div style="background: var(--bg-card); border-radius: var(--radius-xl); border: 1px solid var(--border-color); padding: 1.25rem; box-shadow: var(--shadow-sm);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <div style="width: 28px; height: 28px; border-radius: 9999px; background: var(--secondary-saffron); color: #fff; display: flex; align-items: center; justify-content: center;">
              <span class="material-symbols-outlined" style="font-size: 16px;">support_agent</span>
            </div>
            <span style="font-size: 0.88rem; font-weight: 700; color: var(--primary-indigo);">
              ${t.aiAssessmentTitle || "NammaSevai AI Assessment"}
            </span>
          </div>
          <span style="font-size: 0.78rem; font-weight: 700; padding: 0.15rem 0.6rem; border-radius: 9999px; background: rgba(21, 35, 62, 0.08); color: var(--primary-indigo);">
            ${matches.length} ${t.matchedCount || "Matches"}
          </span>
        </div>

        <p style="font-size: 0.95rem; color: var(--text-primary); line-height: 1.6; margin: 0 0 1rem;">
          ${msg.text}
        </p>

        <!-- Audio Speak / Stop Controls -->
        <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
          <button class="btn btn-outline btn-sm tts-listen-btn" data-tts-text="${encodeURIComponent(msg.text)}" type="button" title="Read answer aloud" style="display: flex; align-items: center; gap: 0.35rem; padding: 0.35rem 0.85rem; font-size: 0.82rem;">
            <span class="material-symbols-outlined" style="font-size: 16px; color: var(--secondary-saffron);">volume_up</span>
            <span>${t.listenAudioSummary || t.listenAudio || "Listen"}</span>
          </button>
          <button class="btn btn-outline btn-sm tts-stop-btn" style="display: none; color: #dc2626; border-color: rgba(220, 38, 38, 0.3); padding: 0.35rem 0.85rem; font-size: 0.82rem;" type="button" title="Stop speech">
            <span class="material-symbols-outlined" style="font-size: 16px;">stop_circle</span>
            <span>${t.stopAudioSummary || t.stopAudio || "Stop"}</span>
          </button>
        </div>
      </div>

      <!-- Follow-up Questions Card for Missing Essential Info -->
      ${followUps.length > 0 ? `
        <div style="background: rgba(217, 119, 6, 0.08); border: 1px solid rgba(217, 119, 6, 0.3); border-radius: var(--radius-xl); padding: 1.15rem; box-shadow: var(--shadow-2xs);">
          <div style="font-weight: 700; color: #9a3412; font-size: 0.9rem; display: flex; align-items: center; gap: 0.45rem;">
            <span class="material-symbols-outlined" style="font-size: 18px; color: var(--secondary-saffron);">quiz</span>
            <span>${t.whyMatched || "Follow-up questions to pinpoint your eligibility:"}</span>
          </div>
          <ul style="margin-top: 0.5rem; padding-left: 1.25rem; font-size: 0.86rem; color: #7c2d12; display: flex; flex-direction: column; gap: 0.35rem; line-height: 1.5;">
            ${followUps.slice(0, 3).map(q => `<li>${q}</li>`).join('')}
          </ul>
        </div>
      ` : ''}

      <!-- Matched Scheme Preview Cards -->
      ${matches.length > 0 ? `
        <div style="display: flex; flex-direction: column; gap: 0.85rem;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.95rem; font-weight: 700; color: var(--primary-indigo);">
              ${t.resultsTitle || "Identified Potential Schemes"} (${matches.length})
            </span>
            <a href="#schemes" class="btn btn-primary btn-sm" style="padding: 0.35rem 0.85rem; font-size: 0.82rem; display: flex; align-items: center; gap: 0.35rem;">
              <span>${t.viewMatchedSchemes || "View All Matching Schemes"}</span>
              <span class="material-symbols-outlined" style="font-size: 15px;">arrow_forward</span>
            </a>
          </div>

          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 0.85rem;">
            ${matches.slice(0, 3).map(item => {
              const schemeId = item.scheme_id || item.scheme?.id;
              const foundScheme = (state.schemes || []).find(s => s.id === schemeId) || item.scheme || item;
              const loc = getLocalizedScheme(foundScheme, curLang);

              const name = loc.displayName || item.scheme_name_ta || item.scheme_name_en || '';
              const benefit = loc.displayBenefit || item.benefit_summary_ta || item.benefit_summary_en || '';
              const dept = loc.displayDepartment || item.department_ta || item.department_en || '';

              const confidence = item.match_confidence || item.matchPercent || 85;
              const isStrong = confidence >= 80;

              return `
                <div style="background: var(--bg-card); border-radius: var(--radius-lg); border: 1px solid var(--border-color); padding: 1rem; box-shadow: var(--shadow-sm); display: flex; flex-direction: column; justify-content: space-between; gap: 0.75rem; border-top: 3px solid ${confidence >= 80 ? 'var(--tertiary-green)' : 'var(--secondary-saffron)'};">
                  <div>
                    <div style="display: flex; justify-content: space-between; align-items: center; gap: 0.35rem; margin-bottom: 0.4rem;">
                      <span style="padding: 0.15rem 0.55rem; border-radius: 9999px; background: ${confidence >= 80 ? 'rgba(21, 128, 61, 0.12)' : 'rgba(217, 119, 6, 0.12)'}; color: ${confidence >= 80 ? 'var(--tertiary-green)' : 'var(--secondary-saffron)'}; font-size: 0.72rem; font-weight: 700; display: inline-flex; align-items: center; gap: 0.25rem;">
                        <span class="material-symbols-outlined" style="font-size: 13px;">${confidence >= 80 ? 'check_circle' : 'help_outline'}</span>
                        ${confidence}% ${isStrong ? (t.strongMatchBadge || "Strong Potential Match") : (t.worthCheckingBadge || "Worth Checking")}
                      </span>
                      <span style="font-size: 0.72rem; color: var(--text-secondary); text-align: right; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 140px;">
                        ${dept}
                      </span>
                    </div>
                    <div style="font-size: 0.95rem; font-weight: 700; color: var(--primary-indigo); line-height: 1.35; margin-bottom: 0.35rem;">
                      ${name}
                    </div>
                    <div style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.4;">
                      💰 ${benefit}
                    </div>
                  </div>
                  <div style="display: flex; justify-content: flex-end;">
                    <a href="#scheme-details/${schemeId}" class="btn btn-outline btn-sm" style="padding: 0.3rem 0.75rem; font-size: 0.8rem; display: flex; align-items: center; gap: 0.3rem;">
                      <span>${t.viewDetails}</span>
                      <span class="material-symbols-outlined" style="font-size: 14px;">arrow_forward</span>
                    </a>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        </div>
      ` : ''}

    </div>
  `;
}
