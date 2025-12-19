# Technical Research: RAG Chatbot Frontend Integration

**Feature**: 003-chatbot-frontend
**Date**: 2025-12-17
**Status**: Phase 0 Complete

This document captures all technical decisions, alternatives considered, and implementation guidance for the RAG Chatbot Frontend Integration feature.

---

## 1. Chat UI Component Approach

**Decision**: Build custom React components instead of using OpenAI ChatKit SDK

**Rationale**: OpenAI ChatKit SDK is primarily designed for OpenAI's Assistants API with built-in UI components that may not integrate cleanly with Docusaurus's theming system. Building custom components gives us full control over the royal indigo theme styling, SSR safety, and integration with our specific backend API structure. Custom components also result in smaller bundle sizes (target <150KB) compared to full SDK integration.

**Alternatives Considered**:
- **OpenAI ChatKit SDK**: Provides pre-built chat UI but designed for Assistants API, not custom RAG backends. Would require extensive customization to match royal indigo theme. Bundle size concerns (~300KB+).
- **@chatscope/chat-ui-kit-react**: Good React chat components but generic styling, still requires heavy customization. Adds unnecessary dependencies.
- **Custom React Components** (CHOSEN): Full control, optimal bundle size, native Docusaurus integration, tailored to our backend API structure.

**Implementation Notes**:
- Create component hierarchy: `ChatWidget` → `ChatHeader`, `ChatMessageList`, `ChatInput`, `ChatMessage`, `CitationBadge`
- Use React hooks for state: `useState` for UI state, `useEffect` for side effects, `useCallback` for optimized handlers
- Wrap in `BrowserOnly` from `@docusaurus/BrowserOnly` for SSR safety
- Place in `src/components/ChatWidget/` directory with CSS modules for styling
- Dynamic import in `src/theme/Root.tsx` for lazy loading

---

## 2. SSR-Safe Initialization Pattern

**Decision**: Use Docusaurus `BrowserOnly` wrapper + React.lazy for chat widget

**Rationale**: Docusaurus performs static site generation (SSG) at build time, where browser APIs (window, document, localStorage) are not available. The `BrowserOnly` component is Docusaurus's recommended approach for client-only components. Combined with React.lazy, this ensures the chat widget code is only loaded and executed in the browser, preventing build errors and optimizing initial page load performance.

**Alternatives Considered**:
- **useEffect-only approach**: Check `typeof window !== 'undefined'` in useEffect. Works but still loads component code during SSR, causing hydration warnings.
- **Dynamic import in useEffect**: Loads component after mount but creates awkward loading states and complicates state management.
- **BrowserOnly + React.lazy** (CHOSEN): Clean separation, no SSR execution, optimal code splitting, Docusaurus-native pattern.

**Implementation Notes**:
```jsx
// src/theme/Root.tsx
import React from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';

const ChatWidget = React.lazy(() => import('@site/src/components/ChatWidget'));

export default function Root({children}) {
  return (
    <>
      {children}
      <BrowserOnly fallback={<div />}>
        {() => (
          <React.Suspense fallback={<div />}>
            <ChatWidget />
          </React.Suspense>
        )}
      </BrowserOnly>
    </>
  );
}
```

**Edge Cases**:
- Ensure no browser API calls in module-level code (only inside component after mount)
- Test build with `npm run build` to verify no "window is not defined" errors
- Fallback div should match chat icon dimensions to prevent layout shift

---

## 3. State Management Architecture

**Decision**: React Context API + useReducer for global chat state

**Rationale**: The chat widget needs to maintain state across page navigations (Docusaurus uses client-side routing). React Context with useReducer provides predictable state management without external dependencies, keeping bundle size minimal. Sufficient for our use case (single widget, moderate state complexity). Easier to debug than Redux, no learning curve for contributors.

