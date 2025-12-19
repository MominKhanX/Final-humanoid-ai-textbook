# Quickstart Guide: RAG Chatbot Backend

**Feature**: 002-rag-chatbot-backend
**Last Updated**: 2025-12-16
**Target Audience**: Backend developers implementing the FastAPI server

## Overview

This guide walks you through setting up and running the NeuroBot RAG Chatbot Backend in **15 minutes**. By the end, you'll have a fully functional API serving intelligent Q&A responses with <3s latency.

---

## Prerequisites

**Required**:
- Python 3.11+ installed
- Git (for cloning the repository)
- Active internet connection

**Recommended**:
- VS Code or PyCharm IDE
- Postman or Thunder Client for API testing
- Basic familiarity with FastAPI and async/await

---

## Step 1: Environment Setup (3 minutes)

### 1.1 Clone Repository & Navigate
```bash
git checkout 002-rag-chatbot-backend
cd backend
```

### 1.2 Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 1.3 Install Dependencies
```bash
pip install -r requirements.txt
```

**Expected `requirements.txt`**:
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
asyncpg==0.29.0
qdrant-client==1.7.0
openai==1.3.0
python-dotenv==1.0.0
httpx==0.25.2
slowapi==0.1.9
cachetools==5.3.2
structlog==23.2.0
alembic==1.13.0
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-httpx==0.27.0
```

---

## Step 2: Configure Services (5 minutes)

### 2.1 Create `.env` File
Create `backend/.env` with your API keys:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
OPENAI_ORG_ID=org-YOUR_ORG_ID_HERE

# Qdrant Cloud Configuration
QDRANT_URL=https://YOUR_CLUSTER.qdrant.io
QDRANT_API_KEY=YOUR_QDRANT_KEY_HERE

# Neon Postgres Configuration
DATABASE_URL=postgresql://user:password@ep-xyz.us-east-1.aws.neon.tech/neurobot_chat

# Frontend CORS Configuration
FRONTEND_URL=https://mominkhanx.github.io

# Rate Limiting Configuration
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_PER_HOUR=100

# Environment
ENVIRONMENT=development
```

**Where to get API keys**:

