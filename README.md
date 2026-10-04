# StrataPy

**An open-source cash flow and valuation engine for asset-backed securities.**

StrataPy is a Python project for modelling the full life cycle of an asset-backed security (ABS): from loan-level contractual payments and credit assumptions to collateral cash flows, tranche waterfalls, and valuation outputs.

The first release will focus on a fixed-rate auto loan ABS with senior, mezzanine, and equity tranches. The project is designed to be transparent, testable, and useful for structured finance analysis, scenario testing, and portfolio demonstrations.

> **Project status:** early development. Fixed-rate contractual loan amortisation is implemented; credit assumptions, portfolio aggregation, and tranche waterfalls are next.

## Why StrataPy?

Structured finance models are often built in spreadsheets, which makes them difficult to audit, extend, and test systematically. StrataPy aims to express the same mechanics in readable Python while keeping every major cash flow assumption explicit.

The project will demonstrate:

- Asset-level amortisation and aggregation
- Prepayment, default, loss, and recovery modelling
- Priority-of-payments logic
- Credit enhancement through subordination, excess spread, and reserves
- Tranche valuation and risk metrics
- Base, upside, and stress scenario analysis
- Reproducible model validation with automated tests

## Model Overview

```text
Loan-level contractual cash flows
                |
                v
 Prepayment / Default / Recovery assumptions
                |
                v
       Collateral cash flow engine
                |
                v
 Fees -> Interest waterfall -> Principal waterfall -> Loss allocation
                |
                v
      Class A / Class B / Equity cash flows
                |
                v
       Price / Yield / WAL / Expected Loss
```

## Initial Transaction Scope

The minimum viable model will represent a simplified auto loan ABS with the following capital structure:

| Component | Role | Payment priority |
|---|---|---:|
| Senior fees | Servicing and transaction expenses | 1 |
| Class A | Senior notes | 2 |
| Class B | Mezzanine notes | 3 |
| Equity | Residual certificate | 4 |

The initial waterfall will use sequential principal allocation. Pro-rata allocation and performance-based triggers are planned extensions.

## Core Modelling Assumptions

### Contractual cash flows

Each loan will be modelled using its outstanding balance, annual coupon, remaining term, and monthly payment schedule. Fixed-rate fully amortising loans will form the initial asset universe.

### Prepayments

Annualised conditional prepayment rate (CPR) will be converted to a monthly single monthly mortality rate (SMM):

```text
SMM = 1 - (1 - CPR)^(1/12)
```

Prepayments will reduce the performing balance after scheduled principal payments.

### Defaults and recoveries

Annualised conditional default rate (CDR) will be converted to a monthly default rate using the same convention:

```text
MDR = 1 - (1 - CDR)^(1/12)
```

Defaulted principal will be removed from the performing pool. Recoveries will be determined by a recovery-rate assumption and paid after a configurable recovery lag. Unrecovered principal will become a realised loss.

### Waterfall

Available funds will be allocated according to a defined priority of payments. The first release will include:

1. Senior fees and servicing expenses
2. Class A interest
3. Class B interest
4. Class A principal
5. Class B principal
6. Residual cash flow to equity

Losses will be allocated in reverse order of seniority: equity first, followed by Class B and then Class A.

### Valuation

Tranche value will be calculated as the present value of projected cash flows:

```text
PV = sum(CF_t / (1 + r / 12)^t)
```

where `CF_t` is the tranche cash flow in month `t` and `r` is the annual discount rate. Additional outputs will include yield, weighted average life (WAL), and expected loss.

## Planned Outputs

For each tranche, the model will produce:

- Monthly interest and principal cash flows
- Ending note balance
- Principal writedowns and realised losses
- Present value and clean price
- Internal rate of return
- Weighted average life
- Expected loss as a percentage of original balance
- Credit enhancement over time

Portfolio-level outputs will include collateral balance, scheduled principal, prepayments, defaults, recoveries, cumulative losses, and excess spread.

## Scenario Analysis

The example transaction will include three transparent scenarios:

| Scenario | CPR | CDR | Recovery rate | Purpose |
|---|---:|---:|---:|---|
| Upside | Higher | Lower | Higher | Strong borrower performance |
| Base | Central assumption | Central assumption | Central assumption | Expected performance |
| Stress | Lower | Higher | Lower | Downside credit analysis |

