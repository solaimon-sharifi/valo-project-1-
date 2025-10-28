FROM python:3.12-slim

# Set workdir
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . /app

# Expose port and set env defaults
ENV PORT=5000

EXPOSE 5000

# Use debug startup wrapper in CI/Render to capture environment and debug logs.
# The wrapper will exec gunicorn with the provided $PORT (or 5000 if unset).
COPY start-debug.sh /app/start-debug.sh
RUN chmod +x /app/start-debug.sh
CMD ["/bin/bash", "/app/start-debug.sh"]
