"""
Qdrant Vector Search Service
Performs semantic search for relevant textbook chunks
"""

from typing import List, Dict, Optional
from src.database.qdrant_client import qdrant
from src.config import settings


async def search_similar_chunks(
    query_embedding: List[float],
    top_k: int = None,
    score_threshold: Optional[float] = None,
) -> List[Dict]:
    """
    Search for similar textbook chunks using vector similarity

    Args:
        query_embedding: 1536-dimensional query vector
        top_k: Number of results to return (default from settings)
        score_threshold: Minimum similarity score (default from settings)

    Returns:
        List of dictionaries containing chunk data and metadata:
        [
            {
                "id": "chunk_uuid",
                "score": 0.92,
                "content": "textbook content...",
                "module_id": "module-1",
                "chapter_id": "chapter-1",
                "section_title": "ROS 2 Nodes",
                "content_type": "text",
                "page_number": 12
            },
            ...
        ]
    """
    if top_k is None:
        top_k = settings.rag_top_k

    if score_threshold is None:
        score_threshold = settings.rag_relevance_threshold

    try:
        results = await qdrant.search(
            query_vector=query_embedding,
            limit=top_k,
            score_threshold=score_threshold,
        )

        # Format results for RAG pipeline
        formatted_results = []
        for hit in results:
            formatted_results.append(
                {
                    "id": hit["id"],
                    "score": hit["score"],
                    "content": hit["payload"].get("content", ""),
                    "module_id": hit["payload"].get("module_id", ""),
                    "chapter_id": hit["payload"].get("chapter_id", ""),
                    "section_title": hit["payload"].get("section_title", ""),
                    "content_type": hit["payload"].get("content_type", "text"),
                    "page_number": hit["payload"].get("page_number"),
                }
            )

        return formatted_results
    except Exception as e:
        print(f"✗ Vector search failed: {e}")
        raise ValueError(f"Failed to search similar chunks: {str(e)}")


async def get_collection_stats() -> Dict:
    """Get statistics about the vector collection"""
    try:
        info = await qdrant.get_collection_info()
        return {
            "total_vectors": info["points_count"],
            "indexed_vectors": info["indexed_vectors_count"],
            "total_points": info["points_count"],
        }
    except Exception as e:
        print(f"✗ Failed to get collection stats: {e}")
        return {"error": str(e)}
