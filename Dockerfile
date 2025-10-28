FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data (para clasificador de texto)
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Copy application
COPY . .

# Create models directory
RUN mkdir -p models

# Expose port
EXPOSE 5015

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:5015/health')" || exit 1

# Run with uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5015", "--reload"]

