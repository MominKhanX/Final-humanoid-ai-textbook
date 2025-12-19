"""
Google Gemini Chat Service (FREE!)
Generates answers using Gemini 1.5 Flash - fast, free, and high quality
"""

import google.generativeai as genai
from typing import List, Dict, Optional
from src.config import settings

# Configure Gemini API
genai.configure(api_key=settings.gemini_api_key)

# Initialize Gemini model
model = genai.GenerativeModel(settings.gemini_chat_model)


async def generate_answer(
    system_prompt: str,
    user_question: str,
    context_chunks: List[Dict],
    conversation_history: Optional[List[Dict]] = None,
) -> str:
    """
    Generate answer using Gemini 1.5 Flash based on retrieved context

    Args:
        system_prompt: System instructions for the model
        user_question: User's question
        context_chunks: Retrieved textbook chunks with metadata
        conversation_history: Previous messages in conversation

    Returns:
        Generated answer text

    Raises:
        Exception: If Gemini API call fails
    """
    # Build context section from retrieved chunks
    context_section = "\n\n".join(
        [
            f"[Source: {chunk['module_id']}, {chunk['chapter_id']}, {chunk.get('section_title', 'N/A')}]\n{chunk['content']}"
            for chunk in context_chunks
        ]
    )

    # Build prompt (Gemini doesn't use separate system/user roles like OpenAI)
    full_prompt = f"""{system_prompt}

Context from textbook:
{context_section}

Question: {user_question}

Please provide a comprehensive answer based on the textbook content above. Include specific citations to the source materials (module, chapter, section) in your response."""

    try:
        # Generate response
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=settings.gemini_temperature,
                max_output_tokens=settings.gemini_max_tokens,
            )
        )

        return response.text
    except Exception as e:
        print(f"[ERROR] Gemini answer generation failed: {e}")
        raise ValueError(f"Failed to generate answer: {str(e)}")


async def detect_out_of_scope(question: str) -> bool:
    """
    Detect if question is outside textbook scope using Gemini

    Args:
        question: User's question

    Returns:
        True if question is out of scope, False otherwise
    """
    prompt = """You are a content moderator for a Physical AI & Humanoid Robotics textbook chatbot.
Determine if the following question is WITHIN the scope of:
- ROS 2 robotics framework
- Gazebo and Unity simulation
- NVIDIA Isaac Sim/Gym
- Vision-Language-Action models
- Humanoid robotics
- Physical AI concepts

Question: {question}

Respond with only "IN_SCOPE" or "OUT_OF_SCOPE".""".format(question=question)

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.0,
                max_output_tokens=10,
            )
        )

        result = response.text.strip()
        return result == "OUT_OF_SCOPE"
    except:
        # Default to in-scope if detection fails
        return False
