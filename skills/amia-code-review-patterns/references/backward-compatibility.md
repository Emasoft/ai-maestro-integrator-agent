# Backward Compatibility Review

## Table of Contents
- When reviewing API compatibility → Verification Checklist: API Compatibility
- If you need to verify data compatibility → Verification Checklist: Data Compatibility
- When checking behavioral compatibility → Verification Checklist: Behavioral Compatibility
- If you're concerned about deprecation → Verification Checklist: Deprecation Strategy
- When verifying versioning practices → Verification Checklist: Versioning
- If you need to assess client impact → Verification Checklist: Client Impact
- When reviewing documentation → Verification Checklist: Documentation
- If you suspect breaking changes → Common Issues to Look For

## Purpose
Identify breaking changes and ensure modifications maintain compatibility with existing code, APIs, and client integrations.

## Verification Checklist

### API Compatibility
- [ ] Public API signatures unchanged
- [ ] No removed public methods
- [ ] No removed public properties
- [ ] Parameter order preserved
- [ ] Return types unchanged
- [ ] Default parameter values preserved
- [ ] Optional parameters remain optional
- [ ] Required parameters remain required

### Data Compatibility
- [ ] Database schema changes backward compatible
- [ ] Data migrations preserve existing data
- [ ] File format changes versioned
- [ ] Configuration format compatible
- [ ] Serialization format unchanged
- [ ] Message formats compatible
- [ ] Protocol versions maintained

### Behavioral Compatibility
- [ ] Function behavior consistent
- [ ] Error conditions unchanged
- [ ] Side effects preserved
- [ ] Performance characteristics similar
- [ ] Concurrency guarantees maintained
- [ ] Security properties unchanged
- [ ] Validation rules consistent

### Deprecation Strategy
- [ ] Deprecated features clearly marked
- [ ] Deprecation warnings added
- [ ] Migration path documented
- [ ] Deprecation timeline communicated
- [ ] Alternatives provided
- [ ] Grace period defined
- [ ] Removal plan scheduled

### Versioning
- [ ] Semantic versioning followed
- [ ] Version numbers updated correctly
- [ ] Breaking changes in major version
- [ ] New features in minor version
- [ ] Bug fixes in patch version
- [ ] Pre-release versions marked
- [ ] Changelog maintained

### Client Impact
- [ ] Existing client code continues working
- [ ] Client migrations not required
- [ ] Client dependencies compatible
- [ ] Client configurations valid
- [ ] Client workflows unaffected
- [ ] Integration tests pass
- [ ] Partner APIs compatible

### Documentation
- [ ] Breaking changes documented
- [ ] Migration guide provided
- [ ] Changelog updated
- [ ] API documentation current
- [ ] Examples updated
- [ ] Version compatibility matrix maintained
- [ ] Upgrade path clear

## Common Issues to Look For

### Breaking API Changes

**Removing parameters**
```python
# WRONG: Breaking change - removed parameter
# v1.0
def process_order(order_id, user_id, options=None):
    pass

# v1.1 - BREAKING
def process_order(order_id, options=None):  # Removed user_id
    pass

# CORRECT: Deprecate parameter
# v1.1
def process_order(order_id, user_id=None, options=None):
    if user_id is not None:
        warnings.warn(
            "user_id parameter is deprecated and will be removed in v2.0",
            DeprecationWarning
        )
    pass
```

**Changing parameter order**
```python
# WRONG: Breaking change - parameter order
# v1.0
def create_user(name, email, age):
    pass

# v1.1 - BREAKING
def create_user(email, name, age):  # Reordered parameters
    pass

# CORRECT: Maintain order, add new parameters at end
# v1.1
def create_user(name, email, age, phone=None):  # New param at end
    pass
```

**Changing return types**
```python
# WRONG: Breaking change - return type
# v1.0
def get_users() -> list:
    return [user1, user2]

# v1.1 - BREAKING
def get_users() -> dict:  # Changed to dict
    return {"users": [user1, user2]}

# CORRECT: Maintain return type
# v1.1
def get_users() -> list:
    return [user1, user2]

# If dict needed, create new method
def get_users_detailed() -> dict:
    return {"users": [user1, user2], "count": 2}
```

