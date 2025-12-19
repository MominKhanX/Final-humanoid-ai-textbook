# Feature Specification: RAG Chatbot Backend

**Feature Branch**: `002-rag-chatbot-backend`
**Created**: 2025-12-16
**Status**: Draft
**Input**: User description: "Intelligent Q&A System Backend"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - General Textbook Q&A (Priority: P1)

A student reading Module 2, Chapter 3 about URDF robot descriptions has a question: "What's the difference between a link and a joint in URDF?" They click the chatbot icon, type their question, and receive an AI-generated answer citing the specific section from Chapter 3 where this is explained, along with a code example from the textbook.

**Why this priority**: This is the core value proposition of the RAG chatbot - helping students understand textbook content without leaving the page. Without this, there's no chatbot feature at all. This represents the absolute MVP.

**Independent Test**: Can be fully tested by deploying a FastAPI endpoint (`POST /chat`) connected to Qdrant with indexed textbook content. Student submits a question, receives contextual answer with citation. Delivers immediate value as a standalone Q&A feature.

**Acceptance Scenarios**:

1. **Given** a student is reading the textbook, **When** they submit "What is a ROS 2 node?", **Then** the system returns an answer citing Module 1, Chapter 1 with relevant textbook content
2. **Given** the chatbot has indexed all 23 chapters, **When** a student asks about "NVIDIA Isaac Sim physics engine", **Then** the system retrieves relevant content from Module 3 and responds within 3 seconds
3. **Given** a student asks an unclear question like "How do I build a robot?", **When** the system processes it, **Then** it returns a focused answer based on the most relevant chapters and asks clarifying questions if needed
4. **Given** a student asks a question outside the textbook scope (e.g., "What's the weather?"), **When** the system processes it, **Then** it politely indicates the question is outside the course material and suggests relevant topics
5. **Given** multiple students are using the chatbot concurrently, **When** they submit questions simultaneously, **Then** all receive responses within 3 seconds without degradation

---

### User Story 2 - Selected Text Queries (Priority: P2)

A student is reading a complex code snippet in Module 3, Chapter 2 about Isaac Gym reinforcement learning. They select a specific line of code: `env.reset()`, click "Ask about selection", and type "Why do we call this here?" The chatbot provides a contextual explanation specifically about that code line within the broader context of the RL training loop.

**Why this priority**: This is a key differentiator from basic chatbots. It enables precise, context-aware questioning about specific passages or code snippets. Enhances learning by allowing students to drill into exact points of confusion. Critical for constitution requirement: "Selected text queries (highlight → ask)".

**Independent Test**: Can be tested by implementing `POST /chat/selected` endpoint that accepts both a question and selected text context. System returns an answer focused specifically on the selected content. Demonstrates advanced context-awareness independently from general Q&A.

**Acceptance Scenarios**:

1. **Given** a student selects the code `publisher = self.create_publisher(String, 'topic', 10)`, **When** they ask "What does the 10 mean?", **Then** the system explains the QoS queue size parameter with reference to the surrounding ROS 2 publisher example
2. **Given** a student highlights a paragraph about "sim-to-real transfer", **When** they ask "Give me an example of this", **Then** the system provides a concrete example from the textbook or related chapter content
3. **Given** a student selects a diagram caption, **When** they ask to explain the diagram in detail, **Then** the system provides a comprehensive explanation referencing the visual and surrounding text
4. **Given** no text is selected, **When** a student uses the selected text endpoint, **Then** the system gracefully handles it by treating it as a general question or prompting for selection

---

### User Story 3 - Conversation History & Context Tracking (Priority: P3)

A student asks "What is ROS 2?" and receives an answer. They follow up with "How does it compare to ROS 1?" without re-stating context. The chatbot understands this is a continuation, retrieves the previous exchange from the database, and provides a comparative answer. Later, the student returns to the textbook and clicks "View history" to see all past conversations organized by date.

