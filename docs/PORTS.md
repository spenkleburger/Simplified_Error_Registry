# Port Configuration

This document tracks all ports used by this project.

## Development Ports

| Service | Port | Protocol | Description |
|---------|------|----------|-------------|
| API Server | xxxx | HTTP | Main REST API |
| Web Frontend | xxxx | HTTP | React/Next.js frontend |
| Database | xxxx | PostgreSQL | PostgreSQL database |
| Redis | xxxx | Redis | Cache and session store |
| WebSocket | xxxx | WS | WebSocket server |
| Jupyter Notebook | xxxx | HTTP | Jupyter notebook server (if used) |

## Production Ports

| Service | Port | Protocol | Description |
|---------|------|----------|-------------|
| API Server | xxxx | HTTP/HTTPS | Production API (behind reverse proxy) |
| Database | xxxx | PostgreSQL | Production database (internal, not exposed) |
| Redis | xxxx | Redis | Production cache (internal, not exposed) |

## Port Conflicts

If you encounter port conflicts:

1. **Check this file** for existing port assignments
2. **Find what's using the port:**
   - Windows: `netstat -ano | findstr :PORT`
   - Linux/Mac: `lsof -i :PORT` or `netstat -tulpn | grep :PORT`
3. **Update this document** when changing ports
4. **Update `.env` file** with new port values

## Port Configuration in Code

Ports are configured via environment variables in `.env`:

```env
API_PORT=8000
WEB_PORT=3000
DATABASE_PORT=5432
```

Access ports in code via `config/settings.py`:

```python
from config.settings import API_PORT, WEB_PORT, DATABASE_PORT

# Use ports directly (already converted to int)
server_port = API_PORT
```

## Notes

- **Development ports** are typically in the 3000-9000 range
- **Well-known ports** (0-1023) require administrator privileges
- **Registered ports** (1024-49151) are commonly used by applications
- **Dynamic/private ports** (49152-65535) are typically used for temporary connections

## Adding New Services

When adding a new service that requires a port:

1. Check this file for available ports
2. Choose an unused port (avoid common ports like 8080, 5000, 3306, etc.)
3. Add the service to this document
4. Add the port to `.env` file
5. Add the port to `config/settings.py` if needed
6. Update this document with the new service

