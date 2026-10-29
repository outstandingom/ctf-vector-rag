FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860 \
    PYTHONPATH=/app/src:/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Setup non-root user UID 1000 for Hugging Face
RUN useradd -m -u 1000 user && \
    mkdir -p /app/data && \
    chown -R user:user /app

COPY --chown=user:user src/ ./src/
COPY --chown=user:user data/ ./data/

USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

EXPOSE 7860

CMD ["python", "src/server.py"]
