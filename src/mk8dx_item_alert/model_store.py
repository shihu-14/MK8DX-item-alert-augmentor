"""Manifest-backed local model storage."""

from __future__ import annotations

import hashlib
import shutil
import tomllib
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from .config import PROJECT_ROOT

DEFAULT_MANIFEST_PATH = PROJECT_ROOT / "models" / "manifest.toml"


class ModelStoreError(RuntimeError):
    """Base error for model manifest and artifact failures."""


class ModelNotPublishedError(ModelStoreError):
    """Raised when a manifest entry has no approved release URL."""


@dataclass(frozen=True)
class ModelArtifact:
    role: str
    version: str
    filename: str
    sha256: str
    size: int
    dataset: str
    labels: tuple[str, ...]
    release_url: str

    def path_in(self, model_dir: Path) -> Path:
        return model_dir / self.filename


@dataclass(frozen=True)
class ModelManifest:
    schema_version: int
    release: str
    publication_status: str
    models: tuple[ModelArtifact, ...]

    def by_role(self, role: str) -> ModelArtifact:
        matches = [model for model in self.models if model.role == role]
        if len(matches) != 1:
            raise ModelStoreError(
                f"manifest must contain exactly one model for role {role!r}"
            )
        return matches[0]


def load_manifest(path: Path = DEFAULT_MANIFEST_PATH) -> ModelManifest:
    with path.open("rb") as handle:
        raw = tomllib.load(handle)

    models = tuple(
        ModelArtifact(
            role=str(entry["role"]),
            version=str(entry["version"]),
            filename=_validate_filename(str(entry["filename"])),
            sha256=_validate_sha256(str(entry["sha256"])),
            size=int(entry["size"]),
            dataset=str(entry["dataset"]),
            labels=tuple(str(label) for label in entry["labels"]),
            release_url=str(entry.get("release_url", "")),
        )
        for entry in raw.get("models", [])
    )
    if not models:
        raise ModelStoreError("manifest contains no models")

    return ModelManifest(
        schema_version=int(raw["schema_version"]),
        release=str(raw["release"]),
        publication_status=str(raw["publication_status"]),
        models=models,
    )


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_artifact(artifact: ModelArtifact, model_dir: Path) -> Path:
    path = artifact.path_in(model_dir)
    return _verify_artifact_path(artifact, path)


def _verify_artifact_path(artifact: ModelArtifact, path: Path) -> Path:
    if not path.is_file():
        raise ModelStoreError(f"model is missing: {path}")
    if path.stat().st_size != artifact.size:
        raise ModelStoreError(f"model size does not match manifest: {path}")
    if sha256_file(path) != artifact.sha256:
        raise ModelStoreError(f"model checksum does not match manifest: {path}")
    return path


def verify_models(manifest: ModelManifest, model_dir: Path) -> tuple[Path, ...]:
    return tuple(verify_artifact(model, model_dir) for model in manifest.models)


def install_models(
    manifest: ModelManifest,
    model_dir: Path,
    *,
    timeout_sec: float = 60.0,
    urlopen=urllib.request.urlopen,
) -> tuple[Path, ...]:
    model_dir.mkdir(parents=True, exist_ok=True)
    installed: list[Path] = []
    for artifact in manifest.models:
        destination = artifact.path_in(model_dir)
        if destination.exists():
            try:
                installed.append(verify_artifact(artifact, model_dir))
                continue
            except ModelStoreError:
                destination.unlink()
        if not artifact.release_url:
            raise ModelNotPublishedError(
                f"{artifact.filename} is pending publication; "
                "place an authorized copy in the model directory"
            )

        temporary = destination.with_suffix(destination.suffix + ".part")
        temporary.unlink(missing_ok=True)
        try:
            with urlopen(
                artifact.release_url,
                timeout=timeout_sec,
            ) as response, temporary.open("wb") as output:
                shutil.copyfileobj(response, output)
            _verify_artifact_path(artifact, temporary)
            temporary.replace(destination)
            installed.append(destination)
        except ModelStoreError:
            raise
        except OSError as error:
            raise ModelStoreError(
                f"model download failed for {artifact.filename}: {error}"
            ) from error
        finally:
            temporary.unlink(missing_ok=True)
    return tuple(installed)


def _validate_filename(filename: str) -> str:
    if not filename or Path(filename).name != filename:
        raise ModelStoreError(f"invalid model filename: {filename!r}")
    return filename


def _validate_sha256(value: str) -> str:
    lowered = value.lower()
    if len(lowered) != 64 or any(char not in "0123456789abcdef" for char in lowered):
        raise ModelStoreError("invalid SHA-256 value in manifest")
    return lowered
