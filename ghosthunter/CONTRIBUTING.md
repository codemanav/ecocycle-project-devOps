# Contributing to Ghost Hunter 🎃

Thanks for helping hunt ghosts! Small, focused pull requests are easiest to review.

## Setup

```bash
cd ghosthunter
python3 -m venv .venv && .venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q tests          # unit tests: no Docker or API key needed
```

For end-to-end work you also need Docker, the EcoCycle demo app (`DB_PASSWORD=ecocycle docker compose up -d`
from the repo root), and either a `GEMINI_API_KEY` in `ghosthunter/.env` or Ollama with `gemma4:e4b`.

## Common contributions

**A new action.** Add a function with `@action(...)` in [`actions.py`](actions.py). Give it a precise
`when` description (the model reads it), typed params, and a `guard` if it needs limits. Add tests in
`tests/test_actions.py` for both accepted and rejected params. Enable it in a target YAML.

**A new target.** Copy [`targets/_template.yaml`](targets/_template.yaml). Include at least one
scenario and a `reset` so others can reproduce your demo.

**A new failure scenario.** Add it to a target's `scenarios:` with a `story` explaining what a naive
restart script would do. Run it against both backends and add the result to [BENCHMARKS.md](BENCHMARKS.md).

**A new model backend.** Add a `_call_<backend>()` in [`model.py`](model.py) that streams thoughts
through `on_thought` and returns the raw answer, then route to it from `_ask()` and `write_postmortem()`.

## Ground rules

- The model only proposes. Every action must go through `actions.validate()`; never execute model
  output directly.
- Don't commit secrets: `.env`, `audit.jsonl` and `postmortems/` are git-ignored.
- Keep prompts in sync with the registry: describe actions in `@action(when=...)`, not in prompt text.
- Run `pytest` before opening a PR, and say in the PR how you tested end to end (backend, scenario, result).
