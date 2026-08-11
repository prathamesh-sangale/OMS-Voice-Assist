import { useState, useRef, useEffect } from 'react';
import { Mic, Loader2, Send, Paperclip, MessageSquare, Plus, FileText } from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { API_BASE_URL } from '../../services/api/client';
import { useAgent } from '../../app/providers/AgentProvider';
import type { ConversationSession } from '../../types/agent';
import { OrderDetailsCard } from './components/OrderDetailsCard';
import { OrderResultRenderer } from './components/OrderResultRenderer';

const VoiceCommandCenter = () => {
  const {
    sessionId, setSessionId,
    currentSession, setCurrentSession,
    voiceState, setVoiceState,
    dispatchCommand
  } = useAgent();

  const [inputText, setInputText] = useState('');
  const [sessions, setSessions] = useState<ConversationSession[]>([]);
  

  const recognitionRef = useRef<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fetch all sessions on mount
  useEffect(() => {
    fetchSessions();
  }, []);

  // Fetch specific session when ID changes externally (like from sidebar)
  useEffect(() => {
    if (sessionId && (!currentSession || currentSession.id !== sessionId)) {
      fetch(`${API_BASE_URL}/api/agent/sessions/${sessionId}`)
        .then(res => res.json())
        .then(data => setCurrentSession(data))
        .catch(e => console.error(e));
    } else if (!sessionId) {
      setCurrentSession(null);
    }
  }, [sessionId]);

  // Scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentSession?.messages, voiceState]);

  const fetchSessions = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/agent/sessions`);
      if (res.ok) {
        const data = await res.json();
        setSessions(data.sessions);
      }
    } catch (e) {
      console.error("Failed to fetch sessions", e);
    }
  };



  const startNewConversation = () => {
    setSessionId(undefined);
    setCurrentSession(null);
    setInputText('');
    setVoiceState('Ready');
  };

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
        setVoiceState('Ready');
        // Auto submit
        setTimeout(() => dispatchCommand(data.transcript, 'voice'), 100);
      } else {
        setVoiceState('Error');
      }
    })
    .catch(err => {
      console.error(err);
      setVoiceState('Error');
    });
    
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  // playTTS removed since we don't use it directly here now

  const startRecording = async () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      try {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
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

        recognition.onerror = () => setVoiceState('Error');
        
        recognition.onend = () => {
          if (voiceState === 'Listening') {
            setTimeout(() => {
              const finalTranscript = document.querySelector('input[type="text"]')?.getAttribute('value') || inputText;
              if (finalTranscript) dispatchCommand(finalTranscript, 'voice');
            }, 100);
            setVoiceState('Analyzing');
          }
        };

        recognition.start();
        return;
      } catch (err) {}
    }

    // MediaRecorder fallback omitted for brevity in rewritten phase, assuming SpeechRecognition works
    alert("Speech recognition not supported in this browser without HTTPS.");
  };

  const stopRecording = () => {
    if (recognitionRef.current) recognitionRef.current.stop();
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputText.trim()) {
      dispatchCommand(inputText, 'text');
      setInputText('');
    }
  };

  return (
    <div className="max-w-6xl mx-auto mt-4 sm:mt-8 flex flex-col md:flex-row gap-6 h-[85vh]">
      
      {/* Sidebar - History */}
      <div className="w-full md:w-64 lg:w-80 flex flex-col gap-4">
        <button 
          onClick={startNewConversation}
          className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-primary text-white rounded-lg shadow-sm hover:bg-primary/90 transition-colors font-medium"
        >
          <Plus size={18} />
          New Conversation
        </button>

        <Card className="flex-1 overflow-y-auto bg-surface border-border shadow-sm flex flex-col p-2 gap-1">
          <div className="text-xs font-semibold text-muted-text uppercase tracking-wider p-2">Recent</div>
          {sessions.map(session => (
            <button
              key={session.id}
              onClick={() => setSessionId(session.id)}
              className={`flex items-center gap-3 p-3 rounded-md text-left transition-colors ${
                sessionId === session.id ? 'bg-primary/10 text-primary font-medium' : 'hover:bg-surface-hover text-text'
              }`}
            >
              <MessageSquare size={16} className={sessionId === session.id ? 'text-primary' : 'text-muted-text'} />
              <div className="truncate text-sm flex-1">{session.title}</div>
            </button>
          ))}
          {sessions.length === 0 && (
            <div className="text-sm text-muted-text text-center p-4">No recent conversations</div>
          )}
        </Card>
      </div>

      {/* Main Chat Area */}
      <Card className="flex-1 flex flex-col bg-surface border-border shadow-md overflow-hidden relative">
        
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
          {!currentSession || currentSession.messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-50">
              <Mic size={48} className="text-muted-text" />
              <div>
                <h2 className="text-xl font-medium text-text">How can I help you?</h2>
                <p className="text-sm text-muted-text mt-1">Say "Create a new order for Acme Corp"</p>
              </div>
            </div>
          ) : (
            currentSession.messages.map((msg, idx) => (
              <div key={msg.id || idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                  msg.role === 'user' 
                    ? 'bg-primary text-white rounded-br-none' 
                    : 'bg-background border border-border text-text rounded-bl-none shadow-sm'
                }`}>
                  <div className="text-sm">{msg.text}</div>
                  
                  {/* Dynamic UI Rendering based on context */}
                  {msg.role === 'agent' && (
                    <div className="mt-3">
                      {msg.response_type === 'order_details' && msg.data && (
                        <OrderDetailsCard order={msg.data} />
                      )}
                      {msg.response_type === 'order_list' && msg.data && (
                        <OrderResultRenderer data={msg.data} />
                      )}
                      
                      {/* Fallback for older messages */}
                      {!msg.response_type && currentSession?.context?.intent === 'LIST_ORDERS' && currentSession?.context?.last_result_context && idx === currentSession.messages.length - 1 && (
                        <div className="text-xs mt-2 bg-background p-2 rounded border border-border">
                          {currentSession.context.last_result_context.identifiers?.length || 0} orders found.
                        </div>
                      )}
                      
                      {/* Confirmation UI (we'll show it for the last message if status is pending_confirmation) */}
                      {currentSession?.context?.operation_status === 'pending_confirmation' && idx === currentSession.messages.length - 1 && (
                         <div className="mt-4 p-4 border border-accent rounded-lg bg-accent/5 space-y-2">
                           <div className="text-xs font-semibold text-accent uppercase tracking-wider">Pending Action</div>
                           <div className="text-sm">
                             <span className="text-muted-text">Target: </span> 
                             <span className="font-medium text-text">
                               {Array.isArray(currentSession.context.target_orders?.order_ids) 
                                 ? `${currentSession.context.target_orders?.order_ids.length} orders` 
                                 : '1 order'}
                             </span>
                           </div>
                           <div className="flex gap-2 pt-2">
                             <button onClick={() => dispatchCommand('Cancel', 'text')} className="px-3 py-1.5 text-sm bg-surface text-text hover:bg-surface-hover rounded-md border border-border">Cancel</button>
                             <button onClick={() => dispatchCommand('Confirm', 'text')} className="px-3 py-1.5 text-sm bg-accent text-white hover:bg-accent/90 rounded-md">Confirm Update</button>
                           </div>
                         </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          
          {/* Typing Indicator */}
          {(voiceState === 'Analyzing' || voiceState === 'Executing') && (
            <div className="flex justify-start">
              <div className="bg-background border border-border rounded-2xl rounded-bl-none px-4 py-3 shadow-sm flex items-center gap-2">
                <Loader2 size={16} className="animate-spin text-primary" />
                <span className="text-sm text-muted-text">Agent is thinking...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Draft Panel overlay if active */}
        {currentSession?.context.operation_status === 'collecting' && currentSession.context.draft && (
          <div className="absolute top-4 right-4 w-64 bg-background border border-accent/30 shadow-lg rounded-lg p-4 animate-in slide-in-from-right-8 fade-in">
            <div className="flex items-center gap-2 mb-3 text-accent font-medium text-sm">
              <FileText size={16} />
              Order Draft
            </div>
            <div className="space-y-2 text-xs">
              {Object.entries(currentSession.context.draft).map(([k, v]) => (
                <div key={k} className="flex justify-between border-b border-border/50 pb-1">
                  <span className="text-muted-text capitalize">{k.replace('_', ' ')}</span>
                  <span className="font-medium text-text truncate max-w-[100px]">{String(v)}</span>
                </div>
              ))}
              {currentSession.context.pending_field && (
                <div className="flex justify-between border-b border-accent/50 pb-1 bg-accent/5 px-1 -mx-1">
                  <span className="text-accent capitalize font-medium">{currentSession.context.pending_field.replace('_', ' ')}</span>
                  <span className="text-accent animate-pulse font-medium">Waiting...</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="p-4 bg-background border-t border-border">
          <form onSubmit={handleFormSubmit} className="flex items-center gap-2 sm:gap-4 w-full">
            <button 
              type="button"
              onClick={voiceState === 'Listening' ? stopRecording : startRecording}
              className={`shrink-0 w-12 h-12 flex items-center justify-center rounded-full transition-colors ${
                voiceState === 'Listening' 
                  ? 'bg-critical text-white animate-pulse shadow-[0_0_15px_rgba(239,68,68,0.5)]' 
                  : 'bg-surface hover:bg-surface-hover text-muted-text hover:text-primary border border-border shadow-sm'
              }`}
            >
              <Mic size={22} />
            </button>
            
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileUpload} 
              accept="audio/*" 
              className="hidden" 
            />
            <button 
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="shrink-0 w-10 h-10 flex items-center justify-center rounded-full transition-colors bg-surface text-muted-text hover:text-primary border border-border"
              disabled={voiceState === 'Listening'}
            >
              <Paperclip size={18} />
            </button>

            <div className="flex-1 bg-surface border border-border rounded-full px-4 py-3 flex items-center shadow-sm focus-within:ring-2 focus-within:ring-primary/20 focus-within:border-primary transition-all">
              <input 
                type="text" 
                placeholder="Ask the OMS..." 
                className="w-full bg-transparent border-none outline-none text-base text-text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                disabled={voiceState === 'Analyzing' || voiceState === 'Executing'}
              />
            </div>
            
            <button 
              type="submit"
              disabled={!inputText.trim() || voiceState === 'Analyzing' || voiceState === 'Executing'}
              className="shrink-0 w-12 h-12 flex items-center justify-center rounded-full transition-colors bg-primary text-white hover:bg-primary/90 shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={20} className="ml-1" />
            </button>
          </form>
        </div>
      </Card>
    </div>
  );
};

export default VoiceCommandCenter;
