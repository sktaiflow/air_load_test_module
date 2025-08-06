FROM python:3.10-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY requirements.txt .
# Use uv to install dependencies (much faster than pip)
RUN uv pip install --no-cache-dir -r requirements.txt

COPY locustfile.py .

CMD ["locust"]

