FROM python:3.10-slim

WORKDIR /app

# Install basic system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files (backend and static frontend)
COPY . .

# Pre-download the local model so it's baked into the Docker image
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')"

# Expose FastAPI port
EXPOSE 7860

# Run FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
