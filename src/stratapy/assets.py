"""Asset-level contractual cash flow models."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class LoanCashFlow:
    """Contractual cash flow for one monthly collection period.

    All monetary values use the same currency as the underlying loan balance.
    Values are kept at full precision; rounding should be applied only when
    presenting or exporting model results.
    """

    month: int
    beginning_balance: float
    scheduled_payment: float
    interest: float
    scheduled_principal: float
    ending_balance: float


@dataclass(frozen=True, slots=True)
class FixedRateLoan:
    """A fully amortising fixed-rate loan.

    Args:
        loan_id: Unique identifier used to trace the loan through the model.
        balance: Outstanding principal at the start of the projection.
        annual_rate: Nominal annual coupon expressed as a decimal. For example,
            6% is entered as ``0.06``.
        remaining_term_months: Number of contractual monthly payments remaining.
    """

    loan_id: str
    balance: float
    annual_rate: float
    remaining_term_months: int

    def __post_init__(self) -> None:
        if not isinstance(self.loan_id, str) or not self.loan_id.strip():
            raise ValueError("loan_id must be a non-empty string")
        if not isfinite(self.balance) or self.balance <= 0:
            raise ValueError("balance must be a positive finite number")
        if not isfinite(self.annual_rate) or self.annual_rate < 0:
            raise ValueError("annual_rate must be a non-negative finite number")
        if (
            isinstance(self.remaining_term_months, bool)
            or not isinstance(self.remaining_term_months, int)
            or self.remaining_term_months <= 0
        ):
            raise ValueError("remaining_term_months must be a positive integer")

    @property
    def monthly_rate(self) -> float:
        """Return the nominal annual coupon converted to a monthly rate."""

        return self.annual_rate / 12

    @property
    def scheduled_payment(self) -> float:
        """Return the level monthly payment required to amortise the loan."""

        if self.monthly_rate == 0:
            return self.balance / self.remaining_term_months

        growth_factor = (1 + self.monthly_rate) ** self.remaining_term_months
        return self.balance * self.monthly_rate * growth_factor / (growth_factor - 1)

    def amortisation_schedule(self) -> tuple[LoanCashFlow, ...]:
        """Generate the loan's contractual monthly amortisation schedule.

        The final period explicitly clears the remaining balance to avoid a
        floating-point residual. Credit events and voluntary prepayments are not
        included here; they will be applied by separate model components.
        """

        rows: list[LoanCashFlow] = []
        beginning_balance = self.balance
        level_payment = self.scheduled_payment

        for month in range(1, self.remaining_term_months + 1):
            interest = beginning_balance * self.monthly_rate

            if month == self.remaining_term_months:
                scheduled_principal = beginning_balance
            else:
                scheduled_principal = min(level_payment - interest, beginning_balance)

            scheduled_payment = interest + scheduled_principal
            ending_balance = max(beginning_balance - scheduled_principal, 0.0)

            rows.append(
                LoanCashFlow(
                    month=month,
                    beginning_balance=beginning_balance,
                    scheduled_payment=scheduled_payment,
                    interest=interest,
                    scheduled_principal=scheduled_principal,
                    ending_balance=ending_balance,
                )
            )
            beginning_balance = ending_balance

        return tuple(rows)

