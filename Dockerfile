# Use a slim official Python image
FROM python:3.13-slim

# Install dependencies needed by Chromium and Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgtk-4-1 \
    libgraphene-1.0-0 \
    libgstreamer-gl1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    libavif15 \
    libenchant-2-2 \
    libsecret-1-0 \
    libgles2-mesa \
    libnss3 \
    libatk-bridge2.0-0 \
    libxss1 \
    libasound2 \
    libatk1.0-0 \
    libgbm1 \
    ca-certificates \
    fonts-liberation \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Copy your project files into container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install

# Set environment variable to ensure browsers installed locally
ENV PLAYWRIGHT_BROWSERS_PATH=0

# Command to run your scraper
CMD ["python", "scrape_postino.py"]
