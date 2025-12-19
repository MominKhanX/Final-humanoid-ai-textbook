# Feature Specification: RAG Chatbot Frontend Integration

**Feature Branch**: `003-chatbot-frontend`
**Created**: 2025-12-16
**Status**: Draft
**Input**: User description: "Interactive Chat Widget with Royal Indigo Academic Theme"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Floating Chat Widget Access (Priority: P1)

A student is reading Module 2, Chapter 3 about URDF robot modeling. They have a quick question about a specific XML attribute but don't want to lose their place in the chapter. They click a floating chat icon in the bottom-right corner. A chat widget smoothly expands upward, styled with the royal indigo theme matching the rest of the site. They type their question, hit send, and receive an answer with a citation linking back to the relevant chapter section. They can minimize the chat and continue reading without interruption.

**Why this priority**: This is the absolute MVP - providing basic chat access without disrupting the reading experience. Without a functional, accessible chat widget, there is no frontend integration at all. This represents the minimum viable UI that enables students to interact with the RAG backend.

**Independent Test**: Can be fully tested by rendering a collapsible chat widget on a single page, connecting to the backend `/chat` endpoint, and verifying that a message can be sent and a response displayed. Delivers immediate value as a standalone Q&A interface that can be demonstrated and tested without any other features.

**Acceptance Scenarios**:

1. **Given** a student is on any textbook page, **When** they click the floating chat icon, **Then** the chat widget expands smoothly with a royal indigo gradient header and dark background matching the site theme
2. **Given** the chat widget is open, **When** the student types "What is a ROS 2 node?" and clicks send, **Then** the message appears in the chat history, a loading indicator shows, and a response from the backend appears within 3 seconds with proper styling
3. **Given** the chat widget is expanded, **When** the student clicks the minimize button, **Then** the widget collapses smoothly to just the floating icon, preserving the conversation in memory
4. **Given** the student navigates to a different chapter, **When** they reopen the chat widget, **Then** the previous conversation history is still visible (persisted in browser session)
5. **Given** the chat widget is open on mobile, **When** the screen width is less than 768px, **Then** the widget expands to full width for better readability

---

### User Story 2 - Selected Text Query Mode (Priority: P2)

A student is reading a complex code example in Module 3, Chapter 4 about Isaac Gym training. They highlight a specific function call: `env.step(action)`. They right-click or use a context menu to select "Ask about this", which opens the chat widget automatically and pre-populates the context: "Explain this code: `env.step(action)`". They add "What does it return?" and hit send. The chatbot provides a detailed explanation specifically about that function in the context of the surrounding code, citing the exact section.

**Why this priority**: This is the key differentiator mentioned in the constitution - "Selected text queries (highlight → ask)". It transforms the chat from a generic Q&A tool into a context-aware learning companion. This significantly enhances learning by allowing precise questioning about confusing passages without needing to retype or copy-paste content.

**Independent Test**: Can be tested independently by implementing text selection detection, opening the chat widget with pre-filled context, and calling the `/chat/selected` backend endpoint with both the selected text and the user's question. Demonstrates advanced context-awareness without requiring the basic chat (P1) to work perfectly first.

**Acceptance Scenarios**:

1. **Given** a student has highlighted text on the page, **When** they click "Ask about selection" button or use keyboard shortcut (Ctrl+Q), **Then** the chat widget opens with the selected text shown as context in a quoted block styled with royal indigo left border
2. **Given** selected text mode is active, **When** the student types a follow-up question and sends it, **Then** both the selected text and question are sent to the backend `/chat/selected` endpoint, and the response specifically addresses the selected content
3. **Given** a code block is selected, **When** the student asks about it, **Then** the selection preserves syntax highlighting and formatting in the chat context display
4. **Given** very long text is selected (>500 words), **When** the chat opens, **Then** the system shows a truncated preview with "... (truncated)" and sends the full text to the backend for processing
5. **Given** the selected text mode is active, **When** the student clears the selection or asks a new general question, **Then** the chat mode switches back to general Q&A mode

---

### User Story 3 - Source Citations with Navigation (Priority: P3)

