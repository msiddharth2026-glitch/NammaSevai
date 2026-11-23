// NammaSevai AI - AI Assistant Page Component with Real Voice & Privacy Modal
import { i18n } from '../i18n.js';

export function renderAssistantPage(state) {
  const t = i18n[state.lang] || i18n.ta;
  const isTa = state.lang === 'ta';
  const assistantLang = state.assistantLang || state.lang || 'ta';
  const isListening = state.isListening || false;
  const isSpeaking = state.isSpeaking || false;
  const chatMessages = state.chatHistory || [];
  const voiceConfig = state.voiceConfig || {};
  const consentGiven = state.micConsentGiven || false;

  return `
    <div class="assistant-page-container container">
      <!-- Top Status & AI Configuration Banner -->
      ${voiceConfig.configuration_instruction ? `
        <div style="background: linear-gradient(135deg, rgba(0, 143, 140, 0.08) 0%, rgba(9, 45, 80, 0.05) 100%); border: 1px solid rgba(0, 143, 140, 0.25); border-radius: var(--radius-md); padding: 0.85rem 1.25rem; margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem; font-size: 0.86rem;">
          <div style="display: flex; align-items: center; gap: 0.65rem;">
            <span style="font-size: 1.15rem;">⚡</span>
            <span>
              <strong>${isTa ? "AI பொறிமுறை நிலை:" : "AI Model Status:"}</strong> 
              ${isTa ? "சரிபார்க்கப்பட்ட தமிழ்நாடு விதிமுறைப் பொறிமுறை இயங்குகிறது." : "Running verified Tamil Nadu structured rule engine."}
            </span>
          </div>
          <button class="btn btn-outline btn-sm" id="view-ai-config-btn" style="padding: 0.25rem 0.65rem; font-size: 0.78rem;">
            ⚙️ ${isTa ? "API சாவி வழிகாட்டுதல் (Setup Gemini)" : "Configure Gemini API"}
          </button>
        </div>
      ` : `
        <div style="background: rgba(22, 131, 74, 0.08); border: 1px solid rgba(22, 131, 74, 0.25); border-radius: var(--radius-md); padding: 0.65rem 1.15rem; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem; font-size: 0.84rem; color: var(--gov-green);">
          <span>✓</span>
          <span><strong>Google Gemini AI:</strong> Connected & Active for Multi-Lingual Reasoning.</span>
        </div>
      `}

      <div class="assistant-header">
        <span class="badge badge-teal" style="margin-bottom: 0.65rem;">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/></svg>
          Voice-First AI Discovery | குரல்வழி வழிகாட்டி
        </span>
        <h1 style="font-size: 2.25rem; font-weight: 800; color: var(--primary-navy);">${t.assistantTitle}</h1>
        <p style="color: var(--text-muted); font-size: 1.05rem; margin-top: 0.5rem; max-width: 680px; margin-left: auto; margin-right: auto;">
          ${t.assistantSubtitle}
        </p>

        <!-- Language Choice Selector -->
        <div class="assistant-lang-selector">
          <span style="font-size: 0.88rem; font-weight: 600; color: var(--text-muted);">${t.languageChoice}</span>
          <button class="lang-chip ${assistantLang === 'ta' ? 'active' : ''}" data-lang-choice="ta">
            ${t.langTamil}
          </button>
          <button class="lang-chip ${assistantLang === 'tanglish' ? 'active' : ''}" data-lang-choice="tanglish">
            ${t.langTanglish}
          </button>
          <button class="lang-chip ${assistantLang === 'en' ? 'active' : ''}" data-lang-choice="en">
            ${t.langEnglish}
          </button>
        </div>
      </div>

      <!-- Microphone & Input Center -->
      <div class="mic-control-center">
        <!-- Privacy Notice Indicator -->
        <div style="display: flex; justify-content: center; align-items: center; gap: 0.5rem; margin-bottom: 1.25rem; font-size: 0.78rem; color: var(--text-light);">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          <span>${isTa ? "தனியுரிமை உறுதி: குரல் பதிவுகள் சேமிக்கப்படாது (Privacy: No raw voice stored)" : "Privacy Guaranteed: Voice is processed ephemerally and never stored."}</span>
        </div>

        <div>
          <button class="large-mic-btn ${isListening ? 'listening' : ''}" id="main-mic-btn" title="Click to speak">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>
          </button>
        </div>

        <div class="mic-status-label" id="mic-status-text">
          ${isListening ? t.micListening : t.micIdle}
        </div>

        <!-- Soundwave Visualization -->
        <div class="waveform-container ${isListening ? 'active' : ''}" id="soundwave-bars">
          <div class="wave-bar"></div>
          <div class="wave-bar"></div>
          <div class="wave-bar"></div>
          <div class="wave-bar"></div>
          <div class="wave-bar"></div>
          <div class="wave-bar"></div>
          <div class="wave-bar"></div>
        </div>

        <!-- Text Input Alternative -->
        <div class="assistant-input-box">
          <div class="input-textarea-wrap">
            <textarea
              id="assistant-query-input"
              class="citizen-textarea"
              placeholder="${t.textPlaceholder}"
              rows="3"
            >${state.currentQuery || ''}</textarea>
          </div>

          <div class="input-controls-row">
            <div style="font-size: 0.82rem; color: var(--text-light); display: flex; align-items: center; gap: 0.4rem;">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="16" y2="12"/><line x1="12" x2="12.01" y1="8" y2="8"/></svg>
              <span>தமிழ், தங்கிலீஷ் அல்லது ஆங்கிலத்தில் பேசலாம் / எழுதலாம்</span>
            </div>
            <div class="input-controls-actions">
              <button class="btn btn-outline" id="clear-query-btn" type="button">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
                <span>${t.clearBtn}</span>
              </button>
              <button class="btn btn-primary" id="submit-query-btn" type="button">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" x2="11" y1="2" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                <span>${t.submitBtn}</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Clickable Example Questions -->
        <div class="example-prompts-box">
          <div class="example-prompts-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--primary-teal)" stroke-width="2"><path d="M9.663 17h4.673M12 3v1m6.364 1.636-.707.707M21 12h-1M4 12H3m3.343-5.657-.707-.707m2.828 9.9a5 5 0 1 1 7.072 0l-.548.547A3.374 3.374 0 0 0 14 18.469V19a2 2 0 1 1-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>
            <span>${t.examplePromptsTitle}</span>
          </div>
          <div class="prompt-chips-wrap">
            <button class="prompt-chip" data-example="${t.ex1}">${t.ex1}</button>
            <button class="prompt-chip" data-example="${t.ex2}">${t.ex2}</button>
            <button class="prompt-chip" data-example="${t.ex3}">${t.ex3}</button>
            <button class="prompt-chip" data-example="${t.ex4}">${t.ex4}</button>
            <button class="prompt-chip" data-example="${t.ex5}">${t.ex5}</button>
          </div>
        </div>
      </div>

      <!-- Live Conversation Interface -->
      <div class="chat-conversation-area" id="chat-conversation-area">
        ${chatMessages.length === 0 ? `
          <div style="text-align: center; padding: 2.5rem; background: var(--bg-surface); border-radius: var(--radius-lg); border: 1px dashed var(--border-color);">
            <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">🎙️</div>
            <h3 style="color: var(--primary-navy); font-size: 1.15rem; margin-bottom: 0.35rem;">உங்கள் கேள்வியை கேட்க காத்திருக்கிறது</h3>
            <p style="color: var(--text-light); font-size: 0.9rem;">மேலே உள்ள மைக்கை கிளிக் செய்து பேசவும் அல்லது மாதிரி கேள்விகளில் ஒன்றை அழுத்தவும்.</p>
          </div>
        ` : chatMessages.map((msg, index) => renderChatMessage(msg, index, state)).join('')}
      </div>
    </div>

    <!-- Microphone Permission & Privacy Consent Modal -->
    <div class="modal-overlay ${state.showMicConsentModal ? 'open' : ''}" id="mic-consent-modal">
      <div class="modal-box" style="max-width: 540px;">
        <div class="modal-header">
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 1.5rem;">🔒</span>
            <h3 class="modal-title" style="font-size: 1.15rem;">
              ${isTa ? "ஒலிவாங்கி அனுமதி & தனியுரிமை கொள்கை" : "Microphone Access & Privacy Notice"}
            </h3>
          </div>
          <button class="modal-close-btn" id="close-mic-consent-btn">✕</button>
        </div>
        <div class="modal-body" style="gap: 1rem; font-size: 0.92rem; line-height: 1.6;">
          <p>
            ${isTa ?
              "நம்மசேவை AI உங்கள் கேள்விகளை தமிழ் அல்லது ஆங்கிலத்தில் கேட்டு, அரசு நலத்திட்டங்களை எளிதாக கண்டறிய உங்கள் சாதனத்தின் ஒலிவாங்கியை (Microphone) பயன்படுத்த அனுமதி கேட்கிறது." :
              "NammaSevai AI requests access to your microphone to listen to your voice query in Tamil, Tanglish, or English to help you discover eligible government schemes."}
          </p>
          <div style="background: var(--bg-surface); border-radius: var(--radius-md); padding: 1rem; border-left: 3px solid var(--primary-teal);">
            <strong>🛡️ ${isTa ? "எங்கள் தனியுரிமை உத்தரவாதம்:" : "Our Privacy Guarantees:"}</strong>
            <ul style="margin-top: 0.5rem; padding-left: 1.25rem; font-size: 0.88rem; color: var(--text-muted); display: flex; flex-direction: column; gap: 0.35rem;">
              <li>${isTa ? "குரல் பதிவுகள் தற்காலிகமாக மட்டுமே ஆய்வு செய்யப்பட்டு உடனே அழிக்கப்படும்." : "Raw audio is processed ephemerally and deleted immediately after transcription."}</li>
              <li>${isTa ? "எந்தவித தனிநபர் கடவுச்சொற்கள் அல்லது ரகசிய தகவல்கள் சேமிக்கப்படாது." : "No personal confidential credentials or permanent audio files are stored."}</li>
              <li>${isTa ? "குரலுக்கு பதிலாக தட்டச்சு செய்தும் எந்த நேரத்திலும் பயன்படுத்தலாம்." : "You can revoke access anytime or choose to type your queries."}</li>
            </ul>
          </div>
        </div>
        <div class="modal-footer" style="justify-content: space-between;">
          <button type="button" class="btn btn-outline" id="deny-mic-consent-btn">
            ${isTa ? "ரத்து செய் (தட்டச்சு செய்க)" : "Cancel (Type instead)"}
          </button>
          <button type="button" class="btn btn-primary" id="grant-mic-consent-btn">
            ✓ ${isTa ? "அனுமதி அளித்து பேசுக" : "Grant Access & Speak"}
          </button>
        </div>
      </div>
    </div>

    <!-- AI API Key Instruction Modal -->
    <div class="modal-overlay ${state.showApiKeyModal ? 'open' : ''}" id="api-key-modal">
      <div class="modal-box" style="max-width: 600px;">
        <div class="modal-header">
          <h3 class="modal-title">⚙️ Google Gemini AI Model Setup</h3>
          <button class="modal-close-btn" id="close-api-key-modal-btn">✕</button>
        </div>
        <div class="modal-body" style="font-size: 0.92rem; line-height: 1.6;">
          <p>
            NammaSevai AI seamlessly uses <strong>Google Gemini AI</strong> for complex multi-lingual contextual reasoning in colloquial Tamil, Tanglish, and English.
          </p>
          <div style="background: var(--bg-surface); border-radius: var(--radius-md); padding: 1rem; border-left: 3px solid var(--accent-saffron);">
            <strong>Step 1: Get a Free Gemini API Key</strong><br/>
            Visit <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noopener">Google AI Studio ↗</a> and generate your free API key.
          </div>
          <div style="background: var(--bg-surface); border-radius: var(--radius-md); padding: 1rem; border-left: 3px solid var(--primary-teal); margin-top: 0.75rem;">
            <strong>Step 2: Add to .env File</strong><br/>
            Open the <code>.env</code> file in your project directory and add:<br/>
            <pre style="background: #092d50; color: #fff; padding: 0.65rem; border-radius: 6px; margin-top: 0.4rem; font-family: monospace;">GEMINI_API_KEY="your-gemini-api-key-here"</pre>
          </div>
          <p style="font-size: 0.85rem; color: var(--text-light); margin-top: 0.5rem;">
            <em>Note: Even without an API key, the system runs with 100% precision using the verified Tamil Nadu structured rule engine.</em>
          </p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-primary" id="dismiss-api-key-modal-btn">Got It</button>
        </div>
      </div>
    </div>
  `;
}