**Alternatives Considered**:
- **Local component state only**: Too simple, loses state on unmount/remount during navigation
- **Redux Toolkit**: Overkill for single widget, adds ~20KB to bundle, more boilerplate
- **Zustand**: Lightweight (3KB), good developer experience, but Context+useReducer is sufficient and built-in
- **Context + useReducer** (CHOSEN): Built-in, no dependencies, sufficient complexity handling, predictable state updates

**Implementation Notes**:
```jsx
// src/contexts/ChatContext.tsx
import React, { createContext, useReducer, useContext, useEffect } from 'react';

const ChatContext = createContext(null);

const initialState = {
  isOpen: false,
  messages: [],
  sessionId: null,
  isLoading: false,
  selectedText: null,
  error: null
};

function chatReducer(state, action) {
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

export function ChatProvider({ children }) {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  // Persist to sessionStorage on state change
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

export const useChatContext = () => useContext(ChatContext);
```

---

## 4. Royal Indigo Theme Integration

**Decision**: CSS Modules + Docusaurus CSS variables for theme consistency

**Rationale**: CSS Modules provide scoped styling without conflicts, essential in Docusaurus where global styles can collide. By using Docusaurus's CSS variables for theme colors and adding custom royal indigo variables, we ensure the chat widget responds to dark/light mode changes automatically. This approach maintains separation of concerns (styles in .module.css files) while leveraging Docusaurus's theming system.

**Alternatives Considered**:
- **Inline styles**: Quick but unmaintainable, no hover states, no theme responsiveness
- **Styled-components**: Adds runtime overhead (~16KB), CSS-in-JS not idiomatic in Docusaurus
- **Global CSS**: High risk of style collisions, hard to maintain scoping
- **CSS Modules + CSS Variables** (CHOSEN): Scoped, maintainable, theme-responsive, zero runtime cost

**Implementation Notes**:
```css
/* src/css/custom.css - Add royal indigo variables */
:root {
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
  --chat-text-primary: #ffffff;
  --chat-text-secondary: #8b949e;
}

[data-theme='light'] {
  --chat-bg-primary: #ffffff;
  --chat-bg-secondary: #f6f8fa;
  --chat-text-primary: #24292f;
  --chat-text-secondary: #57606a;
}
```

```css
/* src/components/ChatWidget/ChatWidget.module.css */
.chatWidget {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 400px;
  height: 600px;
  background: var(--chat-bg-primary);
  border-radius: var(--chat-border-radius);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
  transition: all var(--chat-transition);
  z-index: 9999;
}

.chatHeader {
  background: linear-gradient(135deg, var(--chat-royal-indigo-start), var(--chat-royal-indigo-end));
  padding: 16px;
  border-radius: var(--chat-border-radius) var(--chat-border-radius) 0 0;
}

.assistantMessage {
  border-left: 3px solid var(--chat-royal-indigo-start);
  background: var(--chat-bg-secondary);
}
```

**Edge Cases**:
- Test both dark and light modes to ensure contrast meets WCAG AA standards (4.5:1 for text)
- Ensure smooth transition (0.3s ease) when theme changes
- Verify gradient renders consistently across browsers (Safari, Firefox, Chrome)

---

## 5. Bundle Optimization Strategy

**Decision**: React.lazy for widget + code splitting for markdown renderer

**Rationale**: The chat widget is not needed on initial page load - students will interact with it after starting to read content. By lazy loading the entire widget with React.lazy, we defer ~80KB of JavaScript until the user first opens the widget. Additionally, splitting the markdown renderer (react-markdown + syntax highlighter) into a separate chunk saves another ~40KB, loaded only when the first assistant message arrives. This keeps initial page load under 5 seconds as required by constitution.

**Alternatives Considered**:
- **Load everything on initial page load**: Violates performance requirement, unnecessary for non-interactive users
- **Manual dynamic import()**: More verbose than React.lazy, same result but harder to maintain
- **Service Worker caching**: Complex setup, still requires initial download
- **React.lazy + code splitting** (CHOSEN): Native React pattern, automatic bundle splitting, deferred loading

