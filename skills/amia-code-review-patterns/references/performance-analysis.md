# Performance Analysis Review

## Table of Contents
- When reviewing algorithm efficiency → Verification Checklist: Algorithm Efficiency
- If you need to evaluate data structure choices → Verification Checklist: Data Structure Selection
- When assessing database performance → Verification Checklist: Database Performance
- If you're concerned about I/O operations → Verification Checklist: I/O Operations
- When checking memory management → Verification Checklist: Memory Management
- If you need to verify concurrency handling → Verification Checklist: Concurrency
- When evaluating caching strategy → Verification Checklist: Caching
- If you're reviewing resource usage → Verification Checklist: Resource Usage
- When identifying performance issues → Common Issues to Look For

## Purpose
Evaluate code efficiency, identify performance bottlenecks, and ensure resource usage is optimized for scalability and responsiveness.

## Verification Checklist

### Algorithm Efficiency
- [ ] Time complexity is appropriate for use case
- [ ] Space complexity is reasonable
- [ ] Algorithm choice is justified
- [ ] No unnecessary iterations
- [ ] Recursive calls are optimized
- [ ] Search algorithms are efficient
- [ ] Sorting algorithms are appropriate
- [ ] Data structure choice supports performance

### Data Structure Selection
- [ ] Appropriate data structures for operations
- [ ] Hash tables for O(1) lookups when needed
- [ ] Lists vs sets vs dicts chosen correctly
- [ ] Ordered vs unordered structures as needed
- [ ] Efficient collection types
- [ ] No unnecessary data copies
- [ ] Streaming for large datasets
- [ ] Lazy evaluation where appropriate

### Database Performance
- [ ] Queries are optimized
- [ ] Indexes are properly used
- [ ] N+1 query problem avoided
- [ ] Batch operations instead of loops
- [ ] Connection pooling implemented
- [ ] Appropriate fetch limits
- [ ] Query result caching considered
- [ ] Transactions used appropriately

### I/O Operations
- [ ] File operations are buffered
- [ ] Network calls are minimized
- [ ] Async I/O used where appropriate
- [ ] Batch processing for multiple operations
- [ ] Streaming for large files
- [ ] Connection reuse implemented
- [ ] Timeouts configured properly
- [ ] Retries with backoff

### Memory Management
- [ ] No memory leaks
- [ ] Objects released when no longer needed
- [ ] Large objects not kept in memory unnecessarily
- [ ] Generators used for large sequences
- [ ] Memory-efficient data structures
- [ ] No circular references preventing GC
- [ ] Resource cleanup in finally blocks
- [ ] Context managers for resource management

### Concurrency
- [ ] Thread safety verified
- [ ] Lock contention minimized
- [ ] No race conditions
- [ ] Deadlocks prevented
- [ ] Async operations used appropriately
- [ ] Thread pool sizes configured
- [ ] Concurrent collections used correctly
- [ ] Work distributed efficiently

### Caching
- [ ] Appropriate caching strategy
- [ ] Cache invalidation handled
- [ ] Cache size limits set
- [ ] Cache hit rate monitored
- [ ] Expensive operations cached
- [ ] Cache keys designed properly
- [ ] TTL set appropriately
- [ ] Memory usage controlled

### Resource Usage
- [ ] CPU usage is reasonable
- [ ] Memory footprint is acceptable
- [ ] Network bandwidth efficient
- [ ] Disk I/O minimized
- [ ] Thread/process count controlled
- [ ] Connection limits respected
- [ ] Resource pools configured
- [ ] Cleanup on shutdown

## Common Issues to Look For

### Inefficient Algorithms

**Poor time complexity**
```python
# WRONG: O(n²) for membership check
def has_duplicates(items):
    for i, item in enumerate(items):
        for j, other in enumerate(items[i+1:]):
            if item == other:
                return True
    return False

# CORRECT: O(n) using set
def has_duplicates(items):
    return len(items) != len(set(items))
```