A student asks "How do I set up a Gazebo simulation with ROS 2?" The chatbot responds with an answer and displays two source citations as royal indigo badges: "Module 2, Chapter 1: Gazebo Setup" and "Module 2, Chapter 2: ROS 2-Gazebo Bridge". The student hovers over the first badge, which scales slightly and highlights. They click it, and the page smoothly navigates to Module 2, Chapter 1, scrolling to the relevant section that was cited. The chat widget minimizes automatically but remains accessible for follow-up questions.

**Why this priority**: Citations are a constitution requirement ("Source citation (chapter/section references)") and enhance trust and learning by showing exactly where information comes from. Clickable navigation makes citations actionable rather than decorative. This is essential for academic integrity but works independently of the core chat functionality.

**Independent Test**: Can be tested by mocking backend responses that include citation metadata (module, chapter, section), rendering citation badges with royal indigo styling and hover effects, and implementing click handlers that navigate to the cited page. Demonstrates citation UI and navigation logic separately from the actual chat conversation flow.

**Acceptance Scenarios**:

1. **Given** a chatbot response includes source citations, **When** the response is displayed, **Then** citations appear as styled badges below the message with royal indigo backgrounds, rounded corners, and chapter icons
2. **Given** a citation badge is displayed, **When** the student hovers over it, **Then** the badge scales to 1.05x and shows a subtle glow effect with 0.3s transition (royal indigo theme consistency)
3. **Given** a citation badge shows "Module 2, Chapter 3", **When** the student clicks it, **Then** the browser navigates to `/docs/module-2-digital-twin/chapter-3` and scrolls to the cited section if section ID is provided
4. **Given** multiple citations are present, **When** displayed, **Then** they are arranged horizontally with proper spacing (8px gap) and wrap on smaller screens
5. **Given** a citation link is clicked, **When** navigation occurs, **Then** the chat widget minimizes automatically to avoid blocking the content, but retains the conversation for later access

---

### User Story 4 - Loading States and Error Handling (Priority: P4)

A student asks a complex question that takes 2-3 seconds to process. While waiting, they see an elegant typing indicator animation (three royal indigo dots pulsing) in the chat. If the backend is temporarily unavailable, they see a styled error message: "Unable to connect to the knowledge base. Please try again in a moment." with a retry button. If the request takes longer than 10 seconds, they see a timeout message with options to retry or rephrase their question.

**Why this priority**: Professional UI polish and robust error handling are essential for user trust and production quality, but the core chat functionality works without perfect loading states. This ensures a premium user experience but can be refined iteratively. Critical for meeting constitution's "support concurrent users" requirement gracefully.

**Independent Test**: Can be tested by simulating backend delays (setTimeout), network failures (disconnect), and timeouts (reject after 10s), then verifying that appropriate loading indicators and error messages display with proper styling. Demonstrates error handling UX independently from happy-path chat flows.

**Acceptance Scenarios**:

1. **Given** a student sends a message, **When** the backend is processing (response not yet received), **Then** a typing indicator with three pulsing royal indigo dots appears in the chat window with smooth fade-in animation
2. **Given** the backend returns a 500 error, **When** the error occurs, **Then** a styled error message appears with a dark red background, explaining the issue and offering a "Retry" button that resends the request
3. **Given** a request takes longer than 10 seconds, **When** the timeout threshold is reached, **Then** the loading indicator disappears and a warning message appears: "This is taking longer than expected. Still waiting..." with options to cancel or continue waiting
4. **Given** network connectivity is lost, **When** a student tries to send a message, **Then** an error message appears: "No internet connection. Please check your network and try again." and the send button is disabled until connection is restored
5. **Given** an error occurs, **When** the student clicks "Retry", **Then** the error message clears, the loading indicator reappears, and the request is resent with exponential backoff (max 3 retries)

---

### User Story 5 - Chat History Persistence (Priority: P5)

A student has a 10-message conversation with the chatbot about ROS 2 topics and services. They close the chat widget and navigate to a different chapter. Later, they reopen the chat and see their entire conversation history still visible, with messages properly formatted and citations intact. They can scroll through past messages to review previous answers. If they close the browser and return the next day, they can optionally load previous sessions from the backend (if session is still active).

**Why this priority**: Conversation persistence enhances UX and supports the constitution's "context-aware follow-up questions" requirement by maintaining state across interactions. However, the chat can function in a stateless mode for MVP. This is a quality-of-life feature that can be added after core functionality is proven.

