"""
RAG引擎
基于Chroma向量数据库，支持人教版教材检索
"""
import os
from typing import List, Dict, Optional, Any
from pathlib import Path
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

class RAGEngine:
    def __init__(
        self,
        db_path: Optional[str] = None,
        collection_name: str = "textbook_content"
    ):
        self.db_path = db_path or os.getenv('CHROMA_DB_PATH', './knowledge_base/chroma_db')
        self.collection_name = collection_name

        os.makedirs(self.db_path, exist_ok=True)

        self.client = chromadb.Client(Settings(
            persist_directory=self.db_path,
            anonymized_telemetry=False
        ))

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={'device': 'cuda'}
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", "。", "，", " "]
        )

    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ):
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in texts]

        embeddings = self.embeddings.embed_documents(texts)

        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas or [{} for _ in texts],
            ids=ids
        )

        self.client.persist()

    def add_text_file(
        self,
        file_path: str,
        metadata: Optional[Dict] = None
    ):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        chunks = self.text_splitter.split_text(text)

        chunk_metadata = []
        for i, chunk in enumerate(chunks):
            chunk_meta = metadata.copy() if metadata else {}
            chunk_meta['chunk_id'] = i
            chunk_metadata.append(chunk_meta)

        self.add_texts(chunks, chunk_metadata)

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        query_embedding = self.embeddings.embed_query(query_text)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata
        )

        formatted_results = []
        if results['documents'] and len(results['documents']) > 0:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else 0
                })

        return formatted_results

    def get_relevant_context(
        self,
        query: str,
        grade: Optional[int] = None,
        subject: Optional[str] = None,
        chapter: Optional[str] = None,
        n_results: int = 5
    ) -> str:
        filter_metadata = {}
        if grade:
            filter_metadata['grade'] = grade
        if subject:
            filter_metadata['subject'] = subject
        if chapter:
            filter_metadata['chapter'] = chapter

        results = self.query(
            query,
            n_results=n_results,
            filter_metadata=filter_metadata if filter_metadata else None
        )

        context = "\n\n".join([r['content'] for r in results])
        return context

_engine = None

def get_rag_engine() -> RAGEngine:
    global _engine
    if _engine is None:
        _engine = RAGEngine()
    return _engine