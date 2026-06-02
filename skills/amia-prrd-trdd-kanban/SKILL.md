---
name: amia-prrd-trdd-kanban
description: "INTEGRATOR's role in the PRRD / TRDD / Kanban workflow. Use when INT reviews code in ai_review, dispatches the DEPLOYER subagent for service TRDDs (deploy → live), the RELEASER subagent for tool TRDDs (publish → published), or investigates anomalies in live_auditing."
allowed-tools: "Bash(python3:*), Bash(get-prrd.py:*), Bash(findprrd.py:*), Bash(findtrdd.py:*), Bash(kanban.py:*), Bash(git:*), Bash(gh:*), Read, Edit, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

## Overview

This is the INTEGRATOR's role-specific layer of the PRRD / TRDD /
Kanban model. For universal mechanics, see `prrd-trdd-kanban` in
`ai-maestro-plugin`.

## Approval discipline — INT triggers many non-exempt transitions

Check the **prrd-trdd-kanban** universal skill's `exempt-operations.md`
reference (bundled in ai-maestro-plugin) BEFORE triggering any transition. INT's
**exempt** operations: launching ai_review on a PR (review request
only, NOT merge), running the AI code-reviewer subagent, collecting
audit-evidence in `live_auditing` (entry-mode investigation), CI run
invocations. INT's **non-exempt** (MUST request MANAGER approval
via COS): `complete → publish`, `complete → deploy`, `publish →
published` (after RELEASER success), `deploy → live` (after
DEPLOYER success), `ai_review → human_review` (escalation), merging
ANY PR, `live_auditing (entry) → dev` (audit-confirmed issue
requires alignment), force-`failed`. INT is the role that most often
needs MANAGER approval — almost every shipping decision is gated.

INTEGRATOR owns the **ship and operate** stages. It also spawns two
specialised subagents:

- **DEPLOYER** (`subagent_type: deployer`) — handles `deploy → live`
  for service TRDDs (`release-via: deploy`).
- **RELEASER** (`subagent_type: releaser`) — handles `publish →
  published` for tool TRDDs (`release-via: publish`).

Subagents have NO AMP identity (per R6 v3); they return results to
INTEGRATOR, which relays via AMP up the chain (INT → ORCH → COS →
MANAGER → USER).

## Columns INT owns

| Column | Ownership detail |
|---|---|
| `ai_review` | INT (or its code-reviewer subagent) reviews code that has passed tests. Approves → human_review or complete. Rejects → back to dev. |
| `publish` | INT spawns RELEASER subagent to publish a tool/package. Awaits result. |
| `deploy` | INT spawns DEPLOYER subagent to deploy a service. Awaits result. |
| `live_auditing` | INT (or AUTONOMOUS in some setups) authors new audit TRDDs and investigates; routes to dev if issue-confirmed. |

INT also watches `live` for soak windows that need post-deploy
monitoring before declaring done.

## Subagent dispatch protocol

When a TRDD reaches `complete` AND `release-via != none`, INT spawns
the matching subagent:

```python
# Inside INT's main-agent decision loop:
trdd = load_trdd(uid)
if trdd.release_via == "publish":
    result = Agent(
        subagent_type="releaser",
        description=f"Publish TRDD-{trdd.uid8}",
        prompt=f"""Publish TRDD-{trdd.uid8} '{trdd.title}'.
        Target: {trdd.publish_target} / channel: {trdd.publish_channel}.
        Run the project's publish pipeline; verify the released artifact
        is installable. Return a structured result.""",
    )
elif trdd.release_via == "deploy":
    result = Agent(
        subagent_type="deployer",
        description=f"Deploy TRDD-{trdd.uid8}",
        prompt=f"""Deploy TRDD-{trdd.uid8} '{trdd.title}' to
        {trdd.deploy_target}. Run the project's deploy pipeline; verify
        the service is live and responding. Return a structured result.""",
    )
```

The subagent's return value updates the TRDD frontmatter:

- On success (publish): `column: published`, `published-version:`,
  `published-at:`
- On success (deploy): `column: live`, `live-since:`
- On failure: `column: failed`, body grows a failure post-mortem

## Transitions INT triggers

- **#11** `ai_review → human_review` — when human review required
- **#12** `ai_review → complete` — when only AI review required
- **#13** `ai_review → dev` — review found issues
- **#16, #17** `complete → publish` / `complete → deploy` — spawn
  subagent
- **#19** `publish → published` — RELEASER returned success
- **#20** `publish → failed` — RELEASER returned hard-fail
- **#21** `deploy → live` — DEPLOYER returned success
- **#22** `deploy → failed` — DEPLOYER returned hard-fail
- **#23** `live → live_auditing` — entering soak window
- **#24** `live_auditing (soak) → live` — soak window elapsed clean
- **#25** `(new) → live_auditing (entry)` — author audit TRDD
- **#26** `live_auditing → complete` — audit benign
- **#27** `live_auditing → dev` — issue confirmed; move to fix

## Per-column checklists

### ai_review

- [ ] `findtrdd.py --column ai_review` → find pending reviews
- [ ] For each TRDD, fetch the PR (`gh pr view <pr-url>`)
- [ ] Spawn the existing `amia-code-reviewer` subagent (or run an
      lightweight inline review using llm-externalizer)
- [ ] Review against `relevant-rules:` (`get-prrd.py --cite <N>`)
- [ ] Decide: approve → `column: complete` (or `human_review` if
      required); reject → `column: dev`, write findings to body
- [ ] AMP-send to ORCH (via COS) with the decision

### complete → publish / deploy

- [ ] Verify all EHTs are terminal (`findtrdd.py --grep <parent-id>`
      on `eht:` members)
- [ ] Verify `release-via:` and `publish-target:` / `deploy-target:`
      are set
- [ ] Spawn DEPLOYER or RELEASER subagent (see above)
- [ ] Wait for return; parse structured result
- [ ] Update TRDD frontmatter
- [ ] AMP-send up the chain

### live_auditing (entry — new investigation)

- [ ] Author a new TRDD with `task-type: audit`, `column:
      live_auditing`, `audit-trigger: <source>`, `audit-target:
      <component>`, `audit-evidence: [<links>]`
- [ ] Investigate: read logs, sentry events, behavioral traces
- [ ] If benign: set `audit-conclusion: benign`, `column: complete`
- [ ] If issue: set `audit-conclusion: issue-confirmed`, body grows a
      `## Fix plan` section, `column: dev`. INT becomes the assignee
      OR ORCH re-assigns.

### live_auditing (soak — post-deploy monitoring)

- [ ] After `deploy → live`, if `soak-duration:` is set, edit
      `column: live_auditing` and start a timer
- [ ] During the window, periodically check sentry / log monitoring
      for alerts mentioning the deployed component
- [ ] If clean at the end of the window: `column: live` (terminal)
- [ ] If an issue surfaces: author a new audit TRDD and treat as
      "investigation found issue" — the original TRDD stays in `live`,
      the new audit TRDD drives the fix

## PRRD authority

INT may propose silver rules (e.g. CI / publish / deploy standards):

```bash
prrd-edit.py propose silver "All deploys must include a smoke test" \
            --target null --proposed-by integrator-<team> \
            --routed-via cos-<team>
```

## Resources

- Universal skill: `prrd-trdd-kanban`
- Existing INT skills: `amia-code-review-patterns`,
  `amia-github-pr-workflow`, `amia-ci-failure-patterns`
- DEPLOYER subagent: `agents/deployer.md`
- RELEASER subagent: `agents/releaser.md`
- INTEGRATOR persona: `agents/ai-maestro-integrator-agent-main-agent.md`