**Independent Test**: Can be tested by sending multiple messages, closing/reopening the widget, navigating between pages, and verifying conversation state is maintained in browser sessionStorage/localStorage. Backend session retrieval can be tested separately via the `/chat/history` endpoint. Demonstrates state management independently from real-time chat interactions.

**Acceptance Scenarios**:

1. **Given** a student has an active chat conversation, **When** they minimize the widget and navigate to another chapter, **Then** the conversation history is preserved in browser sessionStorage and reloads when the widget reopens
2. **Given** the student has sent 5 messages, **When** they scroll up in the chat window, **Then** all previous messages and responses are visible with proper formatting, citations, and timestamps
3. **Given** the backend provides a session ID, **When** the student refreshes the page, **Then** the frontend sends the session ID to `/chat/history` endpoint and restores the full conversation from the database
4. **Given** the student closes the browser and returns 30 minutes later, **When** they reopen the chat, **Then** the session is still active and history is loaded from the backend (within 24-hour session expiry window)
5. **Given** a session has expired, **When** the student tries to load history, **Then** a message appears: "Previous session expired. Starting fresh conversation." and the chat begins a new session

---

### Edge Cases

- **What happens when the page is navigated during an active chat request?** The request is allowed to complete, but if the user navigates away before the response arrives, it is stored in sessionStorage and displayed when the chat widget is reopened on the new page.

- **What happens when selected text exceeds 5000 characters?** The frontend truncates the text intelligently (preserve first 2000 and last 500 characters, add "... [truncated] ..." in middle) and displays a warning: "Selected text was very long and has been shortened. Focus on the highlighted portions."

- **What happens when the user spams the send button rapidly?** Frontend implements client-side rate limiting (max 1 request per 2 seconds) and disables the send button while a request is in progress. If user tries to send too quickly, show a toast: "Please wait for the current response before sending another message."

- **What happens during SSR/build time when the widget tries to access browser APIs?** The component is wrapped in `BrowserOnly` from Docusaurus, preventing any execution during static generation. The widget only renders client-side after hydration is complete.

- **What happens when chat history exceeds maximum display limit (e.g., 100 messages)?** The frontend implements virtual scrolling or pagination, showing the most recent 50 messages and loading older ones on scroll-up with a "Load more" button. Very old messages (>100) are archived and accessible via "View full history" link to a dedicated page.

- **What happens when the backend returns a malformed response (invalid JSON)?** The frontend catches parsing errors and displays: "Received an invalid response. Please try again." and logs the error for debugging. The conversation state is preserved and the user can retry.

- **What happens on slow 3G connections where responses take 8-10 seconds?** The loading indicator continues to show with a progress message: "Searching textbook... this may take a moment on slow connections." The timeout threshold is increased to 15 seconds on detected slow connections.

- **What happens when dark/light mode is toggled while chat is open?** The chat widget's theme (background colors, text colors, borders) updates immediately using CSS variables that respond to `[data-theme]` attribute changes. The transition is smooth (0.3s ease) without jarring flashes.

- **What happens when a citation link points to a chapter that doesn't exist (404)?** The frontend validates citation URLs before navigation. If a chapter is not found, display an error: "This chapter is not yet available. Citation: [Module X, Chapter Y]" and prevent navigation.

- **What happens when localStorage/sessionStorage is full or disabled?** The frontend gracefully degrades to in-memory state management. A warning appears: "Browser storage unavailable. Chat history will not persist across page refreshes." The chat still functions for the current page session.

## Requirements *(mandatory)*

### Functional Requirements

#### Widget UI & Interaction

- **FR-001**: System MUST display a floating chat icon in the bottom-right corner of all textbook pages (20px from bottom, 20px from right)
- **FR-002**: Chat icon MUST be styled with royal indigo gradient background, 56px diameter circle, white chat bubble icon, and drop shadow
- **FR-003**: System MUST expand chat widget smoothly when icon is clicked (slide-up animation, 0.3s ease transition, expand to 400px width × 600px height on desktop)
- **FR-004**: Chat widget MUST include a header with royal indigo gradient background displaying "NeuroBot Assistant" title in Georgia serif font (18px, white, bold)
- **FR-005**: Header MUST include minimize/close buttons (white icons, hover scale 1.1×, 0.3s transition)
- **FR-006**: Chat widget MUST include a message display area with dark charcoal background, custom scrollbar styled in royal indigo, and padding (16px)
- **FR-007**: Chat widget MUST include an input area with dark background, text input field (white text on dark), and send button (royal indigo gradient)
- **FR-008**: Send button MUST show paper plane icon, scale to 1.05× on hover, and disable while request is in progress