**Making parameters required**
```python
# WRONG: Breaking change - new required parameter
# v1.0
def send_email(to, subject, body):
    pass

# v1.1 - BREAKING
def send_email(to, subject, body, priority):  # New required param
    pass

# CORRECT: New parameter optional
# v1.1
def send_email(to, subject, body, priority="normal"):  # Optional
    pass
```

### Breaking Data Changes

**Schema changes without migration**
```python
# WRONG: Breaking change - renamed column
# v1.0
class User:
    email = Column(String)

# v1.1 - BREAKING
class User:
    email_address = Column(String)  # Renamed without migration

# CORRECT: Add new column, maintain old
# v1.1
class User:
    email = Column(String)  # Keep for compatibility
    email_address = Column(String)  # New column

    @property
    def email(self):
        # Read from new column, fall back to old
        return self.email_address or self.email
```

**File format changes**
```python
# WRONG: Breaking change - incompatible format
# v1.0
def save_config(config):
    with open('config.txt', 'w') as f:
        f.write(str(config))

# v1.1 - BREAKING
def save_config(config):
    with open('config.json', 'w') as f:  # Changed format
        json.dump(config, f)

# CORRECT: Support both formats
# v1.1
def save_config(config, format='txt'):
    if format == 'txt':
        with open('config.txt', 'w') as f:
            f.write(str(config))
    elif format == 'json':
        with open('config.json', 'w') as f:
            json.dump(config, f)

def load_config():
    # Try new format first, fall back to old
    if os.path.exists('config.json'):
        with open('config.json') as f:
            return json.load(f)
    else:
        with open('config.txt') as f:
            return eval(f.read())
```

### Breaking Behavioral Changes

**Changed error conditions**
```python
# WRONG: Breaking change - different exceptions
# v1.0
def get_user(user_id):
    if user_id < 0:
        raise ValueError("Invalid user ID")
    return User.get(user_id)

# v1.1 - BREAKING
def get_user(user_id):
    if user_id < 0:
        raise UserError("Invalid user ID")  # Different exception
    return User.get(user_id)

# CORRECT: Maintain exception type
# v1.1
def get_user(user_id):
    if user_id < 0:
        raise ValueError("Invalid user ID")  # Same exception
    return User.get(user_id)
```

**Changed side effects**
```python
# WRONG: Breaking change - removed side effect
# v1.0
def update_user(user_id, data):
    user = User.get(user_id)
    user.update(data)
    user.last_modified = datetime.now()  # Side effect
    user.save()

# v1.1 - BREAKING
def update_user(user_id, data):
    user = User.get(user_id)
    user.update(data)
    # Removed last_modified update - BREAKING
    user.save()

# CORRECT: Maintain side effects
# v1.1
def update_user(user_id, data):
    user = User.get(user_id)
    user.update(data)
    user.last_modified = datetime.now()  # Preserved
    user.save()
```

### Poor Deprecation

**No warning**
```python
# WRONG: Removing without deprecation
# v1.0
def old_method():
    pass

# v2.0 - BREAKING
# Removed old_method without warning

# CORRECT: Deprecate first
# v1.5
def old_method():
    warnings.warn(
        "old_method is deprecated, use new_method instead. "
        "Will be removed in v2.0",
        DeprecationWarning,
        stacklevel=2
    )
    return new_method()

def new_method():
    pass

# v2.0
def new_method():
    pass
# old_method removed after deprecation period
```

**No migration path**
```python
# WRONG: Deprecate without alternative
@deprecated("This method is deprecated")
def process():
    pass

# CORRECT: Provide migration path
@deprecated(
    "process() is deprecated, use process_v2() instead. "
    "See migration guide: https://docs.example.com/migration/v2"
)
def process():
    return process_v2()

def process_v2():
    pass
```

### Versioning Issues

