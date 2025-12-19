# Data Model: RAG Chatbot Frontend Integration

**Feature**: 003-chatbot-frontend
**Date**: 2025-12-17
**Status**: Phase 1 Complete

This document defines all frontend entities, their structure, relationships, and state management patterns for the RAG Chatbot Frontend Integration.

---

## Entity Relationship Overview

```
ChatProvider (Context)
    └── ChatState
            ├── isOpen: boolean
            ├── currentSession: ChatSession
            ├── selectedText: string | null
            ├── isLoading: boolean
            └── error: Error | null

ChatSession
    ├── session_id: UUID
    ├── messages: ChatMessage[]
    ├── created_at: timestamp
    └── last_activity: timestamp

ChatMessage
    ├── id: UUID
    ├── role: 'user' | 'assistant'
    ├── content: string (markdown)
    ├── timestamp: ISO8601
    ├── citations: Citation[]
    └── isLoading: boolean

Citation
    ├── module_id: string
    ├── chapter_id: string
    ├── section_title: string
    ├── url: string
    └── relevance_score: number

ComponentTree
    ChatWidget
        ├── ChatHeader
        ├── ChatMessageList
        │   └── ChatMessage[]
        │       └── CitationBadge[]
        ├── ChatInput
        └── ChatIcon
```

---

## 1. ChatState (Global State)

**Description**: Central state management for the entire chat widget, maintained in React Context and synchronized with sessionStorage.

**TypeScript Interface**:
```typescript
interface ChatState {
  // UI State
  isOpen: boolean;                    // Widget visibility
  isLoading: boolean;                 // Request in progress
  error: ChatError | null;            // Current error state

  // Session Data
  currentSession: ChatSession | null; // Active conversation
  selectedText: string | null;        // Text selection for queries

  // Configuration
  backendUrl: string;                 // API base URL
  apiTimeout: number;                 // Request timeout (ms)
  maxRetries: number;                 // Retry attempts
}

interface ChatError {
  type: 'network' | 'timeout' | 'server' | 'rate_limit' | 'validation';
  message: string;
  timestamp: string;
  retryable: boolean;
}
```

**State Transitions**:
```
INITIAL → WIDGET_OPENED → LOADING → LOADED | ERROR
         ↑                              ↓
         └──────────────────────────────┘
              (user closes/reopens)
```

**Persistence Rules**:
- **sessionStorage**: Entire state serialized on every update
- **Key**: `neurobot_chat_session_{session_id}`
- **Expiry**: Cleared on tab close (session-scoped)
- **Restoration**: On mount, restore from sessionStorage + verify with backend

**Validation Rules**:
- `session_id`: Must be valid UUID v4 or null
- `messages`: Array length ≤ 100 (prevent memory issues)
- `selectedText`: Length ≤ 5000 characters (backend limit)
- `error`: Cleared after 10 seconds or on successful request

---

## 2. ChatSession

**Description**: Represents a single conversation session, synchronized with backend session_id.

**TypeScript Interface**:
```typescript
interface ChatSession {
  session_id: string;                 // UUID from backend
  messages: ChatMessage[];            // Conversation history
  created_at: string;                 // ISO8601 timestamp
  last_activity: string;              // ISO8601 timestamp
  backend_synced: boolean;            // Synced with backend history?
  message_count: number;              // Total messages (user + assistant)
}
```

**Creation Flow**:
1. User sends first message
2. Frontend generates temporary ID: `temp_${Date.now()}`
3. Backend response includes `session_id` (UUID)
4. Frontend replaces temp ID with backend ID
5. All subsequent requests include `session_id`

**Lifecycle**:
```
CREATE (first message) → ACTIVE (messages exchanged) → EXPIRED (24h) → ARCHIVED
```

**Storage Strategy**:
- **Local (sessionStorage)**: Last 50 messages for instant restore
- **Backend (Postgres)**: Full history up to 24 hours
- **Sync Trigger**: On page load, if `session_id` exists and `backend_synced = false`

**Validation Rules**:
- `session_id`: Must match backend UUID format after first response
- `messages`: Must alternate user/assistant (except loading states)
- `created_at`: Cannot be in future
- `last_activity`: Must be ≥ `created_at`
- `message_count`: Must equal `messages.length`

---

## 3. ChatMessage

**Description**: Individual message in the conversation (user question or assistant response).

**TypeScript Interface**:
```typescript
interface ChatMessage {
  id: string;                         // UUID (frontend-generated)
  role: 'user' | 'assistant';        // Message sender
  content: string;                    // Message text (markdown for assistant)
  timestamp: string;                  // ISO8601 creation time
  citations: Citation[];              // Sources (assistant only)
  isLoading: boolean;                 // Typing indicator (assistant only)
  selected_text_context?: string;     // Original selection (if from selected text mode)
  error?: string;                     // Error message if send failed
}
```

