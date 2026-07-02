from mk8dx_item_alert.labels import (
    canonicalize_label,
    get_icon_path_for_label,
    model_labels,
)


def test_known_labels_keep_raw_model_names() -> None:
    assert model_labels() == (
        "Piranha-Plant",
        "Super-Horn",
        "FB",
        "Boomerang",
        "Minacle-Eight",
        "green-shell3",
    )


def test_minacle_eight_keeps_raw_label_and_maps_icon() -> None:
    assert get_icon_path_for_label("Minacle-Eight") == "Minacle-Eight.png"
    assert canonicalize_label("Minacle-Eight") == "miracle_eight"


def test_unknown_label_returns_none() -> None:
    assert get_icon_path_for_label("Banana") is None
    assert canonicalize_label("Banana") is None
