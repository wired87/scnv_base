"""Production adapter for the canonical StemCNV-check Docker image."""
from __future__ import annotations

import os
import base64
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
import uuid

from scripts.registry import RUN_ROOT


class StemCNVDockerError(RuntimeError):
    pass


class ActiveStemCNVRunError(StemCNVDockerError):
    """Raised when the single memory-bounded worker already owns a run."""

import shutil
from pathlib import Path

import os
import shutil
from pathlib import Path

def stage_directory_tree(src_dir: Path, dst_dir: Path, copy_function=shutil.copy2):
    """
    Recursively copy src_dir → dst_dir preserving structure.
    After copying, print the full directory tree of dst_dir.
    """

    if not src_dir.is_dir():
        raise ValueError(f"Source directory does not exist: {src_dir}")

    print(f"\n[stage] Copying directory tree from:\n  {src_dir}\ninto:\n  {dst_dir}\n")

    dst_dir.mkdir(parents=True, exist_ok=True)

    # --- COPY PHASE ---
    for root, dirs, files in os.walk(src_dir):
        root_path = Path(root)
        rel_path = root_path.relative_to(src_dir)
        target_root = dst_dir / rel_path

        target_root.mkdir(parents=True, exist_ok=True)

        for file in files:
            src_file = root_path / file
            dst_file = target_root / file
            copy_function(src_file, dst_file)

    # --- PRINT STRUCTURE PHASE ---
    print("\n[stage] Final copied directory structure:\n")

    for root, dirs, files in os.walk(dst_dir):
        root_path = Path(root)
        rel_path = root_path.relative_to(dst_dir)

        # Print directory
        if rel_path == Path("."):
            print("[dir] /")
        else:
            print(f"[dir] {rel_path}")

        # Print files
        for file in files:
            print(f"  [file] {rel_path / file}")

        # Print subdirectories
        for d in dirs:
            print(f"  [subdir] {rel_path / d}")

    print("\n[stage] Copy complete.\n")


#!##


def _safe_relative(value: str) -> Path:
    path = Path(value.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Unsafe path in StemCNV config: {value}")
    return path


def _upload_relative_path(upload) -> Path:
    return _safe_relative(str(getattr(upload, "relative_path", None) or upload.name))


def _upload_bytes(upload) -> bytes:
    upload.seek(0)
    content = upload.read()
    upload.seek(0)
    return content


def _stage_data(in_dir: Path) -> tuple:
    # SET EXECUTION DIR
    ts = datetime.now().isoformat().replace(":", "-").replace(".", "-")
    run_id = f"{uuid.uuid4()}-{ts}"
    print("run ide created", run_id)

    run_dir = RUN_ROOT / run_id
    print("run_dir created", run_dir)

    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)

    #
    if not Path(in_dir).is_dir() or not len(os.listdir(os.path.abspath(in_dir))):
        in_dir = "example_input_data"
    in_dir = Path(in_dir)

    #

    """Stage only the canonical inputs, never outputs from a previous example run."""
    stage_directory_tree(
        src_dir=in_dir, 
        dst_dir=run_dir, 
    )
    return run_id, run_dir


def _link_or_copy(source: str, destination: str) -> str:
    """Hard-link when possible and safely copy individual cross-device files."""
    try:
        os.link(source, destination)
    except OSError:
        return shutil.copy2(source, destination)
    return destination


def _persist_artifacts(run_dir: Path) -> list[str]:
    stored = {}
    for path in run_dir.rglob("*"):
        relative = path.relative_to(run_dir)
        artifact_path = str(relative).replace("\\", "/")
        if not path.is_file() or not _is_final_artifact(artifact_path):
            continue
        content = path.read_bytes()
        if artifact_path.lower().endswith(".html"):
            content = _embed_report_images(content, lambda name: path.parent / "StemCNV-check-report-html_images" / name)
        stored[artifact_path] = content
    return stored


def _is_final_artifact(path: str) -> bool:
    """Return only researcher-facing results, never workflow working files."""
    normalized = path.lower()
    return (
        normalized.endswith(".stemcnv-check-report.html")
        or normalized.endswith(".xlsx")
        or (".cnv_calls." in normalized and normalized.endswith((".vcf", ".vcf.gz")))
    )

_REPORT_IMAGE = re.compile(
    rb"(?:\./)?StemCNV-check-report-html_images/+([A-Za-z0-9_.-]+\.png)"
)


def _embed_report_images(content: bytes, image_source) -> bytes:
    """Make a StemCNV HTML report portable by embedding its linked PNG plots."""
    cache: dict[bytes, bytes] = {}

    def replace(match: re.Match[bytes]) -> bytes:
        name = match.group(1)
        if name not in cache:
            source = image_source(name.decode("ascii"))
            try:
                image = source.read_bytes() if isinstance(source, Path) else bytes(source)
            except (FileNotFoundError, TypeError):
                return match.group(0)
            cache[name] = b"data:image/png;base64," + base64.b64encode(image)
        return cache[name]

    return _REPORT_IMAGE.sub(replace, content)




def _collect_events(log_text: str, existing: list[dict]) -> list[dict]:
    seen = {(event.get("type"), event.get("message")) for event in existing}
    events = list(existing)
    for raw in log_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        event_type = None
        message = line
        if line.startswith("localrule "):
            event_type = "step_started"
            message = line.removeprefix("localrule ").rstrip(":").replace("_", " ")
        elif " of " in line and " steps (" in line and line.endswith("done"):
            event_type = "progress"
        elif line.startswith("Finished job "):
            event_type = "step_finished"
        elif line.startswith("Complete log:"):
            event_type = "workflow_complete"
        elif "Error" in line or "Exception" in line:
            event_type = "error"
        if event_type and (event_type, message) not in seen:
            events.append({"type": event_type, "message": message, "at": datetime.now(timezone.utc).isoformat()})
            seen.add((event_type, message))
    return events[-500:]





"""
WASTELANDS

if not (in_dir / "config.yaml").is_file():
        raise ValueError(f"StemCNV example data is unavailable at {in_dir}")
    for name in ("config.yaml", "sample_table.tsv", "sample_table.xlsx"):
        source = in_dir / name
        if source.is_file():
            shutil.copy2(source, run_dir / name)
    for name in ("RAW", "static-data"):
        source = in_dir / name
        if source.is_dir():
            shutil.copytree(source, run_dir / name, copy_function=_link_or_copy)





"""