"""
Request Models for API Endpoints
Pydantic models for request validation
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ChatRequest(BaseModel):
    """Request model for general Q&A endpoint"""

    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User's question about textbook content",
    )
    session_id: Optional[str] = Field(
        None,
        description="Optional session ID for conversation continuity",
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        """Validate and sanitize question"""
        v = v.strip()
        if not v:
            raise ValueError("Question cannot be empty")
        if len(v) > 1000:
            raise ValueError("Question must be 1000 characters or less")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "question": "What is a ROS 2 node?",
                    "session_id": None,
                },
                {
                    "question": "How does it communicate with other nodes?",
                    "session_id": "550e8400-e29b-41d4-a716-446655440000",
                },
            ]
        }
    }


class SelectedTextRequest(BaseModel):
    """Request model for selected text query endpoint"""

    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User's question about the selected text",
    )
    selected_text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Text snippet selected by user",
    )
    session_id: Optional[str] = Field(
        None,
        description="Optional session ID for conversation continuity",
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        """Validate and sanitize question"""
        v = v.strip()
        if not v:
            raise ValueError("Question cannot be empty")
        if len(v) > 1000:
            raise ValueError("Question must be 1000 characters or less")
        return v

    @field_validator("selected_text")
    @classmethod
    def validate_selected_text(cls, v: str) -> str:
        """Validate and potentially truncate selected text"""
        v = v.strip()
        if not v:
            raise ValueError("Selected text cannot be empty")
        if len(v) > 5000:
            # Truncate intelligently - keep beginning and end
            v = v[:2000] + "\n... [truncated] ...\n" + v[-500:]
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "question": "What does this function do?",
                    "selected_text": "def process_sensor_data(msg):\\n    return msg.data * 2",
                    "session_id": None,
                }
            ]
        }
    }
