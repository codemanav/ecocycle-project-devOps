# InfraPilot — Hackathon Handoff

Hacktoberfest Hack Day Raleigh (Oct 31, 2026). Submissions close **4:30 PM EDT**. Solo build.

## Hackathon
- **Event:** Hacktoberfest Hack Day Raleigh x Hack_NCState Applied AI Club at NC State (MLH).
- **When / where:** Sat Oct 31, 2026, 9:00 AM – 4:30 PM EDT, in person, Raleigh NC. Checked in.
- **Submit:** https://www.mlh.com/events/hacktoberfest-hack-day-raleigh-x-hack_ncstate-applied-ai-club-at-nc-state/submissions/new — submit a draft early and update it.
- **Team:** solo; teammates are not available.
- **One track only** may be selected per submission.

## Prize categories (for reference)
1. **Best Use of Gemma 4** (Google DeepMind) — **our track.**
   > It's time to see how much you can build with a lightweight, open model. Gemma 4 packs multimodal intelligence into an open-weights model that you can access through the Gemini API. So, what can Gemma 4 bring to your project?
   > - **Multimodal Experience:** Work with text and images to create an assistant that understands more of what users share.
   > - **Focused AI Tools:** Build a focused AI tool for learning, creativity, productivity, or your community.
   > - **Rapid Prototyping:** Experiment with an open model while using the Gemini API to move quickly from an idea to a working prototype.
   - Build with Gemma 4: https://mlh.link/gemma
2. **Best Open-Source AI Project** (DigitalOcean / Hacktoberfest) — not entered. Prize: exclusive Hacktoberfest 2026 Winner DEV badge + MLH swag bag.
   > Build an original project that uses open-source or open-weight AI as an important part of how it works. Teams could create an agent skill, build with an open-weight large or small language model, or build or adapt an open-source model harness.
