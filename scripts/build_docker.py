import os
from pathlib import Path
import subprocess

import re
from pathlib import Path


def append_env_to_dockerfile(
    env_path: str = ".env", dockerfile_path: str = "Dockerfile"
) -> None:
    print("append_env_to_dockerfile...")
    env_file = Path(env_path)
    docker_file = Path(dockerfile_path)

    if not env_file.exists():
        raise FileNotFoundError(f"EFile '{env_path}' was not found.")
    if not docker_file.exists():
        raise FileNotFoundError(f"DFile '{dockerfile_path}' was not found.")

    # 1. Read .env file into key-value pairs
    env_vars_dict = {}
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                env_vars_dict[key.strip()] = val.strip()

    if not env_vars_dict:
        print("No env vars in .env found...")
        return

    # 2. Read existing Dockerfile content
    dockerfile_content = docker_file.read_text(encoding="utf-8")

    # Pattern matching multi-line or single-line ENV statements in Dockerfile
    env_pattern = re.compile(
        r"(?:# Auto-generated ENV from \.env\n)?ENV\s+([\s\S]*?)(?=\n\n|\n[A-Z]+|\Z)",
        re.MULTILINE,
    )

    match = env_pattern.search(dockerfile_content)

    formatted_vars = [f"    {k}={v}" for k, v in env_vars_dict.items()]
    new_env_block = (
        "# Auto-generated ENV from .env\nENV " + " \\\n".join(formatted_vars)
    )

    if match:
        # Existing ENV block found: Replace it at the exact same position
        updated_content = (
            dockerfile_content[: match.start()]
            + new_env_block
            + dockerfile_content[match.end() :]
        )
        print(
            f"Updated existing ENV block in '{dockerfile_path}' with {len(env_vars_dict)} variables."
        )
    else:
        # No ENV block found: Append to the end of the Dockerfile
        updated_content = (
            dockerfile_content.rstrip() + "\n\n" + new_env_block + "\n"
        )
        print(
            f"Appended new ENV block to '{dockerfile_path}' with {len(env_vars_dict)} variables."
        )

    print("append_env_to_dockerfile... done")
    docker_file.write_text(updated_content, encoding="utf-8")


def ensure_docker_image(
    image_name: str, 
    build_dir: str | Path,
    env_path,
    dockerfile_path
    ) -> bool:
    """
    Ensure that a Docker image exists locally.
    If not, build it from the given directory.

    Returns:
        True  -> image exists or was built successfully
        False -> build failed
    """
    print("cehck doecker exists ...")
    # SET DIR DOCKER IS BUILD INTO
    build_dir = Path(build_dir).resolve()
    print("build_dir", build_dir)
    # 1) Check if image exists locally
    try:
        result = subprocess.run(
            ["docker", "image", "inspect", image_name],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            print(f"[docker] Image already exists: {image_name}")
            return True
    except Exception as exc:
        print(f"[docker] Failed to check image: {exc}")

    try:
        # 2) Image missing → build it
        dockerfile = os.path.join(build_dir)
        if not Path(dockerfile).exists():
            print(f"[docker] No Dockerfile found in: {build_dir}")
            return False
        else:
            print("Dockerfile found. start building..")
    except Exception as e:
        print("Err get dockerfiel path", e)

    print(f"[docker] Building image '{image_name}' from {dockerfile}")
    try:
        # APPEND ENV VARS TO DOCKERFILE
        append_env_to_dockerfile(
            env_path,
            dockerfile_path
        )

        subprocess.run(
            ["docker", "build", "-t", image_name, Path(dockerfile)],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"[docker] Build successful: {image_name}")
        return True

    except subprocess.CalledProcessError as exc:
        print(f"[docker] Build failed: {exc}")
        return False