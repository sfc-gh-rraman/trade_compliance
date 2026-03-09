import { useState, useRef, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '../lib/api';
import { Card, CardContent, Button, Input } from '../components/ui';
import { Send, Bot, User, Loader2, Code, Table, ChevronDown, ChevronUp, Sparkles } from 'lucide-react';
import type { ChatMessage } from '../types';

const suggestedQuestions = [
  "What are the top 5 exception types this month?",
  "Show me brokers with accuracy below 90%",
  "Which HTS codes have the most misclassifications?",
  "What's the total duty at risk from open exceptions?",
  "List entries from China with ADD/CVD issues",
];

function MessageBubble({ message }: { message: ChatMessage }) {
  const [showSql, setShowSql] = useState(false);
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div className={`h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0 ${isUser ? 'bg-blue-600' : 'bg-slate-700'}`}>
        {isUser ? <User className="h-4 w-4 text-white" /> : <Bot className="h-4 w-4 text-white" />}
      </div>
      <div className={`flex-1 max-w-[80%] ${isUser ? 'text-right' : ''}`}>
        <div className={`inline-block rounded-lg px-4 py-3 ${isUser ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-900'}`}>
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        </div>

        {message.sql && (
          <div className="mt-2">
            <button
              onClick={() => setShowSql(!showSql)}
              className="flex items-center gap-1 text-xs text-slate-500 hover:text-slate-700"
            >
              <Code className="h-3 w-3" />
              {showSql ? 'Hide SQL' : 'Show SQL'}
              {showSql ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
            </button>
            {showSql && (
              <pre className="mt-2 p-3 bg-slate-900 text-slate-100 rounded-lg text-xs overflow-x-auto">
                {message.sql}
              </pre>
            )}
          </div>
        )}

        {message.data && message.data.length > 0 && (
          <div className="mt-2 overflow-x-auto">
            <table className="min-w-full text-xs bg-white border rounded-lg">
              <thead>
                <tr className="bg-slate-50">
                  {Object.keys(message.data[0]).map((key) => (
                    <th key={key} className="px-3 py-2 text-left font-medium text-slate-600 border-b">
                      {key}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {message.data.slice(0, 10).map((row, i) => (
                  <tr key={i} className="border-b last:border-0">
                    {Object.values(row).map((val, j) => (
                      <td key={j} className="px-3 py-2 text-slate-700">
                        {String(val)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            {message.data.length > 10 && (
              <p className="text-xs text-slate-500 mt-1">Showing 10 of {message.data.length} rows</p>
            )}
          </div>
        )}

        {message.thinking && message.thinking.length > 0 && (
          <details className="mt-2">
            <summary className="text-xs text-slate-500 cursor-pointer hover:text-slate-700">
              <Sparkles className="h-3 w-3 inline mr-1" />
              Thinking steps ({message.thinking.length})
            </summary>
            <ul className="mt-1 text-xs text-slate-500 list-disc list-inside">
              {message.thinking.map((step, i) => (
                <li key={i}>{step}</li>
              ))}
            </ul>
          </details>
        )}

        <p className="text-xs text-slate-400 mt-1">
          {new Date(message.timestamp).toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}

export function Chat() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || isStreaming) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsStreaming(true);

    try {
      let assistantContent = '';
      let assistantSql = '';
      let assistantData: Record<string, unknown>[] = [];
      const thinkingSteps: string[] = [];

      for await (const event of api.chat.stream(text)) {
        if (event.type === 'text') {
          assistantContent += event.content;
        } else if (event.type === 'sql') {
          assistantSql = event.content;
        } else if (event.type === 'data') {
          assistantData = event.content;
        } else if (event.type === 'thinking') {
          thinkingSteps.push(event.content);
        }

        setMessages((prev) => {
          const updated = [...prev];
          const lastIdx = updated.length - 1;
          if (updated[lastIdx]?.role === 'assistant') {
            updated[lastIdx] = {
              ...updated[lastIdx],
              content: assistantContent,
              sql: assistantSql || undefined,
              data: assistantData.length > 0 ? assistantData : undefined,
              thinking: thinkingSteps.length > 0 ? [...thinkingSteps] : undefined,
            };
          } else {
            updated.push({
              id: Date.now().toString(),
              role: 'assistant',
              content: assistantContent,
              timestamp: new Date().toISOString(),
              sql: assistantSql || undefined,
              data: assistantData.length > 0 ? assistantData : undefined,
              thinking: thinkingSteps.length > 0 ? [...thinkingSteps] : undefined,
            });
          }
          return updated;
        });
      }
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: 'assistant',
          content: 'Sorry, I encountered an error processing your request. Please try again.',
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsStreaming(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-slate-900">Trade Compliance Analyst</h2>
        <p className="text-sm text-slate-500">Ask questions about your trade data using natural language</p>
      </div>

      <Card className="flex-1 flex flex-col overflow-hidden">
        <CardContent className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <Bot className="h-12 w-12 text-slate-300 mb-4" />
              <h3 className="text-lg font-medium text-slate-700 mb-2">Ask me anything about your trade data</h3>
              <p className="text-sm text-slate-500 mb-6">I can analyze exceptions, broker performance, HTS codes, and more.</p>
              <div className="flex flex-wrap justify-center gap-2 max-w-2xl">
                {suggestedQuestions.map((q) => (
                  <button
                    key={q}
                    onClick={() => sendMessage(q)}
                    className="px-3 py-2 text-sm bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg) => (
                <MessageBubble key={msg.id} message={msg} />
              ))}
              {isStreaming && (
                <div className="flex gap-3">
                  <div className="h-8 w-8 rounded-full bg-slate-700 flex items-center justify-center">
                    <Bot className="h-4 w-4 text-white" />
                  </div>
                  <div className="flex items-center gap-2 text-slate-500">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm">Thinking...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </CardContent>

        <div className="border-t p-4">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about exceptions, brokers, HTS codes..."
              disabled={isStreaming}
              className="flex-1"
            />
            <Button type="submit" disabled={!input.trim() || isStreaming}>
              {isStreaming ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            </Button>
          </form>
        </div>
      </Card>
    </div>
  );
}
