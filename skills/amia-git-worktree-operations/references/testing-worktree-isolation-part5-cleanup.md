# Testing Worktrees: Cleanup After Tests

## Table of Contents

1. [Removing Test Worktrees](#removing-test-worktrees)
2. [Releasing Ports](#releasing-ports)
3. [Cleaning Test Databases](#cleaning-test-databases)

---

## Removing Test Worktrees

**When to Remove**:
- After tests complete
- When branch is merged
- When worktree is no longer needed

**Manual Removal**:
```bash
python scripts/worktree_remove.py --identifier api-endpoints
```

**Automated Removal** (in CI or cleanup script):
```python
# scripts/cleanup_test_worktrees.py
import json
from datetime import datetime, timedelta
from worktree_remove import remove_worktree

def cleanup_old_test_worktrees(max_age_hours=24):
    """Remove test worktrees older than specified hours"""

    with open('worktrees_registry.json') as f:
        registry = json.load(f)

    cutoff = datetime.now() - timedelta(hours=max_age_hours)

    for worktree_id, info in registry.get('worktrees', {}).items():
        # Only cleanup test worktrees
        if not info['purpose'].startswith('test-'):
            continue

        created = datetime.fromisoformat(info['created'])

        if created < cutoff:
            print(f"Removing old test worktree: {worktree_id}")
            remove_worktree(worktree_id)
```

---

## Releasing Ports

**Why Release Ports**: Make them available for future test worktrees.

**How Ports Are Released**:

When you run `worktree_remove.py`, it automatically:
1. Reads allocated ports from worktree metadata
2. Removes port allocation from registry
3. Makes ports available for reuse

**Manual Port Release** (if needed):
```python
# scripts/release_ports.py
import json

def release_ports(worktree_id):
    """Release ports allocated to worktree"""

    with open('worktrees_registry.json', 'r') as f:
        registry = json.load(f)

    # Get worktree info
    worktree = registry['worktrees'].get(worktree_id)
    if not worktree or 'ports' not in worktree:
        return

    # Remove from allocated ports
    allocated = registry.get('allocated_ports', [])
    for port in worktree['ports'].values():
        if port in allocated:
            allocated.remove(port)

    registry['allocated_ports'] = allocated

    with open('worktrees_registry.json', 'w') as f:
        json.dump(registry, f, indent=2)
```

---

## Cleaning Test Databases

**Pattern**: Remove test databases when worktree is removed.

**Automated Cleanup**:
```python
# In worktree_remove.py
def cleanup_test_database(metadata):
    """Drop test database for worktree"""

    if 'database' not in metadata:
        return

    db_name = metadata['database']

    # Drop PostgreSQL database
    subprocess.run(['dropdb', '--if-exists', db_name])

    print(f"✓ Removed test database: {db_name}")
```

**Manual Database Cleanup**:
```bash
# List all test databases
psql -l | grep testdb_

# Drop specific test database
dropdb testdb_integration_api_endpoints

# Drop all test databases (careful!)
psql -l | grep testdb_ | cut -d'|' -f1 | xargs -I {} dropdb {}
```

---

**Related Documents**:
- [Testing Worktree Isolation Overview](testing-worktree-isolation.md)
- [Database Testing Patterns](testing-worktree-isolation-part4-database-testing.md)
- [CI/CD Integration](testing-worktree-isolation-part6-cicd.md)
