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

# Expose FastAPI port
EXPOSE 7860

# Run FastAPI
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860"]
