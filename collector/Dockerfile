FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the collector code
COPY collector/get_router_data.py .

# Run the script in unbuffered mode to see logs immediately
ENV PYTHONUNBUFFERED=1

CMD ["python", "get_router_data.py"]