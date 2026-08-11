import hashlib
from pathlib import Path

import pytest

from mk8dx_item_alert.model_store import (
    ModelArtifact,
    ModelManifest,
    ModelNotPublishedError,
    ModelStoreError,
    install_models,
    load_manifest,
    verify_models,
)


def _artifact(content: bytes) -> ModelArtifact:
    return ModelArtifact(
        role="item",
        version="test",
        filename="model.pt",
        sha256=hashlib.sha256(content).hexdigest(),
        size=len(content),
        dataset="test",
        labels=("Boomerang",),
        release_url="",
    )


def test_repository_manifest_has_one_item_and_one_gate_model() -> None:
    manifest = load_manifest()

    assert manifest.publication_status == "pending-rights-review"
    assert manifest.by_role("item").labels[0] == "Boomerang"
    assert manifest.by_role("gate").labels == ("Face",)


def test_verify_models_checks_size_and_hash(tmp_path: Path) -> None:
    content = b"model"
    artifact = _artifact(content)
    (tmp_path / artifact.filename).write_bytes(content)
    manifest = ModelManifest(1, "test", "local", (artifact,))

    assert verify_models(manifest, tmp_path) == (tmp_path / "model.pt",)
    (tmp_path / "model.pt").write_bytes(b"wrong")
    with pytest.raises(ModelStoreError, match="size"):
        verify_models(manifest, tmp_path)


def test_install_refuses_unpublished_missing_model(tmp_path: Path) -> None:
    manifest = ModelManifest(1, "test", "pending", (_artifact(b"model"),))

    with pytest.raises(ModelNotPublishedError, match="pending publication"):
        install_models(manifest, tmp_path)
