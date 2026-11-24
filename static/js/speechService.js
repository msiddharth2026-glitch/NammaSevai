// NammaSevai AI - Speech Recognition & Text-To-Speech Service
export class SpeechService {
  constructor() {
    this.recognition = null;
    this.isListening = false;
    this.synthesis = window.speechSynthesis || null;
    this.currentUtterance = null;
    this.initRecognition();
  }

  initRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = false;
      this.recognition.interimResults = true;
      this.recognition.maxAlternatives = 1;
    } else {
      console.warn("Speech Recognition API not supported in this browser.");
    }
  }

  isSupported() {
    return !!(window.SpeechRecognition || window.webkitSpeechRecognition);
  }

  isTtsSupported() {
    return !!(window.speechSynthesis);
  }

  startListening(options = {}) {
    if (!this.recognition) {
      if (options.onError) {
        options.onError("Speech recognition is not supported in this browser. Please type your query.");
      }
      return;
    }

    if (this.isListening) {
      this.stopListening();
    }

    const langMap = {
      ta: "ta-IN",
      hi: "hi-IN",
      ml: "ml-IN",
      en: "en-IN",
      tanglish: "ta-IN",
      hinglish: "hi-IN"
    };
    const langCode = langMap[options.lang] || (options.lang && options.lang.includes("-") ? options.lang : "en-IN");
    this.recognition.lang = langCode;

    this.recognition.onstart = () => {
      this.isListening = true;
      if (options.onStart) options.onStart();
    };

    this.recognition.onresult = (event) => {
      let interimTranscript = "";
      let finalTranscript = "";

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }

      if (options.onTranscript) {
        options.onTranscript(finalTranscript || interimTranscript, !!finalTranscript);
      }
    };

    this.recognition.onerror = (event) => {
      this.isListening = false;
      console.error("Speech recognition error:", event.error);
      if (options.onError) {
        options.onError(event.error);
      }
    };

    this.recognition.onend = () => {
      this.isListening = false;
      if (options.onEnd) options.onEnd();
    };

    try {
      this.recognition.start();
    } catch (err) {
      console.error("Error starting speech recognition:", err);
      this.isListening = false;
      if (options.onError) options.onError(err.message);
    }
  }

  stopListening() {
    if (this.recognition && this.isListening) {
      this.recognition.stop();
      this.isListening = false;
    }
  }

  // Text to Speech
  speak(text, lang = "ta", callbacks = {}) {
    if (!this.synthesis) {
      console.warn("Speech synthesis not supported.");
      return;
    }

    this.stopSpeaking();

    // Clean markdown/special characters for clear speech
    const cleanText = text
      .replace(/[*_#`~[\]()]/g, "")
      .replace(/\s+/g, " ")
      .trim();

    if (!cleanText) return;

    this.currentUtterance = new SpeechSynthesisUtterance(cleanText);
    const langMap = {
      ta: "ta-IN",
      hi: "hi-IN",
      ml: "ml-IN",
      en: "en-IN",
      tanglish: "ta-IN",
      hinglish: "hi-IN"
    };
    const ttsLang = langMap[lang] || (lang && lang.includes("-") ? lang : "en-IN");
    this.currentUtterance.lang = ttsLang;
    this.currentUtterance.rate = 0.95; // slightly slower for citizen clarity
    this.currentUtterance.pitch = 1.0;

    // Pick best available voice
    const voices = this.synthesis.getVoices();
    const targetPrefix = ttsLang.split("-")[0];
    const matchedVoice = voices.find(v => v.lang.toLowerCase().startsWith(targetPrefix));
    if (matchedVoice) {
      this.currentUtterance.voice = matchedVoice;
    }

    this.currentUtterance.onstart = () => {
      if (callbacks.onStart) callbacks.onStart();
    };

    this.currentUtterance.onend = () => {
      if (callbacks.onEnd) callbacks.onEnd();
    };

    this.currentUtterance.onerror = (e) => {
      console.warn("TTS error:", e);
      if (callbacks.onError) callbacks.onError(e);
    };

    this.synthesis.speak(this.currentUtterance);
  }

  stopSpeaking() {
    if (this.synthesis) {
      this.synthesis.cancel();
    }
  }

  isSpeaking() {
    return this.synthesis && this.synthesis.speaking;
  }
}
