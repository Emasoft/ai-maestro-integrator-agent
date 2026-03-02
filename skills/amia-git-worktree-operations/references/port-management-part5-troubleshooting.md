# Port Management - Part 5: Troubleshooting

## Table of Contents

1. [If you encounter port management problems → Troubleshooting](#troubleshooting)
   - 1.1 [Problem: Port Already in Use](#problem-port-already-in-use)
   - 1.2 [Problem: Registry Shows Port as Free but It's in Use](#problem-registry-shows-port-as-free-but-its-in-use)
   - 1.3 [Problem: Service Can't Bind to Allocated Port](#problem-service-cant-bind-to-allocated-port)
   - 1.4 [Problem: Docker Container Can't Connect to Port](#problem-docker-container-cant-connect-to-port)
   - 1.5 [Problem: Health Check Reports "not_running" but Service is Running](#problem-health-check-reports-not_running-but-service-is-running)
   - 1.6 [Problem: Port Range is Exhausted](#problem-port-range-is-exhausted)
2. [Summary](#summary)

**Related Parts:**
- [Part 1: Overview and Registry Structure](port-management-part1-overview-registry.md)
- [Part 2: Allocation Functions and CLI](port-management-part2-allocation-cli.md)
- [Part 3: Conflict Detection and Health Checking](port-management-part3-conflicts-health.md)
- [Part 4: Docker Compose Integration](port-management-part4-docker.md)

---

## Troubleshooting

### Problem: Port Already in Use

**Symptoms:**
- Service fails to start with "Address already in use" error
- `check_port_available()` returns False

**Diagnosis:**
```bash
# Check what's using the port
lsof -i :8080  # macOS/Linux
netstat -ano | findstr :8080  # Windows

# Check registry allocation
python scripts/port_status.py --all | grep 8080
```

**Possible Causes:**
1. Another worktree service is using the port
2. A non-worktree process is using the port
3. Previous service instance didn't shut down properly

**Solutions:**

**Solution 1: Port is allocated to another worktree**
```bash
# Find which worktree is using it
python scripts/port_status.py --all

# Either stop that service or allocate a different port to your worktree
python scripts/port_allocate.py --service web --worktree your-worktree
```

**Solution 2: Non-worktree process is using the port**
```bash
# Identify the process
lsof -i :8080  # Note the PID

# Stop the process if safe
kill <PID>

# Or allocate a different port
python scripts/port_allocate.py --service web --worktree your-worktree
```

**Solution 3: Zombie process from previous run**
```bash
# Force kill the process
kill -9 <PID>

# Or restart your computer to clean up zombie processes
```

### Problem: Registry Shows Port as Free but It's in Use

**Symptoms:**
- Registry doesn't show an allocation for a port
- System reports port is in use
- `allocate_port()` succeeds but service fails to start

**Diagnosis:**
```bash
# Check system-level port usage
lsof -i :8080

# Check registry
python scripts/port_status.py --all | grep 8080
```

**Cause:** A process outside the worktree system is using the port.

**Solution:**
```bash
# Option 1: Stop the external process
lsof -i :8080  # Note the PID and command
kill <PID>

# Option 2: Exclude the port from allocation
# Edit design/worktrees/ports.json and adjust the range:
# Change "start": 8080 to "start": 8081
# This reserves 8080 for the external process

# Option 3: Use a different port range
python scripts/port_allocate.py --service web --worktree your-worktree
# Will allocate 8081 instead
```

### Problem: Service Can't Bind to Allocated Port

**Symptoms:**
- Port is allocated in registry
- Port is free on the system
- Service still fails to bind

**Diagnosis:**
```bash
# Verify port is truly free
lsof -i :8080  # Should show nothing

# Check registry
python scripts/port_status.py --worktree your-worktree

# Try manual bind test
python -c "import socket; s = socket.socket(); s.bind(('localhost', 8080)); print('Success')"
```

**Possible Causes:**
1. Service is trying to bind to a different interface (e.g., 0.0.0.0 vs 127.0.0.1)
2. Firewall is blocking the port
3. Service configuration is incorrect

**Solutions:**

**Solution 1: Interface mismatch**
```bash
# Ensure service binds to 127.0.0.1 or 0.0.0.0, not a specific IP
# Check service configuration

# For example, in Python Flask:
app.run(host='0.0.0.0', port=8080)  # Not host='192.168.1.100'
```

**Solution 2: Firewall blocking**
```bash
# macOS: Check firewall settings
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps

# Linux: Check iptables
sudo iptables -L -n

# Windows: Check Windows Firewall
netsh advfirewall firewall show rule name=all
```

**Solution 3: Service configuration**
```bash
# Verify service configuration file
# Ensure port number matches allocated port
# Check for typos or syntax errors
```

### Problem: Docker Container Can't Connect to Port

**Symptoms:**
- Docker Compose starts successfully
- Container logs show connection errors
- Services can't communicate

**Diagnosis:**
```bash
# Check if containers are running
docker ps

# Check container logs
docker logs <container-name>

# Check network connectivity
docker exec <container-name> curl http://localhost:8080
```

**Possible Causes:**
1. Port mapping is incorrect in docker-compose.yml
2. Environment variables are not passed correctly
3. Containers are on different networks

**Solutions:**

**Solution 1: Verify port mapping**
```yaml
# Ensure docker-compose.yml uses correct format
services:
  web:
    ports:
      - "${PORT_WEB}:80"  # External:Internal
```

**Solution 2: Verify environment variables**
```bash
# Check .env file exists
cat .env

# Ensure docker-compose reads it
docker-compose config  # Shows resolved configuration

# If variables are missing, recreate .env and restart
./scripts/docker_start.sh
```

**Solution 3: Network configuration**
```yaml
# Ensure all services are on the same network
services:
  web:
    networks:
      - app-network
  api:
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

### Problem: Health Check Reports "not_running" but Service is Running

**Symptoms:**
- Service is visibly running and responding
- Health check reports `not_running`
- Registry shows incorrect status

**Diagnosis:**
```bash
# Manually check if service is running
curl http://localhost:8080

# Check process
lsof -i :8080

# Run health check with verbose output
python scripts/port_status.py --health-check --verbose
```

**Possible Causes:**
1. Service is binding to a different interface
2. Health check timeout is too short
3. Service requires authentication

**Solutions:**

**Solution 1: Interface binding**
```bash
# Service must bind to 0.0.0.0 or 127.0.0.1
# Check service configuration and restart
```

**Solution 2: Increase timeout**
```python
# Edit scripts/port_status.py
# Increase timeout in check_service_responding():
urllib.request.urlopen(url, timeout=10)  # Increase from 5 to 10
```

**Solution 3: Customize health check**
```python
# For services requiring authentication:
def check_service_responding(port: int) -> bool:
    url = f'http://localhost:{port}/health'  # Use dedicated health endpoint
    # Add authentication headers if needed
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer token'})
    with urllib.request.urlopen(req, timeout=5) as response:
        return response.status == 200
```

### Problem: Port Range is Exhausted

**Symptoms:**
- `allocate_port()` raises RuntimeError
- Error message: "No ports available in range"

**Diagnosis:**
```bash
# Check how many ports are allocated
python scripts/port_status.py --all

# Count allocations per service type
python scripts/port_status.py --all | grep "Available:"
```

**Solutions:**

**Solution 1: Release unused ports**
```bash
# Identify ports that are not running
python scripts/port_status.py --health-check

# Release ports with status "not_running"
python scripts/port_allocate.py --release <port>
```

**Solution 2: Expand the port range**
```bash
# Edit design/worktrees/ports.json
# Increase the end port for the range

# Before:
"web": {"start": 8080, "end": 8099}

# After:
"web": {"start": 8080, "end": 8119}  # 20 additional ports
```

**Solution 3: Add a new service type**
```bash
# Edit design/worktrees/ports.json
# Add a new range for a specific use case

"ranges": {
  "web": {"start": 8080, "end": 8099},
  "web-staging": {"start": 8200, "end": 8219}  # New range
}

# Allocate from the new range
python scripts/port_allocate.py --service web-staging --worktree your-worktree
```

---

## Summary

Port management in Integrator Agent provides:

1. **Centralized Registry** - All port allocations tracked in `design/worktrees/ports.json`
2. **Automatic Allocation** - Functions to allocate and release ports programmatically
3. **CLI Tools** - Scripts for common port operations
4. **Conflict Prevention** - Detects and prevents port conflicts
5. **Health Monitoring** - Verifies services are running correctly
6. **Docker Integration** - Dynamic port mapping for containerized services
7. **Troubleshooting** - Solutions to common port-related issues

**Key Principles:**
- Always allocate ports through the registry system
- Run health checks regularly
- Release ports when services are stopped
- Use Docker integration scripts for consistent behavior
- Check for conflicts before starting services

**Next Steps:**
1. Initialize port registry if it doesn't exist
2. Allocate ports for your worktree services
3. Configure Docker Compose to use allocated ports
4. Run health checks to verify everything is working
5. Refer to troubleshooting section if issues arise

---

**Related Documents:**
- [Worktree Fundamentals](worktree-fundamentals-index.md) - Understanding Git worktrees
- [Registry System](registry-system.md) - Worktree registry structure
- [Creating Worktrees](creating-worktrees.md) - Step-by-step worktree creation
- [Troubleshooting](troubleshooting-index.md) - General worktree troubleshooting

**Last Updated:** 2025-12-31
