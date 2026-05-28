from __future__ import annotations

from app.core.database import SessionLocal
from app.seed.exchange_rates import seed_fixed_exchange_rates


def main() -> None:
    with SessionLocal.begin() as session:
        configured_count = seed_fixed_exchange_rates(session)

    print(f"Ensured {configured_count} fixed current exchange rates exist.")


if __name__ == "__main__":
    main()

