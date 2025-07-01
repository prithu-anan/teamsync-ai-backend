# Use a slim Python base
FROM python:3.11-slim

# Set a working directory
WORKDIR /app

# Install OS deps (if any), then Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . .

# Expose your AI backend’s port (adjust if needed)
EXPOSE 8000

# Default command: run Uvicorn on 0.0.0.0 so it binds inside the container
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

HEALTHCHECK --interval=30s \
            --timeout=5s \
            --start-period=5s \
            --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