**Why this priority**: Enables natural, multi-turn conversations and lets students review their learning journey. Enhances UX significantly but the core Q&A works without it. Supports the constitution requirement for "context-aware follow-up questions" and proper user session management.

**Independent Test**: Can be tested independently by implementing `GET /chat/history` endpoint and session tracking in Neon Postgres. Student makes multiple queries, retrieves history, and verifies conversation continuity. Demonstrates data persistence and context management separately from Q&A logic.

**Acceptance Scenarios**:

1. **Given** a student has asked 5 questions in a session, **When** they ask a follow-up like "Can you explain that in simpler terms?", **Then** the system uses the previous answer as context and simplifies the explanation
2. **Given** a student starts a new browser session, **When** they access the chatbot, **Then** they see their previous conversation history loaded from the database
3. **Given** a student has conversations across multiple days, **When** they view history, **Then** conversations are organized chronologically with timestamps and chapter context
4. **Given** a student wants to clear their history, **When** they trigger the clear action, **Then** all conversation data is removed from their session (pending privacy implementation)
5. **Given** database connection fails, **When** a student asks a question, **Then** the system provides an answer without history context and logs the error gracefully

---

### User Story 4 - Multi-Chapter Cross-Referencing (Priority: P4)

A student asks "How do I integrate ROS 2 with Unity for visualization?" This requires knowledge from Module 1 (ROS 2 basics) and Module 2 (Unity integration). The chatbot retrieves relevant content from both modules, synthesizes an answer that references Chapter 4 of Module 1 and Chapter 3 of Module 2, and provides a coherent integration workflow.

**Why this priority**: Demonstrates advanced RAG capabilities and educational value by connecting concepts across modules. Not essential for MVP but significantly enhances learning outcomes by showing how modules interconnect. Aligns with constitution's "progressive learning curve" and "theory-practice bridge".

**Independent Test**: Can be tested by crafting questions that span multiple modules and verifying the system retrieves and cites content from all relevant chapters. Demonstrates semantic search quality and synthesis capabilities independently from basic Q&A.

**Acceptance Scenarios**:

1. **Given** a student asks about end-to-end workflow (e.g., "Build a robot in sim, train with RL, deploy to hardware"), **When** the system processes it, **Then** it references all 4 modules in logical sequence with specific chapter citations
2. **Given** a student is in Module 3, **When** they ask a question requiring Module 1 fundamentals, **Then** the system provides foundational context from Module 1 before addressing the Module 3 content
3. **Given** contradictory or duplicate information exists across chapters, **When** the system retrieves it, **Then** it prioritizes the most recent or contextually relevant content and notes any important distinctions

---

### Edge Cases

- **What happens when Qdrant is temporarily unavailable?** System returns a graceful error message: "Vector search is temporarily unavailable. Please try again shortly." and logs the incident for monitoring.
- **What happens when OpenAI API rate limit is hit?** System queues the request with exponential backoff (max 3 retries) and informs user: "High traffic detected. Your response may take a few extra seconds."
- **What happens when a question is asked before all chapters are indexed?** System returns answers based on currently indexed content and displays: "Note: Full textbook indexing in progress (X/23 chapters indexed)."
- **What happens when textbook content is updated/corrected?** System must re-index affected chapters. Implement version tracking to detect content changes and trigger re-indexing automatically.
- **What happens when database connection to Neon Postgres fails?** Chatbot operates in stateless mode (no history) and provides a warning: "History temporarily unavailable." Core Q&A continues to function.
- **What happens when selected text exceeds token limits?** System truncates selected text intelligently (preserve beginning and end, summarize middle) and informs user: "Selected text was long; focusing on key sections."
- **What happens when a student rapidly submits multiple questions (spam/abuse)?** Implement rate limiting (e.g., 10 requests per minute per session) and return 429 status with retry-after header.
- **What happens when chat history exceeds storage limits?** Implement automatic archival (move conversations >30 days old to cold storage) or set retention policy (warn users before deletion).

