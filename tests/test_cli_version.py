from __future__ import annotations

import pytest

from genus_egg.cli import build_parser


def test_cli_version_reports_package_version(capsys):
    parser = build_parser()

    with pytest.raises(SystemExit) as exit_info:
        parser.parse_args(["--version"])

    assert exit_info.value.code == 0
    assert "genus-egg 0.8.0" in capsys.readouterr().out
