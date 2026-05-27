from __future__ import annotations

import argparse
import time
from pathlib import Path

from app.core.database import SessionLocal
from app.seed.generator import generate_seed_records, load_names
from app.seed.persistence import (
    SeedPreconditionError,
    assert_empty_employee_dataset,
    current_exchange_rate_ids,
    persist_seed_data,
)


def parse_args() -> argparse.Namespace:
    data_directory = Path(__file__).resolve().parents[2] / "data"
    parser = argparse.ArgumentParser(description="Create the initial employee and salary dataset.")
    parser.add_argument("--count", type=int, default=10_000)
    parser.add_argument("--random-seed", type=int, default=2026)
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--first-names-file", type=Path, default=data_directory / "first_names.txt")
    parser.add_argument("--last-names-file", type=Path, default=data_directory / "last_names.txt")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started_at = time.perf_counter()

    with SessionLocal.begin() as session:
        assert_empty_employee_dataset(session)
        exchange_rate_ids = current_exchange_rate_ids(session)
        seed_data = generate_seed_records(
            count=args.count,
            random_seed=args.random_seed,
            first_names=load_names(args.first_names_file),
            last_names=load_names(args.last_names_file),
            exchange_rate_ids=exchange_rate_ids,
        )
        persist_seed_data(
            session,
            seed_data,
            random_seed=args.random_seed,
            batch_size=args.batch_size,
        )

    elapsed_seconds = time.perf_counter() - started_at
    print(
        f"Created {args.count} employees and salary records in "
        f"{elapsed_seconds:.2f}s using random seed {args.random_seed}."
    )


if __name__ == "__main__":
    try:
        main()
    except (SeedPreconditionError, ValueError) as error:
        raise SystemExit(str(error)) from error