#### Message Display & Styling

- **FR-009**: User messages MUST display right-aligned with dark background, white text, rounded corners (8px), and max-width 80%
- **FR-010**: Assistant messages MUST display left-aligned with tertiary dark background, 3px royal indigo left border, rounded corners (8px), max-width 80%
- **FR-011**: All messages MUST include timestamp in small gray text (12px) below the content
- **FR-012**: Messages MUST support markdown rendering for code blocks, bold, italic, lists, and links while preserving royal indigo theme
- **FR-013**: Code blocks within messages MUST preserve syntax highlighting with dark background and royal indigo accent borders

#### Loading States & Animations

- **FR-014**: System MUST display typing indicator (three dots, royal indigo color, pulsing animation 1.5s infinite) while waiting for backend response
- **FR-015**: Typing indicator MUST appear in the assistant message area (left-aligned) immediately when a request is sent
- **FR-016**: All animations (slide-up, scale, pulse) MUST use 0.3s ease transitions for consistency with royal indigo theme
- **FR-017**: Send button MUST show loading spinner (royal indigo color) and disable while request is in-progress
- **FR-018**: Transition between empty chat state and first message MUST be smooth with fade-in animation

#### Source Citations

- **FR-019**: Citations MUST render as styled badges below assistant messages with royal indigo background, white text, rounded corners (16px), padding (6px 12px)
- **FR-020**: Citation badges MUST include chapter icon (book emoji or SVG) and display format: "Module X, Chapter Y: Section Title"
- **FR-021**: Citation badges MUST scale to 1.05× on hover with smooth transition (0.3s ease) and show subtle glow effect
- **FR-022**: Clicking a citation badge MUST navigate to the corresponding chapter URL and scroll to the section if section ID is provided
- **FR-023**: Multiple citations MUST be displayed horizontally with 8px gap between badges and wrap to new line on smaller screens

#### Selected Text Mode

- **FR-024**: System MUST provide a button/keyboard shortcut (Ctrl+Q or Cmd+Q) to activate "Ask about selection" mode when text is highlighted
- **FR-025**: When selected text mode is triggered, chat widget MUST open automatically if closed and display selected text in a quoted block with royal indigo left border (4px solid)
- **FR-026**: Selected text context MUST be clearly distinguished from user question with different background and "Selected text:" label
- **FR-027**: System MUST send both selected text and user question to backend `/chat/selected` endpoint in structured format
- **FR-028**: If selected text exceeds 5000 characters, system MUST truncate intelligently and show warning message
- **FR-029**: Selected text mode MUST be clearable - user can click an "X" icon to remove selection and return to general Q&A mode

#### Error Handling & Resilience

- **FR-030**: System MUST display error messages in styled error containers with dark red background, white text, rounded corners (8px), and error icon
- **FR-031**: Network errors (fetch failures, timeouts) MUST show message: "Unable to connect. Please check your internet connection." with "Retry" button
- **FR-032**: Backend errors (500, 503) MUST show message: "Something went wrong. Our team has been notified. Please try again." with "Retry" button
- **FR-033**: Rate limit errors (429) MUST show message: "You're asking questions too quickly. Please wait a moment before trying again."
- **FR-034**: Request timeouts (>10 seconds) MUST show warning: "This is taking longer than expected..." with options to "Keep waiting" or "Cancel"
- **FR-035**: Retry buttons MUST implement exponential backoff (retry after 2s, 4s, 8s) with maximum 3 retry attempts
- **FR-036**: All errors MUST be logged to browser console with structured format (timestamp, error type, request details) for debugging

#### State Management & Persistence

- **FR-037**: System MUST persist conversation history in browser sessionStorage with key format: `neurobot_chat_session_{session_id}`
- **FR-038**: Session data MUST include: session_id, messages array (question, answer, timestamp, citations), created_at timestamp
- **FR-039**: When chat widget is reopened, system MUST restore conversation from sessionStorage if available
- **FR-040**: When backend provides session ID in response, system MUST store it and include in all subsequent requests
- **FR-041**: On page refresh, system MUST attempt to load conversation history from backend using stored session ID via GET `/chat/history` endpoint
- **FR-042**: If sessionStorage is unavailable (disabled or full), system MUST gracefully degrade to in-memory state and show warning to user

