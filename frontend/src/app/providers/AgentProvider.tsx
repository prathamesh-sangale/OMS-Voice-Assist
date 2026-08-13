import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';
import type { ConversationSession, AgentResponse, VoiceState } from '../../types/agent';
import { fetchClient } from '../../services/api/client';
import { useNavigate } from 'react-router-dom';

interface AgentContextType {
  sessionId: string | undefined;
  setSessionId: (id: string | undefined) => void;
  currentSession: ConversationSession | null;
  setCurrentSession: (session: ConversationSession | null) => void;
  latestResponse: AgentResponse | null;
  setLatestResponse: (response: AgentResponse | null) => void;
  voiceState: VoiceState;
  setVoiceState: (state: VoiceState) => void;
  isOverlayOpen: boolean;
  setIsOverlayOpen: (isOpen: boolean) => void;
  dispatchCommand: (text: string, source: 'text' | 'voice') => Promise<void>;
}

const AgentContext = createContext<AgentContextType | undefined>(undefined);

export const AgentProvider = ({ children }: { children: ReactNode }) => {
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const [currentSession, setCurrentSession] = useState<ConversationSession | null>(null);
  const [latestResponse, setLatestResponse] = useState<AgentResponse | null>(null);
  const [voiceState, setVoiceState] = useState<VoiceState>('Idle');
  const [isOverlayOpen, setIsOverlayOpen] = useState(false);
  
  const navigate = useNavigate();

  const fetchSessionDetails = async (id: string) => {
    try {
      // Use the same API_BASE_URL logic if needed, but relative URL works with Vite proxy
      const res = await fetch(`http://localhost:8000/api/agent/sessions/${id}`);
      if (res.ok) {
        const data = await res.json();
        setCurrentSession(data);
      }
    } catch (e) {
      console.error("Failed to fetch session details", e);
    }
  };

  const dispatchCommand = async (text: string, source: 'text' | 'voice') => {
    // Optimistically update local session
    const fakeMsg = { id: Date.now().toString(), role: 'user' as const, text, timestamp: new Date().toISOString() };
    if (currentSession) {
      setCurrentSession({ ...currentSession, messages: [...currentSession.messages, fakeMsg] });
    } else {
      setCurrentSession({ id: 'temp', title: 'New Conversation', updated_at: '', messages: [fakeMsg], context: {} });
    }
    try {
      console.log('[Voice] Agent dispatch started...');
      setVoiceState('Understanding');
      if (!isOverlayOpen) setIsOverlayOpen(true);
      
      const response = await fetchClient('/api/agent/command', {
        method: 'POST',
        body: JSON.stringify({
          text,
          source,
          session_id: sessionId
        })
      }) as AgentResponse;
      
      console.log('[Voice] Agent response received.');
      setVoiceState('Executing');
      setLatestResponse(response);
      
      if (response.session_id) {
        setSessionId(response.session_id);
        await fetchSessionDetails(response.session_id);
      }
      
      // Auto-navigation based on backend hint
      if (response.navigation?.target) {
        navigate(response.navigation.target);
      }
      
      // Play TTS for all responses
      if (response.spoken_response) {
        setVoiceState('Playing');
        try {
          const ttsRes = await fetch('http://localhost:8000/api/voice/tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: response.spoken_response })
          });
          
          if (ttsRes.ok) {
            const audioBlob = await ttsRes.blob();
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            
            await new Promise((resolve) => {
              audio.onended = () => {
                URL.revokeObjectURL(audioUrl);
                resolve(null);
              };
              audio.play().catch(e => {
                console.error("Audio playback blocked", e);
                resolve(null);
              });
            });
          }
        } catch (e) {
          console.error("Failed to play TTS", e);
        }
      }
      
      setVoiceState('Completed');
      setTimeout(() => {
        // Continuous Voice Loop: Always wait for user until they manually close the chat or stop
        setVoiceState('Waiting_For_User');
      }, 1000);
      
    } catch (error) {
      console.error("Command execution failed:", error);
      setVoiceState('Error');
      setTimeout(() => setVoiceState('Idle'), 3000);
    }
  };

  return (
    <AgentContext.Provider value={{
      sessionId,
      setSessionId,
      currentSession,
      setCurrentSession,
      latestResponse,
      setLatestResponse,
      voiceState,
      setVoiceState,
      isOverlayOpen,
      setIsOverlayOpen,
      dispatchCommand
    }}>
      {children}
    </AgentContext.Provider>
  );
};

export const useAgent = () => {
  const context = useContext(AgentContext);
  if (context === undefined) {
    throw new Error('useAgent must be used within an AgentProvider');
  }
  return context;
};