**OpenAI** (https://platform.openai.com/api-keys):
1. Create account → Go to API keys
2. Click "Create new secret key"
3. Copy `sk-proj-...` key to `.env`

**Qdrant Cloud** (https://cloud.qdrant.io):
1. Sign up (free tier: 1GB storage)
2. Create cluster → Copy URL and API key
3. Paste to `.env`

**Neon Postgres** (https://neon.tech):
1. Sign up (free tier: 0.5GB storage)
2. Create project → Copy connection string
3. Paste to `.env`

### 2.2 Initialize Database
Run Alembic migrations to create tables:

```bash
# Navigate to backend directory
cd backend

# Run migrations
alembic upgrade head
```

**Expected Output**:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial schema
INFO  [alembic.runtime.migration] Running upgrade 001 -> head, Create tables
```

**Troubleshooting**:
- **Error**: `ModuleNotFoundError: No module named 'alembic'`
  - **Fix**: Run `pip install -r requirements.txt` again
- **Error**: `Connection refused` or `Database does not exist`
  - **Fix**: Verify `DATABASE_URL` in `.env` is correct

---

## Step 3: Index Textbook Content (4 minutes)

### 3.1 Prepare Chapter Files
Ensure your `docs/` directory contains markdown files:

```
docs/
├── module-1-ros2/
│   ├── chapter-1.md
│   ├── chapter-2.md
│   └── ...
├── module-2-digital-twin/
│   └── ...
└── ...
```

### 3.2 Run Indexing Script
```bash
python scripts/index_chapters.py
```

**Expected Output**:
```
[2025-12-16 10:30:00] INFO: Starting indexing for 23 chapters
[2025-12-16 10:30:02] INFO: Processing module-1-ros2/chapter-1.md
[2025-12-16 10:30:02] INFO: Generated 15 chunks (7,523 tokens)
[2025-12-16 10:30:04] INFO: Embeddings created (15 chunks)
[2025-12-16 10:30:05] INFO: Uploaded to Qdrant (15 points)
[2025-12-16 10:30:05] INFO: ✓ module-1-ros2/chapter-1 indexed (15 chunks)
...
[2025-12-16 10:32:00] INFO: ✓ All 23 chapters indexed successfully
[2025-12-16 10:32:00] INFO: Total chunks: 487 | Total time: 2m 0s
```

**What this does**:
1. Reads all markdown files from `docs/`
2. Chunks content (500-1000 tokens/chunk)
3. Generates embeddings via OpenAI API
4. Uploads vectors to Qdrant
5. Updates `indexing_jobs` table in Postgres

**Troubleshooting**:
- **Error**: `OpenAI API key not found`
  - **Fix**: Verify `OPENAI_API_KEY` in `.env`
- **Error**: `Qdrant connection failed`
  - **Fix**: Check `QDRANT_URL` and `QDRANT_API_KEY`
- **Slow indexing** (>5 minutes):
  - **Cause**: Network latency or API rate limits
  - **Fix**: Normal for first run; subsequent runs are incremental

---

## Step 4: Start the Server (1 minute)

### 4.1 Launch Uvicorn
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Will watch for changes in these directories: ['C:\\...\\backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [67890]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 4.2 Verify Health Check
Open browser or use curl:

```bash
curl http://localhost:8000/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-16T10:35:00.000Z",
  "services": {
    "database": {
      "status": "healthy",
      "latency_ms": 12
    },
    "qdrant": {
      "status": "healthy",
      "latency_ms": 45
    },
    "openai": {
      "status": "configured"
    }
  },
  "uptime_seconds": 10
}
```

✅ **Server is running!** Proceed to testing.

---

## Step 5: Test the API (2 minutes)

### 5.1 General Q&A Endpoint

**Request**:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is a ROS 2 node?",
    "session_id": null
  }'
```

**Expected Response** (within 3 seconds):
```json
{
  "answer": "A ROS 2 node is a process that performs computation. Nodes communicate with each other using topics, services, and actions. Each node typically has a specific purpose, such as controlling a motor or processing sensor data.",
  "sources": [
    {
      "module_id": "module-1-ros2",
      "chapter_id": "chapter-1",
      "section_title": "Introduction to ROS 2 Nodes",
      "url": "/docs/module-1-ros2/chapter-1#ros2-nodes",
      "relevance_score": 0.92
    },
    {
      "module_id": "module-1-ros2",
      "chapter_id": "chapter-2",
      "section_title": "Node Communication Patterns",
      "url": "/docs/module-1-ros2/chapter-2#communication",
      "relevance_score": 0.85
    }
  ],
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-12-16T10:36:15.123Z",
  "response_time_ms": 1847
}
```

### 5.2 Selected Text Query Endpoint

**Request**:
```bash
curl -X POST http://localhost:8000/chat/selected \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What does the 10 parameter mean?",
    "selected_text": "publisher = self.create_publisher(String, '\''topic'\'', 10)",
    "session_id": null
  }'
```

**Expected Response**:
```json
{
  "answer": "The '10' parameter in create_publisher() specifies the QoS (Quality of Service) queue size. This determines how many messages can be buffered if the publisher is sending faster than subscribers can receive. A value of 10 means up to 10 messages will be queued before old ones are discarded.",
  "sources": [
    {
      "module_id": "module-1-ros2",
      "chapter_id": "chapter-3",
      "section_title": "Publisher Configuration and QoS",
      "url": "/docs/module-1-ros2/chapter-3#qos-settings",
      "relevance_score": 0.94
    }
  ],
  "session_id": "550e8400-e29b-41d4-a716-446655440001",
  "timestamp": "2025-12-16T10:37:22.456Z",
  "response_time_ms": 1652
}
```

### 5.3 Conversation History Endpoint

**Request** (using `session_id` from previous requests):
```bash
curl "http://localhost:8000/chat/history?session_id=550e8400-e29b-41d4-a716-446655440000"
```

**Expected Response**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "messages": [
    {
      "message_id": 1,
      "question": "What is a ROS 2 node?",
      "answer": "A ROS 2 node is a process that performs computation...",
      "cited_sources": [...],
      "timestamp": "2025-12-16T10:36:15.123Z",
      "response_time_ms": 1847
    }
  ],
  "total_messages": 1,
  "created_at": "2025-12-16T10:36:15.000Z",
  "last_activity": "2025-12-16T10:36:15.123Z"
}
```

---

## Step 6: Interactive API Documentation

### 6.1 Access Swagger UI
Open browser: **http://localhost:8000/docs**

Features:
- **Try it out**: Test endpoints directly from browser
- **Schema Validation**: See request/response formats
- **Authentication**: Test with API keys

### 6.2 Access ReDoc
Alternative documentation: **http://localhost:8000/redoc**

---

## Common Issues & Solutions

### Issue: `ModuleNotFoundError: No module named 'fastapi'`
**Cause**: Dependencies not installed
**Solution**: Run `pip install -r requirements.txt`

### Issue: `Connection to Qdrant failed`
**Cause**: Incorrect Qdrant URL or API key
**Solution**:
1. Verify `QDRANT_URL` and `QDRANT_API_KEY` in `.env`
2. Test connection: `curl -H "api-key: YOUR_KEY" https://YOUR_CLUSTER.qdrant.io/collections`

### Issue: `OpenAI API rate limit exceeded`
**Cause**: Too many requests during indexing or testing
**Solution**: Wait 60 seconds; Tier 1 has 10k TPM limit

### Issue: Response time >3 seconds
**Cause**: Network latency or cold start
**Solution**:
- First request is slow (~3-5s) due to cold start
- Subsequent requests should be <2s
- Check network: `ping api.openai.com`

### Issue: No citations in response
**Cause**: Qdrant returned no results (similarity score too low)
**Solution**: Lower `score_threshold` in `retrieve_chunks()` from 0.7 to 0.5

---

## Next Steps

### Frontend Integration
Connect the Docusaurus frontend to your local backend:

1. Update `frontend/.env`:
   ```bash
   NEXT_PUBLIC_CHAT_API_URL=http://localhost:8000
   ```

2. Start frontend:
   ```bash
   cd frontend
   npm start
   ```

3. Test chat widget on `http://localhost:3000`

### Production Deployment
Deploy to Render.com:

1. Create `render.yaml` (see `research.md` for config)
2. Push to GitHub
3. Connect repository to Render
4. Add environment variables in Render dashboard
5. Deploy automatically on push to main

### Performance Monitoring
Set up Sentry for error tracking:

```bash
pip install sentry-sdk[fastapi]
```

Add to `main.py`:
```python
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=0.1
)
```

---

## Verification Checklist

Before proceeding to production:

- [ ] Health check returns `"status": "healthy"`
- [ ] `/chat` endpoint responds in <3 seconds
- [ ] Citations include valid `module_id`, `chapter_id`, `url`
- [ ] Session history persists across requests
- [ ] Rate limiting works (429 status after 10 requests/minute)
- [ ] Error messages are clear and actionable
- [ ] All 23 chapters successfully indexed (check `indexing_jobs` table)
- [ ] No API keys exposed in logs or responses
- [ ] CORS allows requests from `FRONTEND_URL`
- [ ] Database migrations run successfully

---

## Additional Resources

**Documentation**:
- [API Contracts](./contracts/api.yaml) - OpenAPI spec
- [Data Model](./data-model.md) - Database schema
- [Research Decisions](./research.md) - Technical rationale

**Endpoints**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

**Support**:
- GitHub Issues: https://github.com/MominKhanX/Final-humanoid-ai-textbook/issues
- Constitution: `.specify/memory/constitution.md` (requirements reference)

---

**Time to First Response**: ~15 minutes ✅

You're now ready to implement the RAG Chatbot Backend! Proceed to `/sp.tasks` for detailed implementation tasks.
