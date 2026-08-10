import io
import logging
from .provider import TTSProvider
from gtts import gTTS

logger = logging.getLogger(__name__)

class gTTSProvider(TTSProvider):
    """
    Implementation of TTSProvider using Google Translate's Text-to-Speech (gTTS).
    Does not require an API key.
    """
    def synthesize(self, text: str) -> bytes:
        try:
            logger.info(f"Synthesizing audio for text: '{text[:30]}...'")
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to an in-memory bytes buffer
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            
            audio_data = fp.getvalue()
            fp.close()
            
            return audio_data
        except Exception as e:
            logger.error(f"gTTS synthesis failed: {e}")
            raise Exception(f"TTS Synthesis failed: {str(e)}")
