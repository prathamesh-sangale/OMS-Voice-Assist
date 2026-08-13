import { useState, useRef, useCallback, useEffect } from 'react';
import { API_BASE_URL } from '../services/api/client';
import { useAgent } from '../app/providers/AgentProvider';

let globalAudioContext: AudioContext | null = null;

const initAudioContext = () => {
  if (!globalAudioContext) {
    const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
    if (AudioContextClass) {
      globalAudioContext = new AudioContextClass();
    }
  }
  if (globalAudioContext && globalAudioContext.state === 'suspended') {
    globalAudioContext.resume().catch(console.error);
  }
  return globalAudioContext;
};

if (typeof window !== 'undefined') {
  window.addEventListener('click', initAudioContext, { once: true });
  window.addEventListener('keydown', initAudioContext, { once: true });
}

export const useVoiceRecording = () => {
  const { setVoiceState, dispatchCommand } = useAgent();
  const [transcript, setTranscript] = useState<string>('');
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<BlobPart[]>([]);
  const hasSpokenRef = useRef<boolean>(false);

  const startRecording = useCallback(async () => {
    try {
      hasSpokenRef.current = false;
      // Initialize or resume the global audio context (best effort)
      initAudioContext();

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      let mimeType = 'audio/webm';
      if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
        mimeType = 'audio/webm;codecs=opus';
      } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
        mimeType = 'audio/mp4';
      }

      const mediaRecorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      let animationFrameId: number;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstart = () => {
        console.log(`[Voice] Recording started with mimeType: ${mimeType}`);
        setVoiceState('Listening');
        setTranscript('');

        // 1. Try to use Browser's Native Neural VAD (Web Speech API)
        let usingNativeVAD = false;
        try {
          const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
          if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            
            recognition.onresult = () => {
              hasSpokenRef.current = true;
            };
            
            recognition.onspeechend = () => {
              if (hasSpokenRef.current) {
                console.log('[Voice] Native VAD detected speech end.');
                stopRecording();
              }
            };
            
            recognition.onerror = (e: any) => {
              console.log(`[Voice] Native VAD error: ${e.error}`);
            };

            recognition.onend = () => {
              if (mediaRecorderRef.current?.state === 'recording') {
                if (!hasSpokenRef.current) {
                  console.log('[Voice] Native VAD ended before speech. Restarting listener...');
                  try { recognition.start(); } catch(e) {}
                } else {
                  stopRecording();
                }
              }
            };
            
            recognition.start();
            usingNativeVAD = true;
            console.log('[Voice] Using Native Browser VAD for noise rejection.');
          }
        } catch (e) {
          console.warn('[Voice] Native VAD failed, falling back to pure RMS VAD.', e);
        }

        // 2. Parallel RMS VAD as a fail-safe
        try {
          const audioContext = initAudioContext();
          if (!audioContext) throw new Error("No audio context");
          const source = audioContext.createMediaStreamSource(stream);
          const analyser = audioContext.createAnalyser();
          analyser.fftSize = 512;
          source.connect(analyser);

          const bufferLength = analyser.fftSize;
          const dataArray = new Float32Array(bufferLength);
        
          let silenceStart = 0;
          let minRms = 1.0;
          let smoothedRms = 0;
          const SILENCE_MARGIN = 0.015; 
          // If native VAD is running, make RMS extremely generous (fail-safe).
          const SILENCE_DURATION = usingNativeVAD ? 5000 : 2000; 
          const NO_SPEECH_TIMEOUT = usingNativeVAD ? 15000 : 6000;

            const detectSilence = () => {
              if (mediaRecorder.state !== 'recording') return;
              
              analyser.getFloatTimeDomainData(dataArray);
              let sumSquares = 0;
              for(let i = 0; i < bufferLength; i++) {
                  sumSquares += dataArray[i] * dataArray[i];
              }
              const rms = Math.sqrt(sumSquares / bufferLength);
              
              smoothedRms = (smoothedRms * 0.8) + (rms * 0.2);
              minRms = Math.min(minRms, smoothedRms);
              minRms += 0.00005; 
              
              const dynamicThreshold = minRms + SILENCE_MARGIN;

              if (smoothedRms > dynamicThreshold) {
                hasSpokenRef.current = true;
                silenceStart = 0;
              } else if (hasSpokenRef.current) {
                if (silenceStart === 0) {
                  silenceStart = performance.now();
                } else if (performance.now() - silenceStart > SILENCE_DURATION) {
                  console.log('[Voice] RMS Silence detected. Auto-stopping.');
                  stopRecording();
                  return;
                }
              } else {
                if (silenceStart === 0) silenceStart = performance.now();
                else if (performance.now() - silenceStart > NO_SPEECH_TIMEOUT) {
                  console.log('[Voice] RMS Fail-safe: No speech detected. Auto-stopping.');
                  stopRecording();
                  return;
                }
              }
              
              animationFrameId = requestAnimationFrame(detectSilence);
            };
            detectSilence();
          } catch (e) {
            console.warn('[Voice] RMS VAD initialization failed', e);
          }
      };

      mediaRecorder.onstop = async () => {
        console.log('[Voice] Recording stopped. Processing audio...');
        if (animationFrameId) cancelAnimationFrame(animationFrameId);
        
        setVoiceState('Transcribing');
        
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
        console.log(`[Voice] Audio size: ${audioBlob.size} bytes`);
        
        if (audioBlob.size === 0) {
          console.warn('[Voice] Empty audio recorded.');
          setVoiceState('Idle');
          return;
        }

        if (!hasSpokenRef.current) {
          console.warn('[Voice] No speech detected. Discarding audio to prevent hallucination.');
          setVoiceState('Idle');
          return;
        }

        const formData = new FormData();
        // The backend validation checks the extension/mimetype, so we add an extension
        const ext = mimeType.includes('mp4') ? 'mp4' : 'webm';
        formData.append('file', audioBlob, `voice_command.${ext}`);

        try {
          console.log('[Voice] Upload started...');
          const res = await fetch(`${API_BASE_URL}/api/voice/transcribe`, {
            method: 'POST',
            body: formData,
          });
          
          const data = await res.json();
          if (res.ok && data.status === 'success') {
            if (data.transcript.trim()) {
              console.log(`[Voice] Transcript received: "${data.transcript}"`);
              setTranscript(data.transcript);
              setVoiceState('You_Said');
              
              // Dispatch the command automatically
              setTimeout(() => {
                dispatchCommand(data.transcript, 'voice');
              }, 600);
            } else {
              console.warn('[Voice] Transcript was empty (likely silence or filtered noise).');
              setVoiceState('Idle');
              // Don't alert to be less intrusive, just reset.
            }
          } else {
            console.error('[Voice] Transcription error response:', data);
            setVoiceState('Error');
            alert("Voice transcription failed. Please try again.");
            setTimeout(() => setVoiceState('Idle'), 3000);
          }
        } catch (error) {
          console.error('[Voice] Transcription network error:', error);
          setVoiceState('Error');
          alert("Voice transcription failed. Please try again.");
          setTimeout(() => setVoiceState('Idle'), 3000);
        } finally {
          // Clean up stream tracks
          stream.getTracks().forEach(track => track.stop());
        }
      };

      mediaRecorder.start();
    } catch (error) {
      console.error('[Voice] Error accessing microphone:', error);
      alert("Microphone permission is required to use voice commands.");
      setVoiceState('Idle');
    }
  }, [setVoiceState, dispatchCommand]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
  }, []);

  return {
    startRecording,
    stopRecording,
    transcript,
    setTranscript
  };
};