**Implementation Notes**:
```jsx
// Lazy load chat widget in Root.tsx
const ChatWidget = React.lazy(() => import('@site/src/components/ChatWidget'));

// Lazy load markdown renderer inside ChatMessage component
const MarkdownRenderer = React.lazy(() =>
  import('./MarkdownRenderer').then(module => ({ default: module.MarkdownRenderer }))
);

// Bundle analysis command
"analyze": "ANALYZE=true npm run build"
```

**Performance Budget**:
- Initial page load (without chat): <80KB JS (gzipped)
- Chat widget bundle: <80KB JS (gzipped)
- Markdown renderer bundle: <40KB JS (gzipped)
- Total chat functionality: <120KB JS (within 150KB target)

**Verification**:
- Run `npm run build` and check `build/` output sizes
- Use Lighthouse to verify <5s loading time on simulated 3G
- Monitor bundle size with webpack-bundle-analyzer

---

## 6. Text Selection Detection

**Decision**: Use window.getSelection() API with custom context menu integration

**Rationale**: The native Selection API is well-supported across browsers and provides reliable text selection detection. Combining with a floating action button (appears on selection) gives users a clear affordance for the "Ask about selection" feature without cluttering the UI. The Selection API handles complex scenarios like multi-element selections and code blocks automatically. Keyboard shortcut (Ctrl+Q) provides power-user alternative.

**Alternatives Considered**:
- **Right-click context menu override**: Interferes with native browser context menu, poor UX
- **Toolbar button only**: Users might not discover the feature, no contextual trigger
- **Selection event + floating button** (CHOSEN): Discoverable, non-intrusive, follows modern UI patterns (Medium, Google Docs)

**Implementation Notes**:
```jsx
// src/components/TextSelectionListener/index.tsx
import React, { useEffect, useState } from 'react';
import { useChatContext } from '@site/src/contexts/ChatContext';

export function TextSelectionListener() {
  const [selectionRect, setSelectionRect] = useState(null);
  const { dispatch } = useChatContext();

  useEffect(() => {
    function handleSelection() {
      const selection = window.getSelection();
      const text = selection.toString().trim();

      if (text.length > 10) { // Minimum 10 chars to avoid accidental selections
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        setSelectionRect({
          top: rect.top + window.scrollY - 40,
          left: rect.left + (rect.width / 2) - 75,
          text
        });
      } else {
        setSelectionRect(null);
      }
    }

    document.addEventListener('mouseup', handleSelection);
    document.addEventListener('keyup', handleSelection); // For keyboard selection

    return () => {
      document.removeEventListener('mouseup', handleSelection);
      document.removeEventListener('keyup', handleSelection);
    };
  }, []);

  function handleAskAboutSelection() {
    dispatch({ type: 'SET_SELECTED_TEXT', payload: selectionRect.text });
    dispatch({ type: 'TOGGLE_WIDGET' }); // Open widget
    setSelectionRect(null);
    window.getSelection().removeAllRanges(); // Clear selection
  }

  if (!selectionRect) return null;

  return (
    <div
      style={{
        position: 'absolute',
        top: selectionRect.top,
        left: selectionRect.left,
        zIndex: 10000
      }}
      className="text-selection-button"
    >
      <button onClick={handleAskAboutSelection}>
        Ask about selection (Ctrl+Q)
      </button>
    </div>
  );
}
```

**Edge Cases**:
- Ignore selections inside the chat widget itself (check event.target)
- Handle selections across multiple paragraphs/code blocks (Selection API handles this)
- Mobile: Use 'touchend' event instead of 'mouseup'
- Truncate very long selections (>5000 chars) with intelligent middle truncation

---

## 7. Backend API Integration

**Decision**: Native fetch API + AbortController for timeouts + exponential backoff retry

**Rationale**: The fetch API is native to modern browsers (no dependencies), well-documented, and sufficient for our API needs (3 simple endpoints). AbortController provides timeout handling (15s limit). Custom retry logic with exponential backoff (2s, 4s, 8s) handles transient backend errors gracefully. No need for axios overhead (~14KB) when fetch + simple wrapper covers all requirements.