## Requirements *(mandatory)*

### Functional Requirements

#### Core Chat Functionality

- **FR-001**: System MUST provide a `POST /chat` endpoint that accepts a user question and returns an AI-generated answer based on textbook content
- **FR-002**: System MUST provide a `POST /chat/selected` endpoint that accepts both a question and selected text snippet, returning context-aware answers
- **FR-003**: System MUST provide a `GET /chat/history` endpoint that retrieves conversation history for the current user session
- **FR-004**: System MUST respond to typical queries within 3 seconds (95th percentile latency) as per constitution requirement
- **FR-005**: System MUST include source citations in every answer, specifying module, chapter, and section where information was found

#### Vector Search & RAG

- **FR-006**: System MUST index all 23 chapters of textbook content in Qdrant Cloud vector database upon deployment
- **FR-007**: System MUST use OpenAI embedding models (text-embedding-3-small or text-embedding-3-large) to generate embeddings for textbook content
- **FR-008**: System MUST perform semantic search against Qdrant to retrieve top-k most relevant text chunks (k=5 recommended) for each user query
- **FR-009**: System MUST chunk textbook content intelligently (target 500-1000 tokens per chunk, preserving code blocks and paragraphs)
- **FR-010**: System MUST store metadata with each vector embedding including: chapter_id, module_id, section_title, content_type (text/code/diagram), page_number

#### LLM Integration

- **FR-011**: System MUST use OpenAI GPT-4 (gpt-4-turbo-preview or gpt-4) for generating responses based on retrieved context
- **FR-012**: System MUST construct prompts that include: user question, retrieved textbook chunks, conversation history (if available), and instruction to cite sources
- **FR-013**: System MUST handle context window limits by prioritizing most recent conversation turns and most relevant retrieved chunks
- **FR-014**: System MUST detect when questions are outside textbook scope and politely redirect users to course-relevant topics

#### Database & Persistence

- **FR-015**: System MUST use Neon Serverless Postgres to store user chat history with schema: session_id, user_id (optional), timestamp, question, answer, cited_sources
- **FR-016**: System MUST implement session management using secure session tokens (UUID) stored in cookies or headers
- **FR-017**: System MUST persist conversation context to enable multi-turn dialogues where follow-up questions reference previous exchanges
- **FR-018**: System MUST support session expiration (default: 24 hours of inactivity) and automatic cleanup of expired sessions

#### API Design & Error Handling

- **FR-019**: System MUST return structured JSON responses with format: `{ "answer": string, "sources": array, "timestamp": ISO8601, "session_id": string }`
- **FR-020**: System MUST implement proper HTTP status codes: 200 (success), 400 (bad request), 429 (rate limit), 500 (server error), 503 (service unavailable)
- **FR-021**: System MUST validate input requests: question length (max 1000 chars), selected text length (max 5000 chars), proper encoding
- **FR-022**: System MUST implement rate limiting: 10 requests per minute per session, 100 requests per hour per IP address
- **FR-023**: System MUST log all requests, errors, and performance metrics (response time, token usage) for monitoring and debugging

#### Security & Privacy

- **FR-024**: System MUST NOT expose OpenAI API keys, Qdrant API keys, or Neon Postgres credentials in responses, logs, or client-side code
- **FR-025**: System MUST use environment variables for all sensitive configuration (API keys, database URLs, secrets)
- **FR-026**: System MUST implement CORS (Cross-Origin Resource Sharing) to allow requests only from the deployed Docusaurus frontend domain
- **FR-027**: System MUST sanitize user inputs to prevent injection attacks (SQL injection, prompt injection, XSS)

#### Performance & Scalability

- **FR-028**: System MUST support at least 10 concurrent users without response time degradation (constitution: "support concurrent users")
- **FR-029**: System MUST implement caching for frequently asked questions (optional but recommended for performance)
- **FR-030**: System MUST implement connection pooling for Neon Postgres to handle concurrent database requests efficiently

