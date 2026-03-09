import type { ApiResponse, Broker, Exception, Rule, DashboardData, ChatMessage } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Request failed' }));
    throw new ApiError(response.status, error.message || `HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  dashboard: {
    get: () => request<ApiResponse<DashboardData>>('/dashboard'),
  },

  exceptions: {
    list: (params?: { broker?: string; status?: string; country?: string }) => {
      const query = new URLSearchParams(params as Record<string, string>).toString();
      return request<ApiResponse<Exception[]>>(`/exceptions${query ? `?${query}` : ''}`);
    },
    get: (id: string) => request<ApiResponse<Exception>>(`/exceptions/${id}`),
    resolve: (id: string, comments: string) =>
      request<ApiResponse<Exception>>(`/exceptions/${id}/resolve`, {
        method: 'POST',
        body: JSON.stringify({ comments }),
      }),
    export: (params?: Record<string, string>) => {
      const query = new URLSearchParams(params).toString();
      return `${API_BASE}/exceptions/export${query ? `?${query}` : ''}`;
    },
  },

  rules: {
    list: (params?: { status?: string; type?: string }) => {
      const query = new URLSearchParams(params as Record<string, string>).toString();
      return request<ApiResponse<Rule[]>>(`/rules${query ? `?${query}` : ''}`);
    },
    get: (id: string) => request<ApiResponse<Rule>>(`/rules/${id}`),
    approve: (id: string) =>
      request<ApiResponse<Rule>>(`/rules/${id}/approve`, { method: 'POST' }),
    reject: (id: string, reason: string) =>
      request<ApiResponse<Rule>>(`/rules/${id}/reject`, {
        method: 'POST',
        body: JSON.stringify({ reason }),
      }),
    toggle: (id: string, active: boolean) =>
      request<ApiResponse<Rule>>(`/rules/${id}`, {
        method: 'PATCH',
        body: JSON.stringify({ status: active ? 'active' : 'disabled' }),
      }),
  },

  brokers: {
    list: () => request<ApiResponse<Broker[]>>('/brokers'),
    get: (id: string) => request<ApiResponse<Broker>>(`/brokers/${id}`),
    create: (data: Partial<Broker>) =>
      request<ApiResponse<Broker>>('/brokers', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: string, data: Partial<Broker>) =>
      request<ApiResponse<Broker>>(`/brokers/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
  },

  chat: {
    send: (message: string) =>
      request<ApiResponse<ChatMessage>>('/chat', {
        method: 'POST',
        body: JSON.stringify({ message }),
      }),
    stream: async function* (message: string) {
      const response = await fetch(`${API_BASE}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) throw new ApiError(response.status, 'Stream failed');
      if (!response.body) throw new Error('No response body');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              yield JSON.parse(line.slice(6));
            } catch {
              // Skip invalid JSON
            }
          }
        }
      }
    },
    history: () => request<ApiResponse<ChatMessage[]>>('/chat/history'),
  },
};

export { ApiError };
