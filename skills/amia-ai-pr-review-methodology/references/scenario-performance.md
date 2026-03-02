# Scenario Protocol: Performance Improvement PRs

## Table of Contents

- S-PERF.1 When to use this scenario protocol
- S-PERF.2 Benchmark requirements (before and after)
- S-PERF.3 Multiple test runs and statistical significance
- S-PERF.4 Verifying no functionality regressions
- S-PERF.5 Significance justification (complexity vs improvement tradeoff)
- S-PERF.6 Example: Reviewing a caching optimization PR

---

## S-PERF.1 When to use this scenario protocol

Use this protocol when the PR claims to improve performance. Performance improvement PRs are identified by:

- The PR title or description mentions "optimize", "performance", "speed", "faster", "reduce latency", "reduce memory", or similar terms
- The PR replaces an algorithm with a more efficient one
- The PR adds caching, memoization, or lazy loading
- The PR changes data structures for better access patterns
- The PR reduces I/O operations, network calls, or database queries

Performance claims are particularly susceptible to false positives because:
- Benchmarks can be misleading if not run correctly
- Improvements on one workload may cause regressions on another
- Added complexity may not be justified by the improvement

---

## S-PERF.2 Benchmark requirements (before and after)

**Requirement:** The author must provide benchmark results showing performance before and after the change, using the same test conditions.

**What a valid benchmark must include:**

| Element | Required | Description |
|---------|----------|-------------|
| Test environment | Yes | Hardware specs, OS version, relevant software versions |
| Test workload | Yes | Exact input data or scenario (size, shape, characteristics) |
| Metric measured | Yes | What was measured (wall time, CPU time, memory usage, throughput, latency) |
| Before result | Yes | Measurement on the base branch (without the PR) |
| After result | Yes | Measurement on the PR branch (with the PR) |
| Number of runs | Yes | How many times the benchmark was executed |
| Warm-up runs | Recommended | Whether initial runs were discarded to eliminate cold-start effects |

**Example of a valid benchmark result:**

```
Environment: Ubuntu 22.04, 8-core AMD Ryzen, 32GB RAM, SSD
Workload: Processing a 500MB CSV file with 10 million rows
Metric: Wall clock time to complete processing

Before (base branch):
  Run 1: 45.2s, Run 2: 44.8s, Run 3: 45.1s, Run 4: 44.9s, Run 5: 45.3s
  Mean: 45.06s, Std dev: 0.20s

After (PR branch):
  Run 1: 12.1s, Run 2: 12.3s, Run 3: 11.9s, Run 4: 12.0s, Run 5: 12.2s
  Mean: 12.10s, Std dev: 0.15s

Improvement: 73% reduction in processing time
```

**Example of an invalid benchmark result:**

```
It's faster now. Was slow before, now it's fast.
```

---

## S-PERF.3 Multiple test runs and statistical significance

A single benchmark run is insufficient because performance measurements are noisy. A single run may be affected by:

- Operating system scheduling (other processes consuming CPU)
- Disk cache state (cold vs warm cache)
- Memory pressure from other applications
- Garbage collection pauses (in managed languages)
- Network latency variation (for network-dependent benchmarks)

**Requirements for statistically valid benchmarks:**

1. **Minimum 5 runs** for each measurement (before and after).
2. **Report mean and standard deviation** (or median and interquartile range).
3. **Ensure measurements are stable.** If standard deviation is more than 10% of the mean, the benchmark is too noisy. The author should reduce variance by:
   - Closing other applications
   - Running on a dedicated machine
   - Using CPU affinity to pin the process to specific cores
   - Increasing the workload size (so the measurement is dominated by the work, not by setup/teardown)
4. **Improvement must exceed the noise.** If the before measurement has a mean of 45s with std dev of 5s, and the after measurement has a mean of 43s, the improvement (2s) is within the noise (5s). The improvement is not statistically significant.

**What to ask the author if benchmarks are insufficient:**

"Can you run the benchmark at least 5 times for both the before and after cases, and report the mean and standard deviation? A single run may be affected by system noise. I need to verify that the improvement is statistically significant (larger than the measurement variation)."

---

## S-PERF.4 Verifying no functionality regressions

Performance optimizations sometimes sacrifice correctness for speed. The optimized code must produce exactly the same output as the original code for all inputs.

**Common functionality regressions from performance optimizations:**

