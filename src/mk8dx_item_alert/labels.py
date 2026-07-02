"""Label and alert-icon mappings for the current MK8DX item model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LabelInfo:
    raw_label: str
    canonical_name: str
    display_name: str
    icon_path: str


LABELS: dict[str, LabelInfo] = {
    "Piranha-Plant": LabelInfo(
        raw_label="Piranha-Plant",
        canonical_name="piranha_plant",
        display_name="Piranha Plant",
        icon_path="Piranha-Plant.png",
    ),
    "Super-Horn": LabelInfo(
        raw_label="Super-Horn",
        canonical_name="super_horn",
        display_name="Super Horn",
        icon_path="Super-Horn.png",
    ),
    "FB": LabelInfo(
        raw_label="FB",
        canonical_name="fb",
        display_name="FB",
        icon_path="FB.png",
    ),
    "Boomerang": LabelInfo(
        raw_label="Boomerang",
        canonical_name="boomerang",
        display_name="Boomerang",
        icon_path="Boomerang.png",
    ),
    "Minacle-Eight": LabelInfo(
        raw_label="Minacle-Eight",
        canonical_name="miracle_eight",
        display_name="Miracle Eight",
        icon_path="Minacle-Eight.png",
    ),
    "green-shell3": LabelInfo(
        raw_label="green-shell3",
        canonical_name="triple_green_shell",
        display_name="Triple Green Shell",
        icon_path="Green-Shell3.png",
    ),
}


def get_icon_path_for_label(label: str) -> str | None:
    info = LABELS.get(label)
    return info.icon_path if info else None


def canonicalize_label(label: str) -> str | None:
    info = LABELS.get(label)
    return info.canonical_name if info else None


def model_labels() -> tuple[str, ...]:
    return tuple(LABELS)
