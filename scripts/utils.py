import os
from pathlib import Path
import shlex
import shutil
import subprocess


def _docker_prefix() -> list[str]:
    configured = os.getenv("STEMCNV_DOCKER_COMMAND", "").strip()
    if configured:
        return shlex.split(configured, posix=os.name != "nt")
    if shutil.which("docker"):
        return ["docker"]
    if os.name == "nt" and shutil.which("wsl.exe"):
        return ["wsl.exe", "-d", os.getenv("STEMCNV_WSL_DISTRO", "Ubuntu"), "-u", "root", "--", "docker"]

def stop_container(container_id_or_name: str) -> bool:
    """
    Stop a running Docker container by ID or name.
    Returns True if successful, False otherwise.
    """

    try:
        # Try stopping the container
        result = subprocess.run(
            ["docker", "stop", container_id_or_name],
            capture_output=True,
            text=True,
            check=True
        )

        print(f"[docker] Container stopped: {container_id_or_name}")
        return True

    except subprocess.CalledProcessError as exc:
        print(f"[docker] Failed to stop container '{container_id_or_name}':")
        print(exc.stderr.strip())
        return False

    except Exception as exc:
        print(f"[docker] Unexpected error: {exc}")
        return False

def _docker_host_path(path: Path) -> str:
    resolved = str(path.resolve())
    if _docker_prefix()[0].lower() != "wsl.exe":
        return resolved
    converted = subprocess.run(
        ["wsl.exe", "-d", os.getenv("STEMCNV_WSL_DISTRO", "Ubuntu"), "--", "wslpath", "-a", resolved],
        capture_output=True, text=True, check=True, timeout=30)
    return converted.stdout.strip()

def _run_docker(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    try:
        return subprocess.run([*_docker_prefix(), *args], capture_output=True, text=True,
                              timeout=int(os.getenv("STEMCNV_DOCKER_TIMEOUT", "300")), check=check)
    except Exception as exc:
        detail = getattr(exc, "stderr", None) or str(exc)
        print("Err ru dcoker cmd:", detail)