#### Responsive Design

- **FR-043**: On screens <768px (mobile), chat widget MUST expand to full width (calc(100vw - 32px)) and height (calc(100vh - 100px)) for better usability
- **FR-044**: On mobile, chat icon MUST be positioned 16px from bottom and right (smaller margins)
- **FR-045**: On tablets (768px-1024px), chat widget MUST use 350px width × 550px height
- **FR-046**: Font sizes MUST scale appropriately: desktop (16px base), tablet (15px), mobile (14px) for readability
- **FR-047**: Citation badges MUST stack vertically on mobile (<480px) instead of horizontal layout

#### SSR/Build Safety

- **FR-048**: Chat widget component MUST be wrapped in Docusaurus `BrowserOnly` component to prevent execution during static site generation
- **FR-049**: System MUST NOT access browser APIs (window, document, localStorage) until component is mounted client-side
- **FR-050**: Build process MUST complete successfully without errors related to chat widget (no "window is not defined" errors)
- **FR-051**: Initial page load MUST show chat icon placeholder (empty div with proper dimensions) until client-side hydration completes

#### Performance & Optimization

- **FR-052**: Chat widget JavaScript bundle MUST be lazy-loaded (dynamic import) to avoid blocking initial page render
- **FR-053**: Message rendering MUST be optimized to handle at least 50 messages without noticeable lag (virtual scrolling for >50 messages recommended)
- **FR-054**: Images in chat messages (if supported) MUST be lazy-loaded and have max dimensions (400px width) to prevent layout shift
- **FR-055**: Client-side rate limiting MUST prevent more than 1 request per 2 seconds per session
- **FR-056**: Frequently accessed state (current session ID, last 10 messages) MUST be cached in memory to avoid repeated sessionStorage reads

#### Integration with Backend

- **FR-057**: System MUST send chat requests to backend endpoint POST `/chat` with payload: `{ "question": string, "session_id": string | null }`
- **FR-058**: System MUST send selected text requests to POST `/chat/selected` with payload: `{ "question": string, "selected_text": string, "session_id": string | null }`
- **FR-059**: System MUST request chat history from GET `/chat/history?session_id={session_id}` on page load if session ID exists
- **FR-060**: System MUST include CORS headers (Origin, Content-Type) in all requests to allow cross-origin communication with deployed backend
- **FR-061**: Backend URL MUST be configurable via environment variable for dev/prod environments
- **FR-062**: Request timeout MUST be set to 15 seconds with AbortController for all fetch requests
- **FR-063**: Response handling MUST validate JSON structure before parsing and show error if response is malformed

### Assumptions

- **Assumption 1**: The backend API endpoints (`/chat`, `/chat/selected`, `/chat/history`) are already implemented and accessible (dependency on feature 002-rag-chatbot-backend)
- **Assumption 2**: Backend responses follow the structure: `{ "answer": string, "sources": [{ "module_id": string, "chapter_id": string, "section_title": string, "url": string }], "session_id": string, "timestamp": ISO8601 }`
- **Assumption 3**: Docusaurus site is already deployed with the royal indigo academic theme as implemented in feature 001-docusaurus-init
- **Assumption 4**: Chapter URLs follow the pattern `/docs/module-{id}-{name}/chapter-{id}` for citation navigation
- **Assumption 5**: Users have modern browsers (Chrome/Firefox/Safari latest 2 versions) with JavaScript enabled
- **Assumption 6**: The site supports sessionStorage and localStorage for state persistence (graceful degradation if not available)
- **Assumption 7**: Chat widget will be embedded globally via Docusaurus theme customization (`theme/Root.tsx` or `theme/Layout/index.tsx`)

### Key Entities

- **ChatWidget**: The main UI component containing header, messages, input, and controls
  - Attributes: isOpen (boolean), position (object: x, y), size (object: width, height), theme (royal indigo styles)
  - Relationships: Contains ChatMessageList, ChatInput, ChatHeader

