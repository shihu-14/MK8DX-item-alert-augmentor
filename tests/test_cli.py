from mk8dx_item_alert.cli import build_parser


def test_run_command_parses_documented_options() -> None:
    args = build_parser().parse_args(
        ["run", "--source", "video.mp4", "--no-save", "--profile"]
    )

    assert args.command == "run"
    assert args.source == "video.mp4"
    assert args.no_save is True
    assert args.profile is True
