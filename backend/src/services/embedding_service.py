"""
Qdrant FastEmbed Service (FREE, Local, No API!)
Generates vector embeddings using FastEmbed's BAAI/bge-small-en-v1.5 model
384-dimensional embeddings, completely free, runs locally, no quotas
"""

from fastembed import TextEmbedding
from typing import List
from src.config import settings

# Initialize FastEmbed model (loads once, cached locally)
print("[INFO] Loading FastEmbed model (BAAI/bge-small-en-v1.5)...")
embedding_model = TextEmbedding(model_name=settings.fastembed_model)
print("[OK] FastEmbed model loaded successfully")


async def generate_embedding(text: str) -> List[float]:
    """
    Generate 384-dimensional embedding vector for text using FastEmbed

    Args:
        text: Input text to embed

    Returns:
        List of 384 floats representing the embedding vector

    Raises:
        Exception: If embedding generation fails
    """
    try:
        # FastEmbed returns a generator, convert to list
        embeddings = list(embedding_model.embed([text]))
        return embeddings[0].tolist()
    except Exception as e:
        print(f"[ERROR] FastEmbed embedding generation failed: {e}")
        raise ValueError(f"Failed to generate embedding: {str(e)}")


async def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts in batch

    Args:
        texts: List of input texts

    Returns:
        List of embedding vectors
    """
    try:
        # FastEmbed processes batches efficiently
        embeddings = list(embedding_model.embed(texts))
        return [emb.tolist() for emb in embeddings]
    except Exception as e:
        print(f"[ERROR] Batch embedding generation failed: {e}")
        raise ValueError(f"Failed to generate embeddings: {str(e)}")


async def generate_query_embedding(text: str) -> List[float]:
    """
    Generate embedding optimized for query (search) text

    Note: FastEmbed doesn't distinguish between document/query embeddings,
    but we keep this function for API compatibility

    Args:
        text: Query text to embed

    Returns:
        List of 384 floats representing the embedding vector
    """
    try:
        embeddings = list(embedding_model.embed([text]))
        return embeddings[0].tolist()
    except Exception as e:
        print(f"[ERROR] Query embedding generation failed: {e}")
        raise ValueError(f"Failed to generate query embedding: {str(e)}")