**Unnecessary iterations**
```python
# WRONG: Multiple passes
filtered = [x for x in items if x > 0]
doubled = [x * 2 for x in filtered]
squared = [x ** 2 for x in doubled]

# CORRECT: Single pass
result = [(x * 2) ** 2 for x in items if x > 0]
```

**Inefficient search**
```python
# WRONG: Linear search in list
VALID_CODES = ['A', 'B', 'C', 'D', 'E']  # List
if code in VALID_CODES:  # O(n)
    process()

# CORRECT: O(1) lookup with set
VALID_CODES = {'A', 'B', 'C', 'D', 'E'}  # Set
if code in VALID_CODES:  # O(1)
    process()
```

### Poor Data Structure Choice

**List when dict needed**
```python
# WRONG: Linear search in list
users = [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
user = next(u for u in users if u['id'] == target_id)  # O(n)

# CORRECT: Direct lookup with dict
users = {1: {'name': 'Alice'}, 2: {'name': 'Bob'}}
user = users[target_id]  # O(1)
```

**Inappropriate collection type**
```python
# WRONG: List for unique items with membership checks
seen = []
for item in items:
    if item not in seen:  # O(n) check
        seen.append(item)

# CORRECT: Set for unique items
seen = set()
for item in items:
    seen.add(item)  # O(1) check
```

### Database Performance Issues

**N+1 query problem**
```python
# WRONG: N+1 queries
posts = Post.query.all()  # 1 query
for post in posts:
    author = post.author  # N queries (lazy loading)
    print(author.name)

# CORRECT: Eager loading
posts = Post.query.options(joinedload(Post.author)).all()  # 1 query
for post in posts:
    print(post.author.name)
```

**Missing indexes**
```sql
-- WRONG: No index on frequently queried column
SELECT * FROM users WHERE email = 'user@example.com';

-- CORRECT: Add index
CREATE INDEX idx_users_email ON users(email);
SELECT * FROM users WHERE email = 'user@example.com';
```

**Fetching unnecessary data**
```python
# WRONG: Fetch all columns
users = db.query("SELECT * FROM users WHERE active = true")

# CORRECT: Select only needed columns
users = db.query("SELECT id, name, email FROM users WHERE active = true")
```

### Memory Issues

**Loading entire file**
```python
# WRONG: Load entire file into memory
with open('large_file.txt', 'r') as f:
    content = f.read()  # Could be gigabytes
    for line in content.split('\n'):
        process(line)

# CORRECT: Stream line by line
with open('large_file.txt', 'r') as f:
    for line in f:  # Memory efficient
        process(line)
```

**Unnecessary data copies**
```python
# WRONG: Creates multiple copies
def process_data(data):
    temp1 = data.copy()
    temp2 = [x * 2 for x in temp1]
    temp3 = [x + 1 for x in temp2]
    return temp3

# CORRECT: Single comprehension
def process_data(data):
    return [x * 2 + 1 for x in data]
```

**Memory leaks**
```python
# WRONG: Circular reference prevents GC
class Node:
    def __init__(self, value):
        self.value = value
        self.parent = None
        self.children = []

    def add_child(self, child):
        child.parent = self  # Circular reference
        self.children.append(child)

# CORRECT: Use weak references
import weakref

class Node:
    def __init__(self, value):
        self.value = value
        self._parent = None
        self.children = []

    @property
    def parent(self):
        return self._parent() if self._parent else None

    def add_child(self, child):
        child._parent = weakref.ref(self)
        self.children.append(child)
```

### I/O Bottlenecks

**Synchronous I/O in loops**
```python
# WRONG: Synchronous network calls in loop
results = []
for url in urls:
    response = requests.get(url)  # Blocks
    results.append(response.json())

# CORRECT: Async concurrent requests
import asyncio
import aiohttp

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

**No buffering**
```python
# WRONG: Writing line by line
with open('output.txt', 'w') as f:
    for item in items:
        f.write(item + '\n')  # Many small writes