- **ChatMessage**: Represents a single message in the conversation
  - Attributes: id (UUID), role (enum: user/assistant), content (string/markdown), timestamp (ISO8601), citations (array), isLoading (boolean)
  - Relationships: Belongs to ChatSession

- **ChatSession**: Represents the current conversation session
  - Attributes: session_id (UUID), messages (array of ChatMessage), created_at (timestamp), backend_synced (boolean)
  - Relationships: Has many ChatMessages, syncs with backend via session ID

- **Citation**: Represents a source reference in assistant responses
  - Attributes: module_id (string), chapter_id (string), section_title (string), url (string), display_text (string)
  - Relationships: Belongs to ChatMessage (assistant messages only)

- **ChatState**: Manages global chat widget state
  - Attributes: isWidgetOpen (boolean), currentSession (ChatSession), selectedText (string | null), isSelectedMode (boolean), isLoading (boolean), lastError (Error | null)
  - Relationships: Contains one ChatSession, manages UI state across page navigations

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Students can open the chat widget, send a message, and receive a response in under 5 seconds (including backend processing) in 95% of cases
- **SC-002**: Chat widget displays correctly (no layout breaks, proper styling) on desktop (1920×1080), tablet (768×1024), and mobile (375×667) screen sizes
- **SC-003**: Selected text mode successfully captures highlighted content and sends it to the backend in correct format for 100% of test cases
- **SC-004**: Citation badges are clickable and navigate to the correct chapter page in 100% of cases where valid URLs are provided
- **SC-005**: Chat conversation history persists across page navigations within a single browser session in 100% of cases when sessionStorage is available
- **SC-006**: Docusaurus build completes successfully with zero SSR-related errors (no "window is not defined" or hydration mismatches)
- **SC-007**: Chat widget JavaScript bundle size is under 150KB (gzipped) to ensure fast loading on slower connections
- **SC-008**: Error messages display clearly and provide actionable guidance for 100% of error scenarios (network, timeout, backend failure, rate limit)
- **SC-009**: Chat widget matches royal indigo academic theme in 100% of visual elements (colors, typography, spacing, borders, hover effects) as verified by design review
- **SC-010**: Widget animations (expand/collapse, hover effects, loading indicators) run smoothly at 60fps without jank on devices with moderate specs

### User Experience Metrics

- **UX-001**: Students can initiate a chat conversation without needing instructions or documentation (self-service success rate >90%)
- **UX-002**: Chat interface feels responsive and professional - no janky animations, instant feedback on interactions, smooth transitions
- **UX-003**: Error messages are understandable by non-technical students and provide clear next steps (e.g., "Retry", "Check connection")
- **UX-004**: Chat widget does not obstruct important page content - positioned thoughtfully, easy to minimize, and respects user's reading space

### Technical Quality Metrics

- **TQ-001**: Component code follows best practices (hooks, functional components, proper prop types, no memory leaks)
- **TQ-002**: All user interactions (button clicks, input typing, navigation) are accessible via keyboard (tab navigation, Enter to send, Esc to close)
- **TQ-003**: Chat widget passes WCAG 2.1 Level AA accessibility standards (color contrast, screen reader support, keyboard navigation)
- **TQ-004**: Browser console shows zero errors or warnings during normal chat usage (messages sent, responses received, widget opened/closed)
- **TQ-005**: State management is predictable and debuggable - chat state can be inspected and sessionStorage

### Constitution Alignment

- **CA-001**: Meets "AI-Native Architecture" principle - chat widget is seamlessly integrated and context-aware (constitution Section II)
- **CA-002**: Meets "RAG Chatbot Integration" requirement (constitution Section II)
- **CA-003**: Meets "Selected text queries" feature requirement (constitution Section II, User Story 2)
- **CA-004**: Meets "Source citations" requirement with clickable chapter references (constitution Section II, User Story 3)
- **CA-005**: Meets "Responsive Design" requirement - works on desktop/tablet/mobile (constitution Section IV)
- **CA-006**: Meets "<5 seconds loading time" performance requirement - lazy-loaded widget doesn't block page render (constitution Section IV)
- **CA-007**: Meets "Dark/Light Mode" support - chat widget adapts to theme via CSS variables (constitution Section IV)
- **CA-008**: Meets "Browser Compatibility" requirement - tested on Chrome, Firefox, Safari (constitution Section IV)
