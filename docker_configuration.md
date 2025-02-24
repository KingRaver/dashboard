# Dockerfile for Layer 1 Crypto Analysis Dashboard
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create directories if needed
RUN mkdir -p /app/templates /app/static

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "dashboard.py"]
