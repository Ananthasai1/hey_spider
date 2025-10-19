# Hey Spider Robot - Dockerfile
# For development/testing without hardware

FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    libatlas-base-dev \
    libjasper-dev \
    libtiff5 \
    libharfbuzz0b \
    libwebp6 \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p logs images/raw images/detections data models

# Expose web port
EXPOSE 5000

# Set environment
ENV PYTHONUNBUFFERED=1
ENV MOCK_HARDWARE=true

# Run robot
CMD ["python3", "main.py"]