# GitHub Integration Skill

Complete bidirectional synchronization between Agent tasks and GitHub Projects V2, with standardized 9-label system, pull request workflow automation, and comprehensive issue tracking for orchestrator-driven development.

## Skill Structure

### SKILL.md
The main skill document that serves as a comprehensive map to all learning materials. It covers:
- Quick start overview and prerequisites
- Core concepts (Projects V2, 9-label system, bidirectional sync)
- Main workflows (issue lifecycle, synchronization, pull requests, batch operations)
- Detailed implementation guides
- Provided scripts and how to use them
- Troubleshooting section
- Implementation checklist
- Agent orchestration integration patterns

**Reading Order**: Start here. This is the main entry point.

### references/ Directory

Contains focused, standalone reference documents that cover specific topics in depth. Each reference document:
- Addresses a single specific topic
- Can be read independently
- Includes detailed examples and code samples
- Has its own table of contents

**Reference Documents Included**:

- `prerequisites-and-setup.md` - Prerequisites and initial GitHub CLI setup
- `multi-user-workflow.md` - Setting up multiple GitHub identities for owner/developer separation
- `github-projects-v2-fundamentals.md` - Core concepts of GitHub Projects V2
- `nine-label-system-design.md` - Design and principles of the 9-label system
- `bidirectional-sync-architecture.md` - Architecture and design of synchronization
- `issue-lifecycle-workflow.md` - Complete issue lifecycle from creation to closure
- `bidirectional-sync-workflow.md` - Synchronization operations and monitoring
- `pull-request-workflow.md` - Pull request creation, review, and merge workflows
- `batch-operations-and-filtering.md` - Advanced filtering and bulk operations
- `github-cli-authentication.md` - Detailed authentication setup and troubleshooting
- `creating-and-labeling-issues.md` - Issue creation and 9-label assignment
- `github-projects-v2-operations.md` - Projects V2 board operations
- `nine-label-system-usage-guide.md` - When and how to use each label
- `pull-request-automation.md` - Automating PR creation and workflow
- `script-sync-projects-v2.md` - Using the synchronization script
- `script-bulk-label-assignment.md` - Using the bulk labeling script
- `script-monitor-pull-requests.md` - Using the PR monitoring script
- `troubleshooting-authentication.md` - Authentication issues and solutions
- `troubleshooting-sync-failures.md` - Synchronization failures and solutions
- `troubleshooting-pr-linking.md` - Pull request linking issues
- `troubleshooting-labels.md` - Label-related issues and solutions
- `agent-orchestrator-integration.md` - Integration patterns for agent orchestrators
- `github-api-advanced-queries.md` - Complex GraphQL queries
- `webhook-configuration.md` - Real-time webhook setup
- `custom-automation-rules.md` - Custom GitHub Actions workflows
- `multi-repository-projects.md` - Cross-repository project management
- `github-cli-scripting.md` - Advanced GitHub CLI scripting patterns

### scripts/ Directory

Contains executable scripts that automate complex GitHub operations.

**Included Scripts**:

- `sync-projects-v2.py` - Bidirectional synchronization between agent tasks and GitHub Projects V2
  - When to use: After creating issues in agent system or after updating GitHub Projects V2
  - Syncs status, assignees, labels, and other fields

- `bulk-label-assignment.py` - Assigns labels to multiple issues matching filter criteria
  - When to use: Initializing projects with consistent labeling or correcting labeling across many issues
  - Supports adding and removing labels

- `monitor-pull-requests.py` - Monitors pull request status and alerts on changes
  - When to use: During active development to track CI/CD failures or waiting for reviews
  - Can watch specific states and send alerts

## How to Use This Skill

### For First-Time Users

1. **Read SKILL.md** - Get an overview of all concepts and workflows
2. **Review Prerequisites** - Ensure you have GitHub CLI installed and authenticated
3. **Follow the Checklist** - Use the implementation checklist in SKILL.md to set up your GitHub integration
4. **Try a Workflow** - Create your first issue and pull request following the documented workflows

### For Specific Topics

1. **Identify the topic** - What do you need to do?
2. **Check SKILL.md** - Find the relevant section
3. **Read the reference document** - Follow the link to the detailed reference
4. **Use code examples** - Copy and adapt the provided examples
5. **Run the scripts** - Use provided scripts to automate complex operations

### For Troubleshooting

1. **Check the Troubleshooting section** - See if your issue is listed
2. **Read the troubleshooting reference** - Follow the detailed solution steps
3. **Verify prerequisites** - Ensure you have GitHub CLI and authentication set up
4. **Check script logs** - Review output from any scripts you ran

## What This Skill Teaches

This skill provides comprehensive instruction on:

- **GitHub Projects V2**: Creating boards, managing custom fields, automating status transitions
- **9-Label System**: Standardized issue categorization with exactly nine labels
- **Issue Workflow**: Complete lifecycle from creation through closure
- **Pull Request Management**: Creating, reviewing, and merging pull requests
- **Bidirectional Sync**: Keeping agent tasks and GitHub in perfect synchronization
- **Batch Operations**: Working with multiple issues efficiently
- **Scripting**: Automating complex GitHub operations with Python and Bash
- **Agent Integration**: Integrating GitHub with agent orchestration systems

## Key Concepts

### GitHub Projects V2
Modern table-based project management directly integrated with GitHub. Provides customizable fields, automation rules, and bidirectional synchronization with issues and pull requests.

### 9-Label System
Standardized classification using exactly nine mutually-exclusive or clearly-separated labels:
- feature, bug, refactor, test, docs, performance, security, dependencies, workflow

### Bidirectional Synchronization
Automatic synchronization in both directions: agent system → GitHub and GitHub → agent system. Ensures perfect alignment without manual duplication.

### Orchestrator Context
Integration with agent orchestrators allows automated issue creation, pull request generation, and progress tracking at scale.

## Prerequisites

Before using this skill, you need:
- **GitHub Account** - With access to target repositories
- **GitHub CLI** - Version 2.14 or higher
- **Authentication** - One-time `gh auth login`
- **Repository Access** - Write permissions
- **Git Knowledge** - Basic understanding of commits and branches

## Files and Their Purpose

| File | Purpose |
|------|---------|
| `SKILL.md` | Main skill document - complete learning guide |
| `README.md` | This file - navigation guide for the skill |
| `references/` | Focused reference documents on specific topics |
| `scripts/` | Executable Python and Bash scripts for automation |

## Getting Help

If you encounter issues while following this skill:

1. **Check the Troubleshooting section** in SKILL.md
2. **Read the relevant reference document** for detailed explanations
3. **Review the provided examples** and adapt them to your situation
4. **Check script output** for error messages and solution hints

## Version History

- **1.0.0** (2025-12-29) - Initial release with core GitHub integration features

## Related Skills

This skill integrates with:
- **Agent Orchestration** - For automated issue creation and tracking
- **Python Scripting** - For advanced automation
- **Bash Scripting** - For command-line operations
- **Git Workflow** - For branch management and commits

## Contributing

To contribute improvements or fixes to this skill:
1. Review the skill structure and conventions
2. Follow the established patterns in SKILL.md and reference documents
3. Test any scripts with sample data before submitting
4. Update the version history and file lists
5. Ensure all new documents follow the established style and structure
