from app.seed.exchange_rates import FIXED_RATE_SOURCE, fixed_exchange_rates
from app.seed.generator import required_currencies


def test_exchange_rate_master_data() -> None:
    # Intent: fixed FX master data covers every currency used by employee seeding.
    rates = fixed_exchange_rates()

    assert {rate.source_currency_code for rate in rates} == required_currencies()
    assert all(rate.target_currency_code == "USD" for rate in rates)
    assert all(rate.rate_to_usd > 0 for rate in rates)
    assert all(rate.effective_to is None for rate in rates)
    assert all(rate.rate_source == FIXED_RATE_SOURCE for rate in rates)

