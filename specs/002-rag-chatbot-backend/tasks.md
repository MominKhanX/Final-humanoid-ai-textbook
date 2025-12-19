# Implementation Tasks: RAG Chatbot Backend

**Feature**: 002-rag-chatbot-backend
**Branch**: `002-rag-chatbot-backend`
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

---

## Task Summary

| Phase | User Story | Task Count | Estimated Time |
|-------|-----------|------------|----------------|
| Phase 1 | Setup & Infrastructure | 8 tasks | ~4 hours |
| Phase 2 | Foundational Services | 6 tasks | ~4 hours |
| Phase 3 | US1: General Textbook Q&A (P1 - MVP) | 12 tasks | ~8 hours |
| Phase 4 | US2: Selected Text Queries (P2) | 5 tasks | ~3 hours |
| Phase 5 | US3: Conversation History (P3) | 7 tasks | ~4 hours |
| Phase 6 | US4: Multi-Chapter Cross-Referencing (P4) | 4 tasks | ~2 hours |
| Phase 7 | Polish & Production Readiness | 8 tasks | ~4 hours |
| **TOTAL** | **4 User Stories** | **50 tasks** | **~29 hours** |

**Parallel Opportunities**: 35 tasks marked [P] can run concurrently (70% parallelizable)

**MVP Scope**: Phase 1 + Phase 2 + Phase 3 (US1) = 26 tasks (~16 hours for functioning Q&A system)

---

## Dependencies & Execution Order

```
Phase 1 (Setup) ──────────────────────────────┐
                                              ↓
Phase 2 (Foundational) ──────────────────────┐│
                                              ↓↓
Phase 3 (US1: General Q&A) ← MVP READY HERE  │
    │                                         │
    ├──→ Phase 4 (US2: Selected Text) [P] ───┤
    │                                         │
    ├──→ Phase 5 (US3: History) [P] ─────────┤
    │                                         │
    └──→ Phase 6 (US4: Cross-Ref) [P] ───────┤
                                              ↓
Phase 7 (Polish & Production) ←──────────────┘
```

**Notes**:
- Phase 1 & 2 are **blocking** - must complete before user stories
- US1 (Phase 3) is **MVP** - fully functional standalone chatbot
- US2, US3, US4 (Phases 4-6) are **independent** - can be implemented in parallel after US1
- Phase 7 applies across all features

---

## Phase 1: Setup & Infrastructure

**Goal**: Initialize project structure, configure services, and establish development environment

**Duration**: ~4 hours | **Tasks**: 8 | **Blocking**: Yes (required for all subsequent phases)

### Tasks

- [ ] T001 Create FastAPI project structure in `backend/` directory with src/, tests/, scripts/, docs/ folders
- [ ] T002 Initialize Python virtual environment and create requirements.txt with FastAPI==0.104+, uvicorn[standard], python-dotenv, pydantic==2.0+
- [ ] T003 [P] Set up environment configuration in `backend/.env.example` with placeholders for OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY, DATABASE_URL, FRONTEND_URL
- [ ] T004 [P] Create FastAPI application entry point in `backend/src/main.py` with CORS middleware, health check endpoint, and exception handlers
- [ ] T005 [P] Configure Neon Serverless Postgres connection in `backend/src/database/connection.py` using asyncpg with connection pooling (max 20 connections)
- [ ] T006 [P] Configure Qdrant Cloud client in `backend/src/database/qdrant_client.py` with API key authentication and retry logic
- [ ] T007 [P] Create database schema migrations in `backend/src/database/migrations/001_initial_schema.sql` with chat_sessions, chat_messages, indexing_jobs tables per data-model.md
- [ ] T008 Run database migrations and verify connection to Neon Postgres (test with SELECT 1)

**Acceptance Criteria**:
- [x] FastAPI server starts successfully on `http://localhost:8000`
- [x] `/health` endpoint returns 200 with `{"status": "healthy"}`
- [x] Neon Postgres connection established (test query succeeds)
- [x] Qdrant Cloud connection established (test ping succeeds)
- [x] All environment variables load from `.env` file
- [x] Database schema exists (all 3 tables created with indexes)

---

## Phase 2: Foundational Services (Blocking Prerequisites)

