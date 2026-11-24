// NammaSevai AI - Saved Document Preparation Checklist Page (Stitch Redesign)
import { i18n } from '../i18n.js';

export function renderChecklistPage(state) {
  const t = i18n[state.lang] || i18n.ta;
  const lang = state.lang || 'ta';

  // Multi-lingual default initial documents list
  const defaultDocs = [
    {
      id: 'doc-1',
      name: {
        en: 'College Bonafide Certificate & Student ID',
        ta: 'கல்லூரி படிப்புச் சான்றிதழ் (Bonafide) & அடையாள அட்டை',
        hi: 'कॉलेज बोनाफाइड प्रमाणपत्र एवं छात्र पहचान पत्र',
        ml: 'കോളേജ് ബോണഫൈഡ് സർട്ടിഫിക്കറ്റും വിദ്യാർത്ഥി ഐഡിയും',
        tanglish: 'College Bonafide Certificate & Student ID Card',
        hinglish: 'College Bonafide Certificate aur Student ID'
      },
      desc: {
        en: 'Obtained from college office or Principal’s section with official seal.',
        ta: 'கல்லூரி முதல்வர் அலுவலகத்தில் அதிகாரப்பூர்வ முத்திரையுடன் பெறலாம்.',
        hi: 'कॉलेज कार्यालय या प्राचार्य अनुभाग से आधिकारिक मुहर सहित प्राप्त करें।',
        ml: 'ഔദ്യോഗിക മുദ്രയോടെ കോളേജ് ഓഫീസിൽ നിന്നോ പ്രിൻസിപ്പൽ വിഭാഗത്തിൽ നിന്നോ ലഭ്യമാക്കാം.',
        tanglish: 'College office or Principal section-la official seal-udan vaangavum.',
        hinglish: 'College office ya Principal section se official seal ke sath prapt karein.'
      },
      group: 'ready',
      defaultChecked: true
    },
    {
      id: 'doc-2',
      name: {
        en: 'Aadhaar Card (Linked with Mobile & Bank)',
        ta: 'ஆதார் அட்டை (மொபைல் & வங்கி கணக்குடன் இணைக்கப்பட்டது)',
        hi: 'आधार कार्ड (मोबाइल एवं बैंक खाते से लिंक)',
        ml: 'ആധാർ കാർഡ് (മൊബൈലും ബാങ്കുമായി ലിങ്ക് ചെയ്തത്)',
        tanglish: 'Aadhaar Card (Mobile & Bank link aagirukka vendum)',
        hinglish: 'Aadhaar Card (Mobile aur Bank account se link)'
      },
      desc: {
        en: 'Must be verified with active DBT status for direct government credit.',
        ta: 'நேரடி பணப்பரிவர்த்தனைக்கு (DBT) ஆதார் வங்கி கணக்குடன் இணைக்கப்பட்டிருக்க வேண்டும்.',
        hi: 'प्रत्यक्ष सरकारी लाभ (DBT) के लिए बैंक खाते से लिंक होना अनिवार्य है।',
        ml: 'നേരിട്ടുള്ള സർക്കാർ കൈമാറ്റത്തിന് (DBT) ബാങ്ക് അക്കൗണ്ടുമായി ബന്ധിപ്പിച്ചിരിക്കണം.',
        tanglish: 'Direct DBT credit kku bank account-la Aadhaar link aagirukanum.',
        hinglish: 'Direct DBT subsidy ke liye bank account se link hona zaroori hai.'
      },
      group: 'ready',
      defaultChecked: true
    },
    {
      id: 'doc-3',
      name: {
        en: 'Class 10 & 12 Marksheets',
        ta: '10 மற்றும் 12-ம் வகுப்பு மதிப்பெண் சான்றிதழ்கள்',
        hi: 'कक्षा 10वीं एवं 12वीं की अंकतालिकाएं',
        ml: 'പത്താം ക്ലാസ്, പന്ത്രണ്ടാം ക്ലാസ് മാർക്ക് ലിസ്റ്റുകൾ',
        tanglish: '10th & 12th Standard Marksheets',
        hinglish: '10th aur 12th Class ki Marksheet'
      },
      desc: {
        en: 'Original and two self-attested photocopies.',
        ta: 'அசல் மற்றும் 2 சுய கையொப்பமிட்ட நகல்கள் தேவை.',
        hi: 'मूल प्रति एवं 2 स्वप्रमाणित छायाप्रतियां आवश्यक।',
        ml: 'അസ്സലും സ്വയം സാക്ഷ്യപ്പെടുത്തിയ 2 പകർപ്പുകളും.',
        tanglish: 'Original and 2 self-attested xerox copies thevai.',
        hinglish: 'Original aur 2 self-attested photocopies zaroori.'
      },
      group: 'ready',
      defaultChecked: true
    },
    {
      id: 'doc-4',
      name: {
        en: 'Bank Passbook Front Page (Clear IFSC & A/C)',
        ta: 'வங்கி பாஸ்புக் முதல் பக்கம் (IFSC மற்றும் கணக்கு எண் தெளிவாக)',
        hi: 'बैंक पासबुक प्रथम पृष्ठ (स्पष्ट आईएफएससी एवं खाता संख्या)',
        ml: 'ബാങ്ക് പാസ്ബുക്ക് ആദ്യ പേജ് (വ്യക്തമായ IFSC & അക്കൗണ്ട് നമ്പർ)',
        tanglish: 'Bank Passbook First Page (Clear IFSC & A/C number)',
        hinglish: 'Bank Passbook First Page (Clear IFSC aur Account Number)'
      },
      desc: {
        en: 'Nationalised or scheduled bank account under applicant name.',
        ta: 'விண்ணப்பதாரர் பெயரில் உள்ள தேசியமயமாக்கப்பட்ட வங்கிக் கணக்கு.',
        hi: 'आवेदक के नाम पर राष्ट्रीयकृत या अनुसूचित बैंक खाता।',
        ml: 'അപേക്ഷകന്റെ പേരിലുള്ള ദേശസാൽകൃത ബാങ്ക് അക്കൗണ്ട്.',
        tanglish: 'Applicant peyare-la nationalised bank account irukka vendum.',
        hinglish: 'Applicant ke naam par nationalised bank account hona chahiye.'
      },
      group: 'ready',
      defaultChecked: true
    },
    {
      id: 'doc-5',
      name: {
        en: 'Community Certificate (சாதிச் சான்றிதழ்)',
        ta: 'நிரந்தர சாதிச் சான்றிதழ் (e-Sevai மூலம் பெறப்பட்டது)',
        hi: 'स्थायी जाति प्रमाण पत्र (ई-सेवा पोर्टल द्वारा जारी)',
        ml: 'സ്ഥിരം ജാതി സർട്ടിഫിക്കറ്റ് (ഇ-സേവ വഴി ലഭിച്ചത്)',
        tanglish: 'Permanent Community Certificate (e-Sevai moolam)',
        hinglish: 'Permanent Jati Praman Patra (e-Sevai se prapt)'
      },
      desc: {
        en: 'Digital e-certificate with QR code issued by Revenue Department / Zonal Deputy Tahsildar.',
        ta: 'வருவாய்த்துறை அல்லது மண்டல துணை வட்டாட்சியர் வழங்கிய QR குறியீடு கொண்ட மின்னணு சான்றிதழ்.',
        hi: 'राजस्व विभाग या उप-तहसीलदार द्वारा जारी क्यूआर कोड युक्त डिजिटल ई-प्रमाण पत्र।',
        ml: 'റവന്യൂ വകുപ്പ് നൽകിയ ക്യുആർ കോഡുള്ള ഡിജിറ്റൽ ഇ-സർട്ടിഫിക്കറ്റ്.',
        tanglish: 'Revenue Dept or Deputy Tahsildar issue panna QR code digital e-certificate.',
        hinglish: 'Revenue Department ya Deputy Tehsildar dwara jaari QR code digital certificate.'
      },
      group: 'pending',
      defaultChecked: false
    },
    {
      id: 'doc-6',
      name: {
        en: 'Income Certificate for FY 2024–25 (வருமானச் சான்றிதழ்)',
        ta: 'நடப்பு நிதியாண்டுக்கான குடும்ப வருமானச் சான்றிதழ்',
        hi: 'वित्तीय वर्ष 2024-25 का परिवार आय प्रमाण पत्र',
        ml: 'നടപ്പ് സാമ്പത്തിക വർഷത്തെ കുടുംബ വരുമാന സർട്ടിഫിക്കറ്റ്',
        tanglish: 'Current Year Family Income Certificate (Varumana Saandrithazh)',
        hinglish: 'Current FY 2024-25 ka Family Income Certificate'
      },
      desc: {
        en: 'Annual family income certificate valid within 6 months from issue date.',
        ta: 'வழங்கப்பட்ட தேதியிலிருந்து 6 மாதங்களுக்குள் செல்லுபடியாகும் வருமானச் சான்றிதழ்.',
        hi: 'जारी तिथि से 6 माह तक वैध वार्षिक पारिवारिक आय प्रमाण पत्र।',
        ml: 'നൽകിയ തീയതി മുതൽ 6 മാസത്തേക്ക് സാധുതയുള്ള വാർഷിക വരുമാന സർട്ടിഫിക്കറ്റ്.',
        tanglish: 'Issue panna date-la irundhu 6 months valid aana income certificate.',
        hinglish: 'Jaari hone ki taareekh se 6 mahine tak valid income certificate.'
      },
      group: 'pending',
      defaultChecked: false
    }
  ];

  // Helper to get localized name and desc
  const getDocName = (d) => (d.name && d.name[lang]) || d.name?.en || d.name_ta || d.name;
  const getDocDesc = (d) => (d.desc && d.desc[lang]) || d.desc?.en || d.desc_ta || d.desc;

  // Load saved checklist state from localStorage
  const savedState = JSON.parse(localStorage.getItem('nammasevai_checklist_state') || '{}');
  
  let checkedCount = 0;
  const docs = defaultDocs.map(d => {
    const isChecked = savedState[d.id] !== undefined ? savedState[d.id] : d.defaultChecked;
    if (isChecked) checkedCount++;
    return { ...d, checked: isChecked };
  });

  const totalCount = docs.length;
  const percent = Math.round((checkedCount / totalCount) * 100);
  const readyGroup = docs.filter(d => d.group === 'ready');
  const pendingGroup = docs.filter(d => d.group === 'pending');

  return `
    <div class="checklist-page-container container" style="max-width: 1150px; margin: 0 auto; padding: 1.5rem 1rem 3.5rem;">
      
      <!-- Top Banner & Context Header -->
      <div style="position: relative; background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-2xl); padding: 1.75rem; box-shadow: var(--shadow-sm); margin-bottom: 1.5rem; overflow: hidden;">
        <!-- Kolam Backdrop Blur -->
        <div style="position: absolute; right: -40px; top: -40px; width: 260px; height: 260px; border-radius: 9999px; background: rgba(217, 119, 6, 0.1); filter: blur(50px); pointer-events: none;"></div>
        
        <div style="position: relative; z-index: 10; display: flex; flex-direction: column; gap: 0.75rem;">
          <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
            <span style="display: inline-flex; align-items: center; gap: 0.35rem; padding: 0.25rem 0.75rem; border-radius: 9999px; background: var(--primary-indigo); color: #ffffff; font-size: 0.78rem; font-weight: 700;">
              <span class="material-symbols-outlined" style="font-size: 15px; color: var(--secondary-saffron);">verified</span>
              <span>${t.targetPreparationBadge || "Target Preparation"}</span>
            </span>
            <span style="font-size: 0.95rem; font-weight: 700; color: var(--primary-indigo);">
              ${t.checklistHeaderTitle || "Tamil Nadu Public Welfare Schemes Preparation"}
            </span>
          </div>

          <h1 style="font-size: 2rem; font-weight: 800; color: var(--primary-indigo); margin: 0; line-height: 1.25;">
            ${t.checklist || "Your Preparation Checklist"}
          </h1>

          <p style="font-size: 0.95rem; color: var(--text-secondary); margin: 0; max-width: 720px; line-height: 1.5;">
            ${t.checklistHeaderDesc || "Tick off documents as you gather them. Take this checklist to your college scholarship desk or nearest e-Sevai center for prompt processing."}
          </p>

          <!-- Verified Profile Metadata Capsule -->
          <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; background: var(--bg-canvas); padding: 0.5rem 0.85rem; border-radius: var(--radius-lg); border: 1px solid var(--border-color); font-size: 0.82rem; color: var(--text-secondary); margin-top: 0.25rem;">
            <span style="font-weight: 700; color: var(--primary-indigo); display: flex; align-items: center; gap: 0.25rem;">
              <span class="material-symbols-outlined" style="font-size: 16px; color: var(--secondary-saffron);">badge</span>
              <span>Verified Profile:</span>
            </span>
            <span style="background: #ffffff; padding: 0.15rem 0.55rem; border-radius: 4px; font-weight: 600; color: var(--primary-indigo);">College &amp; Citizen</span>
            <span>•</span>
            <span style="background: #ffffff; padding: 0.15rem 0.55rem; border-radius: 4px; font-weight: 600; color: var(--primary-indigo);">Tamil Nadu</span>
            <span>•</span>
            <span style="background: #ffffff; padding: 0.15rem 0.55rem; border-radius: 4px; font-weight: 600; color: var(--primary-indigo);">Income &lt; ₹2.5L</span>
            <span>•</span>
            <span style="background: #ffffff; padding: 0.15rem 0.55rem; border-radius: 4px; font-weight: 600; color: var(--primary-indigo);">DBT Bank Linked</span>
          </div>
        </div>
      </div>

      <!-- Action & Quick Utility Bar -->
      <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-xl); padding: 0.85rem 1.25rem; box-shadow: var(--shadow-sm); margin-bottom: 1.75rem; display: flex; flex-direction: column; sm:flex-row; justify-content: space-between; align-items: stretch; sm:align-items: center; gap: 0.75rem;">
        <div style="display: flex; align-items: center; gap: 0.65rem; flex-wrap: wrap;">
          <button class="btn btn-primary" id="downloadPdfBtn" onclick="window.print()" type="button" style="padding: 0.45rem 1rem; font-size: 0.86rem; display: flex; align-items: center; gap: 0.4rem;">
            <span class="material-symbols-outlined" style="font-size: 18px;">download</span>
            <span>${t.downloadChecklist || "Download Checklist (PDF)"}</span>
          </button>

          <button class="btn btn-outline" id="downloadTextChecklistBtn" type="button" style="padding: 0.45rem 1rem; font-size: 0.86rem; display: flex; align-items: center; gap: 0.4rem;">
            <span class="material-symbols-outlined" style="font-size: 18px; color: var(--primary-indigo);">description</span>
            <span>${t.downloadChecklist || "Download"} (.txt)</span>
          </button>

          <button class="btn btn-outline" id="copyShareChecklistBtn" type="button" style="padding: 0.45rem 1rem; font-size: 0.86rem; display: flex; align-items: center; gap: 0.4rem;">
            <span class="material-symbols-outlined" style="font-size: 18px; color: var(--secondary-saffron);">content_copy</span>
            <span>${t.shareChecklist || "Copy / Share Checklist"}</span>
          </button>

          <button class="btn btn-outline" id="shareWhatsappBtn" onclick="window.open('https://api.whatsapp.com/send?text=' + encodeURIComponent('Check my NammaSevai AI Scheme Preparation Checklist: All core documents verified!'))" type="button" style="padding: 0.45rem 1rem; font-size: 0.86rem; display: flex; align-items: center; gap: 0.4rem;">
            <span class="material-symbols-outlined" style="font-size: 18px; color: var(--tertiary-green);">share</span>
            <span>WhatsApp</span>
          </button>
        </div>

        <div style="display: flex; align-items: center; gap: 0.5rem; justify-content: flex-end;">
          <button class="tts-listen-btn btn btn-outline btn-sm" data-tts-text="${encodeURIComponent(docs.map(d => getDocName(d)).join('. '))}" type="button" title="Listen to checklist guidance" style="padding: 0.35rem 0.75rem; font-size: 0.8rem; display: flex; align-items: center; gap: 0.35rem;">
            <span class="material-symbols-outlined" style="font-size: 16px; color: var(--secondary-saffron);">volume_up</span>
            <span>${t.listenAudio || "Audio Assist"}</span>
          </button>
          
          <div style="width: 1px; height: 18px; background: var(--border-color);"></div>

          <button class="btn btn-outline btn-sm" id="resetAllChecklist" type="button" title="Reset all checkboxes" style="padding: 0.35rem 0.75rem; font-size: 0.8rem; display: flex; align-items: center; gap: 0.35rem; color: #dc2626; border-color: rgba(220, 38, 38, 0.3);">
            <span class="material-symbols-outlined" style="font-size: 16px;">restart_alt</span>
            <span>${t.resetChecklistBtn || "Reset"}</span>
          </button>
        </div>
      </div>

      <!-- Main Layout: Interactive Checklist vs Next Steps Dossier -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.75rem; align-items: start;">
        
        <!-- Left Column: Interactive Checklist System -->
        <div style="display: flex; flex-direction: column; gap: 1.5rem; flex: 2; min-width: 0;">
          
          <!-- Readiness Tracker Module -->
          <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-xl); padding: 1.25rem 1.5rem; box-shadow: var(--shadow-sm); display: flex; flex-direction: column; gap: 0.65rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <div style="display: flex; align-items: center; gap: 0.4rem;">
                <span class="material-symbols-outlined" style="font-size: 22px; color: var(--secondary-saffron);">task_alt</span>
                <span style="font-size: 1.15rem; font-weight: 800; color: var(--primary-indigo);">${t.checklist || "Readiness Tracker"}</span>
              </div>
              <span id="readinessCountBadge" style="font-size: 0.95rem; font-weight: 800; color: ${percent >= 75 ? 'var(--tertiary-green)' : 'var(--secondary-saffron)'};">
                ${checkedCount} / ${totalCount} (${percent}%)
              </span>
            </div>

            <!-- Progress Bar Meter -->
            <div style="width: 100%; height: 10px; border-radius: 9999px; background: var(--bg-canvas); overflow: hidden; border: 1px solid var(--border-color);">
              <div id="readinessProgressBar" style="height: 100%; width: ${percent}%; background: ${percent >= 75 ? 'var(--tertiary-green)' : 'var(--secondary-saffron)'}; border-radius: 9999px; transition: width 0.4s ease;"></div>
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; color: var(--text-secondary); padding-top: 0.25rem;">
              <span>${totalCount - checkedCount} ${t.pendingDocumentsDesc || "pending certificates require revenue / e-Sevai generation"}</span>
              <span style="font-weight: 700; color: var(--secondary-saffron);">${t.statsTamilNaduFocus || "Target: Active FY 2024–25"}</span>
            </div>
          </div>

          <!-- Group 1: Already Have / Ready (In Hand) -->
          <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-xl); padding: 1.5rem; box-shadow: var(--shadow-sm); display: flex; flex-direction: column; gap: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border-color);">
              <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 32px; height: 32px; border-radius: 9999px; background: rgba(21, 128, 61, 0.12); display: flex; align-items: center; justify-content: center; color: var(--tertiary-green);">
                  <span class="material-symbols-outlined" style="font-size: 18px;">check_circle</span>
                </div>
                <div>
                  <h2 style="font-size: 1.15rem; font-weight: 800; color: var(--primary-indigo); margin: 0;">
                    ${t.readyDocumentsTitle || "Already Have / Ready"}
                  </h2>
                  <span style="font-size: 0.78rem; color: var(--text-secondary);">${t.readyDocumentsDesc || "Verify physical copies are handy"}</span>
                </div>
              </div>
              <span style="padding: 0.2rem 0.65rem; border-radius: 9999px; background: rgba(21, 128, 61, 0.12); color: var(--tertiary-green); font-size: 0.75rem; font-weight: 700;">
                In Hand
              </span>
            </div>

            <div style="display: flex; flex-direction: column; gap: 0.75rem;">
              ${readyGroup.map(d => `
                <label class="checklist-item-interactive" data-doc-id="${d.id}" style="display: flex; align-items: flex-start; gap: 0.75rem; background: var(--bg-canvas); padding: 0.85rem 1rem; border-radius: var(--radius-lg); border: 1.5px solid ${d.checked ? 'var(--tertiary-green)' : 'var(--border-color)'}; cursor: pointer; transition: all 0.2s ease;">
                  <input type="checkbox" class="interactive-doc-checkbox" data-id="${d.id}" ${d.checked ? 'checked' : ''} style="margin-top: 3px; width: 20px; height: 20px; accent-color: var(--secondary-saffron); cursor: pointer;" />
                  <div style="flex: 1;">
                    <span style="font-size: 0.92rem; font-weight: 700; color: var(--primary-indigo); display: block;">
                      ${getDocName(d)}
                    </span>
                    <span style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.4; display: block; margin-top: 0.15rem;">
                      ${getDocDesc(d)}
                    </span>
                  </div>
                  <span class="material-symbols-outlined" style="font-size: 20px; color: ${d.checked ? 'var(--tertiary-green)' : 'var(--border-color)'}; flex-shrink: 0; margin-top: 2px;">
                    ${d.checked ? 'check_circle' : 'radio_button_unchecked'}
                  </span>
                </label>
              `).join('')}
            </div>
          </div>

          <!-- Group 2: Needs to be Obtained / e-Sevai Service -->
          <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-xl); padding: 1.5rem; box-shadow: var(--shadow-sm); display: flex; flex-direction: column; gap: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border-color);">
              <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 32px; height: 32px; border-radius: 9999px; background: rgba(217, 119, 6, 0.12); display: flex; align-items: center; justify-content: center; color: var(--secondary-saffron);">
                  <span class="material-symbols-outlined" style="font-size: 18px;">pending_actions</span>
                </div>
                <div>
                  <h2 style="font-size: 1.15rem; font-weight: 800; color: var(--primary-indigo); margin: 0;">
                    ${t.pendingDocumentsTitle || "Needs to be Obtained (e-Sevai)"}
                  </h2>
                  <span style="font-size: 0.78rem; color: var(--text-secondary);">${t.pendingDocumentsDesc || "Revenue & Tahsildar generation required"}</span>
                </div>
              </div>
              <span style="padding: 0.2rem 0.65rem; border-radius: 9999px; background: rgba(217, 119, 6, 0.12); color: var(--secondary-saffron); font-size: 0.75rem; font-weight: 700;">
                Revenue
              </span>
            </div>

            <div style="display: flex; flex-direction: column; gap: 0.75rem;">
              ${pendingGroup.map(d => `
                <label class="checklist-item-interactive" data-doc-id="${d.id}" style="display: flex; align-items: flex-start; gap: 0.75rem; background: var(--bg-canvas); padding: 0.85rem 1rem; border-radius: var(--radius-lg); border: 1.5px solid ${d.checked ? 'var(--tertiary-green)' : 'var(--border-color)'}; cursor: pointer; transition: all 0.2s ease;">
                  <input type="checkbox" class="interactive-doc-checkbox" data-id="${d.id}" ${d.checked ? 'checked' : ''} style="margin-top: 3px; width: 20px; height: 20px; accent-color: var(--secondary-saffron); cursor: pointer;" />
                  <div style="flex: 1;">
                    <span style="font-size: 0.92rem; font-weight: 700; color: var(--primary-indigo); display: block;">
                      ${getDocName(d)}
                    </span>
                    <span style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.4; display: block; margin-top: 0.15rem;">
                      ${getDocDesc(d)}
                    </span>
                  </div>
                  <span class="material-symbols-outlined" style="font-size: 20px; color: ${d.checked ? 'var(--tertiary-green)' : 'var(--border-color)'}; flex-shrink: 0; margin-top: 2px;">
                    ${d.checked ? 'check_circle' : 'radio_button_unchecked'}
                  </span>
                </label>
              `).join('')}
            </div>
          </div>

        </div>

        <!-- Right Column: Next Steps Dossier -->
        <div style="display: flex; flex-direction: column; gap: 1.5rem; flex: 1; min-width: 0;">
          
          <!-- Next Steps & Where to Go -->
          <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-xl); padding: 1.5rem; box-shadow: var(--shadow-sm);">
            <div style="display: flex; align-items: center; gap: 0.4rem; font-size: 1.05rem; font-weight: 800; color: var(--primary-indigo); margin-bottom: 0.75rem;">
              <span class="material-symbols-outlined" style="font-size: 20px; color: var(--secondary-saffron);">storefront</span>
              <span>Where to apply with this checklist?</span>
            </div>

            <div style="display: flex; flex-direction: column; gap: 0.85rem; font-size: 0.86rem; color: var(--text-secondary); line-height: 1.5;">
              <div style="background: var(--bg-canvas); padding: 0.75rem; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
                <strong style="color: var(--primary-indigo); display: block; margin-bottom: 0.2rem;">1. College Scholarship Cell / Desk</strong>
                Submit bonafide, fee receipt, and marksheet photocopies to your institution nodal officer.
              </div>

              <div style="background: var(--bg-canvas); padding: 0.75rem; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
                <strong style="color: var(--primary-indigo); display: block; margin-bottom: 0.2rem;">2. Nearest e-Sevai Center</strong>
                For digital revenue certificates (Income, Community, Nativity, First-Gen Graduate).
              </div>

              <div style="background: var(--bg-canvas); padding: 0.75rem; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
                <strong style="color: var(--primary-indigo); display: block; margin-bottom: 0.2rem;">3. Online Portals</strong>
                TN e-District, NSP, and Umang portals for direct individual applications.
              </div>
            </div>
          </div>

          <!-- Official Helplines -->
          <div style="background: var(--bg-canvas); border: 1px solid var(--border-color); border-radius: var(--radius-xl); padding: 1.25rem;">
            <div style="font-size: 0.95rem; font-weight: 800; color: var(--primary-indigo); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.35rem;">
              <span class="material-symbols-outlined" style="font-size: 18px; color: var(--secondary-saffron);">call</span>
              <span>${t.helplineTitle}</span>
            </div>
            <p style="font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 0.75rem; line-height: 1.4;">
              ${t.helplineSupport || "Free citizen telephonic guidance for state scholarship certificates:"}
            </p>
            <div style="display: flex; flex-direction: column; gap: 0.35rem; font-size: 0.84rem; color: var(--text-primary); font-weight: 600;">
              <div>📞 1100 – ${t.cmHelpline || "Chief Minister Helpline"}</div>
              <div>📞 14417 – ${t.studentHelpline || "Education Helpline"}</div>
              <div>📞 181 – ${t.womenHelpline || "Women Helpline"}</div>
            </div>
          </div>

          <!-- Quick Return Action -->
          <div style="text-align: center;">
            <a href="#schemes" class="btn btn-outline" style="width: 100%; justify-content: center; padding: 0.5rem;">
              <span>← ${t.backToSchemes || "Return to Schemes Catalog"}</span>
            </a>
          </div>

        </div>

      </div>

      <!-- Public-Service Guidance Disclaimer Strip -->
      <div style="background: rgba(21, 35, 62, 0.04); border: 1px solid var(--border-color); border-radius: var(--radius-xl); padding: 1.15rem 1.5rem; margin-top: 2rem; display: flex; align-items: flex-start; gap: 0.85rem; font-size: 0.86rem; color: var(--text-secondary); line-height: 1.5;">
        <span class="material-symbols-outlined" style="font-size: 22px; color: var(--secondary-saffron); flex-shrink: 0; margin-top: 1px;">gavel</span>
        <div>
          <strong style="color: var(--primary-indigo); font-weight: 700; display: block; margin-bottom: 0.25rem;">
            ${t.guidanceOnlyBadge || "Public-Service Guidance Disclaimer:"}
          </strong>
          ${t.disclaimerDetailedNotice || "This document checklist is generated for preliminary preparation guidance only and does not constitute official document verification or government approval. Final eligibility, certificate scrutiny, and sanction decisions rest exclusively with the designated competent government authorities upon physical/digital verification."}
        </div>
      </div>

    </div>
  `;
}
