# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PATH="/opt/poetry/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry --version

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root --only main

# Copy application code
COPY domain/ ./domain/
COPY youtube/ ./youtube/
COPY telegram_bot/ ./telegram_bot/
COPY report/ ./report/
COPY client_secrets.json ./

# Create directory for token storage
RUN mkdir -p /app/telegram_bot/tokens

# Set volume for persistent token storage
VOLUME ["/app/telegram_bot/tokens"]

# Run the bot
CMD ["poetry", "run", "telegram-bot"]