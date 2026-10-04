"""Tests for contractual asset cash flows."""

import pytest

from stratapy import FixedRateLoan


def test_monthly_payment_matches_known_mortgage_example() -> None:
    loan = FixedRateLoan(
        loan_id="TEST-001",
        balance=100_000,
        annual_rate=0.06,
        remaining_term_months=360,
    )

    assert loan.scheduled_payment == pytest.approx(599.550525, abs=1e-6)


def test_schedule_amortises_balance_to_zero() -> None:
    loan = FixedRateLoan(
        loan_id="AUTO-001",
        balance=25_000,
        annual_rate=0.075,
        remaining_term_months=60,
    )

    schedule = loan.amortisation_schedule()

    assert len(schedule) == 60
    assert schedule[0].beginning_balance == 25_000
    assert schedule[-1].ending_balance == 0
    assert sum(row.scheduled_principal for row in schedule) == pytest.approx(25_000)

    for row in schedule:
        assert row.beginning_balance - row.scheduled_principal == pytest.approx(
            row.ending_balance
        )
        assert row.interest + row.scheduled_principal == pytest.approx(
            row.scheduled_payment
        )


def test_zero_coupon_loan_has_equal_principal_payments() -> None:
    loan = FixedRateLoan(
        loan_id="ZERO-001",
        balance=1_200,
        annual_rate=0,
        remaining_term_months=12,
    )

    schedule = loan.amortisation_schedule()

    assert loan.scheduled_payment == 100
    assert all(row.interest == 0 for row in schedule)
    assert all(row.scheduled_principal == pytest.approx(100) for row in schedule)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("loan_id", ""),
        ("balance", 0),
        ("balance", float("inf")),
        ("annual_rate", -0.01),
        ("remaining_term_months", 0),
        ("remaining_term_months", 12.5),
    ],
)
def test_invalid_loan_inputs_raise_value_error(field: str, value: object) -> None:
    inputs: dict[str, object] = {
        "loan_id": "TEST-001",
        "balance": 10_000,
        "annual_rate": 0.05,
        "remaining_term_months": 36,
    }
    inputs[field] = value

    with pytest.raises(ValueError):
        FixedRateLoan(**inputs)  # type: ignore[arg-type]

