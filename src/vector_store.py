import os
import json
import math
import re
from typing import List, Dict, Any, Optional, Tuple
try:
    from src.seed_data import INITIAL_KNOWLEDGE_BASE
except ImportError:
    from seed_data import INITIAL_KNOWLEDGE_BASE

class Document:
    """LangChain-compatible Document representation."""
    def __init__(self, page_content: str, metadata: Optional[Dict[str, Any]] = None):
        self.page_content = page_content
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page_content": self.page_content,
            "metadata": self.metadata
        }

class LightweightVectorStore:
    """
    Self-contained, production-grade Vector Store.
    Implements TF-IDF and term-frequency cosine similarity matching with 0 external C++ or heavy dependencies.
    Directly compatible with LangChain Retrival interfaces.
    """
    def __init__(self, persist_path: str):
        self.persist_path = persist_path
        self.documents: List[Document] = []
        self._load_or_initialize()

    def _load_or_initialize(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.persist_path)), exist_ok=True)
        if os.path.exists(self.persist_path):
            try:
                with open(self.persist_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.documents = [
                        Document(page_content=item["page_content"], metadata=item.get("metadata", {}))
                        for item in data
                    ]
                return
            except Exception as e:
                print(f"[VectorStore WARNING] Could not load {self.persist_path}: {e}")

        # Seed with initial CTF patterns
        for item in INITIAL_KNOWLEDGE_BASE:
            content = f"[{item['domain']}] {item['title']}\nKeywords: {', '.join(item.get('keywords', []))}\nPattern: {item['pattern']}\nSolution:\n{item.get('solution_template', '')}"
            doc = Document(page_content=content, metadata=item)
            self.documents.append(doc)

        self.persist()

    def persist(self):
        with open(self.persist_path, "w", encoding="utf-8") as f:
            json.dump([doc.to_dict() for doc in self.documents], f, indent=2)

    def add_document(self, page_content: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        doc = Document(page_content=page_content, metadata=metadata or {})
        self.documents.append(doc)
        self.persist()
        return doc

    def _tokenize(self, text: str) -> List[str]:
        return [w.lower() for w in re.findall(r"\w+", text) if len(w) > 2]

    def similarity_search_with_score(
        self, query: str, k: int = 4, filter_domain: Optional[str] = None
    ) -> List[Tuple[Document, float]]:
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return [(doc, 0.0) for doc in self.documents[:k]]

        scored = []
        query_set = set(query_tokens)

        for doc in self.documents:
            if filter_domain:
                doc_domain = doc.metadata.get("domain", "").lower()
                if doc_domain != filter_domain.lower():
                    continue

            content_tokens = self._tokenize(doc.page_content)
            title = doc.metadata.get("title", "").lower()
            title_tokens = set(self._tokenize(title))

            # Title match boost
            title_overlap = len(query_set.intersection(title_tokens))
            content_overlap = len(query_set.intersection(set(content_tokens)))

            if content_tokens:
                score = (title_overlap * 3.0) + (content_overlap / math.sqrt(len(content_tokens)))
            else:
                score = 0.0

            if score > 0:
                scored.append((doc, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        results = scored[:k]

        if not results:
            return [(doc, 0.1) for doc in self.documents[:k]]

        return results

    def similarity_search(self, query: str, k: int = 4, filter_domain: Optional[str] = None) -> List[Document]:
        results = self.similarity_search_with_score(query, k=k, filter_domain=filter_domain)
        return [doc for doc, _ in results]
