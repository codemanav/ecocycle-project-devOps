---
name: ghost-hunter
description: Diagnose and fix failing docker-compose services with Ghost Hunter (Gemma 4 incident response). Use when a local docker-compose app is down, unhealthy, crash-looping, out of memory or hung, or when asked to check service health, find the root cause of an outage, recover a service, or read past incident postmortems.
---

# Ghost Hunter

Ghost Hunter investigates a failing docker-compose app (health checks, container state, OOM flags,
restart counts, filtered error logs, optional metrics chart), asks Gemma 4 for the root cause and a
remediation, checks that remediation against an allowlist, applies it, and verifies with real requests.

The CLI lives at `ghosthunter/ghosthunter` in this repository. Always pass `--json` so output is parseable.

## Workflow

1. **Check health.** `ghosthunter/ghosthunter --json status`. Exit code 0 means healthy; stop there.
2. **Diagnose without changing anything.** `ghosthunter/ghosthunter --json recover --dry-run`.
   Read `decision.root_cause`, `decision.evidence`, `decision.action`, `decision.params`, `allowed`.
3. **Ask the user before acting** unless they already told you to fix it. Show them the root cause,
   the evidence lines, and the proposed action.
4. **Recover.** `ghosthunter/ghosthunter --json recover --yes`. This acts, verifies with health checks
   and real requests, retries once with a new diagnosis if needed, and writes a postmortem.
   Exit code 0 = recovered and verified.
5. **Report.** Summarise `outcome`, the action taken, and give the `postmortem` path.

## Commands

| Command | Effect | Changes anything? |
|---|---|---|
| `status` | Health of each service | No |
| `diagnose [--force]` | Root cause + proposed action from Gemma 4 | No |
| `recover --dry-run` | Same as diagnose, plus allowlist validation | No |
| `recover --yes [--no-postmortem]` | Diagnose → act → verify → postmortem | **Yes** |
| `postmortems [--show N]` | List or print postmortems (newest is 0) | No |
| `scenarios` / `haunt <key>` / `haunt reset` | Demo fault injection | **Yes** (demo only) |
| `watch` | Long-running autonomous mode; do not start it from an agent session | **Yes** |

Global flags: `--json`, `--backend gemini|ollama` (ollama = local open-weight Gemma 4, data stays on the
machine), `--target path.yaml` (another app), `--chart` (send a metrics chart image to Gemma, adds ~20s).

## Exit codes

`0` healthy / recovered · `1` unhealthy or not recovered · `2` proposed action rejected by the allowlist ·
`3` usage or config error.

## Rules

- Never run `haunt` (fault injection) unless the user asked for a demo or test.
- Ghost Hunter can only run actions enabled in the target YAML on containers listed there. If the
  diagnosis is `escalate` or `allowed` is false, do not work around it with raw docker commands; report
  the diagnosis to the user.
- Model calls take 20–60s. Run commands with a timeout of at least 180s.
