FROM python:3.12-slim

# Set workdir
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install both root and valorant coach dependencies
COPY requirements.txt valorant-coach/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r valorant-coach/requirements.txt

# Copy application
COPY . /app

# Expose port and set env defaults
ENV PORT=8002

EXPOSE 8002

# Use debug startup wrapper in CI/Render to capture environment and debug logs.
# The wrapper loads .env.production before invoking gunicorn with the valorant coach app.
COPY start-debug.sh /app/start-debug.sh
RUN chmod +x /app/start-debug.sh
CMD ["/bin/bash", "/app/start-debug.sh"]