**Alternatives Considered**:
- **axios**: Popular but adds 14KB bundle size, unnecessary for simple REST API
- **ky**: Smaller than axios (7KB) but still unnecessary dependency
- **fetch + custom wrapper** (CHOSEN): Zero dependencies, AbortController native, custom retry logic tailored to our needs

**Implementation Notes**:
```js
// src/utils/chatApi.js
const CHAT_API_BASE = process.env.REACT_APP_CHAT_API_URL || 'https://neurobot-api.onrender.com';
const TIMEOUT_MS = 15000;
const MAX_RETRIES = 3;

async function fetchWithRetry(url, options, retries = 0) {
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
      // Retry on 500, 503 errors
      if ((response.status === 500 || response.status === 503) && retries < MAX_RETRIES) {
        const delay = Math.pow(2, retries) * 1000; // Exponential backoff: 1s, 2s, 4s
        await new Promise(resolve => setTimeout(resolve, delay));
        return fetchWithRetry(url, options, retries + 1);
      }
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);

    if (error.name === 'AbortError') {
      throw new Error('Request timeout - please try again');
    }

    // Retry on network errors
    if (retries < MAX_RETRIES) {
      const delay = Math.pow(2, retries) * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));
      return fetchWithRetry(url, options, retries + 1);
    }

    throw error;
  }
}

export async function sendChatMessage(question, sessionId = null) {
  return fetchWithRetry(`${CHAT_API_BASE}/chat`, {
    method: 'POST',
    body: JSON.stringify({ question, session_id: sessionId })
  });
}

export async function sendSelectedTextQuery(question, selectedText, sessionId = null) {
  return fetchWithRetry(`${CHAT_API_BASE}/chat/selected`, {
    method: 'POST',
    body: JSON.stringify({ question, selected_text: selectedText, session_id: sessionId })
  });
}

export async function getChatHistory(sessionId) {
  return fetchWithRetry(`${CHAT_API_BASE}/chat/history?session_id=${sessionId}`, {
    method: 'GET'
  });
}
```

**Environment Configuration**:
```bash
# .env.local (not committed to git)
REACT_APP_CHAT_API_URL=http://localhost:8000

# For production build
REACT_APP_CHAT_API_URL=https://neurobot-api.onrender.com
```

---

## 8. Markdown Rendering in Messages

**Decision**: react-markdown with react-syntax-highlighter for code blocks

**Rationale**: react-markdown is the de-facto standard for rendering markdown in React (2.5M weekly downloads), actively maintained, and handles security (XSS prevention) out of the box. react-syntax-highlighter integrates seamlessly for code blocks with royal indigo theme customization. Combined bundle size ~35KB (gzipped), acceptable when code-split. Safer than marked + DOMPurify (manual XSS handling required).

**Alternatives Considered**:
- **marked + DOMPurify**: Manual setup, requires careful XSS sanitization, not React-optimized
- **remark**: Lower-level, more complex API, overkill for our needs
- **react-markdown + react-syntax-highlighter** (CHOSEN): React-native, secure by default, excellent code highlighting, widely used

**Implementation Notes**:
```jsx
// src/components/ChatMessage/MarkdownRenderer.tsx
import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const customTheme = {
  ...vscDarkPlus,
  'pre[class*="language-"]': {
    ...vscDarkPlus['pre[class*="language-"]'],
    background: 'var(--chat-bg-secondary)',
    borderLeft: '3px solid var(--chat-royal-indigo-start)',
    borderRadius: 'var(--chat-border-radius)'
  }
};

export function MarkdownRenderer({ content }) {
  return (
    <ReactMarkdown
      components={{
        code({ node, inline, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || '');
          return !inline && match ? (
            <SyntaxHighlighter
              style={customTheme}
              language={match[1]}
              PreTag="div"
              {...props}
            >
              {String(children).replace(/\n$/, '')}
            </SyntaxHighlighter>
          ) : (
            <code className={className} {...props}>
              {children}
            </code>
          );
        },
        a({ node, children, href, ...props }) {
          // Ensure external links open in new tab
          const isExternal = href?.startsWith('http');
          return (
            <a
              href={href}
              target={isExternal ? '_blank' : undefined}
              rel={isExternal ? 'noopener noreferrer' : undefined}
              {...props}
            >
              {children}
            </a>
          );
        }
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
```

