# Quick Start Guide - 5 Minutes to Running API

Get the NeuroBot RAG Chatbot Backend running in 5 minutes.

## Prerequisites Checklist

- [ ] Python 3.12+ installed
- [ ] OpenAI API key ready
- [ ] Qdrant Cloud account + API key
- [ ] Neon Postgres database URL
- [ ] Git clone of this repository

---

## Step 1: Install Dependencies (1 min)

```bash
cd backend
pip install -r requirements.txt
```

---

## Step 2: Configure Environment (2 min)

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Required: Replace xxxxx with your actual values
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
QDRANT_URL=https://xxxxx-xxxxx.us-east-1-0.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=xxxxxxxxxxxxxxxxxxxxx
DATABASE_URL=postgresql://username:password@ep-xxxxx.us-east-1.aws.neon.tech/neondb?sslmode=require
FRONTEND_URL=http://localhost:3000
```

---

## Step 3: Setup Database (30 sec)

```bash
python scripts/run_migrations.py
```

**Expected output:**
```
✅ Database migrations completed
Tables created: chat_sessions, chat_messages, indexing_jobs
```

---

## Step 4: Index Textbook Chapters (1-2 min)

```bash
python scripts/index_chapters.py --docs-dir ../docs
```

**Expected output:**
```
🚀 Starting chapter indexing...
📚 Found 23 chapters to index
...
✅ Successful: 23
```

**Cost:** ~$0.10-0.20 in OpenAI credits

---

## Step 5: Start Server (10 sec)

```bash
uvicorn src.main:app --reload
```

**Server running at:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## Quick Test

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

**Expected:**
```json
{"status": "healthy", "dependencies": {...}}
```

### Test 2: Ask a Question

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is ROS 2?"}'
```

**Expected:**
```json
{
  "answer": "ROS 2 (Robot Operating System 2) is...",
  "sources": [{"module_id": "module-2", ...}],
  "session_id": "...",
  "response_time_ms": 1847
}
```

---

## Troubleshooting

### Server won't start?

1. **Check `.env` file exists:** `ls -la .env`
2. **Verify API keys are set:** `cat .env | grep API_KEY`
3. **Test Postgres connection:**
   ```bash
   python -c "import asyncio; from src.database.connection import db; asyncio.run(db.connect()); print('✅ Connected')"
   ```

### Indexing fails?

1. **Check docs directory exists:** `ls -la ../docs/`
2. **Verify markdown structure:** `ls ../docs/module-*/chapter-*.md`
3. **Check OpenAI API key:** Test at https://platform.openai.com/api-keys

### Slow responses?

- **First query is slower** (cold start) - ~2-3s
- **Subsequent queries** should be ~1.5-2s
- If consistently >3s, check OpenAI API status: https://status.openai.com/

---

## What's Next?

✅ **Server is running!** Try these:

1. **Interactive API Docs:** http://localhost:8000/docs
2. **Run Tests:**
   ```bash
   python tests/integration/test_chat_endpoint.py
   python tests/load/test_concurrent_requests.py
   ```
3. **Connect Frontend:** Update frontend to use `http://localhost:8000/chat`
4. **Monitor Logs:** Check uvicorn output for request logs

---

## Quick Reference

| Action | Command |
|--------|---------|
| Start server | `uvicorn src.main:app --reload` |
| Run migrations | `python scripts/run_migrations.py` |
| Re-index chapters | `python scripts/index_chapters.py --docs-dir ../docs` |
| Run tests | `python tests/integration/test_chat_endpoint.py` |
| Check health | `curl http://localhost:8000/health` |
| View API docs | Open http://localhost:8000/docs |

---

**🎉 You're ready! Start asking questions about the textbook.**

For detailed documentation, see [README.md](README.md).
