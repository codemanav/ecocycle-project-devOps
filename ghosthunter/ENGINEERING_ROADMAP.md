# Engineering roadmap: deeper systems work

Ghost Hunter today is an incident-response agent applied to SRE: event-driven detection, model-driven
root-cause analysis, guarded remediation and verified recovery. This roadmap lists the next pieces of work
that push it into deeper engineering areas (model serving, distributed systems, platform), each with a
concrete approach and a measurable result. Baselines below are from the current code and test runs.

## Current baselines

| Area | Today | Where in the code |
|---|---|---|
| Local diagnosis latency | 40–45 s per decision in benchmark runs, 92 s in a later run (`gemma4:e4b`, Ollama on an Apple-silicon GPU) | [`model.py`](model.py) `_call_ollama` |
| Model "thinking" before answering | ~1,700–2,200 tokens per decision; the Gemini API rejects `thinking_level` and `thinking_budget` for Gemma 4 | [`model.py`](model.py) `_call` |
| Output format | Free text, JSON extracted with a regex afterwards | [`model.py`](model.py) `_parse` |
| Coordination | One machine only: in-process mutex plus a `flock` lock file | [`agent.py`](agent.py) `run_incident` |
| Demo app call between services | `transactions-service` calls `users-service` with a blocking WebClient call and no client timeout | [`UsersClient.java`](../transactions-service/src/main/java/com/ecocycle/transactions/client/UsersClient.java) |
| Targets | Local docker-compose only | [`core.py`](core.py), [`targets/`](targets/) |

---

## 1. Model serving and inference performance

**Goal:** cut the local diagnosis time well below 40–92 s without losing decision accuracy, and show the
trade-offs with numbers.

| Work | Approach | Measure |
|---|---|---|
| **Prefix (KV-cache) reuse** | The system prompt (target description, call graph, action list) is identical on every call. Put it in a fixed prefix so the runtime reuses its key/value cache instead of recomputing it; keep the per-incident evidence at the end. | Time to first token and total latency, cold vs warm, same evidence |
| **Constrained JSON output** | Pass a JSON schema for the decision (`root_cause`, `evidence`, `action`, `params`, `confidence`) through Ollama's structured-output `format` field, so the reply is always valid and never needs regex repair. | Parse failures (target 0), output tokens per decision |
| **Quantization comparison** | Run the same A/B/C scenarios on q4, q8 and bf16 builds of Gemma 4. | Latency, resident memory, correct-action rate per build |
| **Speculative decoding** | Compare the multi-token-prediction build (`gemma4:26b-a4b-it-mtp-q4` in the Ollama library) against the standard build. | Tokens per second, total latency, correct-action rate |
| **Context sizing** | Measure prompt size per incident and set `num_ctx` to fit it rather than a fixed 8,192, which reduces KV-cache memory. | Prompt tokens, memory, latency |

**Deliverable:** a benchmark script (`bench/`) that runs every scenario N times per configuration and writes
a results table; the README results section updated with the best configuration and the before/after numbers.

**Done when:** the median local decision is measurably faster than the 40–45 s baseline with no drop in the
correct-action rate across A, B and C.

---

## 2. Distributed coordination and failure handling

**Goal:** make Ghost Hunter safe to run as several instances on several hosts, and handle failures that only
appear in distributed systems.

| Work | Approach | Measure |
|---|---|---|
| **Leader election** | Replace the single-machine `flock` with a lease: a row in Postgres (or an etcd lease) with an expiry and a fencing token. Only the leaseholder may remediate; the token is checked before every action so a paused former leader cannot act late. | Two or three instances watching the same app: exactly one remediation per incident; failover time when the leader is killed |
| **Network-partition scenario** | New fault: disconnect a service from the compose network (`docker network disconnect`). Add a `reconnect_network` action. | Correct diagnosis and fix; time to recovery |
| **Latency-injection scenario** | New fault: add delay to a container's traffic with `tc netem`. The correct response is not a restart. | Whether the model avoids restarting a slow-but-healthy service |
| **Database replication and failover** | Add a streaming replica for one EcoCycle database and a `promote_replica` action guarded by the allowlist. | Recovery time and data checks after the primary is stopped |

**Done when:** the leader-election test shows no double remediation across instances, and each new scenario
has a correct fix that Ghost Hunter chooses in repeated runs.

---

## 3. Resilience fix in the demo app: the cascading hang

**Goal:** remove a real cascading-failure risk and prove it with fault injection.

- **Problem:** when a transaction is marked `COMPLETED`, `transactions-service` calls `users-service`
  (`PUT /users/{id}/greenscore`) and blocks with no timeout. A hung `users-service` hangs
  `transactions-service` too.
- **Fix:** a client timeout on the WebClient call, plus a circuit breaker (for example Resilience4j) that
  fails fast while `users-service` is unhealthy, and a defined fallback for the green-score update.
- **Scenario D:** freeze `users-service`, then complete a transaction. Before the fix: `transactions-service`
  hangs. After: the request fails fast and `transactions-service` stays healthy. Add the scenario to
  [`targets/ecocycle.yaml`](targets/ecocycle.yaml) and check that Ghost Hunter fixes `users-service`, not
  `transactions-service`.

**Done when:** scenario D passes after the fix, and fails as described without it.

---

## 4. Platform: Kubernetes target and reliability metrics

| Work | Approach | Measure |
|---|---|---|
| **Kubernetes target** | A target type for a local k3d cluster: health from readiness probes, evidence from pod status, events and logs, and actions such as `rollout_restart`, `scale` and `patch_resources`, all behind the same allowlist. | A/B/C equivalents pass on Kubernetes |
| **Chaos benchmark** | Inject N random faults from the scenario list and record detection time, time to recovery and correct-action rate for each. | Distribution of time to recovery (median, p90), correct-action rate |
| **Metrics export** | Expose detection time, decision latency, remediation outcomes and escalations as Prometheus metrics. | Dashboards and alerts on Ghost Hunter itself |

---

## Suggested order

1. **Model serving and inference performance:** builds directly on what exists and produces numbers quickly.
2. **The cascading-hang fix with scenario D:** small, self-contained, and closes a known risk.
3. **Leader election:** the main step from single-machine to multi-instance safety.
4. **Network-partition, latency and replication scenarios.**
5. **Kubernetes target and chaos benchmark.**