3. **Best Use of Maritime** (Maritime, YC F26) — not entered; optional only if access works. Prize: $1000 Maritime credits.
   > Hack together a unique, innovational project that fully utilizes the capabilities of Maritime's hosting agents.
   > - **Autonomous Operations:** Build self-healing systems that automatically isolate faults, remediate bugs, and adjust resources in real time.
   > - **Agentic Workflows:** Create innovative applications that allow hosting agents to dynamically reconfigure architecture and route traffic on the fly.
   > - **Rapid Prototyping:** Experiment with multi-agent orchestration to move seamlessly from a bold concept to a working prototype.
   - Maritime gives every agent its own persistent micro-VM. Signup: https://maritime.sh → https://maritime.sh/billing → Subscribe on Growth → promo code `HACKNCSTATE` under "Add promotion code". Docs index: https://maritime.sh/llms.txt
   - Constraints learned from docs: agent serves HTTP on `0.0.0.0:$PORT` (currently 18789, don't hardcode 8080); `GET /health` must return 2xx; `POST /chat` must reply within 30 s; only `/data` persists; use exec-form `CMD`; builds take 1–3 min. Maritime cannot reach the laptop, so the laptop must initiate all connections.

## Official judging criteria
| # | Criterion | What judges evaluate | Scoring |
|---|---|---|---|
| 1 | Relevance & Problem Definition | Does your project meet the requirements of the challenge(s) you selected? | Yes / No |
| 2 | Impact & Value | How much impact could your project have in its field? Is that impact clear, positive, and credible? | 1–5 |
| 3 | Innovation & Creativity | Does your project address the challenge in an engaging or creative way? | 1–5 |
| 4 | Feasibility & Scalability | Could your project realistically expand in its field with additional time and resources? | 1–5 |
| 5 | Technical Execution | Does the prototype work well enough to demonstrate the concept? Does it apply a technical concept effectively? | 1–5 |
| 6 | Demo & Communication | Is the demonstration professional? Does the team concisely explain the goal, purpose, limitations, and next steps? | 1–5 |

### How InfraPilot answers each criterion
| Criterion | Approach |
|---|---|
| Relevance | Gemma 4 is essential to the working agent: it makes the diagnosis and chooses the action. Add a chart image to the prompt to use multimodal. |
| Impact | Reduce manual incident investigation and time to recovery. |
| Innovation | Evidence-based AI decisions instead of fixed restart rules; fixes the root cause, not the service showing the symptom. |
| Feasibility | Reuses existing Docker infrastructure; next steps are real deployments, Slack/PagerDuty, more actions. |
| Technical execution | A real injected failure and a verified recovery, live. |
| Demo | One clear live incident: inject → detect → Gemma reasons → recover → verify. Explain goal, purpose, limitations, next steps. |

## Decisions already made (don't revisit)
- Considered and dropped: FChain RCA engine on Kubernetes/kind (too heavy for the laptop, 4-node cluster, ~3–4 GB downloads); "Ghost Hunter" RCA explainer; Maritime as the main track (access not working).
- Chose EcoCycle (`codemanav/ecocycle-project-devOps`, 3 Spring Boot services + Postgres + nginx on docker-compose) because it runs light locally and is the user's own project.
- Emphasis is Gemma 4's diagnosis and remediation decisions, not hosting automation.
- Licensing is out of scope; don't bring it up.

## Locked scope
- **Project:** InfraPilot — autonomous AI incident response for EcoCycle, powered by Gemma 4 (via Gemini API).
- **Track:** Best Use of Gemma 4 (primary). Best Open-Source AI is an optional add-on (see "Optional scope" below). Maritime optional, only if it becomes available and doesn't distract.
- **Do not:** use the FChain / microservice-blackbox-rca engine, Kubernetes/kind, or bring up licensing.
- **Goal:** one reliable, genuinely AI-driven end-to-end live demo. No extra infrastructure or features.

## Agent loop (MVP)
1. **Detect** — poll health of EcoCycle services.
2. **Investigate** — collect Docker logs (WARN/ERROR/exceptions only — `show-sql: true` floods logs), container state, exit codes, OOMKilled flag, restart count, health-check failures.
3. **Reason** — Gemma 4 returns structured JSON: `root_cause`, `evidence` (quoted log lines), `action`, `params`, `confidence`.
4. **Recover** — validate against a safe allowlist, then execute automatically. Invalid/unclear → `escalate`.
5. **Verify** — re-run health checks + one real request (create an offer). If not recovered, re-investigate once and give Gemma a second attempt with what it already tried.

Show every step + timings in a Streamlit UI, with an audit log. Optional: send Gemma a small matplotlib chart (CPU / memory / latency per container, last ~2 min) for multimodal input.

## Optional scope: also compete for Best Open-Source AI
Only after the Gemma demo (scenario A at least) works end to end and a backup video is recorded. Check whether the submission form allows more than one track; if it allows only one, stay on Gemma 4. These additions don't change the Gemma story — they make the same build qualify on all three paths the Open-Source track names (open-weight model, agent skill, model harness).

| Priority | Addition | What it means | Est. time |
|---|---|---|---|
| 1 | **Local open-weight backend** | Model client behind one interface with two backends: Gemini API (default) and Gemma 4 running locally via Ollama (`brew install ollama`, pull a small Gemma 4 variant). Switch with one env var, e.g. `INFRAPILOT_MODEL_BACKEND=gemini|ollama`. Pitch: incident logs never leave your infrastructure. EcoCycle uses only ~1.2 GB RAM, so a small model fits alongside it. Start the model download early (hackathon Wi-Fi). | 15–30 min |
| 2 | **Agent skill** | `SKILL.md` + a CLI (e.g. `infrapilot diagnose --target ecocycle`, `infrapilot recover --dry-run`) so coding agents can call InfraPilot as a tool. | ~15 min |
| 3 | **Reusable harness** | Keep the Detect → Investigate → Reason → Recover → Verify loop as a clean Python module. Target system defined in a config file (containers, health URLs, smoke request, call graph) and the allowlist defined as pluggable actions, so it works on any docker-compose app, not just EcoCycle. | ~20 min (mostly structure) |
| 4 | **Public repo polish** | Public GitHub repo, README with architecture diagram, setup steps, how to add a new action or target, a `CONTRIBUTING.md`, and a few `good-first-issue` issues (fits Hacktoberfest). | ~15 min |
| 5 | **Local vs API comparison** | Run scenarios A/B/C on both backends; show a small table of correct action chosen + latency. Proves the open-weight model is genuinely usable. | ~15 min |

Demo line for this track: "The same agent runs fully on your machine with open-weight Gemma 4 — your incident data never leaves your network."

## Allowlist
| Action | Params | Guard |
|---|---|---|
| `start_container` | name | EcoCycle containers only |
| `restart_container` | name | EcoCycle containers only |
| `raise_memory_limit` | name, mb | ≤ 1024 MB |
| `escalate` | reason | always allowed |

## Failure scenarios (agent must choose different actions)
| # | Inject | Naive restart script | Evidence | Correct action |
|---|---|---|---|---|
| A | `docker stop users-db` | restarts users-service (health DOWN because Spring health includes DB) — wrong | users-service logs: Postgres connection refused; users-db state `exited` | `start_container(users-db)` |
| B | low memory limit on marketplace-service | restart → OOM again → loop | OOMKilled true, rising restart count | `raise_memory_limit(marketplace-service, 512)` |
| C | marketplace-service hung (`docker pause` or frozen process) | restart — correct here | health timeout, flat CPU, no errors | `restart_container(marketplace-service)` |

Demo A first. C proves Gemma restarts only when restart is right.

## EcoCycle facts (verified running locally)
- Start: `DB_PASSWORD=ecocycle docker compose up -d` in this directory. Images already built (~1.2 GB RAM total).
- Containers: `marketplace-service` :8081, `transactions-service` :8082, `users-service` :8083, `ecocycle-frontend` :80, `marketplace-db`, `transactions-db`, `users-db` (postgres:16).
- Health: `GET /actuator/health` on each service.
- No real auth: any `Authorization: Bearer x` works. `buyerId` comes back null on new offers.
- Endpoints: `POST/GET /users`, `PUT /users/{id}/greenscore?delta=`, `POST/GET /listings`, `GET /listings/{id}`, `POST /transactions/offer` `{listingId, offerAmount}`, `POST /transactions/donate`, `GET/PUT /transactions/{id}` `{status}`.
- Seeded listings: 1 SALE, 2 RENTAL, 3 DONATION.
- Call graph:
  - transactions → marketplace (`GET /listings/{id}`) on offer/donate
  - transactions → users (`PUT /users/{id}/greenscore`) when status set to `COMPLETED` — **no timeout** (WebClient `.block()`), so a hung users path hangs transactions
  - each service → its own Postgres

## Environment
- macOS arm64, 16 GB RAM; Docker Desktop allotted ~7.75 GB / 8 CPUs.
- Python 3.13, Node 20. Needs `GEMINI_API_KEY` exported (never paste into chat). Confirm exact Gemma 4 model ID and free-tier rate limits with a first test call.
- Put InfraPilot code in `infrapilot/` inside this directory.

## Next steps
1. Scaffold `infrapilot/`: monitor, evidence collector, Gemma client (JSON output), allowlist validator, executor, verifier, Streamlit UI with "Haunt it" buttons for A/B/C.
2. Get scenario A working end to end; then B and C.
3. Record a backup demo video as soon as it works once.
4. Submission write-up: note EcoCycle existed before the event; InfraPilot built today. Cover goal, purpose, limitations (local only, fixed allowlist, injected faults), next steps.

## Security note
`chrono-rca-lab/microservice-blackbox-rca` has a committed `credentials.txt` that appears to contain a token — revoke it.
