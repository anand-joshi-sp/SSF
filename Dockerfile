# Use Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for Render
ENV PORT=5000
EXPOSE 5000

# Run using gunicorn (production-ready WSGI server)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
