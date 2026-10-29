import sys
import os

# Add root and src to python module path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, "src"))
sys.path.insert(0, current_dir)

from src.server import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "7860"))
    print(f"Starting Vector RAG server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
