FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Railway injects $PORT at runtime
CMD gunicorn server:app --bind 0.0.0.0:${PORT:-5001} --workers 2 --timeout 60
