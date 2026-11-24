// NammaSevai AI - NLP Matching Engine
// Understands citizen queries in Tamil, Tanglish, and English
export class SchemeMatcher {
  constructor(schemes) {
    this.schemes = schemes || [];
  }

  setSchemes(schemes) {
    this.schemes = schemes;
  }

  // Tokenize and clean text
  normalizeText(text) {
    if (!text) return "";
    return text
      .toLowerCase()
      .replace(/[.,\/#!$%\^&\*;:{}=\-_`~()?"'’]/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  // Detect query demographics and intent
  extractIntent(rawQuery) {
    const text = this.normalizeText(rawQuery);
    
    const intent = {
      isStudent: false,
      isGirl: false,
      isBoy: false,
      isFarmer: false,
      isMotherOrHousewife: false,
      isWidowOrDestitute: false,
      isTailor: false,
      isSenior: false,
      isDifferentlyAbled: false,
      isJobSeeker: false,
      isEntrepreneur: false,
      needsHealth: false,
      needsHousing: false,
      isScSt: false,
      categories: new Set()
    };

    // Education & Students
    if (
      text.includes("student") || text.includes("college") || text.includes("school") ||
      text.includes("degree") || text.includes("12th") || text.includes("10th") ||
      text.includes("scholarship") || text.includes("kalloori") || text.includes("padipu") ||
      text.includes("maanavi") || text.includes("maanavar") || text.includes("பள்ளி") ||
      text.includes("கல்லூரி") || text.includes("மாணவி") || text.includes("மாணவர்") ||
      text.includes("படிப்பு") || text.includes("உதவித்தொகை") || text.includes("கல்வி")
    ) {
      intent.isStudent = true;
      intent.categories.add("education");
    }

    // Gender
    if (
      text.includes("girl") || text.includes("female") || text.includes("woman") ||
      text.includes("women") || text.includes("mother") || text.includes("lady") ||
      text.includes("pen") || text.includes("thaimaar") || text.includes("பெண்") ||
      text.includes("மகளிர்") || text.includes("தாய்") || text.includes("அம்மா") ||
      text.includes("மனைவி")
    ) {
      intent.isGirl = true;
      intent.categories.add("women");
    }

    if (
      text.includes("boy") || text.includes("male") || text.includes("man") ||
      text.includes("aan") || text.includes("ஆண்") || text.includes("மாணவன்")
    ) {
      intent.isBoy = true;
    }

    // Agriculture & Farmers
    if (
      text.includes("farmer") || text.includes("agriculture") || text.includes("crop") ||
      text.includes("land") || text.includes("dryland") || text.includes("acres") ||
      text.includes("seed") || text.includes("fertilizer") || text.includes("uzhavar") ||
      text.includes("vivasaayi") || text.includes("patta") || text.includes("விவசாயி") ||
      text.includes("உழவர்") || text.includes("பயிர்") || text.includes("நிலம்") ||
      text.includes("வேளாண்") || text.includes("ஏக்கர்") || text.includes("சிட்டா")
    ) {
      intent.isFarmer = true;
      intent.categories.add("agriculture");
    }

    // Tailoring / Sewing
    if (
      text.includes("sewing") || text.includes("tailor") || text.includes("tailoring") ||
      text.includes("stitch") || text.includes("machine") || text.includes("thaiyal") ||
      text.includes("தையல்") || text.includes("இயந்திரம்") || text.includes("துணி")
    ) {
      intent.isTailor = true;
      intent.categories.add("women");
      intent.categories.add("employment");
    }

    // Widow / Destitute
    if (
      text.includes("widow") || text.includes("destitute") || text.includes("single mother") ||
      text.includes("deserted") || text.includes("kaividapatta") || text.includes("vidhavai") ||
      text.includes("விதவை") || text.includes("ஆதரவற்ற") || text.includes("கைவிடப்பட்ட")
    ) {
      intent.isWidowOrDestitute = true;
      intent.categories.add("women");
    }

    // Senior Citizens
    if (
      text.includes("senior") || text.includes("old age") || text.includes("60") ||
      text.includes("65") || text.includes("70") || text.includes("elderly") ||
      text.includes("pension") || text.includes("grandfather") || text.includes("grandmother") ||
      text.includes("periyavar") || text.includes("thaatha") || text.includes("paati") ||
      text.includes("முதியோர்") || text.includes("வயதான") || text.includes("ஓய்வூதியம்") ||
      text.includes("தாத்தா") || text.includes("பாட்டி")
    ) {
      intent.isSenior = true;
      intent.categories.add("seniors");
    }

    // Differently Abled / Disability
    if (
      text.includes("handicapped") || text.includes("disabled") || text.includes("disability") ||
      text.includes("wheelchair") || text.includes("blind") || text.includes("deaf") ||
      text.includes("udid") || text.includes("maatru thiranaali") || text.includes("oonam") ||
      text.includes("மாற்றுத்திறனாளி") || text.includes("ஊனம்") || text.includes("பார்வையற்ற")
    ) {
      intent.isDifferentlyAbled = true;
      intent.categories.add("disability");
    }

    // Health & Medical
    if (
      text.includes("health") || text.includes("hospital") || text.includes("treatment") ||
      text.includes("surgery") || text.includes("insurance") || text.includes("medicine") ||
      text.includes("doctor") || text.includes("pregnant") || text.includes("delivery") ||
      text.includes("maruthuvam") || text.includes("kaappeettu") || text.includes("பிரசவம்") ||
      text.includes("மருத்துவம்") || text.includes("காப்பீடு") || text.includes("சிகிச்சை") ||
      text.includes("கர்ப்பிணி") || text.includes("மருத்துவமனை")
    ) {
      intent.needsHealth = true;
      intent.categories.add("health");
    }

    // Housing & Shelter
    if (
      text.includes("house") || text.includes("housing") || text.includes("hut") ||
      text.includes("concrete") || text.includes("patta") || text.includes("roof") ||
      text.includes("kudisai") || text.includes("veedu") || text.includes("வீடு") ||
      text.includes("குடிசை") || text.includes("கான்கிரீட்") || text.includes("கனவு இல்லம்")
    ) {
      intent.needsHousing = true;
      intent.categories.add("housing");
    }

    // Jobs & Upskilling
    if (
      text.includes("skill") || text.includes("training") || text.includes("job") ||
      text.includes("course") || text.includes("coding") || text.includes("upsc") ||
      text.includes("tnpsc") || text.includes("unemployed") || text.includes("graduate") ||
      text.includes("velaivaippu") || text.includes("thiran") || text.includes("பயிற்சி") ||
      text.includes("வேலை") || text.includes("திறன்") || text.includes("போட்டித் தேர்வு")
    ) {
      intent.isJobSeeker = true;
      intent.categories.add("employment");
    }

    // Business & SC/ST Entrepreneurship
    if (
      text.includes("business") || text.includes("startup") || text.includes("loan") ||
      text.includes("subsidy") || text.includes("msme") || text.includes("sc") ||
      text.includes("st") || text.includes("dalit") || text.includes("thozhil") ||
      text.includes("தொழில்") || text.includes("மானியம்") || text.includes("கடன்") ||
      text.includes("தொழில்முனைவோர்") || text.includes("ஆதிதிராவிடர்")
    ) {
      intent.isEntrepreneur = true;
      if (text.includes("sc") || text.includes("st") || text.includes("dalit") || text.includes("ஆதிதிராவிடர்")) {
        intent.isScSt = true;
      }
      intent.categories.add("employment");
    }

    return intent;
  }

  // Match schemes based on natural query
  match(rawQuery, lang = "ta") {
    if (!rawQuery || rawQuery.trim().length === 0) {
      return { matches: [], profile: null, responseMessage: "" };
    }

    const intent = this.extractIntent(rawQuery);
    const normalized = this.normalizeText(rawQuery);
    const tokens = normalized.split(/\s+/).filter(t => t.length > 2);

    const scoredSchemes = this.schemes.map(scheme => {
      let score = 0;
      let reasonsEn = [];
      let reasonsTa = [];

      // Category match
      if (intent.categories.has(scheme.category)) {
        score += 35;
      }

      // Keyword matching
      let keywordHits = 0;
      if (scheme.keywords && Array.isArray(scheme.keywords)) {
        for (const kw of scheme.keywords) {
          const normKw = kw.toLowerCase();
          if (normalized.includes(normKw)) {
            score += 15;
            keywordHits++;
          }
        }
      }

      // Token overlap in name, description
      const schemeText = (scheme.name + " " + scheme.name_ta + " " + scheme.description + " " + scheme.description_ta).toLowerCase();
      for (const token of tokens) {
        if (schemeText.includes(token)) {
          score += 5;
        }
      }

      // Domain-specific rule evaluation
      if (scheme.id === "pudhumai-penn") {
        if (intent.isStudent && intent.isGirl) {
          score += 50;
          reasonsEn.push("You are a female student joining college. This scheme guarantees ₹1,000/month directly to your bank account.");
          reasonsTa.push("நீங்கள் கல்லூரி செல்லும் பெண் மாணவி என்பதால், இந்த திட்டத்தில் மாதம் ₹1,000 நேரடி உதவித்தொகை பெறலாம்.");
        } else if (intent.isStudent) {
          score += 20;
          reasonsEn.push("Higher education assistance for eligible students.");
          reasonsTa.push("உயர்கல்வி பயிலும் மாணவர்களுக்கான நிதி உதவித் திட்டம்.");
        }
      }

      if (scheme.id === "tamil-pudhalvan") {
        if (intent.isStudent && (intent.isBoy || !intent.isGirl)) {
          score += 45;
          reasonsEn.push("You are a male student joining higher education. This scheme provides ₹1,000/month for college books and needs.");
          reasonsTa.push("நீங்கள் உயர்கல்வி பயிலும் மாணவர் என்பதால், புத்தகங்கள் மற்றும் கல்லூரி செலவுகளுக்கு மாதம் ₹1,000 பெறலாம்.");
        }
      }

      if (scheme.id === "kmut-magalir") {
        if (intent.isGirl && !intent.isStudent) {
          score += 40;
          reasonsEn.push("Provides ₹1,000/month basic income for eligible women heads of households in Tamil Nadu.");
          reasonsTa.push("குடும்பத் தலைவிகளுக்கு மாதம் ₹1,000 உரிமைத் தொகை வழங்கும் வரலாற்று சிறப்புமிக்க திட்டம்.");
        }
      }

      if (scheme.id === "sewing-machine-welfare") {
        if (intent.isTailor || (intent.isGirl && (intent.isWidowOrDestitute || normalized.includes("machine") || normalized.includes("தையல்")))) {
          score += 60;
          reasonsEn.push("Free motorized sewing machine provided for self-employment livelihood.");
          reasonsTa.push("தையல் தொழில் மூலம் சுயவாழ்வாதாரம் பெற இலவச நவீன தையல் இயந்திரம் வழங்கப்படுகிறது.");
        }
      }

      if (scheme.id === "pm-kisan-tn") {
        if (intent.isFarmer) {
          score += 65;
          reasonsEn.push("Direct ₹6,000 annual installment income support + Tamil Nadu crop relief for farmers.");
          reasonsTa.push("சிறு, குறு விவசாயிகளுக்கு ஆண்டுக்கு ₹6,000 நேரடி உதவித்தொகை மற்றும் பயிர் மானியங்கள் கிடைக்கின்றன.");
        }
      }

      if (scheme.id === "naan-mudhalvan") {
        if (intent.isJobSeeker || (intent.isStudent && !intent.isFarmer)) {
          score += 40;
          reasonsEn.push("Free high-tech training courses and competitive exam coaching allowances.");
          reasonsTa.push("இலவச தொழில்முறை திறன் பயிற்சிகள் மற்றும் போட்டித் தேர்வுக்கான நிதி உதவி திட்டம்.");
        }
      }

      if (scheme.id === "muthulakshmi-maternity") {
        if (normalized.includes("pregnant") || normalized.includes("baby") || normalized.includes("maternity") || normalized.includes("கர்ப்பிணி") || normalized.includes("பிரசவம்")) {
          score += 70;
          reasonsEn.push("Provides ₹18,000 total maternity assistance and nutrition kits for pregnant mothers.");
          reasonsTa.push("ஏழை கர்ப்பிணித் தாய்மார்களுக்கு ₹18,000 மதிப்புள்ள நிதி உதவி மற்றும் ஊட்டச்சத்து பெட்டகம் வழங்கப்படுகிறது.");
        }
      }

      if (scheme.id === "oap-senior-pension") {
        if (intent.isSenior) {
          score += 65;
          reasonsEn.push("Monthly ₹1,200 pension + free rice for destitute citizens aged 60 and above.");
          reasonsTa.push("60 வயதுக்கு மேற்பட்ட ஆதரவற்ற முதியவர்களுக்கு மாதம் ₹1,200 ஓய்வூதியம் மற்றும் இலவச அரிசி வழங்கப்படுகிறது.");
        }
      }

      if (scheme.id === "differently-abled-welfare") {
        if (intent.isDifferentlyAbled) {
          score += 75;
          reasonsEn.push("₹1,500 - ₹2,000 monthly maintenance allowance, assistive devices and free transport pass.");
          reasonsTa.push("மாற்றுத்திறனாளிகளுக்கு மாதம் ₹1,500 - ₹2,000 பராமரிப்பு உதவித்தொகை மற்றும் இலவச உபகரணங்கள் கிடைக்கின்றன.");
        }
      }

      if (scheme.id === "aabcs-scst-entrepreneur") {
        if (intent.isEntrepreneur || intent.isScSt) {
          score += 55;
          reasonsEn.push("35% capital subsidy up to ₹1.5 Cr and 6% interest relief for SC/ST entrepreneurs.");
          reasonsTa.push("ஆதிதிராவிடர் (SC/ST) தொழில் முனைவோருக்கு 35% மூலதன மானியம் மற்றும் கடன் உதவி வழங்கப்படுகிறது.");
        }
      }

      if (scheme.id === "cmchis-health") {
        if (intent.needsHealth) {
          score += 60;
          reasonsEn.push("Cashless hospitalization treatment up to ₹5 Lakhs per family per year.");
          reasonsTa.push("குடும்பத்திற்கு ஆண்டுக்கு ₹5 லட்சம் வரை கட்டணமில்லா சிகிச்சை காப்பீடு வழங்கப்படுகிறது.");
        }
      }

      if (scheme.id === "kalaignar-kanavu-illam") {
        if (intent.needsHousing) {
          score += 65;
          reasonsEn.push("₹3,50,000 grant assistance to build a durable permanent concrete home.");
          reasonsTa.push("புதிய நிரந்தர கான்கிரீட் வீடு கட்ட ₹3,50,000 நேரடி அரசு நிதி உதவி வழங்கப்படுகிறது.");
        }
      }

      // Default fallback match reason if none generated
      if (reasonsEn.length === 0) {
        reasonsEn.push(`Matches your interest in ${scheme.category} welfare benefits (${scheme.benefit_amount}).`);
        reasonsTa.push(`உங்கள் தேவையின் அடிப்படையில் ${scheme.benefit_amount} உதவி வழங்கும் இந்த திட்டம் பொருந்துகிறது.`);
      }

      // Normalize score between 10% and 99%
      let matchPercent = Math.min(Math.max(Math.round(score), 20), 99);
      if (score >= 60) matchPercent = Math.min(90 + Math.round(score / 10), 98);

      let status = "moderate";
      if (matchPercent >= 85) status = "high";
      else if (matchPercent < 50) status = "check";

      return {
        scheme,
        score,
        matchPercent,
        status,
        reasonEn: reasonsEn.join(" "),
        reasonTa: reasonsTa.join(" ")
      };
    });

    // Filter and sort schemes with positive relevance
    const matches = scoredSchemes
      .filter(item => item.score > 15 || tokens.some(t => item.scheme.name.toLowerCase().includes(t)))
      .sort((a, b) => b.score - a.score);

    // If query was very generic, return top relevant schemes
    const finalMatches = matches.length > 0 ? matches : scoredSchemes.slice(0, 3);

    // Generate conversational response text
    let responseMessageEn = "";
    let responseMessageTa = "";
    let responseMessageHi = "";
    let responseMessageMl = "";
    let responseMessageTanglish = "";
    let responseMessageHinglish = "";

    if (finalMatches.length > 0) {
      const top = finalMatches[0];
      const count = finalMatches.length;

      const nameTa = top.scheme.name_ta || top.scheme.name;
      const benefitTa = top.scheme.benefit_summary_ta || top.scheme.benefit_summary;
      const nameHi = top.scheme.name_hi || top.scheme.name;
      const benefitHi = top.scheme.benefit_summary_hi || top.scheme.benefit_summary;
      const nameMl = top.scheme.name_ml || top.scheme.name;
      const benefitMl = top.scheme.benefit_summary_ml || top.scheme.benefit_summary;

      responseMessageEn = `I have analyzed your situation and found ${count} welfare scheme${count > 1 ? "s" : ""} matching your profile. The top recommendation is "${top.scheme.name}", which provides ${top.scheme.benefit_summary}. You will need documents like Aadhaar, Smart Ration Card, and relevant certificates to apply.`;
      
      responseMessageTa = `உங்கள் தேவையை ஆய்வு செய்து, உங்களுக்கு தகுதியான ${count} அரசு நலத்திட்டங்களை கண்டறிந்துள்ளேன். இதில் முதன்மையான திட்டம் "${nameTa}" ஆகும். இதன் மூலம் ${benefitTa} பெறலாம். இதற்கு ஆதார், குடும்ப அட்டை போன்ற ஆவணங்கள் தேவைப்படும். கீழே உள்ள விவரங்களை சரிபார்க்கவும்.`;

      responseMessageTanglish = `Unga situation-ah analyze panni ${count} welfare schemes match pannirukken. Top scheme "${nameTa}" (Benefit: ${benefitTa}). Thevaiyaana certificates & documents check pannunga.`;

      responseMessageHi = `आपकी स्थिति का विश्लेषण करने के बाद मुझे ${count} कल्याणकारी योजनाएं मिली हैं। मुख्य योजना "${nameHi}" है (लाभ: ${benefitHi})। आवेदन के लिए आधार कार्ड और संबंधित प्रमाण पत्र आवश्यक होंगे।`;

      responseMessageHinglish = `Aapki profile analyze karke ${count} matching welfare schemes identify hui hain. Top scheme "${nameHi}" hai (Benefit: ${benefitHi}). Kripya neeche zaroori documents checklist check karein.`;

      responseMessageMl = `നിങ്ങളുടെ സാഹചര്യം പരിശോധിച്ച് ${count} ക്ഷേമപദ്ധതികൾ കണ്ടെത്തിയിട്ടുണ്ട്. പ്രധാന പദ്ധതി "${nameMl}" ആണ് (ആനുകൂല്യം: ${benefitMl}). താഴെ നൽകിയിട്ടുള്ള രേഖകൾ പരിശോധിക്കുക.`;
    } else {
      responseMessageEn = "I couldn't find an exact scheme match for your query. Try describing your occupation, education, or whether you are a farmer, student, or senior citizen.";
      responseMessageTa = "உங்கள் தகவலுக்கு நேரடி திட்டம் எதுவும் கிடைக்கவில்லை. உங்கள் படிப்பு, தொழில், விவசாய நிலம் அல்லது வயது போன்ற விவரங்களை குறிப்பிட்டு மீண்டும் பேசுங்கள்.";
      responseMessageTanglish = "Unga details-kku direct scheme edhuvum match aagala. Unga education, land, income, or velai pathi innum konjam sollunga.";
      responseMessageHi = "आपकी जानकारी के अनुसार कोई प्रत्यक्ष योजना नहीं मिली। कृपया अपनी शिक्षा, व्यवसाय, कृषि भूमि या आय का विवरण देकर पुनः प्रयास करें।";
      responseMessageHinglish = "Aapki details se matching koi direct scheme nahi mili. Kripya apni education, zameen ya income ke baare mein thoda aur batayein.";
      responseMessageMl = "നിങ്ങൾ നൽകിയ വിവരങ്ങൾക്ക് അനുയോജ്യമായ നേരിട്ടുള്ള പദ്ധതികൾ ഒന്നും കണ്ടെത്താനായില്ല. ദയവായി നിങ്ങളുടെ വിദ്യാഭ്യാസം അല്ലെങ്കിൽ തൊഴിൽ വിവരങ്ങൾ നൽകുക.";
    }

    let finalMsg = responseMessageEn;
    if (lang === "ta") finalMsg = responseMessageTa;
    else if (lang === "tanglish") finalMsg = responseMessageTanglish;
    else if (lang === "hi") finalMsg = responseMessageHi;
    else if (lang === "hinglish") finalMsg = responseMessageHinglish;
    else if (lang === "ml") finalMsg = responseMessageMl;

    return {
      query: rawQuery,
      matches: finalMatches,
      intent,
      responseMessage: finalMsg,
      responseMessageEn,
      responseMessageTa,
      responseMessageHi,
      responseMessageMl,
      responseMessageTanglish,
      responseMessageHinglish
    };
  }
}
