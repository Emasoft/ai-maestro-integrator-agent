# Merge Strategies

This document explains the three merge strategies available for GitHub pull requests, when to use each one, and how they interact with branch protection rules.

## Table of Contents

- 2.1 Merge commit strategy
  - 2.1.1 When to use merge commits
  - 2.1.2 Commit history implications
- 2.2 Squash merge strategy
  - 2.2.1 When to use squash merge
  - 2.2.2 Commit message handling
- 2.3 Rebase merge strategy
  - 2.3.1 When to use rebase merge
  - 2.3.2 Linear history benefits
- 2.4 Branch protection implications
  - 2.4.1 Required status checks
  - 2.4.2 Required reviewers
  - 2.4.3 Allowed merge methods
- 2.5 Delete branch after merge
  - 2.5.1 Automatic branch deletion
  - 2.5.2 Manual branch deletion

---

## 2.1 Merge Commit Strategy

### 2.1.1 When to Use Merge Commits

The merge commit strategy creates a new commit that joins the PR branch into the base branch. This preserves the complete history of the feature branch.

**Use merge commits when:**

1. **Complete history is important**: You want to see exactly how the feature was developed
2. **Debugging needs context**: Bisecting issues requires understanding the development process
3. **Multiple authors**: The PR has contributions from several people whose attribution should be preserved
4. **Complex features**: Large features where understanding the breakdown is valuable
5. **Long-lived branches**: Feature branches that existed for weeks with meaningful individual commits

**Example result:**

```
*   Merge pull request #123 from user/feature-branch
|\
| * Add tests for new feature
| * Implement feature logic
| * Add feature configuration
|/
* Previous commit on main
```

**GraphQL merge method value**: `MERGE`

**CLI command:**
```bash
gh pr merge 123 --merge
```

### 2.1.2 Commit History Implications

**Advantages:**
- Full development history preserved
- Clear visibility of what was merged and when
- Easy to revert entire feature with single revert
- Git blame shows original commit authors and dates
- Bisect works across all commits

**Disadvantages:**
- Non-linear history can be harder to read
- Many small/fixup commits visible in main branch
- "Merge commit" noise in history
- Can make `git log --oneline` cluttered

**History shape:**
```
main:    A---B---C---M---E
              \     /
feature:       D---F
```

---

## 2.2 Squash Merge Strategy

### 2.2.1 When to Use Squash Merge

The squash merge strategy combines all PR commits into a single commit on the base branch. This creates a clean, linear history.

**Use squash merge when:**

1. **Clean history preferred**: You want main branch to have one commit per feature/fix
2. **Messy commit history**: PR has many fixup commits, "WIP", typo fixes
3. **Small changes**: Bug fixes, small features where individual commits don't add value
4. **Single-author PRs**: No need to preserve multiple contributor attributions
5. **Standard in team**: Team convention is squash for consistency

**Example result:**

```
* Implement user authentication (#123)
* Previous commit on main
* Earlier commit
```

**GraphQL merge method value**: `SQUASH`

**CLI command:**
```bash
gh pr merge 123 --squash
```

### 2.2.2 Commit Message Handling

When squashing, the commit message is constructed from:

1. **Default behavior**: PR title becomes commit subject, PR body becomes commit body
2. **GitHub UI**: Can edit message before merging
3. **API merge**: Can specify custom commit message

**API example with custom message:**

```bash
gh api repos/{owner}/{repo}/pulls/123/merge \
  -X PUT \
  -f merge_method=squash \
  -f commit_title="feat: add user authentication" \
  -f commit_message="Implements OAuth2 flow with Google and GitHub providers.

Closes #100, #101"
```

**Co-author attribution:**

GitHub automatically adds co-author trailers for contributors whose commits are squashed:

```
feat: add user authentication (#123)

Co-authored-by: Alice <alice@example.com>
Co-authored-by: Bob <bob@example.com>
```

**Best practices for commit messages:**

1. Use conventional commit format: `type: description`
2. Reference related issues: `Closes #100`
3. Keep subject under 72 characters
4. Add body for context when needed

---

## 2.3 Rebase Merge Strategy

### 2.3.1 When to Use Rebase Merge

The rebase merge strategy replays each PR commit on top of the base branch, creating new commits with new SHAs but preserving the original commit messages.

**Use rebase merge when:**

1. **Linear history required**: Team wants strictly linear history without merge commits
2. **Meaningful commits**: Each commit in PR is valuable and tested
3. **Bisect optimization**: Want to bisect individual changes, not just the whole PR
4. **Attribution important**: Need to preserve individual commit authorship
5. **No branch merging noise**: Don't want merge commits cluttering history

**Example result:**

```
* Add tests for new feature (rebased from #123)
* Implement feature logic (rebased from #123)
* Add feature configuration (rebased from #123)
* Previous commit on main
```

**GraphQL merge method value**: `REBASE`

**CLI command:**
```bash
gh pr merge 123 --rebase
```

### 2.3.2 Linear History Benefits

