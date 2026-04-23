#!/usr/bin/env python3
"""
构建人教版教材知识库
从教材文本构建向量数据库
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from app.core.rag_engine import RAGEngine
import json

TEXTBOOK_DIR = Path(__file__).parent.parent / "knowledge_base" / "textbooks"

def load_textbook_content(edition: str = "pep") -> list:
    content = []
    edition_dir = TEXTBOOK_DIR / edition

    if not edition_dir.exists():
        print(f"Warning: Textbook directory {edition_dir} does not exist")
        return content

    for grade_dir in edition_dir.iterdir():
        if not grade_dir.is_dir():
            continue
        grade = int(grade_dir.name.replace("grade", "").replace("年级", ""))

        for subject_file in grade_dir.iterdir():
            if subject_file.suffix != '.txt':
                continue
            subject = subject_file.stem

            with open(subject_file, 'r', encoding='utf-8') as f:
                text = f.read()

            chapters = text.split("## 第")
            for i, chapter in enumerate(chapters):
                if not chapter.strip():
                    continue
                if i > 0:
                    chapter = "## 第" + chapter

                metadata = {
                    'grade': grade,
                    'subject': subject,
                    'source': f'{edition}_{grade}_{subject}'
                }
                content.append({
                    'text': chapter,
                    'metadata': metadata
                })

    return content

def build_knowledge_base(edition: str = "pep"):
    print(f"Building knowledge base for {edition}...")
    engine = RAGEngine()

    content = load_textbook_content(edition)
    print(f"Loaded {len(content)} content items")

    for item in content:
        texts = [item['text']]
        metadatas = [item['metadata']]

        engine.add_texts(texts, metadatas)

    print(f"Knowledge base built successfully!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--edition', type=str, default='pep', help='Textbook edition (pep=人教版)')
    args = parser.parse_args()

    build_knowledge_base(args.edition)