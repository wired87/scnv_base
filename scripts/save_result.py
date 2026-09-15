from pathlib import Path

import zipfile
from typing import Callable, List, Union


def collect_and_save_docker_artifacts(
    mount_dir: Union[str, Path],
    output_target_dir: Union[str, Path],
    is_final_artifact_func: Callable[[str], bool] = None,
    embed_images_func: Callable[[bytes, Callable[[str], bytes]], bytes] = None,
    as_zip: bool = False,
    zip_filename: str = "artifacts.zip"
) -> List[Path]:
    #
    mount_path = Path(mount_dir).resolve()
    target_path = Path(output_target_dir).resolve()
    target_path.mkdir(parents=True, exist_ok=True)

    if not mount_path.exists():
        raise FileNotFoundError(f"Mount directory '{mount_path}' does not exist.")

    saved_file_paths: List[Path] = []

    # Standard-Fallback für Filter-Funktion, falls keine übergeben wurde
    if is_final_artifact_func is None:
        is_final_artifact_func = lambda p: True

    # 1. Sammeln & Verarbeiten aller relevanten Artefakte
    collected_artifacts = []  # List of tuples: (relative_str_path, raw_bytes)

    for file_path in mount_path.rglob("*"):
        if not file_path.is_file():
            continue

        relative_path = file_path.relative_to(mount_path)
        artifact_rel_str = str(relative_path).replace("\\", "/")

        # Filter anwenden
        if not is_final_artifact_func(artifact_rel_str):
            continue

        content = file_path.read_bytes()

        # HTML Bild-Einbettungs-Logik (falls Repositories HTML-Reports generieren)
        if artifact_rel_str.lower().endswith(".html") and embed_images_func:
            images_dir = file_path.parent / "StemCNV-check-report-html_images"
            
            def image_source_provider(image_name: str) -> bytes:
                img_path = images_dir / image_name
                if img_path.exists():
                    return img_path.read_bytes()
                return b""

            content = embed_images_func(content, image_source_provider)

        collected_artifacts.append((relative_path, content))

    if not collected_artifacts:
        print(f"[WARN] Keine Artefakte in '{mount_path}' gefunden.")
        return []

    # 2. Ausgeben: Entweder als ZIP oder als lokale Ordnerstruktur
    if as_zip:
        zip_full_path = target_path / zip_filename
        with zipfile.ZipFile(zip_full_path, "w", zipfile.ZIP_DEFLATED) as bundle:
            for rel_path, content in collected_artifacts:
                bundle.writestr(str(rel_path).replace("\\", "/"), content)
        saved_file_paths.append(zip_full_path)
    else:
        for rel_path, content in collected_artifacts:
            dest_file_path = target_path / rel_path
            dest_file_path.parent.mkdir(parents=True, exist_ok=True)
            dest_file_path.write_bytes(content)
            saved_file_paths.append(dest_file_path)

    print(f"[SUCCESS] {len(collected_artifacts)} Artefakt(e) erfolgreich lokal in '{target_path}' gespeichert.")
    return saved_file_paths