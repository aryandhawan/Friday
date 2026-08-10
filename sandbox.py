"""Manages the Friday sandbox container (built from ./dockerfile).

The coordinator agent writes files to the project directory as usual;
that directory is bind-mounted into the container at /workspace, so
whatever gets written on the host is immediately visible inside the
sandbox. run() execs commands inside that same container.
"""
from __future__ import annotations

from pathlib import Path

import docker
from docker.errors import ImageNotFound, NotFound

def get_workspace_dir(workspace_path: str = None) -> Path:
    if workspace_path:
        return Path(workspace_path).resolve()
    return Path(__file__).resolve().parent / "workspace"


BASE_DIR = get_workspace_dir()
IMAGE_TAG = "friday-sandbox:latest"
CONTAINER_NAME = "friday-sandbox"

_client = docker.from_env()


def _ensure_image():
    try:
        _client.images.get(IMAGE_TAG)
        print(f"[sandbox] image {IMAGE_TAG} already built")
    except ImageNotFound:
        print(f"[sandbox] building image {IMAGE_TAG} from ./dockerfile (first run only)...")
        for chunk in _client.api.build(path=str(BASE_DIR), dockerfile="dockerfile", tag=IMAGE_TAG, decode=True):
            line = chunk.get("stream") or chunk.get("status") or ""
            if line.strip():
                print(f"[docker build] {line.strip()}")
            if "error" in chunk:
                raise RuntimeError(chunk["error"])
        print(f"[sandbox] image {IMAGE_TAG} built")


def _ensure_container():
    _ensure_image()
    try:
        container = _client.containers.get(CONTAINER_NAME)
        if container.status != "running":
            print(f"[sandbox] starting existing container {CONTAINER_NAME}")
            container.start()
        else:
            print(f"[sandbox] reusing running container {CONTAINER_NAME}")
        return container
    except NotFound:
        print(f"[sandbox] creating container {CONTAINER_NAME}")
        return _client.containers.run(
            IMAGE_TAG,
            name=CONTAINER_NAME,
            detach=True,
            tty=True,
            command="sleep infinity",
            volumes={str(BASE_DIR): {"bind": "/workspace", "mode": "rw"}},
            working_dir="/workspace",
        )


def run(command: str, timeout: int = 120) -> str:
    """Runs a shell command inside the sandbox container and returns combined output."""
    container = _ensure_container()
    exit_code, output = container.exec_run(
        ["bash", "-lc", command],
        workdir="/workspace",
        demux=False,
    )
    text = output.decode("utf-8", errors="replace") if output else ""
    return f"exit_code={exit_code}\n{text}"