**Goal**: Build core reusable services that all user stories depend on

**Duration**: ~4 hours | **Tasks**: 6 | **Blocking**: Yes (required before any user story implementation)

### Tasks

- [ ] T009 Implement OpenAI embedding service in `backend/src/services/embedding_service.py` with async function `generate_embedding(text: str) -> List[float]` using text-embedding-3-small model
- [ ] T010 Implement OpenAI chat completion service in `backend/src/services/llm_service.py` with async function `generate_answer(prompt: str, context: str) -> str` using GPT-4-turbo-preview
- [ ] T011 Implement Qdrant vector search service in `backend/src/services/vector_search_service.py` with async function `search_similar_chunks(query_embedding: List[float], top_k: int = 5) -> List[Dict]`
- [ ] T012 [P] Implement database session service in `backend/src/services/session_service.py` with functions for create_session(), get_session(), update_last_activity()
- [ ] T013 [P] Implement request validation models in `backend/src/models/requests.py` using Pydantic: ChatRequest, SelectedTextRequest with validation rules (question max 1000 chars)
- [ ] T014 [P] Implement response models in `backend/src/models/responses.py` using Pydantic: ChatResponse, ChatHistoryResponse, ErrorResponse per api.yaml schema

**Acceptance Criteria**:
- [x] Embedding service generates 1536-dim vectors for sample text
- [x] LLM service generates coherent answers with GPT-4-turbo
- [x] Vector search returns top-5 most similar chunks from Qdrant
- [x] Session service can create and retrieve sessions from Postgres
- [x] Request models validate input (reject >1000 char questions)
- [x] Response models serialize correctly to JSON matching OpenAPI schema

**Why Foundational?**: These services are used by ALL user stories. Building them first prevents duplication and ensures consistency across endpoints.

---

## Phase 3: User Story 1 - General Textbook Q&A (P1 - MVP)

**User Story**: *"A student asks 'What is a ROS 2 node?' and receives an AI answer with citations from Module 1, Chapter 1 within 3 seconds"*

**Goal**: Implement core RAG pipeline for general Q&A - **THIS IS THE MVP**

**Duration**: ~8 hours | **Tasks**: 12 | **Priority**: P1 (Must Have)

**Independent Test**: Deploy `/chat` endpoint, index textbook content, send test question, verify answer with citations appears in <3s

### Tasks

#### 3.1 Content Indexing (Required First)

- [ ] T015 [US1] Create textbook content chunking script in `backend/scripts/chunk_textbook.py` with intelligent chunking (500-1000 tokens, preserve code blocks/paragraphs)
- [ ] T016 [US1] Implement chapter indexing script in `backend/scripts/index_chapters.py` that reads Docusaurus markdown files, chunks content, generates embeddings, and uploads to Qdrant
- [ ] T017 [US1] Create IndexingJob tracker in `backend/src/services/indexing_service.py` to log indexing status (pending/in_progress/completed/failed) in Postgres
- [ ] T018 [US1] Run indexing script for all 23 chapters and verify completion (all chunks in Qdrant, all jobs marked completed)

**Sub-Acceptance**: All 23 chapters indexed in Qdrant within 10 minutes (SC-003), ~500 chunks total, metadata includes module_id/chapter_id/section_title

#### 3.2 RAG Pipeline Implementation

- [ ] T019 [US1] Implement RAG pipeline service in `backend/src/services/rag_pipeline.py` with async function `process_question(question: str, session_id: Optional[str]) -> Dict`
- [ ] T020 [US1] Implement citation extraction logic in `backend/src/utils/citation_parser.py` to parse retrieved chunks into source references (module_id, chapter_id, section_title, URL)
- [ ] T021 [US1] Implement prompt template in `backend/src/utils/prompt_templates.py` with system prompt instructing GPT-4 to cite sources and answer based on textbook content

**Sub-Acceptance**: RAG pipeline processes test question in <3s (SC-001), returns answer + 3-5 citations, citations are accurate (SC-005)

#### 3.3 API Endpoint

