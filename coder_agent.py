import re
from agents import Agent, Runner,function_tool
from pydantic import BaseModel
from planner_agent import groq_model, PlannedFile  # reuse the same model + PlannedFile
from pathlib import Path
import asyncio
import sandbox
from agents import SQLiteSession
from openai import APIError,RateLimitError
import time 
# --- Holds a finished file, not an LLM output_type ---
class GeneratedFile(BaseModel):
    filename: str
    domain: str
    code: str


backend_specialist = Agent(
    name="Backend Specialist",
    instructions="""You are a backend development specialist. You write clean, correct, production-quality backend code — API routes, request handling, business logic — for a single file at a time.  You will be given a file's purpose and a list of what it must include. Write ONLY the code for that one file. Do not write explanations, comments about what you're doing, or anything outside the actual code itself unless it's a genuine code comment.  Follow standard conventions for whatever framework is implied by the project (e.g. Flask, FastAPI) — use clear naming, proper error handling, and idiomatic structure.""",
    model=groq_model,
)

database_specialist = Agent(
    name="Database Specialist",
    instructions="""You are a database specialist. You write clean, correct, production-quality database code — schema definitions, ORM models, migrations, or raw SQL — for a single file at a time. You will be given a file's purpose and a list of what it must include. Write ONLY the code for that one file. Do not write explanations, comments about what you're doing, or anything outside the actual code itself unless it's a genuine code comment. Follow standard conventions for whatever stack is implied by the project (e.g. SQLAlchemy, Django ORM, raw SQL) — use explicit primary/foreign keys, proper indexing and constraints, and idiomatic structure.""",
    model=groq_model,
)

web_specialist = Agent(
    name="Web Design Specialist",
     instructions="""You are a web design specialist. You write clean, correct, production-quality frontend code — HTML, CSS, templates, Javascript, typescript or UI components — for a single file at a time. You will be given a file's purpose and a list of what it must include. Write ONLY the code for that one file. Do not write explanations, comments about what you're doing, or anything outside the actual code itself unless it's a genuine code comment. Follow standard conventions for whatever framework is implied by the project (e.g. plain HTML/CSS, Jinja2, React) — use clear naming, responsive/accessible markup, and idiomatic structure.""",
    model=groq_model,
)

data_science_specialist = Agent(
    name="Data Science Specialist",
    instructions="""You are a data science specialist. You write clean, correct, production-quality data science code — data loading, cleaning, feature engineering, model training/evaluation, or visualizations — for a single file at a time. You will be given a file's purpose and a list of what it must include. Write ONLY the code for that one file. Do not write explanations, comments about what you're doing, or anything outside the actual code itself unless it's a genuine code comment. Follow standard conventions for whatever stack is implied by the project (e.g. pandas, scikit-learn, matplotlib) — use clear naming, proper error handling, and idiomatic structure.""",
    model=groq_model,
)

computer_vision_specialist = Agent(
    name="Computer Vision Specialist",
    instructions="""You are a computer vision specialist. You write clean, correct, production-quality CV code — image loading, preprocessing, augmentation pipelines, model architectures, or inference logic — for a single file at a time. You will be given a file's purpose and a list of what it must include. Write ONLY the code for that one file. Do not write explanations, comments about what you're doing, or anything outside the actual code itself unless it's a genuine code comment. Follow standard conventions for whatever stack is implied by the project (e.g. OpenCV, PyTorch, torchvision) — use clear naming, proper error handling, and idiomatic structure.""",
    model=groq_model,
)

mlops_specialist = Agent(
    name="MLOps Specialist",
    instructions="""You are an MLOps specialist. You write clean, correct, production-quality MLOps/LLMOps code — model serving, deployment configs, pipelines, monitoring, or CI/CD for ML systems — for a single file at a time. You will be given a file's purpose and a list of what it must include. Write ONLY the code for that one file. Do not write explanations, comments about what you're doing, or anything outside the actual code itself unless it's a genuine code comment. Follow standard conventions for whatever stack is implied by the project (e.g. Docker, MLflow, FastAPI serving) — use clear naming, proper error handling, and idiomatic structure.You are Skilled at cloud deployment( eg Azure, Aws, GCP), containerization, and orchestration tools.""",
    model=groq_model,
)

# domain -> specialist agent (fill in the rest as you build them)
SPECIALISTS = {
    "backend": backend_specialist,
    "database": database_specialist,
    "web-design": web_specialist,
    "data-science": data_science_specialist,
    "computer-vision": computer_vision_specialist,
    "mlops": mlops_specialist,
}

session = SQLiteSession("friday-build-session")

@function_tool
def extract_file_spec(plan_markdown: str, filename: str) -> str:
    """Pulls the spec section for one specific file out of the full project plan."""
    pattern = rf"### `{re.escape(filename)}`.*?(?=\n### |\n## |\Z)"
    match = re.search(pattern, plan_markdown, re.DOTALL)
    if not match:
        raise ValueError(f"No spec section found for {filename}")
    return match.group(0).strip()

BASE_DIR = Path(__file__).resolve().parent


@function_tool
def write_file(filename: str, code: str) -> str:
    """Writes code to a file inside the sandbox. BOTH filename and code are required —
    filename is the exact file path (e.g. 'train.py'), code is the complete file contents."""
    path = BASE_DIR / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(code, encoding="utf-8")
    return f"Wrote {filename}"