### Key Entities *(include if feature involves data)*

- **ChatSession**: Represents a user's conversation session
  - Attributes: session_id (UUID), created_at (timestamp), last_activity (timestamp), user_id (optional, for future auth)
  - Relationships: Has many ChatMessages

- **ChatMessage**: Represents a single question-answer exchange
  - Attributes: message_id (auto-increment), session_id (foreign key), question (text), answer (text), cited_sources (JSON array), timestamp (ISO8601), response_time_ms (integer)
  - Relationships: Belongs to ChatSession

- **TextbookChunk**: Represents a chunk of textbook content in Qdrant
  - Attributes: chunk_id (UUID), module_id (string), chapter_id (string), section_title (string), content (text), content_type (enum: text/code/diagram), embedding (vector), metadata (JSON)
  - Relationships: Standalone entity stored in Qdrant vector DB

- **IndexingJob**: Represents a content indexing operation (for tracking)
  - Attributes: job_id (auto-increment), chapter_id (string), status (enum: pending/in_progress/completed/failed), started_at (timestamp), completed_at (timestamp), error_message (text, nullable)
  - Relationships: Tracks which chapters have been successfully indexed

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% of chat requests return responses within 3 seconds (measured via application performance monitoring)
- **SC-002**: System successfully retrieves relevant textbook content for 90% of course-related questions (measured via manual evaluation of 100 test questions)
- **SC-003**: All 23 chapters are successfully indexed in Qdrant within 10 minutes of deployment (measured via indexing job completion status)
- **SC-004**: System maintains 99.5% uptime during normal operation excluding scheduled maintenance (measured via health check monitoring)
- **SC-005**: Answer citations are accurate 95% of the time - cited sources actually contain the information provided (measured via random sampling of 50 answers)
- **SC-006**: Selected text queries provide contextually relevant answers 90% of the time (measured via user feedback or manual evaluation)
- **SC-007**: System handles 10 concurrent users with <10% response time degradation compared to single-user baseline (measured via load testing)
- **SC-008**: Zero exposed API keys or credentials in deployed codebase (measured via automated security scanning and manual code review)
- **SC-009**: Rate limiting successfully prevents abuse - no single session can exceed 10 requests/minute (measured via load testing and logging)
- **SC-010**: Conversation history is correctly maintained across multi-turn dialogues for 95% of sessions (measured via end-to-end testing)

### User Experience Metrics

- **UX-001**: Students can ask a question and receive a helpful answer without needing to read API documentation or technical guides (self-service success)
- **UX-002**: Error messages are clear and actionable - users understand what went wrong and how to fix it (e.g., "Question too long. Please shorten to under 1000 characters.")
- **UX-003**: Chatbot responses include specific chapter references that users can navigate to directly (measured by presence of clickable citation links)

### Technical Quality Metrics

- **TQ-001**: API endpoints follow OpenAPI 3.0 specification with complete request/response schemas documented
- **TQ-002**: Code coverage for backend API routes is at least 80% (unit + integration tests)
- **TQ-003**: All database queries use parameterized statements to prevent SQL injection (verified via code review)
- **TQ-004**: System degrades gracefully when external services (OpenAI, Qdrant) are unavailable - returns meaningful errors rather than crashing

### Constitution Alignment

- **CA-001**: Meets "AI-Native Architecture" principle - RAG chatbot is functional and integrated (constitution Section II)
- **CA-002**: Meets "<3 seconds response time" constraint (constitution Section II, FR-004)
- **CA-003**: Meets "Selected text queries" requirement (constitution Section II, User Story 2)
- **CA-004**: Meets "Source citations" requirement (constitution Section II, FR-005)
- **CA-005**: Meets "Context-aware responses" and "Neon Postgres + Qdrant properly configured" (constitution Section II & Success Criteria)
- **CA-006**: Meets "NO API keys exposed" security constraint (constitution Technical Constraints, FR-024)
