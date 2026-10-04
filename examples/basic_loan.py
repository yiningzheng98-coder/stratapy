"""Generate and display a simple fixed-rate auto loan schedule."""

from stratapy import FixedRateLoan


def main() -> None:
    loan = FixedRateLoan(
        loan_id="AUTO-0001",
        balance=25_000,
        annual_rate=0.075,
        remaining_term_months=60,
    )

    print(f"Loan: {loan.loan_id}")
    print(f"Contractual monthly payment: {loan.scheduled_payment:,.2f}\n")
    print("Month | Beginning balance | Payment | Interest | Principal | Ending balance")
    print("-" * 79)

    for row in loan.amortisation_schedule()[:12]:
        print(
            f"{row.month:>5} | "
            f"{row.beginning_balance:>17,.2f} | "
            f"{row.scheduled_payment:>7,.2f} | "
            f"{row.interest:>8,.2f} | "
            f"{row.scheduled_principal:>9,.2f} | "
            f"{row.ending_balance:>14,.2f}"
        )


if __name__ == "__main__":
    main()

