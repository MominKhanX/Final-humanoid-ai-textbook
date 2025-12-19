"""
Integration Test for Chat Endpoints
Tests end-to-end RAG pipeline: embedding -> retrieval -> generation -> citation
"""

import pytest
import asyncio
import httpx
from typing import Dict, List

# Test configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 5.0  # 5 seconds (should be well within <3s target)


@pytest.mark.asyncio
async def test_chat_endpoint_general_qa():
    """
    Test POST /chat endpoint for general Q&A

    Verifies:
    - 200 status code
    - Response contains answer, sources, session_id, timestamp, response_time_ms
    - Response time is under 3000ms
    - Sources contain valid citations with module_id, chapter_id, section_title, url
    """
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Test question about ROS 2 (should be in textbook)
        request_payload = {
            "question": "What is ROS 2 and what are its main components?"
        }

        response = await client.post(
            f"{BASE_URL}/chat",
            json=request_payload,
        )

        # Verify status code
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        # Parse response
        data = response.json()

        # Verify response structure
        assert "answer" in data, "Response missing 'answer' field"
        assert "sources" in data, "Response missing 'sources' field"
        assert "session_id" in data, "Response missing 'session_id' field"
        assert "timestamp" in data, "Response missing 'timestamp' field"
        assert "response_time_ms" in data, "Response missing 'response_time_ms' field"

        # Verify response types
        assert isinstance(data["answer"], str), "Answer should be a string"
        assert isinstance(data["sources"], list), "Sources should be a list"
        assert isinstance(data["session_id"], str), "Session ID should be a string"
        assert isinstance(data["response_time_ms"], int), "Response time should be an integer"

        # Verify answer is not empty
        assert len(data["answer"]) > 0, "Answer should not be empty"

        # Verify response time is under target (<3000ms)
        assert data["response_time_ms"] < 3000, f"Response time {data['response_time_ms']}ms exceeds 3000ms target"

        # Verify sources structure
        if len(data["sources"]) > 0:
            first_source = data["sources"][0]
            assert "module_id" in first_source, "Source missing 'module_id'"
            assert "chapter_id" in first_source, "Source missing 'chapter_id'"
            assert "section_title" in first_source, "Source missing 'section_title'"
            assert "url" in first_source, "Source missing 'url'"
            assert "relevance_score" in first_source, "Source missing 'relevance_score'"

            # Verify source values are not empty
            assert len(first_source["module_id"]) > 0, "module_id should not be empty"
            assert len(first_source["chapter_id"]) > 0, "chapter_id should not be empty"
            assert first_source["url"].startswith("/docs/"), "URL should start with /docs/"

        print(f"\n✅ Chat endpoint test passed!")
        print(f"   Response time: {data['response_time_ms']}ms")
        print(f"   Sources returned: {len(data['sources'])}")
        print(f"   Session ID: {data['session_id']}")


@pytest.mark.asyncio
async def test_chat_endpoint_with_session():
    """
    Test POST /chat with existing session_id

    Verifies:
    - Session ID is preserved across multiple requests
    - Responses are consistent
    """
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # First request - get session ID
        request1 = {"question": "What is a ROS 2 node?"}
        response1 = await client.post(f"{BASE_URL}/chat", json=request1)
        assert response1.status_code == 200

        data1 = response1.json()
        session_id = data1["session_id"]

        # Second request - use same session ID
        request2 = {
            "question": "How do nodes communicate?",
            "session_id": session_id
        }
        response2 = await client.post(f"{BASE_URL}/chat", json=request2)
        assert response2.status_code == 200

        data2 = response2.json()

        # Verify session ID is preserved
        assert data2["session_id"] == session_id, "Session ID should be preserved"

        print(f"\n✅ Session persistence test passed!")
        print(f"   Session ID maintained: {session_id}")


@pytest.mark.asyncio
async def test_chat_endpoint_validation():
    """
    Test POST /chat input validation

    Verifies:
    - Empty question returns 400
    - Missing question returns 422
    - Question too long returns 400
    """
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Test empty question
        response = await client.post(
            f"{BASE_URL}/chat",
            json={"question": ""}
        )
        assert response.status_code == 400, "Empty question should return 400"

        # Test missing question
        response = await client.post(
            f"{BASE_URL}/chat",
            json={}
        )
        assert response.status_code == 422, "Missing question should return 422"

        # Test question too long (>1000 chars)
        long_question = "x" * 1001
        response = await client.post(
            f"{BASE_URL}/chat",
            json={"question": long_question}
        )
        assert response.status_code == 422, "Question >1000 chars should return 422"

        print(f"\n✅ Validation test passed!")


@pytest.mark.asyncio
async def test_chat_selected_text_endpoint():
    """
    Test POST /chat/selected endpoint for selected text queries

    Verifies:
    - Endpoint accepts question and selected_text
    - Returns valid response structure
    - Response time is under 3000ms
    """
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        request_payload = {
            "question": "Explain this concept in simple terms",
            "selected_text": "A ROS 2 node is a fundamental execution unit that encapsulates computation logic and communicates with other nodes via topics, services, and actions."
        }

        response = await client.post(
            f"{BASE_URL}/chat/selected",
            json=request_payload,
        )

        # Verify status code
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        # Parse response
        data = response.json()

        # Verify response structure
        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data
        assert "response_time_ms" in data

        # Verify response time
        assert data["response_time_ms"] < 3000, f"Response time {data['response_time_ms']}ms exceeds 3000ms"

        # Verify answer is not empty
        assert len(data["answer"]) > 0, "Answer should not be empty"

        print(f"\n✅ Selected text endpoint test passed!")
        print(f"   Response time: {data['response_time_ms']}ms")


@pytest.mark.asyncio
async def test_health_endpoint():
    """
    Test GET /health endpoint

    Verifies:
    - Endpoint returns 200
    - Response contains status and dependencies
    """
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(f"{BASE_URL}/health")

        assert response.status_code == 200, f"Health check should return 200"

        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

        print(f"\n✅ Health endpoint test passed!")


if __name__ == "__main__":
    print("🧪 Running integration tests for chat endpoints...")
    print("⚠️  Make sure the FastAPI server is running on http://localhost:8000")
    print("⚠️  Make sure Qdrant and Postgres are connected")
    print("⚠️  Make sure chapters are indexed\n")

    # Run tests
    asyncio.run(test_health_endpoint())
    asyncio.run(test_chat_endpoint_general_qa())
    asyncio.run(test_chat_endpoint_with_session())
    asyncio.run(test_chat_endpoint_validation())
    asyncio.run(test_chat_selected_text_endpoint())

    print("\n" + "=" * 60)
    print("✅ All integration tests passed!")
    print("=" * 60)
