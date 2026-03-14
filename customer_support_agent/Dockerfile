# Use official Python image as base
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port 8000
EXPOSE 8000

# Set environment variables (optional)
ENV PYTHONUNBUFFERED=1

# Start the app
CMD ["python", "main.py"]
