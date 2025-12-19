"""
Chapter Indexing Script
Indexes all textbook chapters into Qdrant vector database
Usage: python scripts/index_chapters.py --docs-dir ../docs
"""

import asyncio
import sys
import os
import argparse
from pathlib import Path
import uuid
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import db, qdrant
from src.services.embedding_service import generate_embeddings_batch
from src.services.indexing_service import (
    create_indexing_job,
    start_indexing_job,
    complete_indexing_job,
    fail_indexing_job,
    get_indexing_status,
)
from scripts.chunk_textbook import chunk_markdown_content
from qdrant_client.models import PointStruct


async def index_chapter(chapter_path: Path, module_id: str, chapter_id: str):
    """
    Index a single chapter into Qdrant

    Args:
        chapter_path: Path to markdown file
        module_id: Module identifier
        chapter_id: Chapter identifier
    """
    job_id = f"{module_id}-{chapter_id}"

    try:
        await create_indexing_job(job_id)
        await start_indexing_job(job_id)

        print(f"\n📄 Processing {job_id}...")

        # Read chapter content
        with open(chapter_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Chunk content
        chunks = chunk_markdown_content(
            content=content,
            module_id=module_id,
            chapter_id=chapter_id,
            min_chunk_chars=1000,  # ~500 tokens
            max_chunk_chars=2000,  # ~1000 tokens
        )

        if not chunks:
            print(f"  ⚠️  No chunks generated for {job_id}")
            await fail_indexing_job(job_id, "No chunks generated")
            return

        print(f"  ✓ Generated {len(chunks)} chunks")

        # Generate embeddings in batches
        print(f"  🔄 Generating embeddings...")
        chunk_texts = [chunk["content"] for chunk in chunks]

        # Process in batches of 50
        batch_size = 50
        all_embeddings = []

        for i in range(0, len(chunk_texts), batch_size):
            batch = chunk_texts[i : i + batch_size]
            batch_embeddings = await generate_embeddings_batch(batch)
            all_embeddings.extend(batch_embeddings)
            print(f"     Processed {min(i + batch_size, len(chunk_texts))}/{len(chunk_texts)} embeddings")

        print(f"  ✓ Generated {len(all_embeddings)} embeddings")

        # Create points for Qdrant
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, all_embeddings)):
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "content": chunk["content"],
                    "module_id": chunk["module_id"],
                    "chapter_id": chunk["chapter_id"],
                    "section_title": chunk["section_title"],
                    "content_type": chunk["content_type"],
                    "page_number": i + 1,  # Simple page numbering
                },
            )
            points.append(point)

        # Upload to Qdrant
        print(f"  🔄 Uploading to Qdrant...")
        await qdrant.upsert_points(points)

        print(f"  ✓ Uploaded {len(points)} points to Qdrant")

        # Mark job complete
        await complete_indexing_job(job_id, len(chunks))
        print(f"  ✅ {job_id} indexed successfully")

    except Exception as e:
        print(f"  ✗ Error indexing {job_id}: {e}")
        await fail_indexing_job(job_id, str(e))
        raise


async def index_all_chapters(docs_dir: str):
    """
    Index all chapters from docs directory

    Args:
        docs_dir: Path to docs directory containing markdown files
    """
    start_time = datetime.now()

    print("🚀 Starting chapter indexing...")
    print(f"📁 Docs directory: {docs_dir}\n")

    # Connect to services
    await db.connect()
    await qdrant.connect()
    await qdrant.create_collection_if_not_exists()

    # Find all markdown files
    docs_path = Path(docs_dir)

    if not docs_path.exists():
        print(f"✗ Docs directory not found: {docs_dir}")
        return

    # Expected structure: docs/module-X-name/chapter-Y.md
    chapters = []

    for module_dir in sorted(docs_path.iterdir()):
        if not module_dir.is_dir() or not module_dir.name.startswith("module-"):
            continue

        module_id = module_dir.name.split("-")[0] + "-" + module_dir.name.split("-")[1]  # e.g., module-1

        for chapter_file in sorted(module_dir.glob("chapter-*.md")):
            chapter_id = chapter_file.stem  # e.g., chapter-1
            chapters.append((chapter_file, module_id, chapter_id))

    if not chapters:
        print("✗ No chapters found in docs directory")
        print(f"  Expected structure: {docs_dir}/module-X-name/chapter-Y.md")
        return

    print(f"📚 Found {len(chapters)} chapters to index\n")

    # Index each chapter
    success_count = 0
    fail_count = 0

    for chapter_path, module_id, chapter_id in chapters:
        try:
            await index_chapter(chapter_path, module_id, chapter_id)
            success_count += 1
        except Exception as e:
            print(f"✗ Failed to index {chapter_path}: {e}")
            fail_count += 1

    # Print summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "=" * 60)
    print("📊 INDEXING SUMMARY")
    print("=" * 60)
    print(f"Total chapters: {len(chapters)}")
    print(f"✅ Successful: {success_count}")
    print(f"✗ Failed: {fail_count}")
    print(f"⏱️  Duration: {duration:.1f} seconds")

    # Get collection stats
    stats = await qdrant.get_collection_info()
    print(f"\n📦 Qdrant Collection Stats:")
    print(f"   Total vectors: {stats['vectors_count']}")
    print(f"   Indexed vectors: {stats['indexed_vectors_count']}")
    print(f"   Total points: {stats['points_count']}")

    # Show indexing status
    print(f"\n📋 Indexing Jobs Status:")
    statuses = await get_indexing_status()
    for status in statuses[:10]:  # Show last 10
        print(f"   {status['chapter_id']}: {status['status']} ({status['chunks_indexed']} chunks)")

    await db.disconnect()


def main():
    parser = argparse.ArgumentParser(description="Index textbook chapters into Qdrant")
    parser.add_argument(
        "--docs-dir",
        type=str,
        default="../docs",
        help="Path to docs directory (default: ../docs)",
    )

    args = parser.parse_args()

    # Run indexing
    asyncio.run(index_all_chapters(args.docs_dir))


if __name__ == "__main__":
    main()
