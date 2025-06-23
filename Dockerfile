# Use a slim Python base
FROM python:3.11-slim

# Set a working directory
WORKDIR /app

# Install OS deps (if any), then Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirement.txt

# Copy the rest of your code
COPY . .

# Expose your AI backend’s port (adjust if needed)
EXPOSE 8000

# Default command: run Uvicorn on 0.0.0.0 so it binds inside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