**Performance Considerations**:
- Lazy load MarkdownRenderer only when first assistant message arrives
- Use React.memo to prevent unnecessary re-renders
- Limit syntax highlighter languages to commonly used: python, javascript, bash, yaml

---

## 9. Session Persistence Strategy

**Decision**: sessionStorage for in-session persistence + backend sync for cross-session

**Rationale**: sessionStorage is ideal for single browsing session (cleared on tab close), which matches the user story requirement (persist across page navigation, not indefinitely). For longer persistence (24-hour session window), we sync with backend via session_id. This two-tier approach balances immediate UX (instant state restoration) with data reliability (backend as source of truth). Graceful degradation when storage is unavailable (in-memory fallback).

**Alternatives Considered**:
- **localStorage only**: Persists indefinitely, can cause stale data issues, privacy concerns
- **Backend only**: Every page load requires API call, slow initial render, network dependency
- **sessionStorage + backend sync** (CHOSEN): Fast local reads, backend backup, session-scoped lifecycle

**Implementation Notes**:
```js
// src/utils/sessionStorage.js
const STORAGE_KEY = 'neurobot_chat_session';

export function saveSessionToStorage(sessionData) {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(sessionData));
  } catch (error) {
    console.warn('sessionStorage unavailable:', error);
    // Fallback: keep state in memory only (handled by React state)
  }
}

export function loadSessionFromStorage() {
  try {
    const data = sessionStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : null;
  } catch (error) {
    console.warn('Failed to load session from storage:', error);
    return null;
  }
}

export function clearSessionStorage() {
  try {
    sessionStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.warn('Failed to clear session storage:', error);
  }
}

// Usage in ChatWidget component
useEffect(() => {
  // On mount: restore from sessionStorage
  const localSession = loadSessionFromStorage();
  if (localSession?.sessionId) {
    // Try to restore from backend
    getChatHistory(localSession.sessionId)
      .then(history => {
        dispatch({ type: 'RESTORE_SESSION', payload: history });
      })
      .catch(() => {
        // Backend failed, use local copy
        dispatch({ type: 'RESTORE_SESSION', payload: localSession });
      });
  }
}, []);

// Save to sessionStorage on every state change
useEffect(() => {
  saveSessionToStorage(state);
}, [state]);
```

**Storage Quota Handling**:
- Typical sessionStorage quota: 5-10MB (varies by browser)
- Our data structure: ~100 messages × ~500 bytes = ~50KB (well within limits)
- If quota exceeded: truncate to last 50 messages, show warning to user

---

## 10. Citation Navigation Implementation

**Decision**: Docusaurus useHistory hook for client-side navigation + smooth scroll

**Rationale**: Docusaurus is a SPA with client-side routing. Using the useHistory hook (from @docusaurus/router) performs instant navigation without full page reload, maintaining app state and providing smooth UX. Combined with native scrollIntoView for section anchors, this gives fast, native-feeling navigation. Better than window.location (causes page reload) or manual route manipulation (breaks Docusaurus routing).

**Alternatives Considered**:
- **window.location.href**: Causes full page reload, loses React state, slower UX
- **<a> tag navigation**: Works but requires rendering links, less flexible for programmatic navigation
- **useHistory + scrollIntoView** (CHOSEN): Native Docusaurus pattern, instant navigation, smooth scroll