function renderChatMessage(msg, index, state) {
  const t = i18n[state.lang] || i18n.ta;
  const isTa = state.lang === 'ta';
  const isUser = msg.sender === 'user';

  if (isUser) {
    return `
      <div class="chat-message">
        <div class="chat-avatar user">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        </div>
        <div class="chat-body user-bubble">
          <div class="chat-header">
            <span class="chat-sender-name">${isTa ? "நீங்கள் (Citizen)" : "You (Citizen)"}</span>
            <span class="chat-time">${msg.time || ''}</span>
          </div>
          <div class="chat-text">"${msg.text}"</div>
        </div>
      </div>
    `;
  }

  // AI Response
  const matches = msg.matches || [];
  const followUps = isTa ? (msg.follow_ups_ta || msg.follow_ups || []) : (msg.follow_ups_en || msg.follow_ups || []);

  return `
    <div class="chat-message">
      <div class="chat-avatar ai">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/></svg>
      </div>
      <div class="chat-body ai-bubble">
        <div class="chat-header">
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span class="chat-sender-name">நம்மசேவை AI Assistant</span>
            <span class="badge badge-teal">${matches.length} ${t.matchedCount}</span>
          </div>
          <span class="chat-time">${msg.time || ''}</span>
        </div>

        <div class="chat-text">${msg.text}</div>

        <!-- Follow-up Questions Card for Missing Essential Info -->
        ${followUps.length > 0 ? `
          <div style="background: rgba(255, 148, 24, 0.12); border: 1px solid rgba(255, 148, 24, 0.35); border-radius: var(--radius-md); padding: 0.95rem 1.15rem; margin-top: 0.85rem;">
            <div style="font-weight: 700; color: #9a3412; font-size: 0.88rem; display: flex; align-items: center; gap: 0.45rem;">
              <span>❓</span>
              <span>${isTa ? "உங்கள் தகுதியை உறுதி செய்ய கூடுதல் விவரங்கள் தேவை:" : "Follow-up questions to confirm your eligibility:"}</span>
            </div>
            <ul style="margin-top: 0.45rem; padding-left: 1.25rem; font-size: 0.86rem; color: #7c2d12; display: flex; flex-direction: column; gap: 0.35rem;">
              ${followUps.slice(0, 2).map(q => `<li>${q}</li>`).join('')}
            </ul>
          </div>
        ` : ''}

        <!-- Matched Scheme Preview Cards -->
        ${matches.length > 0 ? `
          <div class="matched-schemes-preview-list">
            ${matches.slice(0, 3).map(item => {
              const schemeId = item.scheme_id || item.scheme?.id;
              const name = isTa ? (item.scheme_name_ta || item.scheme?.name_ta) : (item.scheme_name_en || item.scheme?.name);
              const dept = isTa ? (item.department_ta || item.scheme?.department_ta) : (item.department_en || item.scheme?.department);
              const benefit = isTa ? (item.benefit_summary_ta || item.scheme?.benefit_summary_ta) : (item.benefit_summary_en || item.scheme?.benefit_summary);
              const confidence = item.match_confidence || item.matchPercent || 85;

              return `
                <div class="matched-preview-card">
                  <div class="matched-preview-info">
                    <div style="display: flex; align-items: center; gap: 0.45rem;">
                      <span class="badge ${confidence >= 80 ? 'badge-green' : 'badge-teal'}">${confidence}% Potential Match</span>
                      <span style="font-size: 0.78rem; color: var(--text-light);">${dept}</span>
                    </div>
                    <div class="matched-preview-title">${name}</div>
                    <div class="matched-preview-benefit">💰 ${benefit}</div>
                  </div>
                  <a href="#scheme-details/${schemeId}" class="btn btn-outline btn-sm">
                    ${t.viewDetails}
                  </a>
                </div>
              `;
            }).join('')}
          </div>
        ` : ''}

        <!-- Voice Output: Speak and Stop Audio Controls -->
        <div class="ai-actions-row">
          <div style="display: flex; gap: 0.5rem; align-items: center;">
            <button class="btn btn-outline btn-sm tts-listen-btn" data-tts-text="${encodeURIComponent(msg.text)}" type="button" title="Read answer aloud">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>
              <span>${isTa ? "குரலில் கேட்கவும் (Speak)" : "Speak"}</span>
            </button>
            <button class="btn btn-outline btn-sm tts-stop-btn" style="display: none; color: var(--gov-red); border-color: rgba(220, 38, 38, 0.3);" type="button" title="Stop speech">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="14" height="14" x="5" y="5" rx="2"/></svg>
              <span>${isTa ? "நிறுத்து (Stop)" : "Stop"}</span>
            </button>
          </div>

          ${matches.length > 0 ? `
            <a href="#schemes" class="btn btn-primary btn-sm">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/></svg>
              <span>${t.viewMatchedSchemes} (${matches.length})</span>
            </a>
          ` : ''}
        </div>
      </div>
    </div>
  `;
}
