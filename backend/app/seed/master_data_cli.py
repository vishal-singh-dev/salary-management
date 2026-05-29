from __future__ import annotations

from app.core.database import SessionLocal
from app.seed.master_data import seed_fixed_master_data


def main() -> None:
    with SessionLocal.begin() as session:
        configured_count = seed_fixed_master_data(session)

    print(f"Ensured {configured_count} fixed master-data records exist.")


if __name__ == "__main__":
    main()
