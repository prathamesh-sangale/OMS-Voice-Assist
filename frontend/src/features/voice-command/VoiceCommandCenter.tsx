import { useState, useRef } from 'react';
import { Mic, CheckCircle2, AlertCircle, Loader2, Send, Paperclip } from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { API_BASE_URL } from '../../services/api/client';
import { OrderResultRenderer } from './components/OrderResultRenderer';

type VoiceState = 'Ready' | 'Listening' | 'Transcribing' | 'Reviewing' | 'Analyzing' | 'Executing' | 'Completed' | 'Error' | 'Needs Clarification' | 'Confirmation Required';

interface AgentResponse {
  status: string;
  message: string;
  intent?: string;
  data?: any;
  metadata?: any;
  requires_clarification?: boolean;
}

const VoiceCommandCenter = () => {
  const [voiceState, setVoiceState] = useState<VoiceState>('Ready');
  const [inputText, setInputText] = useState('');
  const [response, setResponse] = useState<AgentResponse | null>(null);
  
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [_audioChunks, setAudioChunks] = useState<Blob[]>([]);
  const recognitionRef = useRef<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setVoiceState('Transcribing');
    const formData = new FormData();
    formData.append('file', file, file.name);

    fetch(`${API_BASE_URL}/api/voice/transcribe`, {
      method: 'POST',
      body: formData,
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'success') {
        setInputText(data.transcript);
        setVoiceState('Reviewing');
      } else {
        setVoiceState('Error');
      }
    })
    .catch(err => {
      console.error(err);
      setVoiceState('Error');
    });
    
    // Reset input
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const playTTS = async (text: string) => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/voice/tts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        audio.play();
      }
    } catch (e) {
      console.error('Failed to play TTS:', e);
    }
  };

  const startRecording = async () => {
    // 1. Try Native Web Speech API (Live Transcription like Google Assistant)
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      try {
        const recognition = new SpeechRecognition();
        recognition.continuous = false; // Stop automatically when user stops speaking
        recognition.interimResults = true; // Show live text
        recognitionRef.current = recognition;

        recognition.onstart = () => {
          setVoiceState('Listening');
          setInputText('');
        };

        recognition.onresult = (event: any) => {
          let transcript = '';
          for (let i = event.resultIndex; i < event.results.length; ++i) {
            transcript += event.results[i][0].transcript;
          }
          setInputText(transcript);
        };

        recognition.onerror = (event: any) => {
          console.error('Speech recognition error:', event.error);
          if (event.error === 'not-allowed') {
            alert("Microphone access denied. Please allow it in browser settings. (Error: not-allowed)");
          } else if (event.error !== 'no-speech') {
            alert(`Speech recognition failed with error: ${event.error}. Please check your microphone or network connection.`);
          }
          setVoiceState('Error');
        };

        recognition.onend = () => {
          setVoiceState(prev => {
            if (prev === 'Listening') {
              // Auto-submit the form by finding and clicking the submit button
              setTimeout(() => {
                const form = document.querySelector('form');
                if (form) form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
              }, 500);
              return 'Analyzing';
            }
            return prev;
          });
        };

        recognition.start();
        return;
      } catch (err) {
        console.warn("SpeechRecognition failed, falling back to MediaRecorder", err);
      }
    }

    // 2. Fallback to MediaRecorder + Backend Groq Whisper API
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert("Your browser does not support audio recording or no microphone was found.");
        setVoiceState('Error');
        return;
      }
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      setMediaRecorder(recorder);
      
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          setAudioChunks(prev => [...prev, e.data]);
        }
      };

      recorder.onstop = async () => {
        setVoiceState('Transcribing');
        setTimeout(async () => {
          setAudioChunks((currentChunks) => {
            const audioBlob = new Blob(currentChunks, { type: 'audio/webm' });
            const formData = new FormData();
            formData.append('file', audioBlob, 'command.webm');

            fetch(`${API_BASE_URL}/api/voice/transcribe`, {
              method: 'POST',
              body: formData,
            })
            .then(res => res.json())
            .then(data => {
              if (data.status === 'success') {
                setInputText(data.transcript);
                setVoiceState('Reviewing');
              } else {
                setVoiceState('Error');
              }
            })
            .catch(err => {
              console.error(err);
              setVoiceState('Error');
            });
            
            stream.getTracks().forEach(track => track.stop());
            return [];
          });
        }, 100);
      };

      setAudioChunks([]);
      recorder.start();
      setVoiceState('Listening');
    } catch (err: any) {
      console.error('Mic error:', err);
      if (err.name === 'NotFoundError') {
        alert("No microphone found. Please connect a microphone and try again.");
      } else if (err.name === 'NotAllowedError') {
        alert("Microphone access was denied. Please allow microphone access in your browser settings.");
      } else {
        alert(`Microphone error: ${err.message || 'Unknown error'}`);
      }
      setVoiceState('Error');
    }
  };

  const stopRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop();
    }
  };

  const toggleRecording = () => {
    if (voiceState === 'Listening') {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    setVoiceState('Analyzing');
    setResponse(null);

    try {
      // Small artificial delay to show state changes if API is too fast
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setVoiceState('Executing');
      
      const res = await fetch(`${API_BASE_URL}/api/agent/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText }),
      });
      
      const data: AgentResponse = await res.json();
      setResponse(data);
      
      if (data.status === 'success') {
        setVoiceState('Completed');
        playTTS(data.message);
      } else if (data.status === 'needs_clarification') {
        setVoiceState('Needs Clarification');
        playTTS(data.message);
      } else if (data.status === 'confirmation_required') {
        setVoiceState('Confirmation Required');
        playTTS(`Review the change for ${data.data?.target}. Old value was ${data.data?.old_value || 'None'}. New value will be ${data.data?.new_value}. Do you want to confirm?`);
      } else {
        setVoiceState('Error');
        playTTS(data.message || "An error occurred.");
      }
      
    } catch (err) {
      console.error(err);
      setVoiceState('Error');
      setResponse({
        status: 'error',
        message: 'Failed to communicate with the Agent API.',
      });
      playTTS('Failed to communicate with the Agent API.');
    }
  };

  return (
    <div className="max-w-3xl mx-auto mt-12 space-y-8">
      <div className="text-center">
        <h1 className="text-2xl font-semibold text-text mb-2">Voice Command Center</h1>
        <p className="text-muted-text">Type natural language commands to control the OMS</p>
      </div>

      <form onSubmit={handleSubmit}>
        <Card className="p-3 sm:p-4 flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4 bg-surface shadow-md">
          <div className="flex items-center gap-2 sm:gap-4 w-full flex-1">
            <button 
              type="button"
              onClick={toggleRecording}
              className={`shrink-0 w-10 h-10 sm:w-12 sm:h-12 flex items-center justify-center rounded-full transition-colors ${
                voiceState === 'Listening' 
                  ? 'bg-critical text-white animate-pulse' 
                  : 'bg-surface-hover text-muted-text hover:text-primary hover:bg-primary/10'
              }`}
              title="Toggle Microphone"
            >
              <Mic size={24} className="w-5 h-5 sm:w-6 sm:h-6" />
            </button>
            
            <button 
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="shrink-0 w-10 h-10 sm:w-12 sm:h-12 flex items-center justify-center rounded-full transition-colors bg-surface-hover text-muted-text hover:text-primary hover:bg-primary/10"
              title="Upload Audio File"
              disabled={voiceState === 'Listening' || voiceState === 'Analyzing'}
            >
              <Paperclip size={20} className="w-4 h-4 sm:w-5 sm:h-5" />
            </button>
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileUpload} 
              accept="audio/*" 
              className="hidden" 
            />
            
            <div className="flex-1 min-w-0">
              <input 
                type="text" 
                placeholder="Ask the OMS (e.g. 'Show pending orders')..." 
                className="w-full bg-transparent border-none outline-none text-base sm:text-lg placeholder:text-muted-text/50"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                disabled={voiceState === 'Analyzing' || voiceState === 'Executing'}
                autoFocus
              />
            </div>
            
            <button 
              type="submit"
              disabled={!inputText.trim() || voiceState === 'Analyzing' || voiceState === 'Executing'}
              className="shrink-0 w-10 h-10 sm:w-12 sm:h-12 flex items-center justify-center rounded-full transition-colors bg-primary text-white hover:bg-opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={20} className="w-4 h-4 sm:w-5 sm:h-5" />
            </button>
          </div>
          
          <div className="flex items-center gap-2 px-3 py-1.5 sm:py-1 rounded-full bg-background border border-border min-w-[120px] justify-center self-stretch sm:self-auto shrink-0">
            {voiceState === 'Ready' && <span className="w-2 h-2 rounded-full bg-success"></span>}
            {voiceState === 'Listening' && <span className="w-2 h-2 rounded-full bg-critical animate-pulse"></span>}
            {(voiceState === 'Analyzing' || voiceState === 'Transcribing') && <Loader2 size={14} className="animate-spin text-accent" />}
            {voiceState === 'Executing' && <Loader2 size={14} className="animate-spin text-warning" />}
            {(voiceState === 'Completed' || voiceState === 'Reviewing') && <CheckCircle2 size={14} className="text-success" />}
            {(voiceState === 'Error' || voiceState === 'Needs Clarification') && <AlertCircle size={14} className="text-critical" />}
            <span className="text-xs font-medium text-muted-text">{voiceState}</span>
          </div>
        </Card>
      </form>
      
      {/* Review UI */}
      {voiceState === 'Reviewing' && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div>
            <h3 className="text-xs font-semibold text-muted-text uppercase tracking-wider mb-2">You Said (Edit if needed)</h3>
            <Card className="p-4 bg-background border border-accent shadow-none">
              <input
                type="text"
                className="w-full bg-transparent border-none outline-none text-lg text-text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                autoFocus
              />
              <div className="flex justify-end mt-4">
                <button
                  type="button"
                  onClick={() => document.querySelector("form")?.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }))}
                  className="px-4 py-2 text-sm font-medium rounded-md transition-colors bg-accent text-white hover:bg-accent/90"
                >
                  Submit Command
                </button>
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* Simulation Feedback UI */}
      {response && voiceState !== 'Reviewing' && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div>
            <h3 className="text-xs font-semibold text-muted-text uppercase tracking-wider mb-2">Transcript / Command</h3>
            <Card className="p-4 bg-background italic border-none shadow-none text-text">
              "{inputText}"
            </Card>
          </div>

          <div>
            <h3 className="text-xs font-semibold text-muted-text uppercase tracking-wider mb-2">Command</h3>
            <Card className="p-4 bg-surface space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 text-sm gap-4">
                <div>
                  <span className="block text-muted-text text-xs mb-1">Intent</span>
                  <span className="font-medium">{response.intent || 'Unknown'}</span>
                </div>
                <div>
                  <span className="block text-muted-text text-xs mb-1">Confidence</span>
                  <span className="font-medium">
                    {response.metadata?.confidence !== undefined 
                      ? `${(response.metadata.confidence * 100).toFixed(0)}%` 
                      : 'N/A'}
                  </span>
                </div>
                <div>
                  <span className="block text-muted-text text-xs mb-1">Method</span>
                  <span className="font-medium">{response.metadata?.method || 'Rule Engine'}</span>
                </div>
                <div>
                  <span className="block text-muted-text text-xs mb-1">Explanation</span>
                  <span className="font-medium">{response.metadata?.explanation || 'None'}</span>
                </div>
              </div>
            </Card>
          </div>

          <div>
            <h3 className="text-xs font-semibold text-muted-text uppercase tracking-wider mb-2">RESULT</h3>
            <Card className={`p-6 border shadow-sm ${
              response.intent === 'LIST_ORDERS' ? 'bg-white border-border' :
              response.status === 'success' ? 'bg-success/5 border-success/20' : 
              response.status === 'needs_clarification' ? 'bg-warning/5 border-warning/20' :
              'bg-critical/5 border-critical/20'
            }`}>
              
              {response.intent !== 'LIST_ORDERS' && (
                <div className={`text-sm font-medium flex items-center gap-2 ${
                  response.status === 'success' ? 'text-success' : 
                  response.status === 'needs_clarification' ? 'text-warning' :
                  response.status === 'confirmation_required' ? 'text-accent' :
                  'text-critical'
                }`}>
                  {response.status === 'success' && <CheckCircle2 size={16} />}
                  {response.message}
                </div>
              )}
              
              {response.status === 'confirmation_required' && response.data && (
                <div className="mt-4 p-4 border border-accent/30 rounded-lg bg-surface space-y-4">
                  <div className="flex justify-between items-center pb-2 border-b border-border">
                    <span className="text-sm font-semibold text-text">Review Change</span>
                    <span className="text-xs px-2 py-1 bg-accent/10 text-accent rounded-full font-medium">Pending Action</span>
                  </div>
                  
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="block text-muted-text text-xs mb-1">Target</span>
                      <span className="font-medium">{response.data.target}</span>
                    </div>
                    <div>
                      <span className="block text-muted-text text-xs mb-1">Intent</span>
                      <span className="font-medium">{response.data.intent}</span>
                    </div>
                    <div>
                      <span className="block text-muted-text text-xs mb-1">Current Value</span>
                      <span className="font-medium text-warning">{response.data.old_value || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="block text-muted-text text-xs mb-1">New Value</span>
                      <span className="font-medium text-success">{response.data.new_value}</span>
                    </div>
                  </div>

                  <div className="flex justify-end gap-3 pt-4 border-t border-border mt-2">
                    <button
                      onClick={() => {
                        setInputText(`!cancel ${response.data.id}`);
                        setTimeout(() => document.querySelector("form")?.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true })), 100);
                      }}
                      className="px-4 py-2 text-sm font-medium rounded-md transition-colors bg-surface-hover text-text hover:bg-surface border border-border"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => {
                        setInputText(`!confirm ${response.data.id}`);
                        setTimeout(() => document.querySelector("form")?.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true })), 100);
                      }}
                      className="px-4 py-2 text-sm font-medium rounded-md transition-colors bg-accent text-white hover:bg-accent/90"
                    >
                      Confirm Update
                    </button>
                  </div>
                </div>
              )}

              {/* Dynamic Result Rendering */}
              {response.data && response.status !== 'confirmation_required' && (
                response.intent === 'LIST_ORDERS' ? (
                  <OrderResultRenderer data={response.data} />
                ) : (
                  <div className="mt-4 p-3 bg-background rounded border border-border overflow-auto max-h-64 text-xs font-mono text-muted-text">
                    <pre>{JSON.stringify(response.data, null, 2)}</pre>
                  </div>
                )
              )}
            </Card>
          </div>
        </div>
      )}
    </div>
  );
};

export default VoiceCommandCenter;
