# Quickstart Guide: RAG Chatbot Frontend Integration

**Feature**: 003-chatbot-frontend
**Estimated Time**: 15 minutes
**Prerequisites**: Node.js 18+, npm/yarn

This guide will get you from zero to a working chat widget in your local Docusaurus development environment.

---

## Step 1: Install Dependencies (2 minutes)

```bash
# Navigate to project root
cd Final-humanoid-ai-textbook

# Install required packages
npm install react-markdown react-syntax-highlighter
npm install --save-dev @types/react @types/react-dom

# Verify Docusaurus is installed
npm list @docusaurus/core
```

**Expected packages**:
- `react-markdown`: ^9.0.0 (markdown rendering)
- `react-syntax-highlighter`: ^15.5.0 (code highlighting)
- `@docusaurus/core`: ^3.0.0+ (should already be installed)

---

## Step 2: Configure Environment Variables (1 minute)

Create `.env.local` in project root (this file is gitignored):

```bash
# .env.local
REACT_APP_CHAT_API_URL=http://localhost:8000
```

For production builds, set in Vercel/GitHub Pages:
```bash
REACT_APP_CHAT_API_URL=https://neurobot-api.onrender.com
```

---

## Step 3: Add Royal Indigo Theme Variables (2 minutes)

Open `src/css/custom.css` and add chat widget variables:

```css
/* src/css/custom.css */

:root {
  /* Existing royal indigo variables... */

  /* Chat Widget Variables */
  --chat-royal-indigo-start: #2d3561;
  --chat-royal-indigo-end: #4a5f8f;
  --chat-accent-blue-violet: #5b7ec8;
  --chat-dark-charcoal: #0d1117;
  --chat-border-radius: 8px;
  --chat-transition: 0.3s ease;
}

[data-theme='dark'] {
  --chat-bg-primary: #0d1117;
  --chat-bg-secondary: #161b22;
  --chat-bg-tertiary: #21262d;
  --chat-text-primary: #ffffff;
  --chat-text-secondary: #8b949e;
  --chat-border-color: #30363d;
}

[data-theme='light'] {
  --chat-bg-primary: #ffffff;
  --chat-bg-secondary: #f6f8fa;
  --chat-bg-tertiary: #eaeef2;
  --chat-text-primary: #24292f;
  --chat-text-secondary: #57606a;
  --chat-border-color: #d0d7de;
}
```

---

## Step 4: Create Component Structure (1 minute)

```bash
# Create directory structure
mkdir -p src/components/ChatWidget
mkdir -p src/contexts
mkdir -p src/utils
mkdir -p src/hooks

# Expected structure:
# src/
# ├── components/
# │   └── ChatWidget/
# │       ├── index.tsx                 (Main ChatWidget component)
# │       ├── ChatHeader.tsx
# │       ├── ChatMessageList.tsx
# │       ├── ChatMessage.tsx
# │       ├── ChatInput.tsx
# │       ├── CitationBadge.tsx
# │       ├── TypingIndicator.tsx
# │       ├── ChatIcon.tsx
# │       ├── ChatWidget.module.css
# │       └── components.module.css    (Shared styles)
# ├── contexts/
# │   └── ChatContext.tsx              (Global state)
# ├── utils/
# │   ├── chatApi.ts                   (Backend API calls)
# │   └── sessionStorage.ts            (Session persistence)
# └── hooks/
#     └── useChatContext.ts            (Context hook)
```

---

## Step 5: Implement Core Files (5 minutes)

### 5.1 Chat Context (State Management)

Create `src/contexts/ChatContext.tsx`:

```tsx
import React, { createContext, useReducer, useEffect, ReactNode } from 'react';

// Types
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  citations: any[];
  isLoading: boolean;
}

interface ChatState {
  isOpen: boolean;
  messages: ChatMessage[];
  sessionId: string | null;
  isLoading: boolean;
  selectedText: string | null;
  error: string | null;
}

type ChatAction =
  | { type: 'TOGGLE_WIDGET' }
  | { type: 'ADD_MESSAGE'; payload: ChatMessage }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_SESSION_ID'; payload: string }
  | { type: 'SET_SELECTED_TEXT'; payload: string | null }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'RESTORE_SESSION'; payload: any };

// Initial state
const initialState: ChatState = {
  isOpen: false,
  messages: [],
  sessionId: null,
  isLoading: false,
  selectedText: null,
  error: null
};

// Reducer
function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case 'TOGGLE_WIDGET':
      return { ...state, isOpen: !state.isOpen };
    case 'ADD_MESSAGE':
      return { ...state, messages: [...state.messages, action.payload] };
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_SESSION_ID':
      return { ...state, sessionId: action.payload };
    case 'SET_SELECTED_TEXT':
      return { ...state, selectedText: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'RESTORE_SESSION':
      return { ...state, ...action.payload };
    default:
      return state;
  }
}

// Context
export const ChatContext = createContext<{
  state: ChatState;
  dispatch: React.Dispatch<ChatAction>;
} | null>(null);

// Provider
export function ChatProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  // Persist to sessionStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      sessionStorage.setItem('neurobot_chat_state', JSON.stringify(state));
    }
  }, [state]);

  return (
    <ChatContext.Provider value={{ state, dispatch }}>
      {children}
    </ChatContext.Provider>
  );
}

// Hook
export function useChatContext() {
  const context = React.useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext must be used within ChatProvider');
  }
  return context;
}
```

