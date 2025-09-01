# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose Render's $PORT
EXPOSE 5000

# Use environment variable $PORT (Render sets this automatically)
CMD ["sh", "-c", "python app.py"]
