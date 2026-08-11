import type { APIErrorResponse } from './types';

const host = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || `http://${host}:8000`;

class APIError extends Error {
  public code: string;

  constructor(message: string, code: string = 'UNKNOWN_ERROR') {
    super(message);
    this.name = 'APIError';
    this.code = code;
  }
}

export async function fetchClient<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };

  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      let errorData: APIErrorResponse;
      try {
        errorData = await response.json();
      } catch {
        throw new APIError('Unable to parse error response', 'PARSE_ERROR');
      }
      
      throw new APIError(
        errorData?.error?.message || 'An unknown error occurred',
        errorData?.error?.code || 'UNKNOWN_ERROR'
      );
    }
    
    // For 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    return await response.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError('Unable to connect to OMS.', 'NETWORK_ERROR');
  }
}