Exact assumptions will be documented alongside the synthetic loan pool rather than embedded silently in the model.

## Getting Started

StrataPy requires Python 3.11 or later. After cloning the repository, create a virtual environment and install the package with its development tools:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python -m pytest
```

Run the first loan-level example:

```powershell
.\.venv\Scripts\python examples\basic_loan.py
```

The example creates a five-year fixed-rate auto loan and prints the first twelve months of its contractual amortisation schedule.

## Current Python Interface

Contractual loan cash flows can be generated directly:

```python
from stratapy import FixedRateLoan

loan = FixedRateLoan(
    loan_id="AUTO-0001",
    balance=25_000,
    annual_rate=0.075,
    remaining_term_months=60,
)

schedule = loan.amortisation_schedule()
print(schedule[0])
```

## Planned Deal Interface

The public API is expected to follow a simple workflow:

```python
from stratapy import Assumptions, Deal, LoanPool

pool = LoanPool.from_csv("data/synthetic_auto_loans.csv")

assumptions = Assumptions(
    cpr=0.08,
    cdr=0.03,
    recovery_rate=0.50,
    recovery_lag_months=3,
)

deal = Deal.from_yaml("examples/auto_abs/deal.yml")
results = deal.run(pool=pool, assumptions=assumptions)

print(results.tranche_summary())
```

This interface is illustrative and may evolve as the engine is implemented.

## Proposed Repository Structure

```text
stratapy/
|-- src/stratapy/
|   |-- assets.py          # Loan amortisation and asset cash flows
|   |-- assumptions.py     # CPR, CDR, recovery, and scenario inputs
|   |-- pool.py            # Portfolio aggregation
|   |-- waterfall.py       # Priority-of-payments engine
|   |-- tranches.py        # Note balances, interest, and losses
|   |-- valuation.py       # PV, yield, WAL, and expected loss
|   `-- scenarios.py       # Scenario and sensitivity analysis
|-- examples/
|   `-- auto_abs/          # Example deal definition and notebook
|-- data/
|   `-- synthetic_auto_loans.csv
|-- tests/
|-- app/                   # Planned interactive dashboard
|-- pyproject.toml
`-- README.md
```

## Roadmap

- [x] Define project scope and modelling conventions
- [x] Implement fixed-rate loan amortisation
- [ ] Add CPR, CDR, recovery rate, and recovery lag assumptions
- [ ] Aggregate loan-level collateral cash flows
- [ ] Implement sequential-pay tranche waterfall
- [ ] Add fees, reserve account, and excess spread
- [ ] Calculate PV, yield, WAL, and expected loss
- [ ] Create base, upside, and stress scenarios
- [ ] Add unit tests and cash flow reconciliation checks
- [ ] Publish a worked example in Jupyter
- [ ] Build an interactive Streamlit dashboard
- [ ] Add pro-rata waterfalls and performance triggers
- [ ] Add Monte Carlo credit simulations

## Validation Approach

The model will include tests for both software correctness and financial consistency. Key checks will include:

- Beginning balance minus principal reductions equals ending balance
- Asset cash inflows reconcile to fees, note payments, residual cash, and account movements
- Note balances never fall below zero
- Principal paid never exceeds principal outstanding
- Loss allocation follows reverse seniority
- Zero-default and zero-prepayment cases match deterministic benchmark schedules
- Stressed assumptions do not produce unexplained cash creation or loss

## Data

The repository will use a synthetic loan-level dataset so that the complete example can be shared publicly without exposing confidential or proprietary information. The generator and all data assumptions will be documented for reproducibility.

## Intended Audience

StrataPy is intended for:

- Structured finance and asset-backed finance professionals
- Credit analysts and fixed-income investors
- Valuation and risk practitioners
- Students learning securitisation cash flow mechanics
- Developers interested in transparent financial modelling

## Disclaimer

This project is for educational and research purposes only. It does not constitute investment advice, a recommendation, or an offer to buy or sell any security. The synthetic transaction and assumptions do not represent an actual issuer or deal.

## Contributing

The project is at an early stage. Suggestions on modelling conventions, waterfall design, testing, and documentation are welcome through GitHub issues and pull requests once the first working version is available.
