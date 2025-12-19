"""
Chat API Endpoints
Implements POST /chat for general Q&A and POST /chat/selected for selected text queries
"""

from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse
import time

from src.models.requests import ChatRequest, SelectedTextRequest
from src.models.responses import ChatResponse
from src.services.rag_pipeline import process_question, process_selected_text_query
from src.services.session_service import create_session, session_exists, update_last_activity
from src.middleware.rate_limiter import limiter

router = APIRouter()


@router.post("", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat_general(request: Request, chat_request: ChatRequest):
    """
    General textbook Q&A endpoint

    Rate Limit: 10 requests/minute per IP
    Response Time Target: <3 seconds (95th percentile)

    Args:
        chat_request: ChatRequest with question and optional session_id

    Returns:
        ChatResponse with answer, sources, session_id, timestamp, response_time_ms

    Errors:
        400: Invalid request (question too long, empty, etc.)
        429: Rate limit exceeded
        500: Internal server error
        503: Service unavailable (OpenAI or Qdrant down)
    """
    try:
        # Validate and sanitize input
        question = chat_request.question.strip()

        if not question:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question cannot be empty",
            )

        # Handle session management
        session_id = chat_request.session_id

        if session_id:
            # Verify session exists
            if not await session_exists(session_id):
                # Create new session if doesn't exist
                session_id = await create_session()
            else:
                # Update last activity
                await update_last_activity(session_id)
        else:
            # Create new session
            session_id = await create_session()

        # Process question through RAG pipeline
        result = await process_question(
            question=question,
            session_id=session_id,
        )

        return ChatResponse(**result)

    except ValueError as e:
        # Validation errors or RAG pipeline errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        print(f"✗ Chat endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred processing your question. Please try again.",
        )


@router.post("/selected", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat_selected_text(request: Request, selected_request: SelectedTextRequest):
    """
    Selected text query endpoint

    Processes questions about specific text snippets selected by user

    Rate Limit: 10 requests/minute per IP
    Response Time Target: <3 seconds (95th percentile)

    Args:
        selected_request: SelectedTextRequest with question, selected_text, optional session_id

    Returns:
        ChatResponse with answer, sources, session_id, timestamp, response_time_ms

    Errors:
        400: Invalid request
        429: Rate limit exceeded
        500: Internal server error
        503: Service unavailable
    """
    try:
        # Validate input
        question = selected_request.question.strip()
        selected_text = selected_request.selected_text.strip()

        if not question or not selected_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both question and selected text are required",
            )

        # Handle session
        session_id = selected_request.session_id

        if session_id:
            if not await session_exists(session_id):
                session_id = await create_session()
            else:
                await update_last_activity(session_id)
        else:
            session_id = await create_session()

        # Process selected text query
        result = await process_selected_text_query(
            question=question,
            selected_text=selected_text,
            session_id=session_id,
        )

        return ChatResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        print(f"✗ Selected text endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred processing your selected text query. Please try again.",
        )
