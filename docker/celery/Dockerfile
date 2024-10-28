# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set up a non-root user and working directory
RUN addgroup --system appgroup && adduser --system --group appuser
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y gcc git curl \
    && apt-get clean

# Add build argument for GitHub token
ARG GITHUB_TOKEN

# Copy the requirements file and replace the placeholder with the actual token
COPY requirements.txt /app/
RUN sed -i "s/\${GITHUB_TOKEN}/${GITHUB_TOKEN}/g" /app/requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Copy the application code to the container
COPY . /app/

# Ensure manage.py has execute permissions
RUN chmod +x /app/manage.py

# Change ownership of the application directory
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# CMD ["celery", "-A", "app.extensions.celery", "worker", "--loglevel=info"]
# CMD ["celery", "-A", "celery", "worker", "--loglevel=info"]
CMD ["celery", "-A", "app.celery", "worker", "--loglevel=info"]
