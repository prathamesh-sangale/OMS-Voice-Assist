import { useState } from 'react';
import { Mic, CheckCircle2, AlertCircle, Loader2, Send } from 'lucide-react';
import { Card } from '../../components/ui/Card';

type VoiceState = 'Ready' | 'Analyzing' | 'Executing' | 'Completed' | 'Error' | 'Needs Clarification';

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    setVoiceState('Analyzing');
    setResponse(null);

    try {
      // Small artificial delay to show state changes if API is too fast
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setVoiceState('Executing');
      
      const res = await fetch('http://127.0.0.1:8000/api/agent/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText }),
      });
      
      const data: AgentResponse = await res.json();
      setResponse(data);
      
      if (data.status === 'success') {
        setVoiceState('Completed');
      } else if (data.status === 'needs_clarification') {
        setVoiceState('Needs Clarification');
      } else {
        setVoiceState('Error');
      }
      
    } catch (err) {
      console.error(err);
      setVoiceState('Error');
      setResponse({
        status: 'error',
        message: 'Failed to communicate with the Agent API.',
      });
    }
  };

  return (
    <div className="max-w-3xl mx-auto mt-12 space-y-8">
      <div className="text-center">
        <h1 className="text-2xl font-semibold text-text mb-2">Voice Command Center</h1>
        <p className="text-muted-text">Type natural language commands to control the OMS</p>
      </div>

      <form onSubmit={handleSubmit}>
        <Card className="p-4 flex items-center gap-4 bg-surface shadow-md">
          {/* Disabled Microphone for Text-Only Phase */}
          <button 
            type="button"
            className="w-12 h-12 flex items-center justify-center rounded-full transition-colors bg-surface-hover text-muted-text cursor-not-allowed"
            title="Voice input disabled in Phase 3.1"
          >
            <Mic size={24} />
          </button>
          
          <div className="flex-1">
            <input 
              type="text" 
              placeholder="Ask the OMS (e.g. 'Show pending orders')..." 
              className="w-full bg-transparent border-none outline-none text-lg placeholder:text-muted-text/50"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              disabled={voiceState === 'Analyzing' || voiceState === 'Executing'}
              autoFocus
            />
          </div>
          
          <button 
            type="submit"
            disabled={!inputText.trim() || voiceState === 'Analyzing' || voiceState === 'Executing'}
            className="w-12 h-12 flex items-center justify-center rounded-full transition-colors bg-primary text-white hover:bg-opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send size={20} />
          </button>
          
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-background border border-border min-w-[120px] justify-center">
            {voiceState === 'Ready' && <span className="w-2 h-2 rounded-full bg-success"></span>}
            {voiceState === 'Analyzing' && <Loader2 size={14} className="animate-spin text-accent" />}
            {voiceState === 'Executing' && <Loader2 size={14} className="animate-spin text-warning" />}
            {voiceState === 'Completed' && <CheckCircle2 size={14} className="text-success" />}
            {(voiceState === 'Error' || voiceState === 'Needs Clarification') && <AlertCircle size={14} className="text-critical" />}
            <span className="text-xs font-medium text-muted-text">{voiceState}</span>
          </div>
        </Card>
      </form>
      
      {/* Simulation Feedback UI */}
      {response && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div>
            <h3 className="text-xs font-semibold text-muted-text uppercase tracking-wider mb-2">You Typed</h3>
            <Card className="p-4 bg-background italic border-none shadow-none text-text">
              "{inputText}"
            </Card>
          </div>

          <div>
            <h3 className="text-xs font-semibold text-muted-text uppercase tracking-wider mb-2">Command</h3>
            <Card className="p-4 bg-surface space-y-4">
              <div className="grid grid-cols-2 text-sm gap-4">
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
                  <span className="font-medium">Deterministic Analyzer</span>
                </div>
                <div>
                  <span className="block text-muted-text text-xs mb-1">Explanation</span>
                  <span className="font-medium">{response.metadata?.explanation || 'None'}</span>
                </div>
              </div>
            </Card>
          </div>

          <div>
            <h3 className="text-xs font-semibold text-muted-text uppercase tracking-wider mb-2">Result</h3>
            <Card className={`p-4 border ${
              response.status === 'success' ? 'bg-success/5 border-success/20' : 
              response.status === 'needs_clarification' ? 'bg-warning/5 border-warning/20' :
              'bg-critical/5 border-critical/20'
            }`}>
              <div className={`text-sm font-medium ${
                response.status === 'success' ? 'text-success' : 
                response.status === 'needs_clarification' ? 'text-warning' :
                'text-critical'
              }`}>
                {response.message}
              </div>
              
              {/* Optional: Render raw JSON data purely for debugging/verification in this phase */}
              {response.data && (
                <div className="mt-4 p-3 bg-background rounded border border-border overflow-auto max-h-64 text-xs font-mono text-muted-text">
                  <pre>{JSON.stringify(response.data, null, 2)}</pre>
                </div>
              )}
            </Card>
          </div>
        </div>
      )}
    </div>
  );
};

export default VoiceCommandCenter;
