"""
Load Test for Chat Endpoint
Tests concurrent request handling with 10 simultaneous requests
"""

import asyncio
import httpx
import time
from typing import List, Dict
import statistics

# Test configuration
BASE_URL = "http://localhost:8000"
CONCURRENT_REQUESTS = 10
TIMEOUT = 10.0  # 10 seconds for load testing


async def send_chat_request(
    client: httpx.AsyncClient,
    question: str,
    request_id: int
) -> Dict:
    """
    Send a single chat request and measure response time

    Args:
        client: HTTP client
        question: Question to ask
        request_id: Request identifier for tracking

    Returns:
        Dict with request_id, success, response_time_ms, status_code
    """
    start_time = time.time()

    try:
        response = await client.post(
            f"{BASE_URL}/chat",
            json={"question": question},
        )

        elapsed_ms = int((time.time() - start_time) * 1000)

        return {
            "request_id": request_id,
            "success": response.status_code == 200,
            "response_time_ms": elapsed_ms,
            "status_code": response.status_code,
            "error": None if response.status_code == 200 else response.text,
        }

    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        return {
            "request_id": request_id,
            "success": False,
            "response_time_ms": elapsed_ms,
            "status_code": None,
            "error": str(e),
        }


async def run_load_test(num_requests: int = CONCURRENT_REQUESTS):
    """
    Run load test with concurrent requests

    Args:
        num_requests: Number of concurrent requests to send

    Returns:
        List of result dictionaries
    """
    print(f"\n🚀 Starting load test with {num_requests} concurrent requests...")
    print(f"📍 Target URL: {BASE_URL}/chat")
    print(f"⏱️  Timeout: {TIMEOUT}s\n")

    # Test questions (diverse to avoid caching)
    questions = [
        "What is ROS 2?",
        "Explain robot kinematics",
        "How does path planning work?",
        "What are actuators in robotics?",
        "Describe sensor fusion",
        "What is SLAM?",
        "Explain PID control",
        "What is inverse kinematics?",
        "How do humanoid robots balance?",
        "What is computer vision in robotics?",
    ]

    # Create HTTP client with connection pooling
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Create tasks for concurrent requests
        tasks = [
            send_chat_request(
                client,
                questions[i % len(questions)],
                i + 1
            )
            for i in range(num_requests)
        ]

        # Execute all requests concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

    return results, total_time


def analyze_results(results: List[Dict], total_time: float):
    """
    Analyze and print load test results

    Args:
        results: List of result dictionaries
        total_time: Total execution time in seconds
    """
    print("=" * 70)
    print("📊 LOAD TEST RESULTS")
    print("=" * 70)

    # Count successes and failures
    successes = [r for r in results if r["success"]]
    failures = [r for r in results if not r["success"]]

    print(f"\n📈 Summary:")
    print(f"   Total requests: {len(results)}")
    print(f"   Successful: {len(successes)} ({len(successes)/len(results)*100:.1f}%)")
    print(f"   Failed: {len(failures)} ({len(failures)/len(results)*100:.1f}%)")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Requests per second: {len(results)/total_time:.2f}")

    # Response time statistics (for successful requests)
    if successes:
        response_times = [r["response_time_ms"] for r in successes]
        print(f"\n⏱️  Response Time Statistics (successful requests):")
        print(f"   Min: {min(response_times)}ms")
        print(f"   Max: {max(response_times)}ms")
        print(f"   Mean: {statistics.mean(response_times):.0f}ms")
        print(f"   Median: {statistics.median(response_times):.0f}ms")
        print(f"   p95: {sorted(response_times)[int(len(response_times)*0.95)]}ms")
        print(f"   p99: {sorted(response_times)[int(len(response_times)*0.99)]}ms")

        # Check if p95 is under 3000ms target
        p95 = sorted(response_times)[int(len(response_times)*0.95)]
        if p95 < 3000:
            print(f"   ✅ p95 ({p95}ms) is under 3000ms target")
        else:
            print(f"   ❌ p95 ({p95}ms) exceeds 3000ms target")

    # List failures if any
    if failures:
        print(f"\n❌ Failed Requests:")
        for fail in failures:
            print(f"   Request #{fail['request_id']}: {fail['status_code']} - {fail['error']}")

    # Individual request details
    print(f"\n📋 Individual Request Times:")
    for r in sorted(results, key=lambda x: x["request_id"]):
        status = "✅" if r["success"] else "❌"
        print(f"   {status} Request #{r['request_id']:2d}: {r['response_time_ms']:4d}ms")

    print("\n" + "=" * 70)

    # Overall verdict
    success_rate = len(successes) / len(results)
    if success_rate == 1.0 and (not successes or sorted([r["response_time_ms"] for r in successes])[int(len(successes)*0.95)] < 3000):
        print("✅ LOAD TEST PASSED")
        print("   All requests succeeded and p95 response time is under 3000ms")
    elif success_rate >= 0.9:
        print("⚠️  LOAD TEST PARTIAL PASS")
        print(f"   {success_rate*100:.1f}% success rate (>90% threshold)")
    else:
        print("❌ LOAD TEST FAILED")
        print(f"   {success_rate*100:.1f}% success rate (<90% threshold)")

    print("=" * 70)


async def test_rate_limiting():
    """
    Test rate limiting (10 requests/minute per IP)

    Sends 15 requests rapidly and checks if rate limiting kicks in
    """
    print(f"\n🔒 Testing rate limiting (10 requests/minute)...")

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        tasks = [
            send_chat_request(client, "What is ROS 2?", i + 1)
            for i in range(15)  # Send 15 requests (should hit rate limit)
        ]

        results = await asyncio.gather(*tasks)

    # Count 429 responses (rate limited)
    rate_limited = [r for r in results if r["status_code"] == 429]

    print(f"   Total requests sent: 15")
    print(f"   Rate limited (429): {len(rate_limited)}")

    if len(rate_limited) >= 5:
        print(f"   ✅ Rate limiting is working (expected ~5 requests blocked)")
    else:
        print(f"   ⚠️  Rate limiting may not be working as expected")


if __name__ == "__main__":
    print("🧪 RAG Chatbot Backend - Load Testing")
    print("=" * 70)
    print("⚠️  Prerequisites:")
    print("   - FastAPI server running on http://localhost:8000")
    print("   - Qdrant and Postgres connected")
    print("   - Chapters indexed in Qdrant")
    print("   - OpenAI API key configured")
    print("=" * 70)

    # Run main load test
    results, total_time = asyncio.run(run_load_test(CONCURRENT_REQUESTS))
    analyze_results(results, total_time)

    # Run rate limiting test
    asyncio.run(test_rate_limiting())

    print("\n🏁 Load testing complete!")