**Implementation Notes**:
```jsx
// src/components/ChatMessage/CitationBadge.tsx
import React from 'react';
import { useHistory } from '@docusaurus/router';
import styles from './CitationBadge.module.css';

export function CitationBadge({ citation }) {
  const history = useHistory();

  function handleCitationClick() {
    const { module_id, chapter_id, section_id, url } = citation;

    // Validate URL exists (prevent 404 navigation)
    if (!url || url === 'null') {
      console.warn('Citation has invalid URL:', citation);
      return;
    }

    // Navigate using Docusaurus router
    history.push(url);

    // Scroll to section if section_id provided
    if (section_id) {
      // Wait for page to load, then scroll
      setTimeout(() => {
        const element = document.getElementById(section_id);
        if (element) {
          element.scrollIntoView({
            behavior: 'smooth',
            block: 'start',
            inline: 'nearest'
          });
        }
      }, 100);
    }

    // Minimize chat widget after navigation
    dispatch({ type: 'TOGGLE_WIDGET' }); // Close widget
  }

  return (
    <button
      className={styles.citationBadge}
      onClick={handleCitationClick}
      aria-label={`Navigate to ${citation.section_title}`}
    >
      <span className={styles.icon}>📖</span>
      {citation.module_id}, {citation.chapter_id}: {citation.section_title}
    </button>
  );
}
```

**Edge Cases**:
- Citation URL validation: Check URL exists before navigation (prevent 404s)
- External citations: Use window.open for non-book URLs (external resources)
- Section not found: Scroll to top of page if section_id element doesn't exist
- Mobile: Ensure scroll positioning accounts for fixed headers (offset scroll)

---

## 11. Accessibility (WCAG 2.1 Level AA)

**Decision**: Comprehensive keyboard navigation + ARIA attributes + focus management

**Rationale**: Accessibility is a constitution requirement (Principle IV). WCAG 2.1 Level AA compliance ensures the chat widget is usable by students with disabilities, including those using screen readers or keyboard-only navigation. Proper ARIA attributes communicate widget state to assistive technologies. Focus management ensures logical tab order and keyboard shortcuts (Enter, Esc, Tab) work intuitively.

**Implementation Checklist**:

1. **Keyboard Navigation**:
   - Tab: Navigate through chat widget elements (input → send button → messages → close button)
   - Enter: Send message when input is focused
   - Escape: Close chat widget
   - Ctrl+Q / Cmd+Q: Open chat with selected text

2. **ARIA Attributes**:
   ```jsx
   <div
     role="dialog"
     aria-labelledby="chat-header"
     aria-describedby="chat-description"
     aria-modal="true"
   >
     <h2 id="chat-header">NeuroBot Assistant</h2>
     <div id="chat-description" className="sr-only">
       AI-powered chatbot for textbook questions and selected text queries
     </div>

     <div role="log" aria-live="polite" aria-atomic="false">
       {/* Messages appear here, announced by screen readers */}
     </div>

     <input
       type="text"
       aria-label="Type your question"
       aria-required="true"
     />

     <button aria-label="Send message" disabled={isLoading}>
       <SendIcon />
     </button>
   </div>
   ```

3. **Focus Management**:
   ```js
   useEffect(() => {
     if (isOpen) {
       // Focus input when widget opens
       inputRef.current?.focus();
     }
   }, [isOpen]);

   function handleClose() {
     dispatch({ type: 'TOGGLE_WIDGET' });
     // Return focus to chat icon button
     chatIconButtonRef.current?.focus();
   }
   ```

