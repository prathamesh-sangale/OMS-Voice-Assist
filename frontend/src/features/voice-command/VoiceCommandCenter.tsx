import { useState } from 'react';
import { Mic, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { Card } from '../../components/ui/Card';

type VoiceState = 'Ready' | 'Listening' | 'Processing' | 'Executing' | 'Completed' | 'Error';

const VoiceCommandCenter = () => {
  const [voiceState, setVoiceState] = useState<VoiceState>('Ready');

  const handleSimulate = () => {
    setVoiceState('Listening');
    setTimeout(() => setVoiceState('Processing'), 1500);
    setTimeout(() => setVoiceState('Executing'), 3000);
    setTimeout(() => setVoiceState('Completed'), 4500);
  };

  return (
    <div className="max-w-3xl mx-auto mt-12 space-y-8">
      <div className="text-center">
        <h1 className="text-2xl font-semibold text-text mb-2">Voice Command Center</h1>
        <p className="text-muted-text">Speak natural language commands to control the OMS</p>
      </div>

      <Card className="p-4 flex items-center gap-4 bg-surface shadow-md">
        <button 
          className={`w-12 h-12 flex items-center justify-center rounded-full transition-colors ${
            voiceState === 'Listening' 
              ? 'bg-critical text-white animate-pulse' 
              : 'bg-primary text-white hover:bg-opacity-90'
          }`}
          onClick={handleSimulate}
          disabled={voiceState !== 'Ready' && voiceState !== 'Completed' && voiceState !== 'Error'}
        >
          <Mic size={24} />
        </button>
        
        <div className="flex-1">
          <input 
            type="text" 
            placeholder="Ask the OMS..." 
            className="w-full bg-transparent border-none outline-none text-lg placeholder:text-muted-text/50"
            disabled
            value={voiceState === 'Listening' ? 'Listening...' : ''}
          />
        </div>
        
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-background border border-border">
          {voiceState === 'Ready' && <span className="w-2 h-2 rounded-full bg-success"></span>}
          {voiceState === 'Listening' && <span className="w-2 h-2 rounded-full bg-critical animate-pulse"></span>}
          {voiceState === 'Processing' && <Loader2 size={14} className="animate-spin text-accent" />}
          {voiceState === 'Executing' && <Loader2 size={14} className="animate-spin text-warning" />}
          {voiceState === 'Completed' && <CheckCircle2 size={14} className="text-success" />}
          {voiceState === 'Error' && <AlertCircle size={14} className="text-critical" />}
          <span className="text-xs font-medium text-muted-text">{voiceState}</span>
        </div>
      </Card>
      
      {/* Simulation Feedback UI */}
      {voiceState !== 'Ready' && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div>
            <h3 className="text-xs font-semibold text-muted-text uppercase tracking-wider mb-2">You Said</h3>
            <Card className="p-4 bg-background italic border-none shadow-none text-text">
              {voiceState === 'Listening' ? '...' : '"Show me pending reefer orders"'}
            </Card>
          </div>

          {(voiceState === 'Processing' || voiceState === 'Executing' || voiceState === 'Completed') && (
            <div>
              <h3 className="text-xs font-semibold text-muted-text uppercase tracking-wider mb-2">Command</h3>
              <Card className="p-4 bg-surface space-y-4">
                <div className="grid grid-cols-2 text-sm gap-4">
                  <div>
                    <span className="block text-muted-text text-xs mb-1">Intent</span>
                    <span className="font-medium">Filter Orders</span>
                  </div>
                  <div>
                    <span className="block text-muted-text text-xs mb-1">Method</span>
                    <span className="font-medium">Rule Engine</span>
                  </div>
                </div>
                <div className="bg-background p-3 rounded border border-border text-sm">
                  <span className="block text-muted-text text-xs mb-1">Filters Applied</span>
                  <ul className="list-disc list-inside">
                    <li>Status: Pending Approval</li>
                    <li>Product: Reefer Container</li>
                  </ul>
                </div>
              </Card>
            </div>
          )}

          {voiceState === 'Completed' && (
            <div>
              <h3 className="text-xs font-semibold text-muted-text uppercase tracking-wider mb-2">Result</h3>
              <Card className="p-4 bg-success/5 border-success/20">
                <div className="text-sm font-medium text-success">
                  Executed successfully. 2 orders found matching your criteria.
                </div>
              </Card>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default VoiceCommandCenter;
