"""
RAG Pipeline Service
Orchestrates the complete Retrieval-Augmented Generation workflow:
1. Generate question embedding
2. Search vector database for relevant chunks
3. Generate answer with GPT-4 using retrieved context
4. Extract and format citations
"""

from typing import Dict, Optional, List
import time

from src.services.embedding_service import generate_query_embedding
from src.services.vector_search_service import search_similar_chunks
from src.services.llm_service import generate_answer, detect_out_of_scope
from src.utils.prompt_templates import get_system_prompt, OUT_OF_SCOPE_RESPONSE
from src.utils.citation_parser import extract_citations, deduplicate_citations
from src.models.responses import ChatResponse, CitationSource


async def process_question(
    question: str,
    session_id: Optional[str] = None,
    conversation_history: Optional[List[Dict]] = None,
) -> Dict:
    """
    Process a user question through the complete RAG pipeline

    Args:
        question: User's question
        session_id: Optional session ID for tracking
        conversation_history: Optional previous conversation context

    Returns:
        Dictionary with answer, sources, session_id, timestamp, response_time_ms

    Pipeline Steps:
        1. Check if question is in-scope (< 200ms)
        2. Generate question embedding (~200ms)
        3. Search vector database (~100ms)
        4. Generate answer with GPT-4 (~1500ms)
        5. Extract and format citations (~10ms)

    Total expected time: ~1.8 seconds (within <3s requirement)
    """
    start_time = time.time()

    try:
        # Step 1: Check if question is in scope (optional optimization)
        # Commented out to save ~200ms, can enable for better UX
        # is_out_of_scope = await detect_out_of_scope(question)
        # if is_out_of_scope:
        #     return _build_out_of_scope_response(session_id, start_time)

        # Step 2: Generate embedding for question (~200ms)
        query_embedding = await generate_query_embedding(question)

        # Step 3: Search for relevant chunks (~100ms)
        # Retrieve top 15 chunks with lower threshold for better coverage
        retrieved_chunks = await search_similar_chunks(
            query_embedding=query_embedding,
            top_k=15,
            score_threshold=0.6,
        )

        # Even if no chunks found, let LLM handle it gracefully
        # (it will provide friendly redirect for off-topic questions)

        # Step 4: Generate answer with GPT-4 (~1500ms)
        system_prompt = get_system_prompt("general")
        answer = await generate_answer(
            system_prompt=system_prompt,
            user_question=question,
            context_chunks=retrieved_chunks,
            conversation_history=conversation_history,
        )

        # Step 5: Extract and format citations (~10ms)
        citations = extract_citations(retrieved_chunks)
        citations = deduplicate_citations(citations)

        # Calculate response time
        end_time = time.time()
        response_time_ms = int((end_time - start_time) * 1000)

        return {
            "answer": answer,
            "sources": [citation.model_dump() for citation in citations],
            "session_id": session_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
            "response_time_ms": response_time_ms,
        }

    except Exception as e:
        print(f"[ERROR] RAG pipeline error: {e}")
        raise ValueError(f"Failed to process question: {str(e)}")


async def process_selected_text_query(
    question: str,
    selected_text: str,
    session_id: Optional[str] = None,
) -> Dict:
    """
    Process a question about selected text through RAG pipeline

    Args:
        question: User's question about the selected text
        selected_text: Text snippet selected by user
        session_id: Optional session ID

    Returns:
        Dictionary with answer, sources, session_id, timestamp, response_time_ms
    """
    start_time = time.time()

    try:
        # Combine question and selected text for embedding
        combined_query = f"{selected_text}\n\nQuestion: {question}"
        query_embedding = await generate_query_embedding(combined_query)

        # Search for relevant chunks (more context for selected text queries)
        retrieved_chunks = await search_similar_chunks(
            query_embedding=query_embedding,
            top_k=10,
            score_threshold=0.6,  # Lower threshold for better coverage
        )

        if not retrieved_chunks:
            # Fall back to just the selected text as context
            retrieved_chunks = [
                {
                    "content": selected_text,
                    "module_id": "selected",
                    "chapter_id": "text",
                    "section_title": "User Selection",
                    "score": 1.0,
                }
            ]

        # Generate answer with selected text context
        system_prompt = get_system_prompt("selected_text")

        # Add selected text to context
        context_with_selection = [
            {
                "content": f"SELECTED TEXT:\n{selected_text}\n\nADDITIONAL CONTEXT:",
                "module_id": "selected",
                "chapter_id": "text",
                "section_title": "User Selection",
            }
        ] + retrieved_chunks

        answer = await generate_answer(
            system_prompt=system_prompt,
            user_question=question,
            context_chunks=context_with_selection,
        )

        # Extract citations (excluding the selected text entry)
        citations = extract_citations([c for c in retrieved_chunks if c.get("module_id") != "selected"])
        citations = deduplicate_citations(citations)

        end_time = time.time()
        response_time_ms = int((end_time - start_time) * 1000)

        return {
            "answer": answer,
            "sources": [citation.model_dump() for citation in citations],
            "session_id": session_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
            "response_time_ms": response_time_ms,
        }

    except Exception as e:
        print(f"[ERROR] Selected text query error: {e}")
        raise ValueError(f"Failed to process selected text query: {str(e)}")


def _build_out_of_scope_response(session_id: Optional[str], start_time: float) -> Dict:
    """Build response for out-of-scope questions"""
    end_time = time.time()
    response_time_ms = int((end_time - start_time) * 1000)

    return {
        "answer": OUT_OF_SCOPE_RESPONSE,
        "sources": [],
        "session_id": session_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
        "response_time_ms": response_time_ms,
    }


def _build_no_results_response(session_id: Optional[str], start_time: float) -> Dict:
    """Build friendly response when no relevant chunks found - this should rarely happen"""
    end_time = time.time()
    response_time_ms = int((end_time - start_time) * 1000)

    return {
        "answer": "I'm NeuroBot, your friendly assistant for the Physical AI & Humanoid Robotics textbook, and I can't answer any other stuff out of the book! I can help with ROS 2, simulation, Isaac Sim, VLA models, and everything in the book. What would you like to learn about?",
        "sources": [],
        "session_id": session_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
        "response_time_ms": response_time_ms,
    }
