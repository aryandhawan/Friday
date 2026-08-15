# Friday

A terminal-native, multi-agent AI coding assistant that plans, builds, and iterates on AI/ML software projects — with every generated file written and validated inside an isolated Docker sandbox before it ever touches the host machine.

Built as a hands-on exploration of genuine LLM-driven orchestration: the control flow isn't hardcoded — a Coordinator agent decides, at runtime, which specialist to invoke for each file, in what order, and when to validate.

---

## What it does

1. **Plans** — a Planner agent takes a plain-language project description and produces a structured build plan (as markdown), breaking the project into files, tagging each with the domain it belongs to (backend, data science, computer vision, MLOps, web, database), and stating its assumptions explicitly rather than guessing silently
2. **Extracts** — a lightweight structuring step pulls a clean, machine-readable file list out of the plan, so the build loop has something reliable to iterate over
3. **Coordinates** — a Coordinator agent reasons through the plan file-by-file, dispatching each one to the correct domain specialist based on genuine runtime judgment, not a fixed script
4. **Builds, safely** — each specialist generates code for its assigned file; the Coordinator writes it into a Docker container with a bind-mounted workspace, and validates it (compilation checks, executed inside the sandbox) before considering it done
5. **Edits** — a separate Editor agent handles iterative changes: reference an existing file, describe the change, and it reads, understands, and updates the code directly — no full rebuild required
6. **Wakes on command** — a terminal-native CLI with a wake-word activation pattern ("friday") and `@filename` referencing for targeted edits

---

## Why this architecture

### Genuine LLM orchestration, not a scripted pipeline
The Coordinator is itself an LLM — it decides which tool to call and when, based on reasoning over the plan and its own prior actions, not a predetermined sequence written in Python. This is deliberately different from a fixed pipeline: the tradeoff is real (multi-turn agentic loops need session persistence, turn limits, and resilient retry handling that a scripted pipeline never would), taken on purpose to build genuine multi-agent orchestration skill, not just LLM-in-the-loop scripting.

### Specialists as tools, not six copies of the same prompt
Each domain (backend, data science, computer vision, MLOps, web, database) is its own narrowly-scoped agent, wrapped as a callable tool the Coordinator can invoke. This keeps each specialist's system prompt focused on what it actually needs to reason well about, rather than one agent trying to be simultaneously good at API design, model architectures, and database schemas.

### Sandboxing as a hard boundary, not a convention
Generated code runs inside a custom Docker container built around an unprivileged user, with the project workspace exposed via a bind mount — the only directory the container can write to. This isn't "the agent promises to behave" — it's an actual filesystem and process boundary, so a runaway or malicious generation can't reach anything outside the sandboxed scope, regardless of what the LLM decides to do.

### Resilience earned through real multi-provider debugging
Free-tier LLM infrastructure has real, different failure modes depending on the provider — hard token-per-minute ceilings, per-minute request caps, and even zero-quota account states, each requiring a different fix. Friday's retry logic is built around specifically diagnosing and handling each of these, with session-backed state so a retry resumes rather than blindly re-running (and re-billing) completed work.

---

## Tech stack

| Layer | Technology |
|---|---|
| Agent orchestration | OpenAI Agents SDK |
| LLM providers | Groq, Google Gemini (via LiteLLM/OpenAI-compatible endpoints) |
| Sandboxed execution | Docker (custom hardened image, bind-mounted workspace) |
| Session persistence | SQLite-backed agent sessions |
| Structured output | Pydantic |

---

## Project structure

```
friday/
├── planner_agent.py    # Planner: project description -> structured markdown plan
├── coder_agent.py       # Coordinator + 6 domain specialists + Editor agent
├── sandbox.py           # Docker container lifecycle: build, run, exec commands
├── main.py              # Terminal CLI: wake-word loop, @filename edit routing
├── dockerfile            # Hardened sandbox image (non-root user, scoped tooling)
├── workspace/            # Bind-mounted output directory — all generated code lives here
├── requirements.txt
└── .env                  # API keys (gitignored)
```

---

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create `.env`:
```
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
```

**Requires Docker Desktop running** — the sandbox is built and managed automatically on first run, but the Docker daemon must be active.



## Known limitations

- Single, fixed sandbox workspace per instance — not yet designed for managing multiple concurrent projects
- Validation is currently compile-level (syntax correctness), not full test execution — a deliberate, staged scope decision, not an oversight
- Network access is enabled inside the sandbox (needed for dataset ingestion in generated code); resource limits (memory, process count) are a known area for further hardening
- No dedicated mechanism yet for pointing generated code at a local dataset path — currently relies on library-provided or remotely-fetched data
- Terminal-only interface — no graphical or web-based UI

---

## Author

Built by **Aryan Dhawan**, with Rudra Bhavsar and Yug Shah — AI/ML engineering, multi-agent systems, and applied sandboxing.