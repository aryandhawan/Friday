"""
pipeline.py

The actual Friday backend logic (planner -> coder/sandbox, or editor for @file
edits), extracted from the old CLI main.py. print() calls are replaced with an
injectable `log` callback so any frontend (CLI, this UI, anything else) can
capture progress the same way. Every path — success or failure — always ends
with an explicit log() call, so the UI never sits at "Building..." with no
resolution.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, Optional

from agents import Runner

from planner_agent import planning_agent, extract_file_list
from coder_agent import build_project, sandbox_agent
from editor_agent import editor_agent

BASE_DIR = Path(__file__).resolve().parent
AT_FILE_PATTERN = re.compile(r"@([\w./\\-]+)")

LogFn = Callable[[str], None]


async def handle_edit(user_input: str, filename: str, log: LogFn) -> list[str]:
    path = BASE_DIR / filename
    if not path.exists():
        log(f"✗ Can't find '{filename}' in the workspace — nothing to edit.")
        return [f"Can't find '{filename}' — nothing to edit."]

    log(f"→ Reading {filename}...")
    current_code = path.read_text(encoding="utf-8")

    log(f"→ Asking the Editor agent to update {filename}...")
    prompt = f"""Current contents of {filename}:

{current_code}

Requested change: {user_input}

Rewrite the complete file with this change applied."""
    result = await Runner.run(editor_agent, prompt)
    updated_code = result.final_output

    path.write_text(updated_code, encoding="utf-8")
    log(f"✓ {filename} updated.")
    log("✓ Project complete.")
    return [f"{filename} updated successfully."]


async def handle_new_project(user_input: str, log: LogFn) -> list[str]:
    log("→ Planning the project...")
    plan_result = await Runner.run(planning_agent, user_input)
    plan_markdown = plan_result.final_output

    log("→ Extracting the file list from the plan...")
    try:
        file_list = extract_file_list(plan_markdown)
    except ValueError as e:
        log(f"✗ Couldn't make sense of the plan: {e}")
        return [f"Couldn't make sense of the plan: {e}"]
    log(f"→ Plan ready — {len(file_list)} file(s) to build.")

    log("→ Building the project (this can take a while)...")
    try:
        result = await build_project(coordinator=sandbox_agent, plan_input=plan_markdown)
    except Exception as e:
        # Whatever went wrong (Docker, model, max turns, ...), always tell the
        # UI something concrete instead of leaving it hanging on "Building...".
        log(f"✗ Build failed: {e}")
        return [f"Build failed: {e}"]

    log("✓ Build complete.")
    log("✓ Project complete.")
    summary = str(result.final_output).splitlines()
    return [line for line in summary if line.strip()] or ["Build complete."]


async def process_command(user_input: str, log: Optional[LogFn] = None) -> list[str]:
    log = log or (lambda _msg: None)
    match = AT_FILE_PATTERN.search(user_input)
    if match:
        return await handle_edit(user_input, match.group(1), log)
    return await handle_new_project(user_input, log)
