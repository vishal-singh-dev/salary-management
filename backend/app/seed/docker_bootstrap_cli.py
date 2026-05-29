from __future__ import annotations

import os
import time
from pathlib import Path

from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.models import Employee
from app.seed.exchange_rates import seed_fixed_exchange_rates
from app.seed.generator import generate_seed_records, load_names
from app.seed.master_data import seed_fixed_master_data
from app.seed.persistence import current_exchange_rate_ids, persist_seed_data


def main() -> None:
    started_at = time.perf_counter()
    data_directory = Path(__file__).resolve().parents[2] / "data"
    employee_count = int(os.getenv("SEED_EMPLOYEE_COUNT", "10000"))
    random_seed = int(os.getenv("SEED_RANDOM_SEED", "2026"))
    batch_size = int(os.getenv("SEED_BATCH_SIZE", "1000"))

    with SessionLocal.begin() as session:
        exchange_rate_count = seed_fixed_exchange_rates(session)
        master_data_count = seed_fixed_master_data(session)
        existing_employee_count = session.scalar(select(func.count()).select_from(Employee)) or 0

        print(f"Ensured {exchange_rate_count} fixed current exchange rates exist.")
        print(f"Ensured {master_data_count} fixed master-data records exist.")

        if existing_employee_count:
            print(
                "Employee seed skipped because "
                f"{existing_employee_count} employees already exist."
            )
            return

        exchange_rate_ids = current_exchange_rate_ids(session)
        seed_data = generate_seed_records(
            count=employee_count,
            random_seed=random_seed,
            first_names=load_names(data_directory / "first_names.txt"),
            last_names=load_names(data_directory / "last_names.txt"),
            exchange_rate_ids=exchange_rate_ids,
        )
        persist_seed_data(
            session,
            seed_data,
            random_seed=random_seed,
            batch_size=batch_size,
        )

    elapsed_seconds = time.perf_counter() - started_at
    print(
        f"Created {employee_count} employees and salary records in "
        f"{elapsed_seconds:.2f}s using random seed {random_seed}."
    )


if __name__ == "__main__":
    main()