# CORRECT: Batch writes
with open('output.txt', 'w', buffering=8192) as f:
    f.writelines(item + '\n' for item in items)
```

### Caching Opportunities Missed

**Repeated expensive calculations**
```python
# WRONG: Recalculate every time
def get_stats(data):
    mean = sum(data) / len(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    return variance

# Call multiple times
for i in range(1000):
    result = get_stats(large_dataset)  # Recalculates each time

# CORRECT: Cache result
from functools import lru_cache

@lru_cache(maxsize=128)
def get_stats(data_tuple):
    data = list(data_tuple)
    mean = sum(data) / len(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    return variance

data_tuple = tuple(large_dataset)
for i in range(1000):
    result = get_stats(data_tuple)  # Cached after first call
```

### Concurrency Issues

**Sequential when parallel possible**
```python
# WRONG: Process sequentially
def process_all(items):
    results = []
    for item in items:
        results.append(expensive_operation(item))
    return results

# CORRECT: Process in parallel
from concurrent.futures import ThreadPoolExecutor

def process_all(items):
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(expensive_operation, items))
    return results
```

## Scoring Criteria

### Critical (Must Fix)
- O(n²) or worse when O(n) or O(n log n) available
- Memory leaks
- N+1 query problems
- Missing database indexes on frequently queried columns
- Loading large files entirely into memory
- Synchronous I/O blocking main thread
- Resource leaks (unclosed connections, files)

### High Priority (Should Fix)
- Suboptimal algorithm complexity
- Poor data structure choice
- Inefficient database queries
- Missing caching for expensive operations
- Excessive memory usage
- Sequential processing when parallelizable
- No connection pooling
- Large data copies

### Medium Priority (Consider Fixing)
- Minor algorithm improvements available
- Potential caching opportunities
- Memory usage optimizations
- Better data structure choices
- Query optimization opportunities
- I/O buffering improvements
- Resource pool sizing

### Low Priority (Nice to Have)
- Micro-optimizations
- Premature optimization concerns
- Speculative performance improvements
- Future scalability enhancements
- Additional caching layers

## Review Questions

1. Is the algorithm complexity appropriate?
2. Are data structures chosen optimally?
3. Are database queries efficient?
4. Is I/O handled efficiently?
5. Are there memory leaks or excessive usage?
6. Is concurrency utilized appropriately?
7. Are expensive operations cached?
8. Are resources cleaned up properly?
9. Can operations be batched or parallelized?
10. Will this scale with increased load?

## Red Flags

- Nested loops over large datasets
- Linear search when hash lookup available
- N+1 query patterns
- Missing database indexes
- Loading entire large files
- Synchronous I/O in loops
- No connection pooling
- Memory leaks from circular references
- Unbounded cache growth
- No resource cleanup
- Thread creation in loops
- Excessive object creation
- String concatenation in loops
- Deep recursion without memoization
- Polling instead of event-driven

## Performance Testing

### Profiling Areas
- **CPU Profiling**: Identify hot spots in code
- **Memory Profiling**: Track allocation and leaks
- **I/O Profiling**: Measure file and network operations
- **Database Profiling**: Analyze query performance
- **Concurrency Profiling**: Find contention points

### Benchmarking
- Measure execution time for critical paths
- Test with realistic data volumes
- Profile under expected load
- Monitor resource usage trends
- Compare before/after optimization

## Best Practices

- Choose appropriate algorithm complexity for scale
- Use optimal data structures for access patterns
- Index database columns used in WHERE, JOIN, ORDER BY
- Avoid N+1 queries; use eager loading or joins
- Stream large files; don't load entirely
- Use async I/O for network operations
- Implement connection pooling
- Cache expensive operations appropriately
- Release resources in finally/context managers
- Use generators for large sequences
- Batch database operations
- Parallelize independent operations
- Profile before optimizing
- Measure performance impact of changes
- Don't optimize prematurely
