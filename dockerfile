# Use an official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency file and install packages
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY app/ .

# Expose port
EXPOSE 8000

# Environment variable for production mode
ENV ENV=production

# Run MCP server
CMD ["python", "gmail.py"]
