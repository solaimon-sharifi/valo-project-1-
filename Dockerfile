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

# Use Gunicorn for production. Use shell form so $PORT (provided by Render) is expanded.
# If $PORT is not set, default to 5000 via the ENV above.
CMD gunicorn app:app --bind 0.0.0.0:${PORT:-5000} --workers 2