**Message Types**:

1. **User Message** (Question):
```typescript
{
  id: "550e8400-e29b-41d4-a716-446655440000",
  role: "user",
  content: "What is a ROS 2 node?",
  timestamp: "2025-12-17T10:30:00.000Z",
  citations: [],
  isLoading: false
}
```

2. **Assistant Message** (Response):
```typescript
{
  id: "660e8400-e29b-41d4-a716-446655440001",
  role: "assistant",
  content: "A ROS 2 node is a fundamental execution unit...",
  timestamp: "2025-12-17T10:30:02.500Z",
  citations: [
    {
      module_id: "module-1",
      chapter_id: "chapter-1",
      section_title: "Understanding Nodes",
      url: "/docs/module-1-ros2/chapter-1#nodes",
      relevance_score: 0.92
    }
  ],
  isLoading: false
}
```

3. **Loading Message** (Temporary):
```typescript
{
  id: "temp_loading",
  role: "assistant",
  content: "",
  timestamp: "2025-12-17T10:30:01.000Z",
  citations: [],
  isLoading: true
}
```

4. **Selected Text Message** (User with context):
```typescript
{
  id: "770e8400-e29b-41d4-a716-446655440002",
  role: "user",
  content: "What does this function do?",
  timestamp: "2025-12-17T10:35:00.000Z",
  citations: [],
  isLoading: false,
  selected_text_context: "def process_sensor_data(msg):\n    return msg.data * 2"
}
```

**Rendering Rules**:
- **User messages**: Right-aligned, dark background, white text, no markdown parsing
- **Assistant messages**: Left-aligned, royal indigo border, markdown rendered with syntax highlighting
- **Loading messages**: Show typing indicator (3 pulsing dots), replace with actual message on response
- **Error messages**: Show error icon + red border, keep user message visible for retry

**Validation Rules**:
- `id`: Must be unique within session
- `content`: Required, max 5000 characters
- `timestamp`: Must be valid ISO8601
- `citations`: Only allowed for assistant messages
- `isLoading`: Only true for temporary assistant messages

---

## 4. Citation

**Description**: Source reference linking assistant responses to specific textbook chapters.

**TypeScript Interface**:
```typescript
interface Citation {
  module_id: string;                  // e.g., "module-1", "module-2"
  chapter_id: string;                 // e.g., "chapter-1", "chapter-2"
  section_title: string;              // Human-readable section name
  url: string;                        // Full URL: "/docs/module-1-ros2/chapter-1#section"
  relevance_score: number;            // 0.0-1.0 (from vector search)
}
```

**Example**:
```typescript
{
  module_id: "module-3",
  chapter_id: "chapter-2",
  section_title: "Isaac Gym Environment Setup",
  url: "/docs/module-3-isaac/chapter-2#environment-setup",
  relevance_score: 0.89
}
```

