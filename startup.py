from __future__ import annotations
# py libs incldue
# der benetrator
import time 
import os
# 
import sys
import subprocess
from pathlib import Path
import subprocess
from pathlib import Path
from scripts.build_docker import ensure_docker_image
from scripts.get_run_state import _update_docker_state
from scripts.registry import IMAGE
from scripts.run_engine import _launch_record
from scripts.save_result import collect_and_save_docker_artifacts
from scripts.stemcnv_docker import _stage_data
from scripts.utils import stop_container

def env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def setup_venv(
    venv_dir: str | Path = ".venv",
    requirements: str | Path = "requirements.txt",
) -> Path | None:

    try:
        venv_dir = Path(venv_dir)
        requirements = Path(requirements)

        # Resolve venv Python executable
        if sys.platform == "win32":
            venv_python = venv_dir / "Scripts" / "python.exe"
        else:
            venv_python = venv_dir / "bin" / "python"

        # Venv already exists
        if not venv_python.exists():

            # Create venv
            print(f"Creating venv: {venv_dir}")

            subprocess.check_call([
                sys.executable,
                "-m",
                "venv",
                str(venv_dir),
            ])
        else:
            print(f"Venv already exists: {venv_dir}")

        # Install requirements
        if requirements.exists():
            print(f"Installing requirements: {requirements}")

            subprocess.check_call([
                str(venv_python),
                "-m",
                "pip",
                "install",
                "--upgrade",
                "pip",
            ])

            subprocess.check_call([
                str(venv_python),
                "-m",
                "pip",
                "install",
                "-r",
                str(requirements),
            ])
        else:
            print(f"Requirements not found: {requirements}")

        return venv_python

    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}: {e}")
        return None

    except OSError as e:
        print(f"OS error while setting up venv: {e}")
        return None

    except Exception as e:
        print(f"Unexpected error while setting up venv: {e}")
        return None

def calc_seconds_to_hours_minutes(seconds: int | float) -> str:
    """Convert seconds (int or float) into HH:MM format."""
    if not isinstance(seconds, (int, float)) or seconds < 0:
        seconds = 0  

    total_seconds = int(seconds)  
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    return f"{hours:02d}:{minutes:02d}"


def start_engine():
    print("starting engine...")
    start=time.perf_counter()
    
    try:
        # CP FILES TO RUN DIR
        run_id, run_dir = _stage_data(in_dir="input")
        launch_result = _launch_record(run_id, run_dir)
        # RUN ENGINE
        last_log_message = None
        while not any(item in launch_result["status"] for item in ["complete", "failed"]):
            launch_result["status"], launch_result["events"], last_log_message = _update_docker_state(
                run_id, 
                launch_result["events"], 
                last_log_message,
            )
            time.sleep(1)

        # SAVE STATE LOCAL
        collect_and_save_docker_artifacts(
            mount_dir=run_dir,
            output_target_dir=Path("output"),
            as_zip=True,
        )

    except KeyboardInterrupt:
        # stop container
        stop_container(
            container_id_or_name=run_id
        )
        sys.exit(0)

    end = time.perf_counter()
    duration = end-start
    print("process finsiehd after", calc_seconds_to_hours_minutes(seconds=duration))


def main() -> None:
    print("performing wakeup...")
    # build docker image stemcnv local
    ensure_docker_image(
        image_name=IMAGE, 
        build_dir=os.path.abspath(Path(__file__).resolve().parent),
        env_path=os.path.abspath(".env"),
        dockerfile_path=os.path.abspath("Dockerfile"),
    )
    start_engine()
    print("process... done")




if __name__ == "__main__":
    setup_venv()
    from dotenv import load_dotenv
    from pathlib import Path
    import subprocess

    ROOT = Path(__file__).resolve().parent
    os.chdir(ROOT)
    sys.path.insert(0, str(ROOT))

    load_dotenv()
    main()