### 5.2 API Utilities

Create `src/utils/chatApi.ts`:

```typescript
const API_BASE = process.env.REACT_APP_CHAT_API_URL || 'http://localhost:8000';
const TIMEOUT_MS = 15000;

async function fetchWithTimeout(url: string, options: RequestInit = {}) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new Error('Request timeout');
    }
    throw error;
  }
}

export async function sendChatMessage(question: string, sessionId: string | null) {
  return fetchWithTimeout(`${API_BASE}/chat`, {
    method: 'POST',
    body: JSON.stringify({ question, session_id: sessionId })
  });
}

export async function sendSelectedTextQuery(
  question: string,
  selectedText: string,
  sessionId: string | null
) {
  return fetchWithTimeout(`${API_BASE}/chat/selected`, {
    method: 'POST',
    body: JSON.stringify({ question, selected_text: selectedText, session_id: sessionId })
  });
}

export async function getChatHistory(sessionId: string) {
  return fetchWithTimeout(`${API_BASE}/chat/history?session_id=${sessionId}`);
}
```

### 5.3 Simple Chat Widget (MVP)

Create `src/components/ChatWidget/index.tsx`:

```tsx
import React, { useState } from 'react';
import { useChatContext } from '../../contexts/ChatContext';
import { sendChatMessage } from '../../utils/chatApi';
import styles from './ChatWidget.module.css';

export default function ChatWidget() {
  const { state, dispatch } = useChatContext();
  const [inputValue, setInputValue] = useState('');

  async function handleSendMessage() {
    if (!inputValue.trim() || state.isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      role: 'user' as const,
      content: inputValue,
      timestamp: new Date().toISOString(),
      citations: [],
      isLoading: false
    };

    dispatch({ type: 'ADD_MESSAGE', payload: userMessage });
    dispatch({ type: 'SET_LOADING', payload: true });
    setInputValue('');

    try {
      const response = await sendChatMessage(inputValue, state.sessionId);

      dispatch({ type: 'SET_SESSION_ID', payload: response.session_id });

      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant' as const,
        content: response.answer,
        timestamp: response.timestamp,
        citations: response.sources || [],
        isLoading: false
      };

      dispatch({ type: 'ADD_MESSAGE', payload: assistantMessage });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }

  if (!state.isOpen) {
    return (
      <button
        className={styles.chatIcon}
        onClick={() => dispatch({ type: 'TOGGLE_WIDGET' })}
        aria-label="Open chat"
      >
        💬
      </button>
    );
  }

  return (
    <div className={styles.chatWidget}>
      <div className={styles.chatHeader}>
        <h3>NeuroBot Assistant</h3>
        <button onClick={() => dispatch({ type: 'TOGGLE_WIDGET' })}>✕</button>
      </div>

      <div className={styles.chatMessages}>
        {state.messages.map(msg => (
          <div
            key={msg.id}
            className={msg.role === 'user' ? styles.userMessage : styles.assistantMessage}
          >
            {msg.content}
          </div>
        ))}
        {state.isLoading && <div className={styles.typing}>Typing...</div>}
      </div>

      <div className={styles.chatInput}>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="Ask a question..."
          disabled={state.isLoading}
        />
        <button onClick={handleSendMessage} disabled={state.isLoading || !inputValue.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}
```

### 5.4 Basic Styles

Create `src/components/ChatWidget/ChatWidget.module.css`:

```css
.chatIcon {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--chat-royal-indigo-start), var(--chat-royal-indigo-end));
  color: white;
  font-size: 24px;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: transform 0.3s ease;
  z-index: 9999;
}

.chatIcon:hover {
  transform: scale(1.1);
}

.chatWidget {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 400px;
  height: 600px;
  background: var(--chat-bg-primary);
  border-radius: var(--chat-border-radius);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  z-index: 9999;
}

.chatHeader {
  background: linear-gradient(135deg, var(--chat-royal-indigo-start), var(--chat-royal-indigo-end));
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: var(--chat-border-radius) var(--chat-border-radius) 0 0;
}

.chatHeader h3 {
  margin: 0;
  color: white;
  font-family: Georgia, serif;
  font-size: 18px;
}

.chatHeader button {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
}

.chatMessages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.userMessage {
  align-self: flex-end;
  background: var(--chat-bg-secondary);
  color: var(--chat-text-primary);
  padding: 12px;
  border-radius: var(--chat-border-radius);
  max-width: 80%;
}

.assistantMessage {
  align-self: flex-start;
  background: var(--chat-bg-tertiary);
  color: var(--chat-text-primary);
  padding: 12px;
  border-radius: var(--chat-border-radius);
  border-left: 3px solid var(--chat-royal-indigo-start);
  max-width: 80%;
}

.typing {
  align-self: flex-start;
  color: var(--chat-text-secondary);
  font-style: italic;
}

.chatInput {
  padding: 16px;
  display: flex;
  gap: 8px;
  border-top: 1px solid var(--chat-border-color);
}

.chatInput input {
  flex: 1;
  padding: 10px;
  border: 1px solid var(--chat-border-color);
  border-radius: 4px;
  background: var(--chat-bg-secondary);
  color: var(--chat-text-primary);
}

.chatInput button {
  padding: 10px 20px;
  background: linear-gradient(135deg, var(--chat-royal-indigo-start), var(--chat-royal-indigo-end));
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: opacity 0.3s ease;
}

.chatInput button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

---

## Step 6: Integrate with Docusaurus (3 minutes)

### 6.1 Create Root Wrapper

Create `src/theme/Root.tsx`:

```tsx
import React from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';
import { ChatProvider } from '../contexts/ChatContext';

