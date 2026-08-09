import re
from agents import Agent, Runner
from pydantic import BaseModel
from planner_agent import groq_model, PlannedFile  # reuse the same model + PlannedFile

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


def extract_file_spec(plan_markdown: str, filename: str) -> str:
    """Pull the '### `filename` — [domain]' subsection out of the planner's markdown,
    so the specialist only sees the purpose/must-include for its one file."""
    pattern = rf"### `{re.escape(filename)}`.*?(?=\n### |\n## |\Z)"
    match = re.search(pattern, plan_markdown, re.DOTALL)
    if not match:
        raise ValueError(f"No spec section found for {filename}")
    return match.group(0).strip()


def extract_code_block(raw_text: str) -> str:
    """Strip the ```lang ... ``` fence the specialist was told to use."""
    match = re.search(r"```[a-zA-Z0-9_+-]*\n(.*?)```", raw_text, re.DOTALL)
    if not match:
        # model didn't fence it — fall back to using the raw text as-is
        return raw_text.strip()
    return match.group(1).strip()


def generate_file(file: PlannedFile, plan_markdown: str) -> GeneratedFile:
    specialist = SPECIALISTS.get(file.domain)
    if specialist is None:
        raise ValueError(f"No specialist registered for domain '{file.domain}'")

    spec = extract_file_spec(plan_markdown, file.filename)
    prompt = f"File to generate: `{file.filename}`\n\n{spec}"

    result = Runner.run_sync(specialist, prompt)
    code = extract_code_block(result.final_output)

    return GeneratedFile(filename=file.filename, domain=file.domain, code=code)