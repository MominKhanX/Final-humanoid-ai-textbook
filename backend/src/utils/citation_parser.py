"""
Citation Parser
Extracts and formats citations from retrieved textbook chunks
"""

from typing import List, Dict
from src.models.responses import CitationSource


def extract_citations(retrieved_chunks: List[Dict]) -> List[CitationSource]:
    """
    Convert retrieved chunks into formatted citation sources

    Args:
        retrieved_chunks: List of chunks from vector search with metadata

    Returns:
        List of CitationSource objects
    """
    citations = []
    seen_sources = set()  # Avoid duplicate citations

    for chunk in retrieved_chunks:
        # Create unique key for deduplication
        source_key = f"{chunk['module_id']}/{chunk['chapter_id']}/{chunk['section_title']}"

        if source_key not in seen_sources:
            # Build URL to cited content
            # Format: /docs/module-1-ros2/chapter-1#section-slug
            module_slug = chunk['module_id'].replace('module-', 'module-')
            chapter_slug = chunk['chapter_id'].replace('chapter-', 'chapter-')
            section_slug = chunk['section_title'].lower().replace(' ', '-').replace('/', '-')

            url = f"/docs/{module_slug}/{chapter_slug}#{section_slug}"

            citation = CitationSource(
                module_id=chunk['module_id'],
                chapter_id=chunk['chapter_id'],
                section_title=chunk['section_title'],
                url=url,
                relevance_score=round(chunk['score'], 2) if 'score' in chunk else None,
            )

            citations.append(citation)
            seen_sources.add(source_key)

    return citations


def format_citation_text(citation: CitationSource) -> str:
    """
    Format citation as human-readable text

    Args:
        citation: CitationSource object

    Returns:
        Formatted string like "[Module 1, Chapter 2: Section Title]"
    """
    module_num = citation.module_id.replace('module-', '')
    chapter_num = citation.chapter_id.replace('chapter-', '')

    return f"[Module {module_num}, Chapter {chapter_num}: {citation.section_title}]"


def deduplicate_citations(citations: List[CitationSource]) -> List[CitationSource]:
    """
    Remove duplicate citations, keeping highest relevance scores

    Args:
        citations: List of citations that may contain duplicates

    Returns:
        Deduplicated list of citations
    """
    seen = {}

    for citation in citations:
        key = f"{citation.module_id}/{citation.chapter_id}/{citation.section_title}"

        if key not in seen:
            seen[key] = citation
        elif citation.relevance_score and seen[key].relevance_score:
            # Keep citation with higher relevance score
            if citation.relevance_score > seen[key].relevance_score:
                seen[key] = citation

    return list(seen.values())
