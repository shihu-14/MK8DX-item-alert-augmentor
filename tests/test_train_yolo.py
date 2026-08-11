import importlib.util
import json
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "train_yolo.py"
SPEC = importlib.util.spec_from_file_location("train_yolo", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
train_yolo = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(train_yolo)


def test_training_parser_exposes_seed_and_deterministic_options() -> None:
    args = train_yolo.build_parser().parse_args(
        ["--data", "data.yaml", "--seed", "17", "--no-deterministic"]
    )

    options = train_yolo.build_training_options(args)

    assert options["seed"] == 17
    assert options["deterministic"] is False


def test_training_metadata_records_inputs_without_running_yolo(
    tmp_path: Path,
) -> None:
    data = tmp_path / "data.yaml"
    model = tmp_path / "base.pt"
    data.write_text("names: [Boomerang]\n", encoding="utf-8")
    model.write_bytes(b"base-model")
    args = train_yolo.build_parser().parse_args(
        [
            "--data",
            str(data),
            "--model",
            str(model),
            "--name",
            "repro-run",
        ]
    )
    options = train_yolo.build_training_options(args)

    metadata = train_yolo.build_training_metadata(
        args,
        options,
        package_versions={"python": "test"},
    )
    run_directory = tmp_path / "run"
    run_directory.mkdir()
    metadata_path = train_yolo.write_training_metadata(run_directory, metadata)
    written = json.loads(metadata_path.read_text(encoding="utf-8"))

    assert written["dataset"]["config_path"] == str(data.resolve())
    assert len(written["dataset"]["config_sha256"]) == 64
    assert written["base_model"]["path"] == str(model.resolve())
    assert len(written["base_model"]["sha256"]) == 64
    assert written["training_options"]["name"] == "repro-run"
    assert written["package_versions"] == {"python": "test"}
