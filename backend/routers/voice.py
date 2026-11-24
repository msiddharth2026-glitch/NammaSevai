import io
import base64
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from ..services.voice_service import voice_service
from ..services.tts_service import tts_service
from ..services.ai_service import ai_service

router = APIRouter(prefix="/api/voice", tags=["Voice & Audio"])

class SynthesizeRequest(BaseModel):
    text: str
    lang: Optional[str] = "ta"

class Base64AudioRequest(BaseModel):
    audio_base64: str
    mime_type: Optional[str] = "audio/wav"
    lang: Optional[str] = "ta"

@router.get("/config", summary="Get voice and AI model status")
def get_voice_config():
    """Returns AI model status, voice capabilities, and setup instructions."""
    config_instruction = ai_service.get_configuration_instruction()
    return {
        "voice_recognition_available": True,
        "tts_available": True,
        "supported_languages": ["ta", "en", "hi", "ml", "tanglish", "hinglish"],
        "ai_model_configured": ai_service.is_api_configured(),
        "configuration_instruction": config_instruction,
        "privacy_policy": {
            "consent_required": True,
            "raw_audio_stored": False,
            "data_usage": "Ephemeral speech recognition for welfare scheme discovery only."
        }
    }

@router.post("/transcribe", summary="Transcribe citizen voice recording")
async def transcribe_audio(
    file: Optional[UploadFile] = File(None),
    lang: str = Form("ta")
):
    """
    Transcribes uploaded audio (Tamil/English/Tanglish) to text.
    Strict privacy: audio is purged immediately from memory/temp.
    """
    if not file:
        raise HTTPException(status_code=400, detail="No audio file uploaded")

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded audio file is empty")

    mime_type = file.content_type or "audio/wav"
    result = voice_service.process_audio(content, mime_type=mime_type, lang=lang)
    return result

@router.post("/transcribe-base64", summary="Transcribe base64 encoded audio")
def transcribe_base64(payload: Base64AudioRequest):
    """Transcribes base64 encoded audio from browser MediaRecorder."""
    try:
        audio_bytes = base64.b64decode(payload.audio_base64)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 audio data: {e}")

    result = voice_service.process_audio(
        audio_bytes=audio_bytes, 
        mime_type=payload.mime_type or "audio/wav", 
        lang=payload.lang or "ta"
    )
    return result

@router.post("/synthesize", summary="Synthesize speech audio in Tamil or English")
def synthesize_speech(payload: SynthesizeRequest):
    """
    Synthesizes clear speech audio for citizen response in Tamil or English.
    Returns streaming MP3 audio.
    """
    audio_bytes = tts_service.synthesize(payload.text, lang=payload.lang or "ta")
    if not audio_bytes:
        raise HTTPException(status_code=500, detail="Could not synthesize speech audio")

    return StreamingResponse(
        io.BytesIO(audio_bytes), 
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=nammasevai_speech.mp3"}
    )