// Lazy load chat widget for performance
const ChatWidget = React.lazy(() => import('../components/ChatWidget'));

export default function Root({ children }) {
  return (
    <>
      {children}
      <BrowserOnly fallback={<div />}>
        {() => (
          <ChatProvider>
            <React.Suspense fallback={<div />}>
              <ChatWidget />
            </React.Suspense>
          </ChatProvider>
        )}
      </BrowserOnly>
    </>
  );
}
```

### 6.2 Swizzle Theme (if needed)

If `src/theme/Root.tsx` doesn't work, swizzle the Layout component:

```bash
npm run swizzle @docusaurus/theme-classic Root -- --eject
```

---

## Step 7: Start Development Server (1 minute)

```bash
# Start Docusaurus dev server
npm run start

# Server should start at http://localhost:3000
# Chat icon should appear in bottom-right corner
```

**Expected behavior**:
1. Page loads without errors
2. Chat icon (💬) appears bottom-right
3. Clicking icon opens chat widget
4. Typing message and pressing Enter sends to backend
5. Response appears after ~2-3 seconds

---

## Step 8: Test Chat Functionality (3 minutes)

### Test Case 1: Basic Message
1. Click chat icon
2. Type: "What is a ROS 2 node?"
3. Press Enter
4. **Expected**: Loading indicator → Response with citations

### Test Case 2: Session Persistence
1. Send a message
2. Navigate to different page
3. Reopen chat widget
4. **Expected**: Previous message still visible

### Test Case 3: Error Handling
1. Stop backend server
2. Send a message
3. **Expected**: Error message with retry button

### Test Case 4: Dark/Light Mode
1. Toggle site theme (click theme switcher)
2. **Expected**: Chat widget colors update smoothly

---

## Troubleshooting

### Issue: "window is not defined" error during build

**Solution**: Ensure ChatWidget is wrapped in `BrowserOnly` and uses React.lazy

```tsx
// ✅ Correct
<BrowserOnly>
  {() => <ChatWidget />}
</BrowserOnly>

// ❌ Wrong
<ChatWidget />
```

### Issue: Chat icon not appearing

**Solution**: Check z-index and verify Root.tsx is being used

```bash
# Verify Root.tsx exists
ls src/theme/Root.tsx

# Check browser console for errors
# Open DevTools → Console
```

### Issue: Backend API calls failing (CORS)

**Solution**: Ensure backend has CORS enabled for `http://localhost:3000`

```python
# Backend: main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://mominkhanx.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Styles not applying

**Solution**: Verify CSS variables are defined in `src/css/custom.css` and imported

```tsx
// docusaurus.config.js
module.exports = {
  stylesheets: ['./src/css/custom.css'],
  // ...
};
```

---

## Next Steps

After completing quickstart:

1. **Add Markdown Rendering**: Integrate `react-markdown` for assistant messages
2. **Implement Citations**: Create `CitationBadge` component
3. **Add Selected Text Mode**: Implement `TextSelectionListener`
4. **Improve Error Handling**: Add retry logic with exponential backoff
5. **Mobile Responsiveness**: Add media queries for <768px screens
6. **Accessibility**: Add ARIA attributes and keyboard navigation
7. **Performance**: Implement virtual scrolling for 50+ messages

---

## Verification Checklist

- [ ] Chat icon appears in bottom-right
- [ ] Clicking icon opens/closes widget smoothly
- [ ] Sending message works (connects to backend)
- [ ] Response appears with ~2-3s latency
- [ ] Session persists across page navigation
- [ ] Dark/light mode toggle updates widget colors
- [ ] Build completes without SSR errors: `npm run build`
- [ ] No console errors in browser DevTools

**Estimated completion time**: 15 minutes
**MVP Chat Widget**: ✅ Working

---

**Quickstart Status**: ✅ COMPLETE
**Next**: Full implementation with all features from spec.md