**Rendering Specification**:
- **Badge Style**: Royal indigo background (#2d3561), white text, rounded (16px), padding (6px 12px)
- **Icon**: Book emoji (📖) or SVG icon before text
- **Text Format**: "{module_id}, {chapter_id}: {section_title}"
- **Hover Effect**: Scale 1.05×, subtle glow, 0.3s transition
- **Click Behavior**: Navigate to `url` using Docusaurus router, scroll to section, minimize widget

**Validation Rules**:
- `module_id`: Must match pattern `module-[1-4]`
- `chapter_id`: Must match pattern `chapter-[1-5]`
- `section_title`: Max 100 characters
- `url`: Must start with `/docs/` or be valid external URL
- `relevance_score`: Must be between 0.0 and 1.0

**Sorting**:
- Display citations sorted by `relevance_score` descending
- Show max 5 citations per message (backend filters top 5)

---

## 5. Component Data Contracts

### ChatWidget (Root Component)

**Props**:
```typescript
interface ChatWidgetProps {
  // No props - reads from ChatContext
}
```

**State** (local):
```typescript
interface ChatWidgetState {
  isMinimized: boolean;               // Collapsed to icon only
  hasUnreadMessages: boolean;         // Show notification badge
}
```

**Events**:
- `onOpen`: Widget expanded by user
- `onClose`: Widget minimized by user
- `onSendMessage`: User sends message
- `onCitationClick`: User clicks citation badge

---

### ChatHeader

**Props**:
```typescript
interface ChatHeaderProps {
  title: string;                      // "NeuroBot Assistant"
  onMinimize: () => void;             // Minimize button click
  onClose: () => void;                // Close button click
  isLoading: boolean;                 // Show loading indicator in header
}
```

**Rendering**:
- Royal indigo gradient background: `linear-gradient(135deg, #2d3561, #4a5f8f)`
- Georgia serif font, 18px, bold, white
- Minimize/close icons: white, 24×24px, hover scale 1.1×

---

### ChatMessageList

**Props**:
```typescript
interface ChatMessageListProps {
  messages: ChatMessage[];            // Array of messages to display
  isLoading: boolean;                 // Show typing indicator
  onCitationClick: (citation: Citation) => void;
}
```

**State** (local):
```typescript
interface ChatMessageListState {
  autoScroll: boolean;                // Auto-scroll to bottom on new message
  showScrollButton: boolean;          // Show "scroll to bottom" button
}
```

**Behavior**:
- Auto-scroll to bottom when new message arrives (if user is near bottom)
- Show "New message" button if user scrolled up and new message arrives
- Virtual scrolling if messages > 50 (performance optimization)

---

### ChatMessage

**Props**:
```typescript
interface ChatMessageProps {
  message: ChatMessage;
  onCitationClick: (citation: Citation) => void;
}
```

**Rendering**:
```typescript
// User message
<div className={styles.userMessage}>
  {message.selected_text_context && (
    <div className={styles.selectedContext}>
      <span className={styles.label}>Selected text:</span>
      <pre>{message.selected_text_context}</pre>
    </div>
  )}
  <p>{message.content}</p>
  <span className={styles.timestamp}>
    {formatTimestamp(message.timestamp)}
  </span>
</div>

// Assistant message
<div className={styles.assistantMessage}>
  {message.isLoading ? (
    <TypingIndicator />
  ) : (
    <>
      <MarkdownRenderer content={message.content} />
      {message.citations.length > 0 && (
        <div className={styles.citations}>
          {message.citations.map(citation => (
            <CitationBadge
              key={citation.url}
              citation={citation}
              onClick={() => onCitationClick(citation)}
            />
          ))}
        </div>
      )}
      <span className={styles.timestamp}>
        {formatTimestamp(message.timestamp)}
      </span>
    </>
  )}
</div>
```

---

### ChatInput

**Props**:
```typescript
interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;                 // Disable input while loading
  selectedText: string | null;        // Show selected text context
  onClearSelection: () => void;       // Clear selected text mode
}
```

**State** (local):
```typescript
interface ChatInputState {
  inputValue: string;                 // Current input text
  charCount: number;                  // Character counter
  isComposing: boolean;               // IME composition state
}
```

**Behavior**:
- Enter key: Send message (Shift+Enter for newline)
- Esc key: Clear input / close widget
- Max length: 1000 characters (show counter at 800+)
- Disable send button if input is empty or loading

---

### CitationBadge

**Props**:
```typescript
interface CitationBadgeProps {
  citation: Citation;
  onClick: (citation: Citation) => void;
}
```

**Rendering**:
```typescript
<button
  className={styles.citationBadge}
  onClick={() => onClick(citation)}
  aria-label={`Navigate to ${citation.section_title}`}
>
  <span className={styles.icon}>📖</span>
  <span className={styles.text}>
    {citation.module_id}, {citation.chapter_id}: {citation.section_title}
  </span>
  <span className={styles.score} title="Relevance score">
    {Math.round(citation.relevance_score * 100)}%
  </span>
</button>
```

---

### TextSelectionListener

**Props**:
```typescript
interface TextSelectionListenerProps {
  onSelectionMade: (text: string) => void;
  isWidgetOpen: boolean;              // Don't trigger if widget is open
}
```

**State** (local):
```typescript
interface TextSelectionListenerState {
  selectionRect: DOMRect | null;     // Position for floating button
  selectedText: string;               // Current selection
}
```

**Behavior**:
- Listen for `mouseup` / `touchend` events
- Check if selection length > 10 characters
- Show floating "Ask about selection" button near selection
- Keyboard shortcut: Ctrl+Q / Cmd+Q triggers with current selection

---

## 6. State Management Flow

### Send Message Flow

```
1. User types message, clicks send
2. Dispatch: SET_LOADING(true)
3. Create user message, add to state
4. Create loading message (assistant)
5. Call backend API (sendChatMessage)
6. On success:
   - Remove loading message
   - Create assistant message with response
   - Update session_id if first message
   - Dispatch: ADD_MESSAGE(assistant)
   - Dispatch: SET_LOADING(false)
7. On error:
   - Remove loading message
   - Dispatch: SET_ERROR(error)
   - Keep user message for retry
```

### Selected Text Query Flow

```
1. User highlights text
2. TextSelectionListener captures selection
3. User clicks "Ask about selection" or presses Ctrl+Q
4. Dispatch: SET_SELECTED_TEXT(text)
5. Dispatch: TOGGLE_WIDGET (open)
6. ChatInput shows selected text context
7. User types question
8. Send to backend /chat/selected endpoint
9. Backend response includes context-aware answer
10. Display with selected text context badge
```

### Session Restoration Flow

```
1. ChatWidget mounts
2. Check sessionStorage for existing session
3. If found:
   a. Load session_id
   b. Call backend /chat/history?session_id=...
   c. If backend success: Restore full history
   d. If backend fails: Use sessionStorage copy
4. If not found:
   - Start new session (session_id = null)
   - First message will create backend session
```

---

## 7. Storage Schema

### sessionStorage Key-Value Structure

**Key**: `neurobot_chat_session`

**Value** (JSON):
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "messages": [
    {
      "id": "msg-001",
      "role": "user",
      "content": "What is a ROS 2 node?",
      "timestamp": "2025-12-17T10:30:00.000Z",
      "citations": [],
      "isLoading": false
    },
    {
      "id": "msg-002",
      "role": "assistant",
      "content": "A ROS 2 node is...",
      "timestamp": "2025-12-17T10:30:02.500Z",
      "citations": [...],
      "isLoading": false
    }
  ],
  "created_at": "2025-12-17T10:30:00.000Z",
  "last_activity": "2025-12-17T10:30:02.500Z",
  "backend_synced": true,
  "message_count": 2
}
```

**Size Estimate**: ~500 bytes per message × 50 messages = ~25KB (well within 5MB quota)

---

## 8. Validation & Error Handling

### Client-Side Validation

| Field | Rule | Error Message |
|-------|------|---------------|
| message content | 1-1000 chars | "Message must be between 1 and 1000 characters" |
| selected_text | ≤5000 chars | "Selected text is too long. Please select a shorter passage." |
| session_id | UUID v4 or null | "Invalid session ID format" |
| timestamp | Valid ISO8601 | "Invalid timestamp format" |
| citation.url | Valid URL | "Invalid citation URL" |

### Error States

```typescript
enum ChatErrorType {
  NETWORK = 'network',          // fetch failed, no internet
  TIMEOUT = 'timeout',          // Request >15s
  SERVER = 'server',            // 500, 503 errors
  RATE_LIMIT = 'rate_limit',    // 429 error
  VALIDATION = 'validation'     // Invalid input
}

