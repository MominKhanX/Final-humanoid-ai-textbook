"""
Response Models for API Endpoints
Pydantic models for response serialization
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class CitationSource(BaseModel):
    """Citation source reference"""

    module_id: str = Field(..., description="Module identifier (e.g., module-1)")
    chapter_id: str = Field(..., description="Chapter identifier (e.g., chapter-1)")
    section_title: str = Field(..., description="Section title")
    url: str = Field(..., description="URL to cited content")
    relevance_score: Optional[float] = Field(
        None, description="Similarity score (0.0-1.0)"
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoints"""

    answer: str = Field(..., description="AI-generated answer")
    sources: List[CitationSource] = Field(
        ..., description="List of cited sources from textbook"
    )
    session_id: str = Field(..., description="Session UUID")
    timestamp: str = Field(..., description="ISO8601 timestamp")
    response_time_ms: int = Field(..., description="Response time in milliseconds")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "answer": "A ROS 2 node is a fundamental execution unit in the ROS 2 ecosystem. It's a process that performs computation and communicates with other nodes via topics, services, and actions.",
                    "sources": [
                        {
                            "module_id": "module-1",
                            "chapter_id": "chapter-1",
                            "section_title": "Understanding ROS 2 Nodes",
                            "url": "/docs/module-1-ros2/chapter-1#nodes",
                            "relevance_score": 0.92,
                        }
                    ],
                    "session_id": "550e8400-e29b-41d4-a716-446655440000",
                    "timestamp": "2025-12-17T10:30:00.000Z",
                    "response_time_ms": 2150,
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Error response model"""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    timestamp: float = Field(..., description="Unix timestamp")
    details: Optional[dict] = Field(None, description="Additional error details")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": "Validation error",
                    "message": "Question must be 1000 characters or less",
                    "timestamp": 1702814400.0,
                    "details": {"field": "question", "provided_length": 1250},
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """Health check response model"""

    status: str = Field(..., description="Overall health status")
    timestamp: float = Field(..., description="Unix timestamp")
    services: dict = Field(..., description="Individual service health statuses")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "healthy",
                    "timestamp": 1702814400.0,
                    "services": {
                        "postgres": "healthy",
                        "qdrant": {"status": "healthy", "points_count": 487},
                    },
                }
            ]
        }
    }
