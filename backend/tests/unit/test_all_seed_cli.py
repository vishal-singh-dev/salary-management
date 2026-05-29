from pathlib import Path

from app.seed import setup_cli


def test_all_seed_cli_defaults(monkeypatch) -> None:
    # Intent: combined seed command defaults match assessment-scale dataset setup.
    monkeypatch.setattr("sys.argv", ["salary-seed-all"])

    args = setup_cli.parse_args()

    assert args.count == 10_000
    assert args.random_seed == 2026
    assert args.batch_size == 1000
    assert args.first_names_file == Path("app/seed/setup_cli.py").resolve().parents[2] / "data" / "first_names.txt"


def test_all_seed_cli_accepts_employee_seed_options(monkeypatch, tmp_path) -> None:
    # Intent: engineers can tune volume and input files through the combined seed command.
    first_names = tmp_path / "first_names.txt"
    last_names = tmp_path / "last_names.txt"
    monkeypatch.setattr(
        "sys.argv",
        [
            "salary-seed-all",
            "--count",
            "25",
            "--random-seed",
            "99",
            "--batch-size",
            "5",
            "--first-names-file",
            str(first_names),
            "--last-names-file",
            str(last_names),
        ],
    )

    args = setup_cli.parse_args()

    assert args.count == 25
    assert args.random_seed == 99
    assert args.batch_size == 5
    assert args.first_names_file == first_names
    assert args.last_names_file == last_names
