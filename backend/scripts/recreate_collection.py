"""
Recreate Qdrant Collection Script
Deletes old collection and creates new one with correct FastEmbed dimensions (384)
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import qdrant
from qdrant_client.models import Distance, VectorParams
from src.config import settings


async def recreate_collection():
    """Delete old collection and create new one with FastEmbed dimensions"""
    print("\n" + "="*70)
    print("  Recreating Qdrant Collection for FastEmbed (384-dim)")
    print("="*70)

    await qdrant.connect()

    # Delete old collection if it exists
    try:
        qdrant.client.get_collection(qdrant.collection_name)
        print(f"\n[INFO] Deleting old collection '{qdrant.collection_name}'...")
        qdrant.client.delete_collection(qdrant.collection_name)
        print(f"[OK] Collection deleted successfully")
    except Exception as e:
        print(f"[INFO] Collection doesn't exist yet (this is fine)")

    # Create new collection with 384 dimensions
    print(f"\n[INFO] Creating new collection with {settings.qdrant_vector_size} dimensions...")
    qdrant.client.create_collection(
        collection_name=qdrant.collection_name,
        vectors_config=VectorParams(
            size=settings.qdrant_vector_size,  # 384 for FastEmbed
            distance=Distance.COSINE,
        ),
    )
    print(f"[OK] Collection '{qdrant.collection_name}' created successfully")

    # Verify collection info
    info = await qdrant.get_collection_info()
    print(f"\nCollection Info:")
    print(f"   Vector size: {settings.qdrant_vector_size}")
    print(f"   Distance metric: COSINE")
    print(f"   Total points: {info['points_count']}")

    print("\n" + "="*70)
    print("  Collection Ready for Indexing!")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(recreate_collection())
