FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY faac_gateway/ ./faac_gateway/
COPY faac_gateway_mqtt.py .
COPY config/config.yaml.example ./config/

# Create config directory
RUN mkdir -p /app/config

# Expose web interface port
EXPOSE 5000

# Run the application
CMD ["python3", "faac_gateway_mqtt.py", "-c", "/app/config/config.yaml"]
