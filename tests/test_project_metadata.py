import tomllib
from pathlib import Path


def test_lap_is_only_in_tracking_extra() -> None:
    project_root = Path(__file__).resolve().parents[1]
    with (project_root / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)["project"]

    assert all("lap" not in dependency for dependency in project["dependencies"])
    assert any(
        dependency.startswith("lap>=")
        for dependency in project["optional-dependencies"]["tracking"]
    )
