---
title: CTF Vector RAG
emoji: 🧬
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# CTF Vector RAG Gateway

A high-performance, lightweight **Vector RAG (Retrieval-Augmented Generation)** knowledge store and retrieval service for Cybersecurity challenges, CTF writeups, cryptographic algorithms, and exploit templates.

Built for seamless integration with **LangChain**, **LangServe**, and autonomous AI agents.

---

## 🚀 Features

- **LangChain Retrieval Compatibility**: Native `similarity_search_with_score` and document metadata handling.
- **Pre-Seeded CTF Knowledge Base**:
  - **Cryptography**: Time-based PRNG, Single-byte & Multi-byte XOR, RSA Cube Root attack.
  - **Forensics**: Unicode Zero-Width steganography, LSB image extraction, Magic byte header repair.
  - **Web Security**: SQL Injection, IDOR, Client-side timer bypass, JWT none-algorithm bypass.
  - **Binary Exploitation**: Buffer overflow RIP overwrite patterns.
- **Lightweight & Cloud-Ready**: Zero external C++ compiler dependencies. Deployable on Render, Railway, Hugging Face, or LangServe in seconds.
- **Dynamic Knowledge Ingestion**: Add newly solved challenges over REST API to continuously improve your agent's memory.

---

## 📡 REST API Specification

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Service info and indexed document count |
| `GET` | `/health` | Liveness health check |
| `POST` | `/query` | Search knowledge base by query prompt, keywords, or domain |
| `POST` | `/add` | Ingest a new challenge writeup or exploit template |
| `GET` | `/categories` | Distribution of techniques by domain |
| `GET` | `/all` | Export full vector store database |

---

## 💻 Local Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Server
```bash
python src/server.py
```
*The server will start on `http://localhost:8000`.*
*Interactive API docs available at `http://localhost:8000/docs`.*

---

## 🔍 Query Example (Python)

```python
import requests

res = requests.post(
    "http://localhost:8000/query",
    json={
        "query": "time based random seed XOR key",
        "domain": "Cryptography",
        "k": 2
    }
)

for item in res.json()["results"]:
    print(f"[{item['score']}] {item['metadata']['title']}")
    print(item["content"])
```

---

## ☁️ Deployment

### Deploy to Render / Railway
1. Push this repository to GitHub.
2. Create a new **Web Service** linked to this repo.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `python src/server.py`
5. Health Check Path: `/health`

---

## 📜 License
MIT License