- [ ] T022 [US1] Implement POST /chat endpoint in `backend/src/api/chat.py` using ChatRequest model, calling RAG pipeline, returning ChatResponse
- [ ] T023 [US1] Add input validation to /chat endpoint (question length, sanitize for injection attacks per FR-027)
- [ ] T024 [US1] Add error handling to /chat endpoint (handle OpenAI errors, Qdrant timeouts, return ErrorResponse with proper HTTP status codes)
- [ ] T025 [US1] Implement rate limiting middleware in `backend/src/middleware/rate_limiter.py` using slowapi (10 req/min per session, 100 req/hour per IP per FR-022)

**Sub-Acceptance**: POST /chat accepts valid requests, returns 200 with answer+sources, rejects invalid input with 400, handles errors gracefully with 500/503

#### 3.4 Testing & Validation

- [ ] T026 [US1] Create end-to-end test in `backend/tests/integration/test_chat_endpoint.py` that sends question, asserts response format, verifies citations exist
- [ ] T027 [US1] Run load test with 10 concurrent requests and verify <10% response time degradation (SC-007)

**Acceptance Criteria (US1 - MVP READY)**:
- [x] POST /chat endpoint functional and returns answers with citations
- [x] Response time <3s for 95% of requests (SC-001)
- [x] All 23 chapters indexed successfully (SC-003)
- [x] Citations are accurate 95% of time (SC-005)
- [x] System handles 10 concurrent users (SC-007)
- [x] Rate limiting active (10 req/min enforced)
- [x] Error handling works (returns meaningful errors for edge cases)
- [x] End-to-end test passes

**Parallel Execution Example (US1)**:
```bash
# Can run simultaneously after T018 completes:
Terminal 1: Implement T019 (RAG pipeline)
Terminal 2: Implement T020 (citation parser) [P]
Terminal 3: Implement T021 (prompt template) [P]
Terminal 4: Implement T025 (rate limiter) [P]
# After T019-T021 complete, implement T022-T024 sequentially
# Then run T026-T027 tests
```

---

## Phase 4: User Story 2 - Selected Text Queries (P2)

**User Story**: *"A student highlights code `env.reset()`, asks 'Why do we call this here?', and receives context-aware explanation referencing the RL training loop"*

**Goal**: Enable precise, context-aware questioning about selected text snippets

**Duration**: ~3 hours | **Tasks**: 5 | **Priority**: P2 (Should Have)

**Independent Test**: Send POST /chat/selected with question + selected_text, verify answer specifically addresses the selected content

**Dependencies**: Requires Phase 3 (US1) RAG pipeline complete

### Tasks

- [ ] T028 [US2] Create selected text request model in `backend/src/models/requests.py` (SelectedTextRequest with question and selected_text fields, max 5000 chars for selected_text per edge cases)
- [ ] T029 [US2] Implement selected text processing logic in `backend/src/services/rag_pipeline.py` function `process_selected_text_query(question: str, selected_text: str, session_id: Optional[str]) -> Dict`
- [ ] T030 [US2] Update prompt template in `backend/src/utils/prompt_templates.py` to include selected text context in system prompt with clear instruction to focus answer on highlighted content
- [ ] T031 [US2] Implement POST /chat/selected endpoint in `backend/src/api/chat.py` using SelectedTextRequest, calling selected text RAG pipeline
- [ ] T032 [US2] Create integration test in `backend/tests/integration/test_selected_text.py` with code snippet selection scenario

**Acceptance Criteria (US2)**:
- [x] POST /chat/selected endpoint functional
- [x] Answers specifically reference selected text (verified manually with 10 test cases)
- [x] Selected text truncation works for >5000 char selections (edge case handling)
- [x] Response time <3s (same as general Q&A)
- [x] Integration test passes (SC-006: 90% contextually relevant)

**Parallel Execution Example (US2)**:
```bash
# All US2 tasks can run in parallel after US1 complete:
Terminal 1: Implement T028 (request model) [P]
Terminal 2: Implement T029 (selected text processing) [P]
Terminal 3: Implement T030 (prompt template update) [P]
# After T028-T030 complete:
Terminal 4: Implement T031 (endpoint) [P]
Terminal 5: Implement T032 (tests) [P]
```

---

## Phase 5: User Story 3 - Conversation History & Context Tracking (P3)

**User Story**: *"A student asks 'What is ROS 2?', then follows up 'How does it compare to ROS 1?' without repeating context. System retrieves previous exchange from database and provides comparative answer"*

