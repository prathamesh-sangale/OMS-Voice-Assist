import time
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from fastapi.responses import Response

from ...voice.stt.groq_stt import GroqWhisperProvider, GroqSTTException
from ...voice.audio.validation import AudioValidator
from ...voice.audio.normalization import AudioNormalizer
from ...voice.tts.service import gTTSProvider
from pydantic import BaseModel
from app.core.rate_limit import limiter

router = APIRouter()

# Dependency to get STT Provider
def get_stt_provider() -> GroqWhisperProvider:
    return GroqWhisperProvider()

# Dependency to get TTS Provider
def get_tts_provider() -> gTTSProvider:
    return gTTSProvider()

class TTSRequest(BaseModel):
    text: str

@router.post("/transcribe")
@limiter.limit("20/minute")
async def transcribe_audio(
    request: Request,
    file: UploadFile = File(...),
    stt_provider: GroqWhisperProvider = Depends(get_stt_provider)
):
    try:
        # Validate audio
        audio_bytes = await AudioValidator.validate(file)
        
        # Determine a filename since Groq requires one
        filename = file.filename or "audio.webm"
        
        start_time = time.time()
        # Transcribe via Provider
        transcript_response = stt_provider.transcribe(audio_bytes, filename)
        stt_latency = time.time() - start_time
        
        # Normalize
        normalized_text = AudioNormalizer.normalize(transcript_response.text)
        
        # The frontend wants the transcript response
        return {
            "status": "success",
            "transcript": normalized_text,
            "original_text": transcript_response.text,
            "provider": transcript_response.provider,
            "stt_latency_sec": round(stt_latency, 2)
        }
        
    except HTTPException as he:
        raise he
    except GroqSTTException as ge:
        raise HTTPException(status_code=503, detail=str(ge))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")

@router.post("/tts")
@limiter.limit("20/minute")
async def generate_speech(
    request: Request,
    tts_request: TTSRequest,
    tts_provider: gTTSProvider = Depends(get_tts_provider)
):
    try:
        audio_bytes = tts_provider.synthesize(tts_request.text)
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS processing failed: {str(e)}")