4. **Color Contrast**:
   - Royal indigo gradient on white text: Ensure ≥4.5:1 contrast ratio
   - Dark charcoal background (#0d1117) on white text: ~15:1 ratio ✅
   - Error messages: Dark red background with white text: ~7:1 ratio ✅
   - Test with WebAIM Contrast Checker

5. **Screen Reader Announcements**:
   ```jsx
   <div role="status" aria-live="polite" className="sr-only">
     {isLoading && "Sending message, please wait..."}
     {error && `Error: ${error}`}
   </div>
   ```

**Testing Tools**:
- axe DevTools browser extension (automated accessibility testing)
- NVDA / JAWS screen readers (manual testing)
- Keyboard-only navigation test (disconnect mouse)
- Lighthouse accessibility audit (target score: 100)

---

## 12. Mobile Responsive Design

**Decision**: Adaptive layout with breakpoints: full-screen on mobile (<768px), resized on tablet/desktop

**Rationale**: Mobile screens (<768px) are too small for a 400×600px floating widget. A full-screen modal provides better UX on mobile, maximizing available space for conversation while keeping the input area accessible above the virtual keyboard. On tablets and desktops, the floating widget provides non-intrusive access without blocking content. CSS media queries handle responsive transitions smoothly.

**Breakpoints**:
- **Mobile (<768px)**: Full-screen modal, 16px margins, bottom-aligned for keyboard avoidance
- **Tablet (768-1024px)**: Smaller widget (350×550px), bottom-right positioned
- **Desktop (>1024px)**: Full widget (400×600px), bottom-right positioned

**Implementation Notes**:
```css
/* ChatWidget.module.css */
.chatWidget {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 400px;
  height: 600px;
  transition: all var(--chat-transition);
  z-index: 9999;
}

/* Tablet */
@media (max-width: 1024px) {
  .chatWidget {
    width: 350px;
    height: 550px;
  }
}

/* Mobile */
@media (max-width: 768px) {
  .chatWidget {
    width: calc(100vw - 32px);
    height: calc(100vh - 100px);
    bottom: 16px;
    right: 16px;
    left: 16px;
  }

  .chatIcon {
    bottom: 16px;
    right: 16px;
  }

  .citationBadges {
    flex-direction: column; /* Stack vertically on mobile */
    gap: 8px;
  }
}

/* Handle virtual keyboard on mobile */
@media (max-width: 768px) {
  .chatWidget.keyboardOpen {
    height: calc(50vh); /* Shrink when keyboard appears */
  }
}
```

**Virtual Keyboard Handling**:
```js
// Detect virtual keyboard on mobile
useEffect(() => {
  if (typeof window === 'undefined') return;

  const handleResize = () => {
    if (window.innerHeight < window.screen.height * 0.7) {
      // Keyboard likely open
      setKeyboardOpen(true);
    } else {
      setKeyboardOpen(false);
    }
  };

  window.addEventListener('resize', handleResize);
  return () => window.removeEventListener('resize', handleResize);
}, []);
```

**Touch Interactions**:
- Increase tap targets to minimum 44×44px (WCAG guideline)
- Add touch feedback (scale animation on press)
- Support swipe-down gesture to close chat on mobile
- Prevent scroll-behind when chat is open (body scroll lock)

---

## Summary of Technical Decisions

| Decision Area | Choice | Rationale | Bundle Impact |
|--------------|--------|-----------|---------------|
| Chat UI | Custom React components | Full control, theme integration, smaller bundle | +50KB |
| SSR Safety | BrowserOnly + React.lazy | Native Docusaurus pattern, prevents build errors | 0KB |
| State Management | Context + useReducer | Built-in, sufficient complexity, predictable | 0KB |
| Styling | CSS Modules + CSS Variables | Scoped, theme-responsive, zero runtime cost | +5KB |
| Bundle Strategy | React.lazy + code splitting | Deferred loading, optimal performance | 0KB (deferred) |
| Text Selection | Selection API + floating button | Native API, discoverable UX | +3KB |
| API Integration | fetch + AbortController | Native, zero dependencies, custom retry logic | 0KB |
| Markdown | react-markdown + syntax highlighter | Secure, React-native, code highlighting | +35KB |
| Persistence | sessionStorage + backend sync | Fast local, backend backup, session-scoped | 0KB |
| Navigation | useHistory + scrollIntoView | Native Docusaurus, instant routing | 0KB |
| Accessibility | Full WCAG 2.1 AA compliance | Constitution requirement, inclusive | +2KB |
| Responsive | Adaptive layout with breakpoints | Optimal UX per device type | +3KB |

**Total Estimated Bundle Size**: ~98KB (gzipped), within 150KB target ✅

---

**Phase 0 Status**: ✅ COMPLETE
**Next Phase**: Phase 1 - Design data model and component contracts