interface ChatErrorState {
  type: ChatErrorType;
  message: string;
  timestamp: string;
  retryable: boolean;
  retryCount: number;
  maxRetries: number;
}
```

### Error Recovery

| Error Type | User Message | Action | Retry |
|------------|-------------|---------|-------|
| NETWORK | "Unable to connect. Check your internet." | Show retry button | ✅ Yes (3x) |
| TIMEOUT | "Request timed out. Try again." | Show retry button | ✅ Yes (3x) |
| SERVER | "Something went wrong. Please try again." | Show retry button | ✅ Yes (3x) |
| RATE_LIMIT | "Too many requests. Wait a moment." | Disable send (30s) | ❌ No |
| VALIDATION | "Invalid input. Please check your message." | Show error inline | ❌ No |

---

## 9. Performance Optimizations

### React.memo Usage

```typescript
// Memoize message components (prevent re-render on list updates)
export const ChatMessage = React.memo(ChatMessageComponent, (prev, next) => {
  return prev.message.id === next.message.id &&
         prev.message.isLoading === next.message.isLoading;
});

// Memoize citation badges (prevent re-render on citation array reference change)
export const CitationBadge = React.memo(CitationBadgeComponent);
```

### Virtual Scrolling (50+ messages)

```typescript
import { FixedSizeList } from 'react-window';

function ChatMessageList({ messages }) {
  if (messages.length > 50) {
    return (
      <FixedSizeList
        height={500}
        itemCount={messages.length}
        itemSize={100}
        width="100%"
      >
        {({ index, style }) => (
          <div style={style}>
            <ChatMessage message={messages[index]} />
          </div>
        )}
      </FixedSizeList>
    );
  }

  // Normal rendering for <50 messages
  return messages.map(msg => <ChatMessage key={msg.id} message={msg} />);
}
```

### Debounced Storage Writes

```typescript
import { debounce } from 'lodash-es';

// Only write to sessionStorage max once per 500ms
const saveToStorage = debounce((state) => {
  sessionStorage.setItem('neurobot_chat_session', JSON.stringify(state));
}, 500);
```

---

**Phase 1 Status**: ✅ COMPLETE (Data Model)
**Next Artifact**: Component API contracts (contracts/)