@function_tool
def run_in_sandbox(command: str) -> str:
    """Runs a shell command inside the Docker sandbox (built from ./dockerfile) and
    returns its exit code and combined output. The project directory is mounted at
    /workspace inside the sandbox, so any files already written are visible there."""
    return sandbox.run(command)


sandbox_agent = Agent(
    name="sandbox",
    tools=[
        specialist.as_tool(
            tool_name=f"write_{domain.replace('-', '_')}_file",
            tool_description=f"Generates code for a {domain} file, given its spec"
        )
        for domain, specialist in SPECIALISTS.items()
    ] + [extract_file_spec, write_file, run_in_sandbox],
    instructions="""You are Friday's build Coordinator, running with a Docker sandbox at
your disposal. You are given a full project plan in markdown, listing every file to build
with its domain and requirements.

For EACH file listed in the plan:
1. Call extract_file_spec to get that file's specific spec section from the plan.
2. Call the specialist tool matching that file's domain, passing it the spec, to generate
   the code.
3. Write the generated code to a real file in the project directory using write_file.

Once all files are written, use run_in_sandbox to sanity-check the project inside the
sandbox container — e.g. install dependencies and run the entrypoint or a quick syntax
check (`python3 -m py_compile <file>` for each Python file, or run the main script) —
and report any failures.

Do not just describe or print the generated code in your final response — the actual files
must be written to disk. Your final response should be a short confirmation listing which
files were written and the result of the sandbox check, nothing more.""",
    model=groq_model,
)

async def build_project(coordinator: Agent, plan_input: str, max_retries: int = 3):
    from agents.items import ToolCallItem, ToolCallOutputItem
    from agents.stream_events import RunItemStreamEvent

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            print(f"[run] starting agent run (attempt {attempt}/{max_retries})")
            # session already holds every tool call/output from prior attempts, so on
            # retry we nudge it to continue rather than re-sending the full plan, which
            # would otherwise look like a brand-new request and risk redoing finished files.
            current_input = plan_input if attempt == 1 else (
                "Continue exactly where you left off. Do not regenerate or rewrite any "
                "file you already wrote successfully in this session — check what's been "
                "written so far and pick up with the next unfinished step."
            )
            stream = Runner.run_streamed(coordinator, current_input, max_turns=30, session=session)
            async for event in stream.stream_events():
                if not isinstance(event, RunItemStreamEvent):
                    continue
                item = event.item
                if isinstance(item, ToolCallItem):
                    raw = item.raw_item
                    name = getattr(raw, "name", None)
                    args = getattr(raw, "arguments", None)
                    print(f"\n--- tool call: {name} ---\n{args}")
                elif isinstance(item, ToolCallOutputItem):
                    print(f"--- tool output ---\n{item.output}")
            return stream
        except RateLimitError as e:
            last_error = e
            wait_time = 25
            print(f"[retry] Rate limit hit, waiting {wait_time}s before retrying...")
            time.sleep(wait_time)
            continue
        except APIError as e:
            message = str(e)
            if "tool_use_failed" not in message and "Failed to parse tool call arguments" not in message and "did not match schema" not in message:
                raise
            last_error = e
            print(f"[retry] tool call parsing failed on attempt {attempt}/{max_retries}, retrying...")
    raise last_error
 
 
if __name__ == "__main__":

    plan_markdown = """
# Project Plan: Simple Iris Classifier

## Summary
A small script that trains a logistic regression model on the Iris dataset and prints
its accuracy. Spans the data-science domain only.

## Files

### `data_loader.py` — data-science
**Purpose:** Loads and splits the Iris dataset.
**Must include:**
- A function `load_data()` that loads the sklearn Iris dataset
- Splits it into train/test sets (80/20) using train_test_split
- Returns X_train, X_test, y_train, y_test

### `train.py` — data-science
**Purpose:** Trains a logistic regression model and reports accuracy.
**Must include:**
- Imports load_data from data_loader
- Trains a scikit-learn LogisticRegression model on the training data
- Evaluates accuracy on the test set
- Prints the accuracy to the console

### `mlops.py` — mlops
**Purpose:** Contains MLOps-related functionality for managing the machine learning lifecycle.
**Must include:**
- A function `log_metrics()` that logs training metrics to a tracking service
- A function `save_model()` that saves the trained model to disk
- A function `load_model()` that loads a saved model from disk
- A function `deploy_model()` that deploys the model to a serving environment

### `server.py` — backend
**Purpose:** Serves the trained model via a REST API.
**Must include:**
- A FastAPI app that exposes an endpoint `/predict` which accepts input features and returns the model's prediction
- A function `load_model()` that loads the trained model at startup
- An endpoint `/health` that returns a simple health check response
- An endpoint `/metrics` that returns model performance metrics

## Dependencies
- scikit-learn
- numpy
- fastapi
- uvicorn
- pydantic
- mlflow
- joblib
- pytest

## Assumptions
- Using the built-in sklearn Iris dataset rather than an external file, since none was specified.
- Using LogisticRegression as a simple, standard baseline classifier.
"""

    print("Building project...")
    
    output = asyncio.run(build_project(coordinator=sandbox_agent, plan_input=plan_markdown))
    print("\n=== final summary ===")
    print(output.final_output)