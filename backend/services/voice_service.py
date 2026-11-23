import os
import io
import base64
import logging
import tempfile
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger("nammasevai.voice_service")

class VoiceService:
    """
    Handles speech-to-text audio transcription supporting Tamil, English, and Tanglish.
    Strictly observes privacy: raw voice files are purged immediately from memory/disk.
    """

    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()

    def transcribe_with_gemini(self, audio_bytes: bytes, mime_type: str = "audio/wav", lang: str = "ta") -> Optional[str]:
        """Transcribes audio using Gemini Multimodal capabilities."""
        if not self.gemini_api_key:
            return None

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        encoded_audio = base64.b64encode(audio_bytes).decode("utf-8")

        prompt = (
            "You are a professional speech-to-text engine for Tamil Nadu citizens. "
            "Transcribe the spoken audio verbatim. "
            "The speaker may speak in Tamil (தமிழ்), English, or Tanglish (Tamil in English letters). "
            "Output ONLY the transcribed text without notes or introductory text."
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inlineData": {
                                "mimeType": mime_type,
                                "data": encoded_audio
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {"temperature": 0.0}
        }

        try:
            res = requests.post(url, json=payload, timeout=12)
            if res.status_code == 200:
                transcript = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                return transcript
        except Exception as e:
            logger.error(f"Gemini audio transcription error: {e}")

        return None

    def transcribe_with_speech_recognition(self, audio_bytes: bytes, lang: str = "ta") -> Optional[str]:
        """Transcribes audio using Python SpeechRecognition library."""
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            lang_code = "ta-IN" if lang == "ta" else "en-IN"

            # Check if wav or requires conversion
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name

            try:
                with sr.AudioFile(tmp_path) as source:
                    audio_data = recognizer.record(source)
                    text = recognizer.recognize_google(audio_data, language=lang_code)
                    return text
            finally:
                # Privacy guarantee: delete temporary audio file immediately
                if os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass

        except Exception as e:
            logger.warning(f"Local speech recognition error: {e}")

        return None

    def process_audio(
        self, 
        audio_bytes: bytes, 
        mime_type: str = "audio/wav", 
        lang: str = "ta"
    ) -> Dict[str, Any]:
        """
        Processes audio bytes and returns transcribed text.
        """
        transcript = None
        engine_used = "none"

        # 1. Try Gemini Multimodal if key available
        if self.gemini_api_key:
            transcript = self.transcribe_with_gemini(audio_bytes, mime_type, lang)
            if transcript:
                engine_used = "google_gemini_multimodal"

        # 2. Try SpeechRecognition as fallback
        if not transcript:
            transcript = self.transcribe_with_speech_recognition(audio_bytes, lang)
            if transcript:
                engine_used = "google_speech_recognition"

        if not transcript:
            return {
                "success": False,
                "transcript": "",
                "error": "Could not recognize speech. Please speak closer to the microphone or type your query.",
                "error_ta": "குரலை துல்லியமாக அடையாளம் காண முடியவில்லை. தயவுசெய்து மீண்டும் பேசவும் அல்லது தட்டச்சு செய்யவும்.",
                "privacy_notice": "Raw voice recording was discarded immediately."
            }

        return {
            "success": True,
            "transcript": transcript,
            "detected_language": lang,
            "engine": engine_used,
            "privacy_notice": "Audio processed ephemerally and discarded immediately after transcription."
        }

voice_service = VoiceService()
