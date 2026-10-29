import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

try:
    from src.config import PORT, DB_FILE_PATH
    from src.vector_store import LightweightVectorStore
except ImportError:
    from config import PORT, DB_FILE_PATH
    from vector_store import LightweightVectorStore

app = FastAPI(
    title="CTF LangChain Vector RAG Gateway",
    description="Vector store and retrieval microservice for CTF writeups, cryptography patterns, and exploit templates.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vector_store = LightweightVectorStore(persist_path=DB_FILE_PATH)

class QueryPayload(BaseModel):
    query: str = Field(..., description="Challenge prompt, keywords, or error output")
    domain: Optional[str] = Field(None, description="Optional domain filter (Cryptography, Forensics, Web, Binary Exploitation)")
    k: int = Field(default=3, ge=1, le=20, description="Number of results to return")

class AddDocumentPayload(BaseModel):
    title: str = Field(..., description="Challenge title / concept name")
    domain: str = Field(..., description="Domain category")
    pattern: str = Field(..., description="Pattern / vulnerability description")
    solution_template: Optional[str] = Field("", description="Python solver or command snippet")
    keywords: Optional[List[str]] = Field(default=[], description="Keywords for indexing")

@app.get("/")
def get_service_info():
    return {
        "service": "CTF LangChain Vector RAG Gateway",
        "status": "online",
        "indexed_documents": len(vector_store.documents),
        "db_path": DB_FILE_PATH,
        "endpoints": {
            "health": "/health",
            "query": "POST /query",
            "add": "POST /add",
            "categories": "GET /categories",
            "all": "GET /all"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "total_documents": len(vector_store.documents)
    }

@app.post("/query")
def query_vector_store(payload: QueryPayload):
    scored_results = vector_store.similarity_search_with_score(
        query=payload.query,
        k=payload.k,
        filter_domain=payload.domain
    )

    results = []
    for doc, score in scored_results:
        results.append({
            "score": round(score, 4),
            "content": doc.page_content,
            "metadata": doc.metadata
        })

    return {
        "query": payload.query,
        "domain_filter": payload.domain,
        "count": len(results),
        "results": results
    }

@app.post("/add")
def add_new_document(payload: AddDocumentPayload):
    try:
        content = f"[{payload.domain}] {payload.title}\nKeywords: {', '.join(payload.keywords or [])}\nPattern: {payload.pattern}\nSolution:\n{payload.solution_template}"
        metadata = {
            "title": payload.title,
            "domain": payload.domain,
            "pattern": payload.pattern,
            "solution_template": payload.solution_template,
            "keywords": payload.keywords or []
        }
        doc = vector_store.add_document(page_content=content, metadata=metadata)
        return {
            "status": "success",
            "message": f"Document '{payload.title}' added to Vector RAG DB.",
            "document": doc.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories")
def get_categories():
    counts: Dict[str, int] = {}
    for doc in vector_store.documents:
        d = doc.metadata.get("domain", "General")
        counts[d] = counts.get(d, 0) + 1
    return {"categories": counts}

@app.get("/all")
def get_all_documents():
    return {
        "total": len(vector_store.documents),
        "documents": [doc.to_dict() for doc in vector_store.documents]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
