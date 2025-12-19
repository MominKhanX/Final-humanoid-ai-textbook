"""
Textbook Content Chunking Script (Tiktoken-Free Version)
Intelligently chunks markdown content for vector embedding using character count
Target: ~1000-2000 characters per chunk (~500-1000 tokens approx)
"""

import re
from typing import List, Dict


def count_characters(text: str) -> int:
    """Simple character count as token approximation"""
    return len(text)


def chunk_markdown_content(
    content: str,
    module_id: str,
    chapter_id: str,
    min_chunk_chars: int = 1000,   # ~500 tokens
    max_chunk_chars: int = 2000,   # ~1000 tokens
) -> List[Dict]:
    """
    Chunk markdown content intelligently without tiktoken
    """
    chunks = []

    # Split by headers (##, ###) - captures header as separate item
    sections = re.split(r"(^#{2,3}\s+.+$)", content, flags=re.MULTILINE)

    current_section_title = "Introduction"
    current_content_parts = []
    current_chars = 0

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # If this part is a header
        if re.match(r"^#{2,3}\s+", section):
            # Save previous accumulated content as chunks
            if current_content_parts:
                chunks.extend(
                    _create_chunks_from_content(
                        current_content_parts,
                        module_id,
                        chapter_id,
                        current_section_title,
                        min_chunk_chars,
                        max_chunk_chars,
                    )
                )
                current_content_parts = []
                current_chars = 0

            # Update current section title
            current_section_title = re.sub(r"^#{2,3}\s+", "", section).strip()
        else:
            # Regular content - add to current section
            current_content_parts.append(section)

    # Don't forget the last section
    if current_content_parts:
        chunks.extend(
            _create_chunks_from_content(
                current_content_parts,
                module_id,
                chapter_id,
                current_section_title,
                min_chunk_chars,
                max_chunk_chars,
            )
        )

    return chunks


def _create_chunks_from_content(
    content_parts: List[str],
    module_id: str,
    chapter_id: str,
    section_title: str,
    min_chunk_chars: int,
    max_chunk_chars: int,
) -> List[Dict]:
    """Create properly sized chunks from accumulated content"""
    full_content = "\n\n".join(content_parts).strip()
    if not full_content:
        return []

    # Detect content type
    content_type = "text"
    if "```" in full_content:
        content_type = "code"
    elif "![" in full_content or "graph" in full_content.lower():
        content_type = "diagram"

    # Split into paragraphs
    paragraphs = re.split(r"\n\n+", full_content)

    chunks = []
    current_chunk_parts = []
    current_chars = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        para_chars = count_characters(para + "\n\n")  # include paragraph spacing

        # If paragraph alone is too big, split by sentences
        if para_chars > max_chunk_chars:
            if current_chunk_parts:
                chunk_text = "\n\n".join(current_chunk_parts).strip()
                if count_characters(chunk_text) >= min_chunk_chars:
                    chunks.append(_create_chunk_dict(chunk_text, module_id, chapter_id, section_title, content_type))

                current_chunk_parts = []
                current_chars = 0

            # Split large paragraph by sentences
            sentences = re.split(r"([.!?]+[\s\n]+)", para)
            temp_chunk = []
            temp_chars = 0
            for sent in sentences:
                if not sent.strip():
                    continue
                sent_chars = count_characters(sent)
                if temp_chars + sent_chars > max_chunk_chars and temp_chunk:
                    chunk_text = "".join(temp_chunk).strip()
                    chunks.append(_create_chunk_dict(chunk_text, module_id, chapter_id, section_title, content_type))
                    temp_chunk = []
                    temp_chars = 0
                temp_chunk.append(sent)
                temp_chars += sent_chars

            if temp_chunk:
                chunk_text = "".join(temp_chunk).strip()
                chunks.append(_create_chunk_dict(chunk_text, module_id, chapter_id, section_title, content_type))

        # Normal case: add to current chunk
        elif current_chars + para_chars > max_chunk_chars and current_chunk_parts:
            chunk_text = "\n\n".join(current_chunk_parts).strip()
            chunks.append(_create_chunk_dict(chunk_text, module_id, chapter_id, section_title, content_type))
            current_chunk_parts = [para]
            current_chars = para_chars
        else:
            current_chunk_parts.append(para)
            current_chars += para_chars

    # Final chunk (relaxed minimum for last chunk to avoid losing content)
    if current_chunk_parts:
        chunk_text = "\n\n".join(current_chunk_parts).strip()
        # Accept chunks that are at least 50% of minimum or if it's the only chunk
        if count_characters(chunk_text) >= (min_chunk_chars * 0.5) or not chunks:
            chunks.append(_create_chunk_dict(chunk_text, module_id, chapter_id, section_title, content_type))

    return chunks


def _create_chunk_dict(
    content: str,
    module_id: str,
    chapter_id: str,
    section_title: str,
    content_type: str,
) -> Dict:
    """Create final chunk dictionary"""
    return {
        "content": content,
        "module_id": module_id,
        "chapter_id": chapter_id,
        "section_title": section_title,
        "content_type": content_type,
        "char_count": count_characters(content),
    }