| Optimization | Potential Regression |
|-------------|---------------------|
| Caching | Stale data returned when the source changes |
| Lazy loading | Object not available when needed by a different code path |
| Parallel processing | Race conditions causing intermittent wrong results |
| Algorithm replacement | Edge cases handled differently by the new algorithm |
| Buffer size reduction | Truncation of large inputs |

**Checklist:**

- [ ] All existing tests pass with the optimization applied
- [ ] The optimized code produces the same output as the original for the benchmark workload
- [ ] Edge cases are tested (empty input, very large input, malformed input)
- [ ] If caching is added, cache invalidation is tested (what happens when the source data changes?)

**What to ask the author:**

"Do all existing tests pass with this optimization? Have you verified that the output is identical for the benchmark workload (not just that it completes faster)?"

---

## S-PERF.5 Significance justification (complexity vs improvement tradeoff)

Every performance optimization adds complexity. The improvement must be significant enough to justify the added complexity and maintenance burden.

**Questions to evaluate the tradeoff:**

1. **How large is the improvement?** A 2% improvement in a function called once at startup is not worth adding a complex caching layer. A 73% improvement in a function called millions of times per request is clearly worthwhile.

2. **How critical is the affected code path?** An optimization in the critical request path (user-facing latency) is more valuable than one in a background batch job that runs overnight.

3. **How much complexity is added?** Adding a cache requires cache invalidation logic, which is notoriously error-prone. Is the improvement large enough to justify this risk?

4. **Is the improvement needed now?** Premature optimization adds complexity without immediate benefit. If the code is fast enough for current usage, the optimization can wait.

**Decision framework:**

| Improvement | Complexity Added | Decision |
|-------------|-----------------|----------|
| Large (>50%) | Low | APPROVE -- clear benefit with low risk |
| Large (>50%) | High | APPROVE with caveats -- ensure tests cover the complexity |
| Small (<10%) | Low | APPROVE if the code is cleaner, otherwise COMMENT |
| Small (<10%) | High | REQUEST CHANGES -- not justified |
| Marginal (<5%) | Any | REQUEST CHANGES -- not justified unless in a hot path |

---

## S-PERF.6 Example: Reviewing a caching optimization PR

**PR title:** "Add LRU cache to database query results for user profiles"

**PR diff (simplified):**

```python
+from functools import lru_cache
+
+# Cache user profiles to avoid repeated database queries.
+# Cache size of 1000 covers the typical active user count.
+@lru_cache(maxsize=1000)
 def get_user_profile(user_id: int) -> UserProfile:
     """Fetch user profile from the database."""
     return db.query(UserProfile).filter_by(id=user_id).first()
```

**Review using this protocol:**

**S-PERF.2 (Benchmarks):**

Author provides:
```
Before: API response time for /dashboard endpoint
  Mean: 320ms, Std dev: 45ms (10 runs)

After: API response time for /dashboard endpoint
  Mean: 85ms, Std dev: 12ms (10 runs)

Improvement: 73% reduction in response time
```

PASS -- Benchmarks are provided with multiple runs.

**S-PERF.3 (Statistical significance):**

Before: 320ms +/- 45ms. After: 85ms +/- 12ms. The improvement (235ms) far exceeds the noise (45ms). The improvement is statistically significant.

PASS.

**S-PERF.4 (Functionality regressions):**

CONCERN -- This is a critical check for caching. The `lru_cache` decorator caches results forever (until the cache is full). If a user profile is updated, the cached version will be stale.

Questions for the author:
1. "What happens when a user updates their profile? The cached version will be returned instead of the updated one. How is cache invalidation handled?"
2. "Is `get_user_profile` called from any code path where real-time data is required (for example, a profile edit page that should show the latest saved data)?"
3. "Is the `lru_cache` appropriate here, or should a time-based cache (TTL cache) be used instead?"

**S-PERF.5 (Significance justification):**

The improvement is 73% on a user-facing endpoint. The added complexity is moderate (caching with no invalidation). The improvement is significant enough to justify the optimization IF cache invalidation is properly addressed.

**Review response:**

"The benchmark results show a significant improvement (73% reduction in response time). However, using `lru_cache` on a database query creates a stale data risk. The cache has no invalidation mechanism, so if a user updates their profile, the old data will be served from cache until it is evicted by cache pressure.

Please address:
1. How will cache be invalidated when a user profile is updated?
2. Consider using a TTL-based cache (for example, `cachetools.TTLCache` with a 60-second expiry) instead of `lru_cache`, so stale data is automatically refreshed.
3. Add a test that verifies cache invalidation: update a profile, then call `get_user_profile` and confirm the updated data is returned."
