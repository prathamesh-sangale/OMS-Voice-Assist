import React, { useState, useRef, useEffect } from 'react';
import { Mic, X, Send, Loader2, Maximize2, MessageSquare } from 'lucide-react';
import { useAgent } from '../../app/providers/AgentProvider';
import { useNavigate } from 'react-router-dom';

const GlobalCommandOverlay = () => {
  const { 
    isOverlayOpen, 
    setIsOverlayOpen, 
    voiceState, 
    dispatchCommand, 
    latestResponse 
  } = useAgent();
  
  const [inputText, setInputText] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  // Focus input when overlay opens
  useEffect(() => {
    if (isOverlayOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOverlayOpen]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputText.trim()) {
      dispatchCommand(inputText, 'text');
      setInputText('');
    }
  };

  const handleVoice = () => {
    // Basic mock voice handling for this demo
    // In production, this would use the SpeechRecognition API from VoiceCommandCenter
    if (voiceState === 'Ready') {
      // simulate listening and transcribing for UI feel
      dispatchCommand("Voice command simulation", 'voice');
    }
  };

  if (!isOverlayOpen) {
    return (
      <button
        onClick={() => setIsOverlayOpen(true)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 flex items-center justify-center rounded-full bg-primary text-white shadow-[0_4px_20px_rgba(37,99,235,0.4)] hover:bg-opacity-90 transition-all hover:scale-105 active:scale-95"
        title="Open Command Center"
      >
        <Mic size={24} />
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 z-50 w-80 sm:w-96 bg-surface border border-border shadow-2xl rounded-2xl overflow-hidden flex flex-col animate-in slide-in-from-bottom-8 fade-in duration-200">
      
      {/* Header */}
      <div className="flex items-center justify-between p-3 bg-primary text-white">
        <div className="flex items-center gap-2 font-medium text-sm">
          <MessageSquare size={16} />
          <span>OMS Agent</span>
        </div>
        <div className="flex items-center gap-1">
          <button 
            onClick={() => {
              setIsOverlayOpen(false);
              navigate('/voice-command');
            }}
            className="p-1 hover:bg-white/20 rounded transition-colors text-white/80 hover:text-white"
            title="Expand to Full View"
          >
            <Maximize2 size={16} />
          </button>
          <button 
            onClick={() => setIsOverlayOpen(false)}
            className="p-1 hover:bg-white/20 rounded transition-colors text-white/80 hover:text-white"
          >
            <X size={18} />
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="p-4 flex flex-col gap-3 max-h-60 overflow-y-auto">
        {voiceState === 'Analyzing' || voiceState === 'Executing' ? (
          <div className="flex items-center gap-3 text-primary text-sm p-2">
            <Loader2 size={16} className="animate-spin" />
            <span>Agent is working...</span>
          </div>
        ) : latestResponse ? (
          <div className="flex flex-col gap-2 text-sm">
            <div className="text-muted-text text-xs uppercase tracking-wider font-semibold">Latest Response</div>
            <div className="bg-background border border-border p-3 rounded-lg text-text">
              {latestResponse.message}
            </div>
            {latestResponse.requires_clarification && (
              <div className="text-accent text-xs mt-1 animate-pulse font-medium">Waiting for your answer...</div>
            )}
          </div>
        ) : (
          <div className="text-muted-text text-sm text-center py-4">
            How can I help you? Try: <br/> "Show me pending orders"
          </div>
        )}
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="p-3 border-t border-border flex items-center gap-2 bg-background">
        <button 
          type="button"
          onClick={handleVoice}
          className={`shrink-0 w-10 h-10 flex items-center justify-center rounded-full transition-colors ${
            voiceState === 'Listening' 
              ? 'bg-critical text-white animate-pulse' 
              : 'bg-surface hover:bg-surface-hover text-muted-text hover:text-primary border border-border'
          }`}
        >
          <Mic size={18} />
        </button>
        
        <div className="flex-1 bg-surface border border-border rounded-full px-4 py-2 flex items-center focus-within:ring-2 focus-within:ring-primary/20 focus-within:border-primary transition-all">
          <input 
            ref={inputRef}
            type="text" 
            placeholder="Type a command..." 
            className="w-full bg-transparent border-none outline-none text-sm text-text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={voiceState === 'Analyzing' || voiceState === 'Executing'}
          />
        </div>
        
        <button 
          type="submit"
          disabled={!inputText.trim() || voiceState === 'Analyzing' || voiceState === 'Executing'}
          className="shrink-0 w-10 h-10 flex items-center justify-center rounded-full transition-colors bg-primary text-white hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Send size={16} className="ml-0.5" />
        </button>
      </form>
    </div>
  );
};

export default GlobalCommandOverlay;
