# NeuroBot Textbook - Chapter Organization

This directory contains the textbook chapters organized for backend RAG indexing.

## Structure

```
docs/
└── module-1-neurobot-textbook/
    ├── chapter-1.md   (Introduction to Physical AI)
    ├── chapter-2.md   (Humanoid Robotics Overview)
    ├── chapter-3.md   (ROS 2 Architecture)
    ├── chapter-4.md   (ROS 2 Topics and Publishers)
    ├── chapter-5.md   (ROS 2 Services and Actions)
    ├── ...
    └── chapter-23.md  (Advanced Control Systems)
```

## Current Content

**Status**: Sample chapters with realistic Physical AI and Humanoid Robotics content

These sample chapters contain:
- Technical content about ROS 2, Gazebo, Isaac Sim, and VLA models
- Code examples in Python
- Proper markdown structure with headers and sections
- Sufficient content for testing the RAG indexing system

## Replacing with Your Chapters

### Option 1: Manual Replacement

Simply replace the chapter-N.md files with your own content:

```bash
# Replace individual chapters
cp your-chapters/intro.md docs/module-1-neurobot-textbook/chapter-1.md
cp your-chapters/ros2.md docs/module-1-neurobot-textbook/chapter-2.md
# ... and so on
```

### Option 2: Using the Organization Script

If your chapters are in another directory:

```bash
python organize_chapters.py --mode organize --source <your-chapters-directory>
```

This will:
- Find all markdown files in the source directory
- Automatically number them as chapter-1.md, chapter-2.md, etc.
- Copy them to the correct location
- Preserve all original content

### Option 3: Custom Script

Use the `organize_chapters.py` script with different modes:

```bash
# Just create the folder structure (empty)
python organize_chapters.py --mode create-structure

# Create sample chapters (default, already done)
python organize_chapters.py --mode create-samples --num-chapters 23

# Organize existing chapters from another location
python organize_chapters.py --mode organize --source /path/to/your/chapters
```

## Requirements for Backend Indexing

For the backend RAG system to work correctly, chapters must:

1. **Be in the correct location**: `docs/module-1-neurobot-textbook/chapter-N.md`
2. **Be numbered sequentially**: chapter-1.md, chapter-2.md, ..., chapter-23.md
3. **Be valid markdown**: Proper syntax with headers and content
4. **Have sufficient content**: At least a few paragraphs (500+ tokens recommended)

## Indexing Your Chapters

Once your chapters are organized, run the indexing script:

```bash
cd backend
python scripts/index_chapters.py --docs-dir ../docs
```

This will:
- Read all 23 chapters
- Chunk them into 500-1000 token segments
- Generate OpenAI embeddings
- Upload to Qdrant vector database
- Track progress in Postgres

Expected output:
```
Starting chapter indexing...
Found 23 chapters to index

Processing module-1-chapter-1...
  Generated 45 chunks
  Generated 45 embeddings
  Uploaded 45 points to Qdrant
  module-1-chapter-1 indexed successfully

... (repeats for all chapters)

INDEXING SUMMARY
Total chapters: 23
Successful: 23
Failed: 0
Duration: 127.3 seconds
```

## Chapter Content Guidelines

For best results with the RAG system:

### Structure
- Use markdown headers (`#`, `##`, `###`)
- Include code blocks with proper syntax highlighting
- Break content into logical sections

### Content
- Aim for 500-1000 tokens per section
- Include technical details and examples
- Use clear, educational language
- Add code examples where relevant

### Example Chapter Template

```markdown
# Chapter N: Chapter Title

## Introduction

Brief overview of the chapter topic and learning objectives.

## Core Concepts

### Concept 1

Explanation with details...

Code example:
\`\`\`python
import rclpy
from rclpy.node import Node

class MyNode(Node):
    def __init__(self):
        super().__init__('my_node')
\`\`\`

### Concept 2

More explanation...

## Practical Applications

Real-world examples and use cases.

## Summary

Key takeaways and review.

## Exercises

1. Practice problem 1
2. Practice problem 2
```

## Troubleshooting

### Indexing Issues

**Error: "No chapters found"**
- Verify files are in `docs/module-1-neurobot-textbook/`
- Check files are named `chapter-1.md`, `chapter-2.md`, etc.
- Ensure files are not empty

**Error: "No chunks generated"**
- Check that chapters have sufficient content (>100 characters)
- Verify markdown syntax is valid
- Ensure files are UTF-8 encoded

### Content Issues

**RAG returns poor answers**
- Increase content detail and technical accuracy
- Add more code examples and explanations
- Break long paragraphs into smaller sections
- Ensure content covers the full scope of topics

## Files

- `module-1-neurobot-textbook/` - All 23 textbook chapters
- `technical-documentation.md` - Additional project documentation
- `README.md` - This file

---

**Note**: The current sample chapters are for testing the indexing system. Replace them with your actual textbook content when ready!
