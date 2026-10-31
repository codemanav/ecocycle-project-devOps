# Benchmarks: Gemini API vs local open-weight Gemma 4

Same agent, same evidence, same prompt, same allowlist; only the model backend changes.
Measured 2026-10-31 on a MacBook (Apple silicon, 16 GB RAM) with the EcoCycle demo app running
alongside. Metrics chart sent as image input in every run.

| Scenario | Correct action | Gemini API `gemma-4-26b-a4b-it` | Local Ollama `gemma4:e4b` |
|---|---|---|---|
| **A** users-db stopped | `start_container(users-db)` | ✅ 23.0 s · conf 1.0 | ✅ 39.9 s · conf 1.0 |
| **B** OOM crash loop | `raise_memory_limit(marketplace-service, 512)` | ✅ 28.6 s · conf 1.0 | ✅ 39.7 s · conf 0.9 |
| **C** service frozen | `restart_container(marketplace-service)` | ✅ 44.0 s · conf 0.9 | ✅ 43.1 s · conf 1.0 |
| | **Correct** | **3 / 3** | **3 / 3** |

Time is model reasoning only (one decision). Detection, the action and verification add roughly 10–20 s;
every run above was verified recovered with all health checks and smoke requests passing.

## Observations

- **Across the whole day's audit log, 17 of 17 Gemma decisions (both backends, all scenarios, manual
  and watch mode) chose the correct action.**
- **Both backends chose the right action in every scenario**, including C, where restarting is
  correct, so neither model is simply defaulting to "restart".
- **Gemini API latency varies a lot.** Across the day the same kind of decision took 13–180 s, and one call hit
  a server-side deadline, which is why model calls have a wall-clock deadline and a retry.
  The local model was steady at about 40 s.
- **Chart reading.** The API model described the chart accurately every time, for example "users-db
  memory drops to 0 MB at −18 s" and "memory limit line at 100 MB with usage above it". The local e4b
  model described it in B only, and said "no chart" in A and C, although its decisions were still right
  from logs and container state alone.
- **Resources.** `gemma4:e4b` is a 9.5 GB download and uses ~9.4 GB while loaded (100% GPU via MLX).
  On a 16 GB machine that runs, but with little memory to spare.

## Reproduce

```bash
./ghosthunter haunt A && sleep 25 && ./ghosthunter --chart recover --yes --no-postmortem && ./ghosthunter haunt reset
./ghosthunter --backend ollama haunt A && sleep 25 && ./ghosthunter --backend ollama --chart recover --yes --no-postmortem
```