**Wrong version bump**
```python
# WRONG: Breaking change in minor version
# v1.5.0
def get_data() -> list:
    return [1, 2, 3]

# v1.6.0 - Should be 2.0.0
def get_data() -> dict:  # BREAKING CHANGE
    return {"data": [1, 2, 3]}

# CORRECT: Breaking change in major version
# v1.5.0
def get_data() -> list:
    return [1, 2, 3]

# v2.0.0 - Major version for breaking change
def get_data() -> dict:
    return {"data": [1, 2, 3]}
```

## Scoring Criteria

### Critical (Must Fix)
- Breaking API changes in minor/patch version
- Removed public methods without deprecation
- Changed return types without migration
- Data loss in migrations
- Removed configuration options
- Changed exception types
- Breaking changes without documentation

### High Priority (Should Fix)
- Changed parameter order
- New required parameters
- Removed deprecated features without grace period
- Schema changes without backward compatibility
- Changed default behavior
- Missing migration path
- Inadequate deprecation warnings

### Medium Priority (Consider Fixing)
- Deprecation without clear timeline
- Missing upgrade documentation
- Version number inconsistencies
- Behavioral changes not documented
- Performance regressions
- Missing compatibility tests
- Unclear migration guides

### Low Priority (Nice to Have)
- Enhanced deprecation messages
- Additional migration examples
- Better version documentation
- Extended compatibility period
- Additional compatibility tests
- Improved changelog details

## Review Questions

1. Are there breaking changes to public APIs?
2. Are deprecated features properly marked?
3. Is a migration path provided?
4. Is semantic versioning followed?
5. Are existing clients compatible?
6. Are data migrations backward compatible?
7. Is behavior consistent with previous versions?
8. Are breaking changes documented?
9. Is there adequate deprecation period?
10. Will existing integrations continue working?

## Red Flags

- Removing public methods
- Changing parameter order
- Changing return types
- Making optional parameters required
- Removing parameters
- Changing exception types
- Breaking data format changes
- No deprecation warnings
- Breaking changes in patch/minor versions
- No migration documentation
- Schema changes without migration
- Changed default behavior
- Removed configuration options
- No backward compatibility tests
- Breaking changes without communication

## Compatibility Strategies

### API Evolution Patterns

**Additive changes only**
```python
# Safe: Add new optional parameters
def process(data, format='json', validate=True):
    pass
```

**Facade for compatibility**
```python
# Old API (deprecated)
def old_api(x, y):
    warnings.warn("Use new_api instead", DeprecationWarning)
    return new_api(x=x, y=y)

# New API
def new_api(x, y, z=None):
    pass
```

**Version-specific endpoints**
```python
# Multiple API versions
@app.route('/v1/users')
def get_users_v1():
    return jsonify([user.to_dict_v1() for user in users])

@app.route('/v2/users')
def get_users_v2():
    return jsonify({"users": [user.to_dict_v2() for user in users]})
```

### Data Migration Patterns

**Multi-phase migration**
```python
# Phase 1: Add new column
ALTER TABLE users ADD COLUMN email_address VARCHAR(255);

# Phase 2: Migrate data
UPDATE users SET email_address = email WHERE email_address IS NULL;

# Phase 3: Deprecate old column (mark in code)
# Phase 4: Remove old column (major version)
ALTER TABLE users DROP COLUMN email;
```

**Read both, write new**
```python
def get_config():
    # Read from new location, fall back to old
    if os.path.exists('config.json'):
        return load_json('config.json')
    return load_txt('config.txt')

def save_config(config):
    # Always write to new location
    save_json('config.json', config)
```

## Best Practices

- Follow semantic versioning strictly
- Never break APIs in minor/patch versions
- Deprecate before removing
- Provide clear migration paths
- Document all breaking changes
- Maintain changelog
- Test backward compatibility
- Support multiple API versions
- Use feature flags for gradual rollout
- Communicate breaking changes early
- Provide adequate deprecation period (6+ months)
- Add compatibility tests to CI
- Version database schemas
- Support data migration
- Maintain compatibility layers
- Document version compatibility matrix
- Provide upgrade guides
- Use deprecation warnings
- Keep old behavior until major version
- Test with existing client code