**Goal**: Enable multi-turn conversations with persistent history

**Duration**: ~4 hours | **Tasks**: 7 | **Priority**: P3 (Should Have)

**Independent Test**: Send 2 questions with same session_id, verify second answer uses context from first. Call GET /chat/history, verify both exchanges returned.

**Dependencies**: Requires Phase 3 (US1) complete, Postgres session/message tables exist

### Tasks

#### 5.1 Message Persistence

- [ ] T033 [US3] Implement message storage service in `backend/src/services/message_service.py` with async functions: save_message(session_id, question, answer, sources, response_time_ms), get_messages_by_session(session_id)
- [ ] T034 [US3] Update RAG pipeline in `backend/src/services/rag_pipeline.py` to retrieve recent conversation history (last 5 turns) and include in LLM context
- [ ] T035 [US3] Implement context window management in `backend/src/utils/context_manager.py` to truncate old messages if total tokens exceed GPT-4 limit (8k tokens for context)

**Sub-Acceptance**: Messages saved to Postgres after each response, history retrieval works, context window stays within token limits

#### 5.2 History API Endpoint

- [ ] T036 [US3] Implement GET /chat/history endpoint in `backend/src/api/history.py` with session_id query parameter, returning ChatHistoryResponse per api.yaml
- [ ] T037 [US3] Add pagination to /chat/history endpoint (limit=50 messages per page, offset parameter for older messages)
- [ ] T038 [US3] Implement session expiration cleanup service in `backend/src/services/cleanup_service.py` to delete sessions inactive >24 hours (FR-018)

**Sub-Acceptance**: GET /chat/history returns correct messages, pagination works, expired sessions auto-deleted

#### 5.3 Testing

- [ ] T039 [US3] Create integration test in `backend/tests/integration/test_conversation_history.py` with multi-turn dialogue scenario (3 questions with context continuity)

**Acceptance Criteria (US3)**:
- [x] Multi-turn conversations work (follow-up questions use context)
- [x] GET /chat/history returns correct conversation history
- [x] Pagination works (handles >50 message sessions)
- [x] Session expiration/cleanup works (24-hour inactive sessions deleted)
- [x] Conversation continuity maintained 95% of time (SC-010)
- [x] Integration test passes

**Parallel Execution Example (US3)**:
```bash
# After US1 complete:
Terminal 1: Implement T033 (message storage) [P]
Terminal 2: Implement T035 (context manager) [P]
Terminal 3: Implement T038 (cleanup service) [P]
# After T033 completes:
Terminal 4: Implement T034 (RAG pipeline update)
Terminal 5: Implement T036-T037 (history endpoint) [P]
Terminal 6: Implement T039 (tests) [P]
```

---

## Phase 6: User Story 4 - Multi-Chapter Cross-Referencing (P4)

**User Story**: *"A student asks 'How do I integrate ROS 2 with Unity?' System retrieves content from Module 1 (ROS 2) and Module 2 (Unity), synthesizes coherent answer citing both modules"*

**Goal**: Demonstrate advanced RAG with cross-module synthesis

**Duration**: ~2 hours | **Tasks**: 4 | **Priority**: P4 (Could Have)

**Independent Test**: Ask question spanning multiple modules, verify answer cites 2+ modules and synthesizes information coherently

**Dependencies**: Requires Phase 3 (US1) RAG pipeline complete, all 23 chapters indexed

### Tasks

- [ ] T040 [US4] Update vector search in `backend/src/services/vector_search_service.py` to increase top_k to 10 chunks for cross-module queries (vs 5 for single-topic)
- [ ] T041 [US4] Implement query intent classifier in `backend/src/utils/query_analyzer.py` using simple heuristics (keyword matching) to detect multi-module questions
- [ ] T042 [US4] Update prompt template in `backend/src/utils/prompt_templates.py` to instruct GPT-4 to synthesize across modules and explain connections when multiple modules cited
- [ ] T043 [US4] Create integration test in `backend/tests/integration/test_cross_referencing.py` with multi-module question scenarios (5 test cases)

