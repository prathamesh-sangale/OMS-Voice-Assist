export type VoiceState = 'Idle' | 'Listening' | 'Transcribing' | 'You_Said' | 'Understanding' | 'Executing' | 'Completed' | 'Playing' | 'Waiting_For_User' | 'Error';

export interface SessionMessage {
  id: string;
  role: 'user' | 'agent';
  text: string;
  timestamp: string;
  input_mode?: string;
  response_type?: string;
  data?: any;
}

export interface ConversationSession {
  id: string;
  title: string;
  updated_at: string;
  messages: SessionMessage[];
  context: {
    intent?: string;
    draft?: any;
    operation_status?: string;
    pending_field?: string;
    last_result_context?: any;
    target_orders?: any;
  };
}

export interface AgentResponse {
  status: string;
  message: string;
  spoken_response?: string;
  intent?: string;
  data?: any;
  metadata?: any;
  requires_clarification?: boolean;
  session_id?: string;
  response_type?: string;
  navigation?: {
    target: string;
    reason?: string;
  };
}
