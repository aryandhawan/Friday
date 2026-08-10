import asyncio
import re
from pathlib import Path

from agents import Runner

from planner_agent import planning_agent, extract_file_list
from coder_agent import build_project, sandbox_agent
from editor_agent import editor_agent

BASE_DIR = Path(__file__).resolve().parent
WAKE_WORD = "friday"
AT_FILE_PATTERN = re.compile(r"@([\w./\\-]+)")


def contains_wake_word(text: str) -> bool:
    return WAKE_WORD in text.lower()


async def handle_edit(user_input: str, filename: str) -> None:
    path = BASE_DIR / filename
    if not path.exists():
        print(f"✗ Can't find '{filename}' in the workspace — nothing to edit.")
        return

    print(f"→ Reading {filename}...")
    current_code = path.read_text(encoding="utf-8")

    print(f"→ Asking the Editor agent to update {filename}...")
    prompt = f"""Current contents of {filename}:

{current_code}

Requested change: {user_input}

Rewrite the complete file with this change applied."""
    result = await Runner.run(editor_agent, prompt)
    updated_code = result.final_output

    path.write_text(updated_code, encoding="utf-8")
    print(f"✓ {filename} updated.")


async def handle_new_project(user_input: str) -> None:
    print("→ Planning the project...")
    plan_result = await Runner.run(planning_agent, user_input)
    plan_markdown = plan_result.final_output

    print("→ Extracting the file list from the plan...")
    try:
        file_list = extract_file_list(plan_markdown)
    except ValueError as e:
        print(f"✗ Couldn't make sense of the plan: {e}")
        return
    print(f"→ Plan ready — {len(file_list)} file(s) to build.")

    print("→ Building the project (this can take a while)...")
    result = await build_project(coordinator=sandbox_agent, plan_input=plan_markdown)

    print("✓ Build complete.")
    print(result.final_output)


async def process_command(user_input: str) -> None:
    match = AT_FILE_PATTERN.search(user_input)
    if match:
        await handle_edit(user_input, match.group(1))
    else:
        await handle_new_project(user_input)


def main() -> None:
    print("Friday is listening. Start your message with 'Friday' to give a command.")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye.")
            break

        if not contains_wake_word(user_input):
            print('(Say "Friday" to give me a command, e.g. "Friday, build a ...")')
            continue

        asyncio.run(process_command(user_input))
        print()


if __name__ == "__main__":
    main()
