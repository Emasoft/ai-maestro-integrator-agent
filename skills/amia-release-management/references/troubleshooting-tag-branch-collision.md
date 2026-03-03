# Troubleshooting: Tag-Branch Name Collision

## Contents
- What is a tag-branch name collision
- How collisions cause HTTP 300 errors
- How to detect collisions using amia_cleanup_version_branches.py
- How to resolve collisions safely
- Best practices to prevent future collisions

---

## What is a Tag-Branch Name Collision

A tag-branch name collision occurs when a git branch and a git tag share the same name. For example, if both a branch named `v1.2.0` and a tag named `v1.2.0` exist in the same repository.

This is a problem because git references (branches and tags) share a namespace. When both exist, tools that request the reference by name cannot determine which one is intended.

---

## How Collisions Cause HTTP 300 Errors

When GitHub's API receives a request for a tarball download using a version reference (e.g., `v1.2.0`), it needs to resolve the reference to a specific commit. If both a branch and tag with that name exist, the API returns HTTP 300 (Multiple Choices) instead of the expected HTTP 200 with the tarball.

This breaks:
- Auto-updater scripts that download release tarballs
- CI/CD pipelines that fetch specific versions
- Package managers that resolve versions via GitHub releases

The fix is to use explicit `refs/tags/` prefix in API calls. But for older tool versions that don't use this prefix, the collision must be resolved by deleting the branch.

---

## How to Detect Collisions

Run the cleanup script:

```bash
uv run scripts/amia_cleanup_version_branches.py
```

The script will:
1. List all version tags matching `vX.Y.Z` pattern
2. List all local and remote branches matching `vX.Y.Z` pattern
3. Identify collisions (where both a tag and branch have the same name)
4. Print deletion commands for review (does NOT auto-delete)

If no collisions are found, the script exits with code 0 and prints a success message.

---

## How to Resolve Collisions Safely

**IMPORTANT**: The script only prints commands. It does NOT execute them automatically.

1. Run the script to identify collisions
2. Review the printed deletion commands carefully
3. Verify that the colliding branches are not needed (check for open PRs)
4. Copy and execute the commands manually:

```bash
# Delete local branch
git branch -D v1.2.0

# Delete remote branch
git push origin --delete v1.2.0
```

5. Verify the tag still exists: `git tag | grep v1.2.0`

---

## Best Practices to Prevent Future Collisions

1. **Never create branches with version names** — Use `feature/`, `fix/`, `release/` prefixes instead
2. **Use release tags only** for versioned releases (`vX.Y.Z`)
3. **Use feature branches** for development (`feature/my-feature`, `fix/bug-123`)
4. **Delete release branches after merge** — If using a `release/vX.Y.Z` branch workflow, delete it after the tag is created
5. **Add a CI check** — Use the cleanup script in CI to detect collisions early

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | No collisions found (or script completed analysis) |
| Non-zero | Script error (e.g., not in a git repository) |