**Advantages:**
- Perfectly linear history (no merge commits)
- Each commit preserves its message and author
- Easy to read `git log --oneline`
- Bisect works on individual commits
- Cherry-pick individual commits easily

**Disadvantages:**
- New commit SHAs created (original SHAs lost)
- Can't easily identify "this feature was merged as one unit"
- If PR had conflicts resolved, resolution may need re-application
- Pre-merge CI ran on different SHAs than final commits

**History shape:**
```
Before:
main:    A---B---C
              \
feature:       D---E

After rebase merge:
main:    A---B---C---D'---E'
(D' and E' are new commits with same content as D, E)
```

**Important note on SHAs:**

The rebased commits have different SHAs than the original PR commits. This means:
- References to original commit SHAs won't work
- CI that ran on PR won't match final commits
- Any downstream branches based on PR will diverge

---

## 2.4 Branch Protection Implications

### 2.4.1 Required Status Checks

Branch protection can require specific status checks to pass before merge.

**How status checks interact with merge strategies:**

| Strategy | Status Check Target |
|----------|-------------------|
| Merge | Last commit SHA of PR branch |
| Squash | Last commit SHA of PR branch |
| Rebase | Last commit SHA of PR branch (but final commits have new SHAs) |

**Important**: For rebase merge, status checks run on original commits, but merged commits have different SHAs. Some teams consider this a security concern.

**Query to check required status checks:**

```graphql
query {
  repository(owner: "owner", name: "repo") {
    branchProtectionRules(first: 10) {
      nodes {
        pattern
        requiredStatusCheckContexts
        requiresStatusChecks
        requiresStrictStatusChecks
      }
    }
  }
}
```

### 2.4.2 Required Reviewers

Branch protection can require a minimum number of approving reviews.

**Review requirements:**
- Minimum number of approvals (1, 2, 3, etc.)
- CODEOWNERS approval
- Dismiss stale reviews on new commits
- Require review from specific teams

**Query to check review status:**

```graphql
query {
  repository(owner: "owner", name: "repo") {
    pullRequest(number: 123) {
      reviewDecision
      reviews(last: 10) {
        nodes {
          state
          author { login }
        }
      }
    }
  }
}
```

**Review decision values:**
- `APPROVED`: Has required approvals
- `CHANGES_REQUESTED`: Has unaddressed change requests
- `REVIEW_REQUIRED`: Waiting for required reviews
- `null`: No review policy or no reviews yet

### 2.4.3 Allowed Merge Methods

Repository settings control which merge methods are allowed:

**Check allowed methods via API:**

```bash
gh api repos/{owner}/{repo} --jq '{
  allow_merge_commit: .allow_merge_commit,
  allow_squash_merge: .allow_squash_merge,
  allow_rebase_merge: .allow_rebase_merge
}'
```

**Branch protection can further restrict:**

Some organizations use branch protection to enforce specific merge methods for different branches:
- `main`: Squash only for clean history
- `develop`: Merge commits allowed for feature tracking
- `release/*`: Merge commits for audit trail

**Error when using disallowed method:**

```json
{
  "message": "Merge method 'rebase' is not allowed on this repository",
  "documentation_url": "https://docs.github.com/rest/pulls/pulls#merge-a-pull-request"
}
```

---

## 2.5 Delete Branch After Merge

### 2.5.1 Automatic Branch Deletion

GitHub can automatically delete the PR branch after merge.

**Repository setting:**
- Settings > General > "Automatically delete head branches"
- When enabled, PR branches are deleted immediately after merge

**Benefits:**
- Keeps repository clean
- No stale branches accumulating
- Clear signal that work is complete

**Check repository setting:**

```bash
gh api repos/{owner}/{repo} --jq '.delete_branch_on_merge'
```

### 2.5.2 Manual Branch Deletion

When automatic deletion is disabled, delete branches manually.

**Via gh CLI:**

```bash
# Delete after merge
gh pr merge 123 --delete-branch

# Delete remote branch directly
git push origin --delete feature-branch

# Via API
gh api repos/{owner}/{repo}/git/refs/heads/feature-branch -X DELETE
```

**Via GraphQL:**

```graphql
mutation {
  deleteRef(input: {
    refId: "MDM6UmVmMTIzNDU2Nzg5OnJlZnMvaGVhZHMvZmVhdHVyZS1icmFuY2g="
  }) {
    clientMutationId
  }
}
```

**Getting the ref ID:**

```graphql
query {
  repository(owner: "owner", name: "repo") {
    ref(qualifiedName: "refs/heads/feature-branch") {
      id
    }
  }
}
```

**When NOT to delete branches:**
- Release branches that may need hotfixes
- Long-lived development branches
- Branches used by other PRs as base
- Branches with ongoing related work

**Safety check before deletion:**

```bash
# Check if branch is used as base for other PRs
gh pr list --base feature-branch --state open
```

If other PRs use this branch as their base, do not delete it until those PRs are also merged or rebased.
