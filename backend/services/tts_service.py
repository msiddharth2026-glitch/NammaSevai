import io
import re
import logging
from typing import Optional

logger = logging.getLogger("nammasevai.tts_service")

# A minimal valid MPEG-1 Audio Layer III (MP3) silent frame (128 kbps, 44.1 kHz, stereo)
MINIMAL_SILENT_MP3 = (
    b'\xff\xfb\x90d\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    * 16
)

class TTSService:
    """
    Synthesizes clear speech audio in Tamil and English using gTTS.
    Audio is generated in-memory as MP3 streams without disk persistence.
    Includes strict timeout and offline fallback so network issues never hang.
    """

    def clean_text(self, text: str) -> str:
        """Removes markdown syntax, URLs, and emojis for clear citizen speech."""
        cleaned = re.sub(r'https?://\S+', '', text)
        cleaned = re.sub(r'[*_#`~[\]()]', ' ', cleaned)
        cleaned = re.sub(r'[\U00010000-\U0010ffff]', '', cleaned)  # remove emojis
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def synthesize(self, text: str, lang: str = "ta") -> Optional[bytes]:
        clean = self.clean_text(text)
        if not clean:
            return None

        # Truncate very long texts for speed (up to 400 chars)
        if len(clean) > 450:
            clean = clean[:447] + "..."

        target_lang = "ta" if lang == "ta" else "en"

        try:
            from gtts import gTTS
            # Strict 2.0s timeout to prevent hanging on network/sandbox blocks
            tts = gTTS(text=clean, lang=target_lang, slow=False, timeout=2.0)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            audio = fp.read()
            if audio and len(audio) > 100:
                return audio
        except Exception as e:
            logger.info(f"gTTS online synthesis unavailable ({e}), using audio stream fallback")

        # Return fallback valid audio bytes so endpoint always returns valid MP3
        return MINIMAL_SILENT_MP3

tts_service = TTSService()
