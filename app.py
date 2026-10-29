import sys
import os

# Add root and src to python module path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, "src"))
sys.path.insert(0, current_dir)

import gradio as gr
from src.server import app, vector_store

def ctf_search(query: str, domain: str, top_k: int):
    if not query.strip():
        return "Please enter a challenge query or keywords."

    results = vector_store.similarity_search_with_score(
        query=query,
        k=int(top_k),
        filter_domain=domain if domain != "All" else None
    )

    output = []
    for doc, score in results:
        title = doc.metadata.get("title", "Untitled")
        dom = doc.metadata.get("domain", "General")
        output.append(f"### 🎯 [{dom}] {title} `(Score: {round(score, 2)})`\n\n```text\n{doc.page_content}\n```\n\n---\n")

    return "\n".join(output) if output else "No matching techniques found."

with gr.Blocks(title="CTF Vector RAG Gateway", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🧬 CTF Vector RAG Knowledge Base")
    gr.Markdown("Search past CTF challenge writeups, cryptographic patterns, and exploit templates. Directly queryable via LangChain & REST API.")

    with gr.Row():
        query_input = gr.Textbox(
            label="Challenge Prompt / Query",
            placeholder="e.g. time based random seed XOR key, or zero width steganography",
            scale=3
        )
        domain_dropdown = gr.Dropdown(
            choices=["All", "Cryptography", "Forensics", "Web", "Binary Exploitation"],
            value="All",
            label="Domain",
            scale=1
        )
        top_k_slider = gr.Slider(
            minimum=1,
            maximum=10,
            value=3,
            step=1,
            label="Results (k)",
            scale=1
        )

    search_btn = gr.Button("Search Knowledge Base", variant="primary")
    output_box = gr.Markdown(label="Retrieved Writeups & Code")

    search_btn.click(
        fn=ctf_search,
        inputs=[query_input, domain_dropdown, top_k_slider],
        outputs=output_box,
        api_name="query"
    )

    gr.Markdown("### 📡 API Endpoints available:\n- `POST /query`: Search knowledge base via JSON\n- `POST /add`: Ingest new challenge writeup\n- `GET /health`: Liveness probe\n- `GET /docs`: Interactive OpenAPI documentation")

if __name__ == "__main__":
    demo.launch()
