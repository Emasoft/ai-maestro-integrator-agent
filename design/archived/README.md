# design/archived/

Once-approved TRDDs that reached a terminal-DONE state — `completed`,
`cancelled`, or `superseded`. Kept as the audit trail (never deleted).
**`failed` is NOT archived** — it stays OPEN in `design/tasks/` and is retried;
giving up on a failed TRDD is an explicit cancel. See
`~/.claude/rules/trdd-approval-tiers.md`.
