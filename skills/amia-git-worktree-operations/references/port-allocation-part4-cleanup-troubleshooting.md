# Port Allocation: Cleanup & Troubleshooting

## Table of Contents

1. [If you need to release or reset ports → Port Cleanup](#port-cleanup)
2. [When you encounter port allocation problems → Troubleshooting](#troubleshooting)
3. [Quick Reference](#quick-reference)

---

## Port Cleanup

### When to Clean Up Ports

Ports should be released when:
1. Worktree is deleted
2. Project is archived
3. Registry becomes corrupt
4. Switching to different port ranges

### Automatic Cleanup on Worktree Removal

**Integrated cleanup:**
```bash
eia worktree remove feature-old
```

**This automatically:**
1. Stops all services using the ports
2. Removes Docker containers
3. Releases ports from registry
4. Cleans up configuration files

**Implementation:**
```python
def remove_worktree_with_cleanup(worktree_name):
    """
    Remove worktree and clean up all allocated resources.
    """
    # 1. Get allocated ports before removal
    registry = load_registry()
    ports = registry["allocated_ports"].get(worktree_name, {})

    # 2. Stop all services using these ports
    for service, port in ports.items():
        stop_service_on_port(port)

    # 3. Stop and remove Docker containers
    os.chdir(worktree_name)
    os.system('docker-compose down -v')

    # 4. Remove worktree
    os.system(f'git worktree remove {worktree_name}')

    # 5. Release ports from registry
    if worktree_name in registry["allocated_ports"]:
        del registry["allocated_ports"][worktree_name]
        save_registry(registry)

    # 6. Remove configuration files
    os.remove(f'{worktree_name}/.env.worktree')
    os.remove(f'{worktree_name}/docker-compose.yml')

    print(f"✓ Removed worktree: {worktree_name}")
    print(f"✓ Released {len(ports)} ports")
```

### Manual Cleanup Commands

#### Clean Up Stale Allocations

```bash
eia port cleanup

# This will:
# 1. List all worktrees in registry
# 2. Check if they still exist
# 3. Release ports for deleted worktrees
```

**Output:**
```
Cleaning up port allocations...
═════════════════════════════════════════════════════════
Checking: main                    ✓ exists
Checking: feature-login           ✓ exists
Checking: feature-payment         ✗ NOT FOUND
Checking: old-feature-1           ✗ NOT FOUND

Releasing ports for deleted worktrees:
  feature-payment: 4 ports released
  old-feature-1: 4 ports released

Cleanup complete: 8 ports released
```

#### Force Release All Ports

```bash
eia port release-all --force

# WARNING: This releases ALL ports
# Use only when starting fresh
```

#### Reset Port Registry

```bash
eia port reset

# This will:
# 1. Scan all existing worktrees
# 2. Rebuild port registry from scratch
# 3. Reallocate ports sequentially
```

### Cleanup on Project Deletion

When deleting the entire project:

```bash
# Clean up everything
cd ~/projects/myapp
eia port release-all
eia worktree remove-all
cd ..
rm -rf myapp

# Port registry is deleted with .git directory
```

---

## Troubleshooting

### Problem: Port Allocation Fails

**Symptom:**
```bash
$ eia worktree create feature-new
ERROR: Failed to allocate ports
```

**Diagnosis:**
```bash
# Check port range capacity
eia port status

# Check for conflicts
eia port check-conflicts
```

**Solution:**
1. Expand port ranges if near capacity
2. Clean up unused worktrees
3. Release stale allocations

### Problem: Services Fail to Start

**Symptom:**
```bash
$ npm start
ERROR: Port 8082 already in use
```

**Diagnosis:**
```bash
# What's using the port?
lsof -i :8082

# Is it allocated correctly?
eia port show feature-payment
```

**Solution:**
```bash
# If another process is using it:
kill <PID>

# If registry is wrong:
eia port scan-rebuild

# If port is wrong in config:
eia worktree regenerate-config feature-payment
```

### Problem: Docker Containers Conflict

**Symptom:**
```bash
$ docker-compose up
ERROR: Bind for 0.0.0.0:8082 failed: port is already allocated
```

**Diagnosis:**
```bash
# Check running containers
docker ps | grep 8082

# Check port allocation
eia port list
```

**Solution:**
```bash
# Stop conflicting container
docker stop <container_id>

# Or regenerate docker-compose.yml
eia docker regenerate feature-payment
```

### Problem: Registry Corruption

**Symptom:**
```bash
$ eia port list
ERROR: Invalid registry format
```

**Diagnosis:**
```bash
# Check registry file
cat .git/worktree-registry/ports.json

# Validate JSON
python -m json.tool .git/worktree-registry/ports.json
```

**Solution:**
```bash
# Backup current registry
cp .git/worktree-registry/ports.json .git/worktree-registry/ports.json.backup

# Rebuild from scratch
eia port reset

# Or restore from backup
cp .git/worktree-registry/ports.json.backup .git/worktree-registry/ports.json
```

### Problem: Ports Not Released After Worktree Deletion

**Symptom:**
```bash
$ eia port list
# Shows ports for deleted worktree
```

**Diagnosis:**
```bash
# Check if worktree exists
git worktree list | grep feature-old

# If not found, it's stale
```

**Solution:**
```bash
# Release manually
eia port release feature-old

# Or run cleanup
eia port cleanup
```

### Problem: Cannot Expand Port Range

**Symptom:**
```bash
$ eia port config --web-range 8080-8199
ERROR: Range conflicts with existing allocations
```

**Diagnosis:**
```bash
# Check current allocations
eia port list --service web
```

**Solution:**
```bash
# Compact existing allocations first
eia port compact

# Then expand range
eia port config --web-range 8080-8199
```

### Problem: Port Check Shows Wrong Status

**Symptom:**
```bash
$ eia port check 8082
Status: AVAILABLE
# But it's actually in use!
```

**Diagnosis:**
```bash
# Check actual port status
lsof -i :8082
netstat -an | grep 8082
```

**Solution:**
```bash
# Rebuild registry from actual port usage
eia port scan-rebuild

# This will update registry to match reality
```

---

## Quick Reference

### Common Commands

```bash
# Allocate ports for new worktree
eia worktree create <name>  # Auto-allocates

# List all ports
eia port list

# Check specific port
eia port check <port>

# Show ports for worktree
eia port show <worktree>

# Release ports
eia port release <worktree>

# Clean up stale allocations
eia port cleanup

# Rebuild registry
eia port scan-rebuild

# Check port conflicts
eia port check-conflicts
```

### Port Ranges Reference

```
Web:      8080-8099  (20 ports)
Database: 5432-5439  (8 ports)
Testing:  9000-9099  (100 ports)
Debug:    5555-5564  (10 ports)
API:      3000-3099  (100 ports)
```

### Configuration Files

```
Registry:           .git/worktree-registry/ports.json
Config Template:    .env.worktree.template
Docker Template:    docker-compose.worktree.template.yml
Generated Config:   <worktree>/.env.worktree
Generated Docker:   <worktree>/docker-compose.yml
```

---

## Related Documents

- [Core Concepts](port-allocation-part1-core-concepts.md) - Why ports matter and allocation algorithm
- [Configuration & Status](port-allocation-part2-config-status.md) - How to generate configs and check port status
- [Conflict Resolution & Docker](port-allocation-part3-conflict-docker.md) - Handling conflicts and Docker integration