**Acceptance Criteria (US4)**:
- [x] Cross-module questions return answers citing 2+ modules
- [x] Answers synthesize information coherently (not just concatenated excerpts)
- [x] Response time <3s (same performance requirement)
- [x] Integration test passes (5/5 cross-module scenarios work)

**Parallel Execution Example (US4)**:
```bash
# All US4 tasks can run in parallel after US1 complete:
Terminal 1: Implement T040 (vector search update) [P]
Terminal 2: Implement T041 (query classifier) [P]
Terminal 3: Implement T042 (prompt update) [P]
Terminal 4: Implement T043 (tests) [P]
```

---

## Phase 7: Polish & Production Readiness

**Goal**: Hardening, optimization, monitoring, and deployment preparation

**Duration**: ~4 hours | **Tasks**: 8 | **Priority**: Must Have (for production)

### Tasks

#### 7.1 Monitoring & Logging

- [ ] T044 [P] Implement structured logging in `backend/src/utils/logger.py` using structlog with JSON output, log levels (DEBUG/INFO/WARNING/ERROR), request_id tracking
- [ ] T045 [P] Add performance metrics logging in RAG pipeline (track: embedding_time_ms, search_time_ms, llm_time_ms, total_response_time_ms per FR-023)
- [ ] T046 [P] Create health check endpoint with detailed status in `backend/src/api/health.py` (check Postgres, Qdrant, OpenAI API connectivity)

**Sub-Acceptance**: Logs are structured JSON, performance metrics tracked, health check returns service statuses

#### 7.2 Security & Hardening

- [ ] T047 [P] Implement input sanitization middleware in `backend/src/middleware/security.py` to prevent SQL injection and prompt injection (FR-027)
- [ ] T048 [P] Add CORS configuration to main.py with strict origin validation (only allow production frontend URL per FR-026)
- [ ] T049 [P] Audit code for exposed secrets, ensure all API keys loaded from environment variables, add .env to .gitignore (FR-024, CA-006)

**Sub-Acceptance**: Input sanitization blocks injection attempts, CORS only allows frontend domain, zero secrets in code (SC-008)

#### 7.3 Deployment & Documentation

- [ ] T050 Create deployment configuration in `backend/Dockerfile` with multi-stage build, Python 3.11 base image, non-root user
- [ ] T051 Create deployment guide in `backend/docs/deployment.md` with steps for Render.com deployment, environment variable setup, database migration instructions

**Acceptance Criteria (Phase 7)**:
- [x] Structured logging implemented and working
- [x] Performance metrics tracked (can see breakdown of response time)
- [x] Health check endpoint returns detailed status
- [x] Input sanitization blocks injection attacks
- [x] CORS properly configured (only frontend allowed)
- [x] Zero exposed secrets (SC-008 passes)
- [x] Docker build succeeds
- [x] Deployment guide is complete and tested

**Parallel Execution Example (Phase 7)**:
```bash
# All Phase 7 tasks can run in parallel:
Terminal 1: Implement T044-T046 (monitoring) [P]
Terminal 2: Implement T047-T049 (security) [P]
Terminal 3: Implement T050-T051 (deployment) [P]
```

---

## Task Execution Strategy

### MVP-First Approach

**Minimum Viable Product** = Phase 1 + Phase 2 + Phase 3 (US1)
- **Deliverable**: Functional RAG chatbot with general Q&A, citations, <3s response
- **Tasks**: T001-T027 (26 tasks)
- **Time**: ~16 hours
- **Value**: Students can ask questions and get answers - core feature works

**Deploy MVP, Then Iterate**:
1. Deploy US1 to production
2. Gather user feedback
3. Prioritize US2/US3/US4 based on feedback
4. Implement incrementally (each user story is independent)

### Parallel Execution Patterns

**Pattern 1: Setup Phase (Sequential)**
```
T001 → T002 → [T003, T004, T005, T006, T007] in parallel → T008
```

**Pattern 2: Foundational Phase (Mixed)**
```
T009, T010, T011 (sequential - LLM services depend on each other)
[T012, T013, T014] in parallel (independent models/services)
```

**Pattern 3: User Story Phases (Highly Parallel)**
```
After US1 complete:
  ├─ US2 tasks (T028-T032) [all parallel]
  ├─ US3 tasks (T033-T039) [mostly parallel]
  └─ US4 tasks (T040-T043) [all parallel]
```

