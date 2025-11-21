# Terminal Service

WebSocket-based terminal service for the Compute Commons dashboard.

## Features

- PTY-based bash sessions
- WebSocket communication
- JWT authentication (Keycloak)
- Multiple concurrent sessions
- cc CLI integration

## Development

```bash
# Install dependencies
pip install fastapi uvicorn websockets pyjwt

# Run locally
python main.py
```

Service runs on port 8001.

## Docker

```bash
# Build
docker build -t terminal-service .

# Run
docker run -p 8001:8001 terminal-service
```

## API

### WebSocket Endpoint

`ws://localhost:8001/ws/terminal?token=<jwt>`

**Messages:**

Send:
```json
{
  "type": "command",
  "data": "cc merit"
}
```

Receive:
```json
{
  "type": "output",
  "data": "output text"
}
```

### Health Check

`GET /health`

Returns active session count and status.

## Integration

Add to docker-compose.yml:

```yaml
terminal-service:
  build: ./services/terminal-service
  ports:
    - "8001:8001"
  volumes:
    - ./cc-cli:/app/cc-cli:ro
  networks:
    - compute-net
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.terminal.rule=Host(`api.computecommons.org`) && PathPrefix(`/ws/terminal`)"
    - "traefik.http.services.terminal.loadbalancer.server.port=8001"
```
