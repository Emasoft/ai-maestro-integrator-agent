# Creating Worktrees: Environment Setup

## Overview

After creating a worktree, it needs to be configured before you can work in it. This document covers all 7 steps of environment setup.

## Table of Contents

1. [STEP 1: Navigate to Worktree](#step-1-navigate-to-worktree)
2. [STEP 2: Install Dependencies](#step-2-install-dependencies)
3. [STEP 3: Configure Environment Variables](#step-3-configure-environment-variables)
4. [STEP 4: Setup Database](#step-4-setup-database)
5. [STEP 5: Build Assets](#step-5-build-assets)
6. [STEP 6: Verify Tests Pass](#step-6-verify-tests-pass)
7. [STEP 7: Start Services](#step-7-start-services)

---

## STEP 1: Navigate to Worktree

**Action**: Change directory to the newly created worktree.

```bash
cd ../review-GH-42
```

**Verification**: Confirm you're in the correct directory:
```bash
pwd
# Should output something like: /Users/username/projects/review-GH-42

git branch --show-current
# Should show the branch name checked out in this worktree
```

---

## STEP 2: Install Dependencies

**Purpose**: Install all libraries and packages required by the project.

**For Node.js projects**:
```bash
# Using npm
npm install

# Using pnpm (faster, recommended)
pnpm install

# Using yarn
yarn install
```

**For Python projects**:
```bash
# Using pip with requirements file
pip install -r requirements.txt

# Using uv (faster, recommended)
uv venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt

# Using poetry
poetry install
```

**For Ruby projects**:
```bash
bundle install
```

**For Go projects**:
```bash
go mod download
```

**What "install dependencies" means**: Most projects rely on external libraries (dependencies). This step downloads and installs all required libraries so the code can run.

**Complexity factors** (affects download duration):
- Small projects: Few dependencies, quick downloads
- Medium projects: Moderate dependencies
- Large projects: Many dependencies, longer downloads

**Common issues**:
- If install fails, check Node/Python/Ruby version matches project requirements
- Clear package manager cache if seeing corruption errors
- Check network connection if downloads fail

---

## STEP 3: Configure Environment Variables

**Purpose**: Set up environment-specific configuration (API keys, database URLs, ports, etc.).

**Action**: Copy the environment template and customize it.

```bash
# Copy template
cp .env.example .env

# Edit .env file with worktree-specific values
```

**Required customizations**:

1. **Ports** (use allocated ports from registry):
```bash
PORT=3002
API_PORT=3003
```

2. **Database URL** (use worktree-specific database):
```bash
DATABASE_URL=postgresql://localhost:5433/myapp_review_gh_42
```

3. **Application name** (for logging/monitoring):
```bash
APP_NAME=myapp-review-gh-42
```

4. **API keys and secrets** (copy from main repo or use test keys):
```bash
# For review/test worktrees, use test API keys
STRIPE_API_KEY=sk_test_xxxxx

# For production testing, use real keys (CAREFUL!)
# Only if absolutely necessary and you understand the risks
```

**What NOT to customize**:
- Production API keys (use test keys)
- Production database URLs (use local/test databases)
- Any credentials that could affect production systems

---

## STEP 4: Setup Database

**Purpose**: Create and configure a separate database for the worktree.

**Why separate databases**: Each worktree should have its own database to prevent:
- Data conflicts between worktrees
- Accidental data corruption
- Migration conflicts
- Test data pollution

**For PostgreSQL**:
```bash
# Create new database
createdb -p 5433 myapp_review_gh_42

# Run migrations
npm run db:migrate
# or: python manage.py migrate
# or: rails db:migrate
```

**For MySQL**:
```bash
# Create new database
mysql -P 3307 -e "CREATE DATABASE myapp_review_gh_42;"

# Run migrations
npm run db:migrate
```

**For SQLite** (no setup needed, file-based):
```bash
# Just run migrations
npm run db:migrate
# Creates: db/review_gh_42.sqlite3
```

**Seed test data** (optional):
```bash
npm run db:seed
# or: python manage.py loaddata fixtures/test_data.json
# or: rails db:seed
```

---

## STEP 5: Build Assets

**Purpose**: Compile/bundle frontend assets if required by the project.

**For projects with asset compilation**:
```bash
# Build frontend assets
npm run build

# Or start dev server with hot reload
npm run dev
```

**For projects without asset compilation**:
Skip this step.

**What "build assets" means**: Modern web apps often use tools like Webpack, Vite, or Parcel to bundle JavaScript, CSS, and images. This step compiles those assets.

---

## STEP 6: Verify Tests Pass

**Purpose**: Ensure the worktree is set up correctly by running tests.

**Action**: Run the test suite.

```bash
# Run all tests
npm test

# Run specific test suite
npm test -- --testPathPattern=integration

# Run with coverage
npm test -- --coverage
```

**Expected result**: All tests should pass. If tests fail:
- Check environment variables are correct
- Verify database is set up properly
- Confirm dependencies installed successfully
- Check ports are not already in use

**If tests fail**:
1. Read error messages carefully
2. Check test logs for specific failures
3. Verify environment matches main repo
4. Ask for help if stuck

---

## STEP 7: Start Services

**Purpose**: Start the application and verify it runs.

```bash
# Start development server
npm run dev

# Or start multiple services (in separate terminals)
# Terminal 1: Frontend
cd ../review-GH-42
npm run dev:frontend

# Terminal 2: Backend
cd ../review-GH-42
npm run dev:backend
```

**Verification**:
```bash
# Check frontend is running
curl http://localhost:3002

# Check API is running
curl http://localhost:3003/api/health
```

**What success looks like**:
- No error messages in terminal
- Application accessible in browser
- API responds to requests
- No port conflict errors

---

## Related Documentation

- [Standard Creation Flow](./creating-worktrees-part1-standard-flow.md)
- [Purpose-Specific Patterns](./creating-worktrees-part2-purpose-patterns.md)
- [Port Allocation Strategy](./creating-worktrees-part3-port-allocation.md)
- [Commands Reference and Checklist](./creating-worktrees-part5-commands-checklist.md)
- [Troubleshooting](./creating-worktrees-part6-troubleshooting.md)
