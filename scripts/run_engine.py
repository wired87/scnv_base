from datetime import datetime, timezone
import pprint
import shutil
from scripts.utils import _docker_host_path, _run_docker


from scripts.registry import (
    DOCKER_MEMORY_LIMIT, 
    MEMORY_SWAP_LIMIT,
    CORES,
    WORKFLOW_MEMORY_MB,
    SNAKEMAKE_OPTIONS,
    CACHE_VOLUME,
    IMAGE
)

def _launch_record(run_id, run_dir) -> dict:
    events=[]
    try:
        result = _run_docker("run", "-d", "--name", run_id, "--privileged",
            "--memory", DOCKER_MEMORY_LIMIT, 
            "--memory-swap", MEMORY_SWAP_LIMIT,
            "--cpus", str(CORES),
            "-e", f"STEMCNV_LOCAL_CORES={CORES}",
            "-e", f"STEMCNV_MEMORY_MB={WORKFLOW_MEMORY_MB}",
            "-e", f"STEMCNV_SNAKEMAKE_OPTIONS={SNAKEMAKE_OPTIONS}",
            "-v", f"{_docker_host_path(run_dir)}:/work",
            "-v", f"{CACHE_VOLUME}:/cache", IMAGE, "run")
    except Exception as exc:
        print("Err onstart docker", exc)
        events = [*events, {"type": "failed", "message": str(exc),
                                        "at": datetime.now(timezone.utc).isoformat()}]
        
        shutil.rmtree(run_dir, ignore_errors=True)
    #        
    container_id = result.stdout.strip()
    
    status = "running"
    events = [*events, {"type": "run_started", "message": "Docker analysis started",
                                    "at": datetime.now(timezone.utc).isoformat()}]
    launch_result = {"status": status, "run_id": run_id, "container_id": container_id,
            "events": events}
    print("LAUNCH RESULT")
    pprint.pp(launch_result)
    return launch_result