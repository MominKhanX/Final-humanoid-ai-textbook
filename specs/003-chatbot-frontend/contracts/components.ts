/**
 * Component API Contracts for RAG Chatbot Frontend
 *
 * Feature: 003-chatbot-frontend
 * Date: 2025-12-17
 *
 * This file defines TypeScript interfaces for all chat widget components.
 * Used for implementation guidance and type safety.
 */

// ============================================================================
// Core Data Types
// ============================================================================

export type MessageRole = 'user' | 'assistant';

export type ChatErrorType = 'network' | 'timeout' | 'server' | 'rate_limit' | 'validation';

export interface ChatError {
  type: ChatErrorType;
  message: string;
  timestamp: string;
  retryable: boolean;
}

export interface Citation {
  module_id: string;
  chapter_id: string;
  section_title: string;
  url: string;
  relevance_score: number;
}

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
  citations: Citation[];
  isLoading: boolean;
  selected_text_context?: string;
  error?: string;
}

export interface ChatSession {
  session_id: string;
  messages: ChatMessage[];
  created_at: string;
  last_activity: string;
  backend_synced: boolean;
  message_count: number;
}

export interface ChatState {
  isOpen: boolean;
  isLoading: boolean;
  error: ChatError | null;
  currentSession: ChatSession | null;
  selectedText: string | null;
  backendUrl: string;
  apiTimeout: number;
  maxRetries: number;
}

// ============================================================================
// Context API
// ============================================================================

export type ChatAction =
  | { type: 'TOGGLE_WIDGET' }
  | { type: 'OPEN_WIDGET' }
  | { type: 'CLOSE_WIDGET' }
  | { type: 'ADD_MESSAGE'; payload: ChatMessage }
  | { type: 'UPDATE_MESSAGE'; payload: { id: string; updates: Partial<ChatMessage> } }
  | { type: 'REMOVE_MESSAGE'; payload: string }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_SESSION_ID'; payload: string }
  | { type: 'SET_SELECTED_TEXT'; payload: string | null }
  | { type: 'SET_ERROR'; payload: ChatError | null }
  | { type: 'CLEAR_ERROR' }
  | { type: 'RESTORE_SESSION'; payload: ChatSession }
  | { type: 'CLEAR_SESSION' };

export interface ChatContextValue {
  state: ChatState;
  dispatch: React.Dispatch<ChatAction>;
}

export interface ChatProviderProps {
  children: React.ReactNode;
}

// ============================================================================
// Component Props
// ============================================================================

/**
 * ChatWidget - Root component containing the entire chat interface
 * Wrapped in BrowserOnly for SSR safety
 */
export interface ChatWidgetProps {
  // No external props - all state from ChatContext
}

/**
 * ChatHeader - Top bar with title and control buttons
 */
export interface ChatHeaderProps {
  title: string;
  onMinimize: () => void;
  onClose: () => void;
  isLoading: boolean;
}

/**
 * ChatMessageList - Scrollable container for messages
 */
export interface ChatMessageListProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onCitationClick: (citation: Citation) => void;
}

/**
 * ChatMessage - Individual message bubble (user or assistant)
 */
export interface ChatMessageProps {
  message: ChatMessage;
  onCitationClick: (citation: Citation) => void;
}

/**
 * ChatInput - Text input area with send button
 */
export interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  selectedText: string | null;
  onClearSelection: () => void;
}

/**
 * CitationBadge - Clickable badge for source references
 */
export interface CitationBadgeProps {
  citation: Citation;
  onClick: (citation: Citation) => void;
}

/**
 * TypingIndicator - Animated loading indicator
 */
export interface TypingIndicatorProps {
  // No props - pure UI component
}

/**
 * ErrorMessage - Error display with retry button
 */
export interface ErrorMessageProps {
  error: ChatError;
  onRetry: () => void;
  onDismiss: () => void;
}

/**
 * ChatIcon - Floating button to open chat widget
 */
export interface ChatIconProps {
  onClick: () => void;
  hasUnreadMessages: boolean;
}

/**
 * MarkdownRenderer - Renders markdown content with syntax highlighting
 */
export interface MarkdownRendererProps {
  content: string;
}

/**
 * TextSelectionListener - Detects text selection and shows action button
 */
export interface TextSelectionListenerProps {
  onSelectionMade: (text: string) => void;
  isWidgetOpen: boolean;
}

// ============================================================================
// API Response Types (from backend)
// ============================================================================

export interface ChatResponse {
  answer: string;
  sources: Citation[];
  session_id: string;
  timestamp: string;
  response_time_ms: number;
}

export interface ChatHistoryResponse {
  session_id: string;
  messages: Array<{
    message_id: number;
    question: string;
    answer: string;
    cited_sources: Citation[];
    timestamp: string;
    response_time_ms: number;
  }>;
  created_at: string;
  last_activity: string;
}

export interface ChatRequest {
  question: string;
  session_id: string | null;
}

export interface SelectedTextRequest {
  question: string;
  selected_text: string;
  session_id: string | null;
}

// ============================================================================
// Utility Types
// ============================================================================

export interface SelectionRect {
  top: number;
  left: number;
  width: number;
  height: number;
  text: string;
}

export interface ScrollState {
  isAtBottom: boolean;
  showScrollButton: boolean;
}

export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

// ============================================================================
// Hook Return Types
// ============================================================================

export interface UseChatReturn {
  state: ChatState;
  sendMessage: (message: string) => Promise<void>;
  sendSelectedTextQuery: (question: string, selectedText: string) => Promise<void>;
  restoreSession: (sessionId: string) => Promise<void>;
  clearSession: () => void;
  toggleWidget: () => void;
  openWidget: () => void;
  closeWidget: () => void;
}

export interface UseTextSelectionReturn {
  selectionRect: SelectionRect | null;
  clearSelection: () => void;
}

export interface UseSessionStorageReturn<T> {
  value: T | null;
  setValue: (value: T) => void;
  clearValue: () => void;
}
