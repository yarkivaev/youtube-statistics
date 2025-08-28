# Docker Deployment Guide

This guide explains how to deploy the YouTube Statistics Telegram Bot using Docker.

## Prerequisites

- Docker and Docker Compose installed on your server
- Telegram Bot Token (from @BotFather)
- Google OAuth 2.0 credentials (client_secrets.json)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd youtube-statistics
```

### 2. Set Up Configuration

#### Create .env file:
```bash
# Copy the example and edit it
echo "TELEGRAM_BOT_TOKEN=your_bot_token_here" > .env
```

#### Ensure client_secrets.json exists:
- Place your Google OAuth credentials file in the project root
- This file is required for YouTube API authentication

### 3. Build and Run with Docker Compose

```bash
# Build the Docker image
docker-compose build

# Start the bot in detached mode
docker-compose up -d

# Check if it's running
docker-compose ps

# View logs
docker-compose logs -f
```

## Deployment Options

### Option 1: Using Docker Compose (Recommended)

```bash
# Start the bot
docker-compose up -d

# Stop the bot
docker-compose down

# Restart the bot
docker-compose restart

# Update and restart
git pull
docker-compose build
docker-compose up -d
```

### Option 2: Using Docker CLI

```bash
# Build the image
docker build -t youtube-stats-bot .

# Run the container
docker run -d \
  --name youtube-stats-bot \
  --restart unless-stopped \
  -e TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN \
  -v $(pwd)/telegram_bot/tokens:/app/telegram_bot/tokens \
  -v $(pwd)/client_secrets.json:/app/client_secrets.json:ro \
  youtube-stats-bot
```

### Option 3: Using Docker on Remote Host

```bash
# Build locally and push to registry
docker build -t your-registry/youtube-stats-bot:latest .
docker push your-registry/youtube-stats-bot:latest

# On remote server
docker pull your-registry/youtube-stats-bot:latest
docker run -d \
  --name youtube-stats-bot \
  --restart unless-stopped \
  -e TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN \
  -v /path/to/telegram_bot/tokens:/app/telegram_bot/tokens \
  -v /path/to/client_secrets.json:/app/client_secrets.json:ro \
  your-registry/youtube-stats-bot:latest
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | Your Telegram Bot Token from @BotFather |
| `TZ` | No | Timezone (default: UTC). Example: `Europe/Moscow` |

## Volume Mounts

| Path | Purpose |
|------|---------|
| `/app/telegram_bot/tokens` | Persistent storage for OAuth tokens |
| `/app/client_secrets.json` | Google OAuth credentials (read-only) |
| `/app/.env` | Environment variables file (optional) |

## First-Time Setup

1. Start the bot:
   ```bash
   docker-compose up -d
   ```

2. Open Telegram and send `/start` to your bot

3. Authenticate with Google:
   - Send `/auth` to the bot
   - Click the provided Google OAuth link
   - Authorize the application
   - Copy the authorization code
   - Send `/code YOUR_AUTH_CODE` to the bot

4. Test with `/stats` command

## Monitoring

### Check Status
```bash
# Container status
docker-compose ps

# Health check
docker inspect youtube-stats-bot --format='{{.State.Health.Status}}'

# Resource usage
docker stats youtube-stats-bot
```

### View Logs
```bash
# All logs
docker-compose logs

# Follow logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Logs since specific time
docker-compose logs --since="2024-01-01T00:00:00"
```

## Troubleshooting

### Bot Not Responding
```bash
# Check if container is running
docker-compose ps

# Check logs for errors
docker-compose logs --tail=50

# Restart the bot
docker-compose restart
```

### Authentication Issues
```bash
# Check if tokens volume is mounted correctly
docker exec youtube-stats-bot ls -la /app/telegram_bot/tokens

# Remove old tokens and re-authenticate
docker-compose down
rm -rf telegram_bot/tokens/*
docker-compose up -d
```

### Container Crashes
```bash
# Check exit code
docker-compose ps -a

# Inspect container
docker inspect youtube-stats-bot

# Check system resources
df -h
free -h
```

## Backup and Restore

### Backup OAuth Tokens
```bash
# Create backup
tar -czf tokens-backup-$(date +%Y%m%d).tar.gz telegram_bot/tokens/

# Restore backup
tar -xzf tokens-backup-20240101.tar.gz
```

### Full Backup
```bash
# Backup everything
tar -czf youtube-bot-backup-$(date +%Y%m%d).tar.gz \
  telegram_bot/tokens/ \
  client_secrets.json \
  .env \
  docker-compose.yml
```

## Security Recommendations

1. **Secrets Management**:
   - Never commit `.env` or `client_secrets.json` to git
   - Use Docker secrets in production
   - Rotate bot token regularly

2. **Network Security**:
   - Run container with limited network access
   - Use firewall rules to restrict outbound connections
   - Consider using a reverse proxy

3. **Container Security**:
   - Run as non-root user (already configured)
   - Keep base image updated
   - Scan image for vulnerabilities regularly

4. **Data Protection**:
   - Encrypt token storage volume
   - Regular backups of persistent data
   - Limit file permissions on mounted volumes

## Production Deployment

### Using systemd (for Docker Compose)

Create `/etc/systemd/system/youtube-bot.service`:
```ini
[Unit]
Description=YouTube Statistics Telegram Bot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/youtube-statistics
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable youtube-bot
sudo systemctl start youtube-bot
```

### Using Docker Swarm

```bash
# Initialize swarm (if not already done)
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml youtube-bot

# Check service
docker service ls
docker service logs youtube-bot_telegram-bot
```

## Updating the Bot

```bash
# Stop the bot
docker-compose down

# Pull latest changes
git pull

# Rebuild image
docker-compose build --no-cache

# Start with new version
docker-compose up -d

# Verify update
docker-compose logs --tail=20
```

## Performance Tuning

### Memory Limits
Add to docker-compose.yml:
```yaml
services:
  telegram-bot:
    mem_limit: 512m
    memswap_limit: 512m
    cpu_shares: 512
```

### Log Rotation
Already configured in docker-compose.yml:
- Max size: 10MB
- Max files: 3

## Support

For issues or questions:
1. Check the logs: `docker-compose logs`
2. Verify environment variables are set correctly
3. Ensure client_secrets.json is valid
4. Check Docker daemon is running
5. Verify network connectivity

## License

See LICENSE file in the repository root.