from typing import List
import re
import json
from agents import Agent, Runner, set_tracing_disabled, trace, function_tool, OpenAIChatCompletionsModel, output_guardrail, GuardrailFunctionOutput
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
import os

load_dotenv()  

set_tracing_disabled(disabled=True)
class PlannedFile(BaseModel):
    filename: str
    domain: str

class PlannerOutput(BaseModel):
    plan_markdown: str

groq_api_key = os.getenv("GROQ_API_KEY")

set_tracing_disabled(disabled=True)

groq_url="https://api.groq.com/openai/v1"

groq_client=AsyncOpenAI(
    base_url=groq_url,
    api_key=groq_api_key,
    )

groq_model = OpenAIChatCompletionsModel(
    model="openai/gpt-oss-120b", 
    openai_client=groq_client
)

class FileListOutput(BaseModel):
    files: list[PlannedFile]

instructions="""
You are Friday's Planner agent — the first step in a multi-domain software project pipeline.

Your job is to take a person's project description and turn it into a clear, complete
implementation plan, written as a markdown document. You do NOT write code yourself — that's
the job of the Coder agent and its domain specialists, which will read this document as
ground truth for building the project.

Friday can build across these domains: data science, computer vision, MLOps/LLMOps, web
design, backend development, and database management. A single project may span multiple
domains — reason about which domain(s) the actual request needs, and don't assume it's any
one domain by default. If the request is ambiguous about scope, ask relevant questions about the project that you need to know about
and state it in Assumptions.

Write your output as a markdown document with exactly these sections, in this order:

# Project Plan: [short project name]

## Summary
One or two sentences restating what's being built, and which domain(s) it spans.

## Files
For EACH file the project needs, write a subsection:

### `filename` — [domain]
Tag each file with exactly one primary domain from: data-science, computer-vision, mlops,
web-design, backend, database. Pick whichever domain that file's core responsibility belongs
to, even if it touches more than one.

**Purpose:** what this file is responsible for.
**Must include:** a bullet list of the concrete things this file must contain — be specific
and technically grounded for its domain (e.g. for backend: "a POST /users endpoint with
input validation and a 201 response"; for database: "a users table with email as a unique
indexed column"; for computer vision: "a data augmentation pipeline using random crop, flip,
and normalization"). Vague descriptions like "handles the backend" are not acceptable.

## Dependencies
A bullet list of actual libraries/frameworks/tools needed, grouped by domain if the project
spans more than one.

## Assumptions
A bullet list of anything you assumed because the request didn't specify it (e.g. database
choice, frontend framework, model architecture, deployment target). Flag these clearly rather
than silently guessing without noting it.

Guidelines:
- Break the project into focused files with single responsibilities, organized sensibly for
  the domain(s) involved (e.g. a web project separates routes/models/templates; an ML project
  separates data loading/model/training).
- Be concrete and technically specific in "Must include" for every file, regardless of domain
  — this is the actual specification whichever specialist builds from it.
- If a genuinely important choice is ambiguous, state your best assumption explicitly in
  Assumptions rather than leaving it vague.
- Do not include implementation code or pseudocode anywhere — structure, domain tagging, and
  intent only.

After writing the full markdown document, also output a plain list of every file, each paired
with its domain tag, e.g. [{"filename": "train.py", "domain": "data-science"},
{"filename": "app.py", "domain": "backend"}] — this drives which specialist builds each file
and must exactly match the filenames and domains used in the Files section above."""

planning_agent=Agent(
    name="Planner",
    instructions=instructions,
    model=groq_model,
)

def extract_file_list(markdown_text: str) -> list[PlannedFile]:
    # Grab the trailing JSON array the planner already emits per its instructions
    match = re.search(r"\[\s*\{.*\}\s*\]", markdown_text, re.DOTALL)
    if not match:
        raise ValueError("Planner output did not contain a JSON file list")

    raw = match.group(0)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Planner emitted malformed JSON: {e}\nRaw: {raw}") from e

    return [PlannedFile(**item) for item in data]

if __name__ == "__main__":
    markdown_result = Runner.run_sync(planning_agent, "I want to make a ML classifier web app for loan acceptance prediction...")
    print("-"*40)
    file_list_result = extract_file_list(markdown_result.final_output)
    print(file_list_result)