import os
from pathlib import Path
import tempfile

import dotenv 
dotenv.load_dotenv()


IMAGE = os.getenv("STEMCNV_DOCKER_IMAGE", "stemcnv-check:1.0.0")
RUN_ROOT = Path(os.getenv("STEMCNV_RUN_ROOT", Path(tempfile.gettempdir()) / "stemcnv-runs"))
CACHE_VOLUME = os.getenv("STEMCNV_CACHE_VOLUME", "stemcnv-cache")
EXAMPLE_DATA_ROOT = Path(os.getenv("STEMCNV_EXAMPLE_DATA_DIR", "/var/lib/stemcnv-upstream/example_data"))
DOCKER_MEMORY_LIMIT = os.getenv("MEMORY_LIMIT", "2700m")
MEMORY_SWAP_LIMIT = os.getenv("STEMCNV_MEMORY_SWAP_LIMIT", "10g")
WORKFLOW_MEMORY_MB = os.getenv("STEMCNV_WORKFLOW_MEMORY_MB", "6500")
CORES = os.getenv("CORES", "6")

SNAKEMAKE_OPTIONS = os.getenv(
    "STEMCNV_SNAKEMAKE_OPTIONS",
    "--set-resources run_CBS:mem_mb=6500 combined_PennCNV_output:mem_mb=6500",
)
EXECUTION_MODE = os.getenv("STEMCNV_EXECUTION_MODE", "direct")
PROCESS_ROLE = os.getenv("STEMCNV_PROCESS_ROLE", "all")