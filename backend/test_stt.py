import os
import wave
import struct
from app.voice.stt.groq_stt import GroqWhisperProvider

def create_dummy_wav(filename):
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        # Write 1 second of silence
        for _ in range(16000):
            value = 0
            data = struct.pack('<h', value)
            wav_file.writeframesraw(data)

def test():
    print("Testing STT Provider directly...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        provider = GroqWhisperProvider()
        
        # Create a dummy valid audio file
        create_dummy_wav("dummy.wav")
        
        with open("dummy.wav", "rb") as f:
            audio_bytes = f.read()
            
        print("Sending audio to Groq...")
        res = provider.transcribe(audio_bytes, "dummy.wav")
        print(f"Success! Transcript: '{res.text}'")
        print(f"Provider: {res.provider}")
        
    except Exception as e:
        print(f"STT Error: {e}")
    finally:
        if os.path.exists("dummy.wav"):
            os.remove("dummy.wav")

if __name__ == "__main__":
    test()
