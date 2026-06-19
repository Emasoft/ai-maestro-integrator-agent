---
prrd-version: 1.1
updated: 2026-06-11T11:25:03+0200
project: ai-maestro-integrator-agent
project-id: ai-maestro-integrator-agent
canonical-source: design/requirements/PRRD.md
mirrors: []
---

# Project Requirements & Rules — ai-maestro-integrator-agent

INTEGRATOR role plugin (AMIA) — quality gates, review, deploy/publish via DEPLOYER/RELEASER subagents.

## §0. Canonical source + copies

| Path | Role | Update strategy |
|---|---|---|
| `design/requirements/PRRD.md` | **CANONICAL** for this project | Edit first. Bump `prrd-version:`. Update `updated:`. |

## §I. How to read this document

Rule citation form: `PRRD G<n>.<v>` (golden, user-set) or `PRRD S<n>.<v>`
(silver, manager-mutable). Rule numbers are globally unique across G/S;
promote/demote flips the letter without changing the number. The
`get-prrd.py <n>` script returns a rule's text by bare number. Full
spec: `~/.claude/rules/prrd-design-rules.md`.

## 🥇 GOLDEN — set by the USER (immutable to MANAGER)

- **G1.1** — Every agent that writes to GitHub (issue, issue comment, PR, PR comment, PR review, discussion, release note) MUST begin the body with a one-line self-identification of which agent/role/plugin authored it, because all AI Maestro agents share the single human-owner GitHub identity (the owner's gh CLI auth). Recommended leading line: _Posted by the Claude developing **<plugin-or-role>** (via the shared @owner gh auth)._ Commit messages SHOULD carry an `Agent: <role>` trailer.

## 🥈 SILVER — MANAGER-mutable (agents propose via COS)

- **S2.1** — Entering the release pipeline (ship/publish/deploy to users) requires a recorded MANAGER Tier-2 approval BEFORE execution. The approval lives as an `APPROVED` release entry in the approving TRDD's `## Approval log` and is passed to the release scripts via `--approval-trdd`; the scripts hard-refuse (exit 7) without it. Team membership is NOT approval.
- **S3.1** — Every GitHub repo in this project carries the ratified `baseline-history-protect` + `baseline-pr-and-checks` rulesets. Applying the baseline as-is is Tier 0; ANY deviation (extra/loosened rule, new/removed bypass actor, downgraded check, enforcement downgrade) is Tier 2 and needs MANAGER approval before it is applied.
- **S4.1** — Every skill, command, hook, and runtime behavior ships a REAL test (no mocks). The `tests/` runner exits 0 on all-pass / non-zero on any-fail and gates publish; a skill/command/hook without a test is not done.
- **S5.1** — The release pipeline is INTEGRATOR-designed per project type (library→registry, app→sign+release, service→containerize+deploy). The CPV canonical `publish.py` applies ONLY to the Claude-Code-plugin project type and only as a recommendation; the USER may mandate any custom pipeline, which overrides the type default.
- **S6.1** — INTEGRATOR owns the `column → completed/published/live` flip and validates the shipped artifact satisfies the TRDD before flipping. No agent self-marks its own work completed.
- **S7.1** — Reports, audits, and scan outputs are written under `./reports/<component>/` (gitignored, local-time+offset timestamped) and never committed; both `/reports/` and `/reports_dev/` stay in `.gitignore`.
