"""
Run this once from your project root to scaffold Friday.
Usage: python setup_structure.py
"""

import os

STARTER_CONTENT = {
    ".gitignore": (
        "venv/\n"
        "__pycache__/\n"
        "*.pyc\n"
        ".env\n"
        "workspace/\n"          # generated project files — not source-controlled
    ),
    ".env": "# API keys go here — never commit this file\nGROQ_API_KEY=\n",
    "README.md": "# Friday\n\nA multi-agent AI/ML coding assistant. Planner breaks down the project, "
                 "Coder generates and self-validates files, all scoped to a dedicated workspace directory.\n",
    "requirements.txt": (
        "openai-agents\n"
        "python-dotenv\n"
        "pydantic\n"
    ),
}

FILES = [
    "main.py",             # entry point — terminal loop, takes user's project description
    "planner_agent.py",     # Planner agent definition + system prompt
    "coder_agent.py",       # Coder agent + the validate_code tool it calls on itself
    "requirements.txt",
    ".env",
    ".gitignore",
    "README.md",
]

DIRS = [
    "workspace",   # the sandboxed directory Friday actually reads/writes to — nothing outside this
]


def create_file(path: str):
    if os.path.exists(path):
        print(f"  skip (exists): {path}")
        return
    content = STARTER_CONTENT.get(path, "")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  created: {path}")


def create_dir(path: str):
    if os.path.exists(path):
        print(f"  skip (exists): {path}/")
        return
    os.makedirs(path)
    # drop a .gitkeep so the empty folder still shows up if you ever want to track its existence
    with open(os.path.join(path, ".gitkeep"), "w") as f:
        pass
    print(f"  created: {path}/")


def main():
    print("Scaffolding Friday...\n")
    for dname in DIRS:
        create_dir(dname)
    for fname in FILES:
        create_file(fname)
    print("\nDone.")


if __name__ == "__main__":
    main()