import React, { useState, useRef, useEffect } from 'react';
import ExecutionEnvironment from '@docusaurus/ExecutionEnvironment';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Array<{
    module_id: string;
    chapter_id: string;
    section_title: string;
    url: string;
    relevance_score: number;
  }>;
  timestamp: string;
}

const API_BASE_URL = 'https://final-humanoid-ai-textbook-production.up.railway.app';
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

export default function ChatWidget(): JSX.Element {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const STORAGE_KEY = 'neurobot-chat-history';
  const SESSION_KEY = 'neurobot-session-id';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load chat history and session from localStorage on mount
  useEffect(() => {
    if (!ExecutionEnvironment.canUseDOM) return;

    // Load or create session ID
    let savedSessionId = localStorage.getItem(SESSION_KEY);
    if (!savedSessionId) {
      savedSessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem(SESSION_KEY, savedSessionId);
    }
    setSessionId(savedSessionId);

    // Load chat history
    const savedMessages = localStorage.getItem(STORAGE_KEY);
    if (savedMessages) {
      try {
        setMessages(JSON.parse(savedMessages));
      } catch (e) {
        console.error('Failed to load chat history:', e);
      }
    }
  }, []);

  // Save chat history to localStorage whenever messages change
  useEffect(() => {
    if (!ExecutionEnvironment.canUseDOM || messages.length === 0) return;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

  const fetchWithRetry = async (url: string, options: RequestInit, retries = MAX_RETRIES): Promise<Response> => {
    try {
      const response = await fetch(url, options);
      return response;
    } catch (error) {
      if (retries > 0) {
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
        return fetchWithRetry(url, options, retries - 1);
      }
      throw error;
    }
  };

  const isGreeting = (text: string): boolean => {
    const greetings = ['hi', 'hello', 'hey', 'sup', 'yo', 'greetings', 'howdy', 'hiya', 'who are you', 'what are you', 'introduce yourself'];
    const lowerText = text.toLowerCase().trim();
    return greetings.some(greeting => lowerText === greeting || lowerText.startsWith(greeting + ' ') || lowerText.endsWith(' ' + greeting));
  };

  const typeMessage = async (fullText: string, sources?: any[], timestamp?: string) => {
    setIsTyping(true);

    const tempMessage: Message = {
      role: 'assistant',
      content: '',
      sources: sources,
      timestamp: timestamp || new Date().toISOString(),
    };

    setMessages(prev => [...prev, tempMessage]);

    const chars = fullText.split('');
    let currentText = '';
    const CHAR_DELAY = 15;

    for (let i = 0; i < chars.length; i++) {
      currentText += chars[i];
      setMessages(prev => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1] = {
          ...tempMessage,
          content: currentText,
        };
        return newMessages;
      });
      await new Promise(resolve => setTimeout(resolve, CHAR_DELAY));
    }

    setIsTyping(false);
  };

  const handleSend = async (customMessage?: string) => {
    const messageText = customMessage || inputValue;
    if (!messageText.trim() || isLoading || isTyping) return;

    const userMessage: Message = {
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');

    if (isGreeting(messageText)) {
      const introMessage = "Hi! I'm NeuroBot, your AI assistant for the Physical AI & Humanoid Robotics textbook!\n\nI'm here to help you understand ROS 2, simulation, NVIDIA Isaac, VLA models, and everything in the book.\n\nWhat would you like to learn about today?";
      await typeMessage(introMessage, [], new Date().toISOString());
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetchWithRetry(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          question: messageText,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      setIsLoading(false);

      await typeMessage(
        data.answer || data.message || 'No response received',
        data.sources || data.citations,
        data.timestamp || new Date().toISOString()
      );
    } catch (error) {
      console.error('Chat error:', error);
      setIsLoading(false);
      await typeMessage(
        'Sorry, I encountered an error connecting to the backend. Please make sure the server is running on http://localhost:8000',
        [],
        new Date().toISOString()
      );
    }
  };

  const handleClearHistory = () => {
    if (confirm('Clear all chat history?')) {
      setMessages([]);
      if (ExecutionEnvironment.canUseDOM) {
        localStorage.removeItem(STORAGE_KEY);
      }
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <>
      {/* Chat Toggle Button */}
      <div
        className={`neurobot-chatbot-toggle ${isOpen ? 'hidden' : ''}`}
        onClick={() => setIsOpen(true)}
      >
        <span className="neurobot-chatbot-toggle-icon">💬</span>
        {messages.length > 0 && (
          <span style={{
            position: 'absolute',
            top: '-4px',
            right: '-4px',
            background: 'var(--neurobot-accent-primary)',
            color: 'white',
            borderRadius: '50%',
            width: '20px',
            height: '20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '0.6875rem',
            fontWeight: 700
          }}>
            {messages.filter(m => m.role === 'user').length}
          </span>
        )}
      </div>

      {/* Chat Widget */}
      <div className={`neurobot-chatbot ${!isOpen ? 'hidden' : ''}`}>
        {/* Header */}
        <div className="neurobot-chatbot-header">
          <div className="neurobot-chatbot-title-container">
            <div className="neurobot-chatbot-title">NeuroBot Assistant</div>
            <div className="neurobot-chatbot-subtitle">Ask about Physical AI & Robotics</div>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            {messages.length > 0 && (
              <button
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'white',
                  fontSize: '1.125rem',
                  cursor: 'pointer',
                  padding: '0.25rem',
                  transition: 'all 0.2s ease',
                  opacity: 0.7
                }}
                onClick={handleClearHistory}
                onMouseEnter={(e) => {
                  e.currentTarget.style.opacity = '1';
                  e.currentTarget.style.transform = 'scale(1.1)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.opacity = '0.7';
                  e.currentTarget.style.transform = 'scale(1)';
                }}
                title="Clear history">
                🗑️
              </button>
            )}
            <button className="neurobot-chatbot-close" onClick={() => setIsOpen(false)}>
              ×
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="neurobot-chatbot-messages">
          {messages.length === 0 && (
            <div style={{
              textAlign: 'center',
              color: 'var(--neurobot-text-tertiary)',
              padding: '2rem 1rem'
            }}>
              <p style={{ marginBottom: '0.5rem', fontSize: '1.125rem' }}>👋 Welcome!</p>
              <p style={{ margin: 0, fontSize: '0.9375rem', marginBottom: '1rem' }}>
                Ask me anything about ROS 2, robotics simulation, NVIDIA Isaac, or VLA models.
              </p>
              <p style={{
                margin: 0,
                fontSize: '0.8125rem',
                color: 'var(--neurobot-accent-primary)',
                fontWeight: 600
              }}>
                💡 Tip: Highlight any text on this page to ask questions about it!
              </p>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={`neurobot-message neurobot-message-${message.role}`}
            >
              <div className="neurobot-message-bubble">
                {message.content}
                {message.sources && message.sources.length > 0 && (
                  <div style={{ marginTop: '0.75rem', fontSize: '0.8125rem' }}>
                    <strong>Sources:</strong>
                    <div style={{ marginTop: '0.5rem', display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                      {message.sources.map((source, idx) => (
                        <a
                          key={idx}
                          href={source.url}
                          className="neurobot-citation"
                          title={`${source.module_id} / ${source.chapter_id} / ${source.section_title} (${(source.relevance_score * 100).toFixed(0)}% relevant)`}
                        >
                          {source.chapter_id}
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              <div className="neurobot-message-time">
                {formatTime(message.timestamp)}
              </div>
            </div>
          ))}

          {(isLoading || isTyping) && (
            <div className="neurobot-message neurobot-message-assistant">
              <div className="neurobot-typing-indicator">
                <div className="neurobot-typing-dot"></div>
                <div className="neurobot-typing-dot"></div>
                <div className="neurobot-typing-dot"></div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="neurobot-chatbot-input">
          <div className="neurobot-input-wrapper">
            <input
              type="text"
              className="neurobot-input-field"
              placeholder="Ask about Physical AI..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading || isTyping}
            />
            <button
              className="neurobot-send-button"
              onClick={() => handleSend()}
              disabled={isLoading || isTyping || !inputValue.trim()}
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
