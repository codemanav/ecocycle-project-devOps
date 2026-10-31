# Good first issues 🎃

Drafts for GitHub issues labelled `good first issue` / `hacktoberfest`.

1. **Add a `scale_service` action.** Register an action in `actions.py` that runs
   `docker compose up -d --scale <service>=<n>`, with a guard on max replicas from the target YAML. Add tests.
2. **Slack webhook notifications.** When an incident starts, is escalated, or is resolved, post a short
   message (root cause, action, postmortem title) to a webhook set in `SLACK_WEBHOOK_URL`.
3. **Scenario D: cascading hang.** Freeze `users-service` and trigger a transaction `COMPLETED` update;
   transactions-service hangs because its WebClient call has no timeout. Correct action: restart
   users-service, not transactions-service. Add it to `targets/ecocycle.yaml` and the benchmark.
4. **A second example target.** Write `targets/` YAML for a small public docker-compose app (for example
   a Flask + Redis sample) with one scenario, to prove the harness is app-agnostic.
5. **Confidence threshold.** Add `min_confidence` to the target YAML; below it, Ghost Hunter escalates
   instead of acting (and the UI offers an "approve" button).
6. **Postmortem index.** `ghosthunter postmortems --summary` prints a table of incidents (date, root
   cause, action, time to recover) parsed from the saved Markdown.
7. **Tests for `core.collect_evidence`.** Mock `docker inspect` / `docker logs` and check which
   containers get logs pulled (failing service, its dependencies, non-running containers).
