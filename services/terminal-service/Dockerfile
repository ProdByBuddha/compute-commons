FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    bash \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy terminal service
COPY main.py /app/

# Install Python dependencies
RUN pip install fastapi uvicorn websockets pyjwt

# Copy cc CLI (would be mounted or copied from build)
# For now, create a placeholder
RUN mkdir -p /app/cc-cli && \
    echo '#!/bin/bash\necho "cc CLI placeholder - install full CLI for production"' > /app/cc-cli/cc && \
    chmod +x /app/cc-cli/cc

# Add cc to PATH
ENV PATH="/app/cc-cli:${PATH}"

# Expose port
EXPOSE 8001

# Run service
CMD ["python", "main.py"]