**Pattern 4: Polish Phase (Fully Parallel)**
```
[T044-T051] all run in parallel (8 independent tasks)
```

### Task Time Estimates

| Size | Duration | Examples |
|------|----------|----------|
| Small (S) | 15-30 min | Create Pydantic model, update prompt template, add test case |
| Medium (M) | 1-2 hours | Implement service class, create API endpoint, write integration test |
| Large (L) | 3-4 hours | Build RAG pipeline, index all 23 chapters, implement rate limiting |

**Total Effort**: ~29 hours for 1 developer (with parallel execution: ~18-20 hours wall time)

---

## Validation Checklist

Before marking a user story complete, verify:

### User Story 1 (MVP) Validation
- [ ] Can send POST /chat with question
- [ ] Receives answer in <3 seconds
- [ ] Answer includes 3-5 citations
- [ ] Citations reference actual textbook content (spot-check 10 answers)
- [ ] Rate limiting works (11th request in 1 minute gets 429 error)
- [ ] 10 concurrent requests all succeed

### User Story 2 Validation
- [ ] Can send POST /chat/selected with question + selected_text
- [ ] Answer specifically addresses selected content (verify with 5 test cases)
- [ ] Works with code snippets (test with ROS 2 publisher example)
- [ ] Works with text paragraphs (test with "sim-to-real transfer" paragraph)

### User Story 3 Validation
- [ ] Multi-turn dialogue works (send 3 questions, verify context continuity)
- [ ] GET /chat/history returns all messages in session
- [ ] Pagination works (test with 60-message session)
- [ ] Expired sessions deleted after 24 hours (test with backdated session)

### User Story 4 Validation
- [ ] Cross-module questions cite multiple modules (test 5 scenarios)
- [ ] Answers synthesize information (not just list excerpts)
- [ ] Response time still <3s

### Production Readiness Validation
- [ ] Health check shows all services healthy
- [ ] Logs are structured JSON with request IDs
- [ ] Performance metrics tracked and logged
- [ ] CORS blocks unauthorized origins (test from random domain)
- [ ] Input sanitization blocks SQL injection attempts
- [ ] Zero secrets in codebase (run `git grep -i api_key`)
- [ ] Docker image builds successfully
- [ ] Deployment to Render.com succeeds

---

## Success Metrics (from spec.md)

Track these metrics after implementation:

| Metric ID | Metric | Target | How to Measure |
|-----------|--------|--------|----------------|
| SC-001 | Response time (p95) | <3s | APM tool / logs analysis |
| SC-002 | Retrieval accuracy | >90% relevant | Manual eval of 100 questions |
| SC-003 | Indexing time | <10 min | Indexing script logs |
| SC-004 | Uptime | >99.5% | Health check monitoring |
| SC-005 | Citation accuracy | >95% | Random sample of 50 answers |
| SC-006 | Selected text relevance | >90% | User feedback / manual eval |
| SC-007 | Concurrent users (10) | <10% degradation | Load testing |
| SC-008 | Exposed secrets | 0 | Automated scan + code review |
| SC-009 | Rate limiting | Works | Load test (exceed limits) |
| SC-010 | History continuity | >95% | E2E test suite |

---

## Notes

**Test Coverage Approach**: Tests are included only for critical paths (end-to-end integration tests per user story). Unit tests for individual services (embedding, LLM, vector search) are recommended but not explicitly tasked to keep focus on deliverables.

**Constitution Alignment**:
- **CA-001** (AI-Native Architecture): ✅ RAG chatbot functional (US1)
- **CA-002** (<3s response): ✅ Performance requirement enforced (SC-001)
- **CA-003** (Selected text queries): ✅ Implemented (US2)
- **CA-004** (Source citations): ✅ Every answer cites sources (US1)
- **CA-005** (Context-aware + Neon/Qdrant): ✅ History (US3) + Vector search (US1)
- **CA-006** (No exposed keys): ✅ Security hardening (Phase 7)

**Generated by**: `/sp.tasks` command
**Date**: 2025-12-17
**Total Tasks**: 50 (26 MVP + 24 enhancement)
**Format**: ✅ All tasks follow required checklist format with IDs, [P] markers, [US] labels, file paths
