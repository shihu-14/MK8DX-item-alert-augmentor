import hashlib
import io
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


def _artifact(content: bytes, release_url: str = "") -> ModelArtifact:
    return ModelArtifact(
        role="item",
        version="test",
        filename="model.pt",
        sha256=hashlib.sha256(content).hexdigest(),
        size=len(content),
        dataset="test",
        labels=("Boomerang",),
        release_url=release_url,
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


def test_install_verifies_temporary_file_before_atomic_replace(
    tmp_path: Path,
) -> None:
    content = b"valid-model"
    artifact = _artifact(content, "https://example.test/model.pt")
    manifest = ModelManifest(1, "test", "published", (artifact,))

    paths = install_models(
        manifest,
        tmp_path,
        urlopen=lambda url, timeout: io.BytesIO(content),
    )

    assert paths == (tmp_path / "model.pt",)
    assert paths[0].read_bytes() == content
    assert not (tmp_path / "model.pt.part").exists()


@pytest.mark.parametrize(
    ("invalid_content", "error"),
    [(b"bad", "size"), (b"invalid-mod", "checksum")],
)
def test_failed_install_leaves_no_final_file_and_can_retry(
    tmp_path: Path,
    invalid_content: bytes,
    error: str,
) -> None:
    content = b"valid-model"
    artifact = _artifact(content, "https://example.test/model.pt")
    manifest = ModelManifest(1, "test", "published", (artifact,))

    with pytest.raises(ModelStoreError, match=error):
        install_models(
            manifest,
            tmp_path,
            urlopen=lambda url, timeout: io.BytesIO(invalid_content),
        )

    assert not (tmp_path / "model.pt").exists()
    assert not (tmp_path / "model.pt.part").exists()
    install_models(
        manifest,
        tmp_path,
        urlopen=lambda url, timeout: io.BytesIO(content),
    )
    assert (tmp_path / "model.pt").read_bytes() == content


def test_network_error_removes_stale_part_file(tmp_path: Path) -> None:
    content = b"valid-model"
    artifact = _artifact(content, "https://example.test/model.pt")
    manifest = ModelManifest(1, "test", "published", (artifact,))
    (tmp_path / "model.pt.part").write_bytes(b"stale")

    def fail(url, timeout):
        raise OSError("network unavailable")

    with pytest.raises(ModelStoreError, match="network unavailable"):
        install_models(manifest, tmp_path, urlopen=fail)

    assert not (tmp_path / "model.pt").exists()
    assert not (tmp_path / "model.pt.part").exists()
    install_models(
        manifest,
        tmp_path,
        urlopen=lambda url, timeout: io.BytesIO(content),
    )
    assert (tmp_path / "model.pt").read_bytes() == content
