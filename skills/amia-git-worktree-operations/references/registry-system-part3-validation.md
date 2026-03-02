# Registry System - Part 3: Validation Rules

## Validation Rules

All registry operations must enforce these validation rules:

### 1. Unique IDs

**Rule:** Each `id` must be unique across all entries

**Check:**
```python
def validate_unique_id(registry, new_id):
    existing_ids = [wt["id"] for wt in registry["worktrees"]]
    if new_id in existing_ids:
        raise ValueError(f"Worktree ID '{new_id}' already exists")
```

**Why:** Prevents confusion and ensures each worktree can be uniquely identified

### 2. Valid Paths

**Rule:** Each `path` must:
- Be relative (start with `../`)
- Not already exist in registry
- Not point inside main repository
- Follow naming convention for the purpose

**Check:**
```python
def validate_path(registry, path, purpose):
    # Check path is relative
    if not path.startswith("../"):
        raise ValueError("Path must be relative (start with '../')")

    # Check path doesn't exist
    existing_paths = [wt["path"] for wt in registry["worktrees"]]
    if path in existing_paths:
        raise ValueError(f"Path '{path}' already in use")

    # Check follows naming convention
    template = registry["naming_convention"][purpose]
    # ... validate against template
```

**Why:** Prevents path conflicts and maintains consistent directory structure

### 3. No Port Conflicts

**Rule:** Each port can only be allocated to one worktree at a time

**Check:**
```python
def validate_ports(registry, new_ports):
    allocated_ports = []
    for wt in registry["worktrees"]:
        if wt["status"] != "pending-removal":
            allocated_ports.extend(wt["port_allocations"])

    conflicts = set(new_ports) & set(allocated_ports)
    if conflicts:
        raise ValueError(f"Ports already allocated: {conflicts}")
```

**Why:** Prevents service conflicts when running multiple worktrees simultaneously

### 4. Valid Status Values

**Rule:** `status` must be one of: `active`, `locked`, `pending-removal`

**Check:**
```python
VALID_STATUSES = ["active", "locked", "pending-removal"]

def validate_status(status):
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Must be one of: {VALID_STATUSES}")
```

**Why:** Ensures consistent state management across the system

### 5. Required Fields Present

**Rule:** All required fields must be present in every entry

**Check:**
```python
REQUIRED_FIELDS = ["id", "path", "branch", "created", "purpose", "status"]

def validate_required_fields(entry):
    missing = [f for f in REQUIRED_FIELDS if f not in entry]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
```

**Why:** Ensures registry integrity and prevents incomplete records
