"""
Qdrant Cloud client configuration for vector search
Manages vector embeddings for textbook chunks
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Optional
from src.config import settings
import uuid


class QdrantConnection:
    """Manages Qdrant Cloud connection and operations"""

    def __init__(self):
        self.client: Optional[QdrantClient] = None
        self.collection_name = settings.qdrant_collection_name

    async def connect(self):
        """Initialize Qdrant client"""
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=30,
        )

        # Verify connection
        try:
            collections = self.client.get_collections()
            print(f"[OK] Connected to Qdrant Cloud ({len(collections.collections)} collections)")
        except Exception as e:
            print(f"[ERROR] Qdrant connection failed: {e}")
            raise

    async def create_collection_if_not_exists(self):
        """Create collection if it doesn't exist"""
        try:
            self.client.get_collection(self.collection_name)
            print(f"[OK] Collection '{self.collection_name}' already exists")
        except:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=settings.qdrant_vector_size,
                    distance=Distance.COSINE,
                ),
            )
            print(f"[OK] Created collection '{self.collection_name}'")

    async def upsert_points(self, points: List[PointStruct]):
        """Insert or update points in collection"""
        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

    async def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: Optional[float] = None,
    ) -> List[Dict]:
        """Search for similar vectors"""
        search_params = {
            "collection_name": self.collection_name,
            "query_vector": query_vector,
            "limit": limit,
        }

        if score_threshold:
            search_params["score_threshold"] = score_threshold

        results = self.client.search(**search_params)

        return [
            {
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload,
            }
            for hit in results
        ]

    async def get_collection_info(self) -> Dict:
        """Get collection statistics"""
        info = self.client.get_collection(self.collection_name)
        return {
            "points_count": info.points_count,
            "indexed_vectors_count": info.indexed_vectors_count,
            "points_count": info.points_count,
        }


# Global Qdrant connection instance
qdrant = QdrantConnection()
